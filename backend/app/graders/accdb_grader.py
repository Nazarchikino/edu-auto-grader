import re
import shutil
import struct
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from access_parser.access_parser import (  # type: ignore[import-untyped]
    PAGE_SIZE_V4,
    SYSTEM_TABLE_FLAGS,
    AccessParser,
)
from access_parser.parsing_primitives import (  # type: ignore[import-untyped]
    TDEF_HEADER,
    parse_table_data,
    parse_table_head,
)
from access_parser.utils import (  # type: ignore[import-untyped]
    TYPE_BINARY,
    TYPE_BOOLEAN,
    TYPE_COMPLEX,
    TYPE_DATETIME,
    TYPE_FLOAT32,
    TYPE_FLOAT64,
    TYPE_GUID,
    TYPE_INT8,
    TYPE_INT16,
    TYPE_INT32,
    TYPE_MEMO,
    TYPE_MONEY,
    TYPE_OLE,
    TYPE_TEXT,
    TYPE_96_bit_17_BYTES,
)
from construct import ConstructError  # type: ignore[import-untyped]

from app.core.exceptions import GradingError, InvalidFileFormatError
from app.graders.base import BaseGrader
from app.models.course import PracticalFormat
from app.schemas.grading import (
    CriterionResult,
    GradingReport,
    GradingRule,
    GradingRuleType,
)

_ACCESS_HEADER_MAGIC = b"\x00\x01\x00\x00"
_SYSTEM_TABLE_PREFIXES: tuple[str, ...] = ("msys", "usys", "~")
_DB_WIDE_TARGETS: frozenset[str] = frozenset(
    {"database", "db", "schema", "all", "any", "*", "tables", "tables.count"}
)
_TABLE_COLUMN_COUNT_SUFFIX_PATTERN = re.compile(
    r"^(.+?)\.(columns|cols|fields|column_count)$",
    re.IGNORECASE,
)
_COLUMN_TARGET_SPLIT_PATTERN = re.compile(r"[.!:]")
_EXPECTED_TYPE_SIZE_PATTERN = re.compile(
    r"^\s*([a-zA-Zа-яА-ЯіїєґІЇЄҐ0-9_/\-\s]+?)(?:\(\s*(\d+)\s*\))?\s*$"
)
_MDB_CREATE_TABLE_PATTERN = re.compile(
    r"CREATE\s+TABLE\s+\[?([^\]\s(\"']+)\]?\s*\((.*?)\)\s*;",
    re.IGNORECASE | re.DOTALL,
)

_TYPE_CODE_TO_CANONICAL: dict[int, str] = {
    int(TYPE_BOOLEAN): "BOOLEAN",
    int(TYPE_INT8): "BYTE",
    int(TYPE_INT16): "INTEGER",
    int(TYPE_INT32): "LONG",
    int(TYPE_MONEY): "CURRENCY",
    int(TYPE_FLOAT32): "SINGLE",
    int(TYPE_FLOAT64): "DOUBLE",
    int(TYPE_DATETIME): "DATETIME",
    int(TYPE_BINARY): "BINARY",
    int(TYPE_TEXT): "TEXT",
    int(TYPE_OLE): "OLE",
    int(TYPE_MEMO): "MEMO",
    int(TYPE_GUID): "GUID",
    int(TYPE_96_bit_17_BYTES): "DECIMAL",
    int(TYPE_COMPLEX): "COMPLEX",
}

_CANONICAL_TYPE_ALIASES: dict[str, frozenset[str]] = {
    "BOOLEAN": frozenset(
        {"boolean", "bool", "yes/no", "yesno", "bit", "logical", "так/ні"}
    ),
    "BYTE": frozenset(
        {"byte", "int8", "tinyint", "uint8", "number", "integer", "numeric"}
    ),
    "INTEGER": frozenset(
        {
            "integer",
            "int",
            "int16",
            "smallint",
            "short",
            "number",
            "numeric",
            "ціле",
        }
    ),
    "LONG": frozenset(
        {
            "long",
            "long integer",
            "longint",
            "int32",
            "integer",
            "int",
            "number",
            "numeric",
            "довге ціле",
        }
    ),
    "AUTONUMBER": frozenset(
        {
            "autonumber",
            "auto_number",
            "auto",
            "counter",
            "serial",
            "identity",
            "long",
            "long integer",
            "longint",
            "int32",
            "integer",
            "int",
            "number",
            "numeric",
            "лічильник",
        }
    ),
    "CURRENCY": frozenset(
        {
            "currency",
            "money",
            "decimal",
            "numeric",
            "number",
            "грошовий",
        }
    ),
    "SINGLE": frozenset(
        {
            "single",
            "float",
            "float32",
            "real",
            "double",
            "number",
            "numeric",
            "decimal",
        }
    ),
    "DOUBLE": frozenset(
        {
            "double",
            "float64",
            "float",
            "real",
            "number",
            "numeric",
            "decimal",
            "числовий",
        }
    ),
    "DATETIME": frozenset(
        {
            "datetime",
            "date/time",
            "date",
            "time",
            "timestamp",
            "дата/час",
            "дата",
        }
    ),
    "BINARY": frozenset({"binary", "varbinary", "bytes", "raw"}),
    "TEXT": frozenset(
        {
            "text",
            "short text",
            "shorttext",
            "varchar",
            "nvarchar",
            "char",
            "nchar",
            "string",
            "str",
            "текст",
            "короткий текст",
        }
    ),
    "OLE": frozenset(
        {
            "ole",
            "ole object",
            "oleobject",
            "blob",
            "longbinary",
            "image",
            "attachment",
        }
    ),
    "MEMO": frozenset(
        {
            "memo",
            "long text",
            "longtext",
            "ntext",
            "clob",
            "text",
            "string",
            "довгий текст",
            "hyperlink",
            "гіперпосилання",
        }
    ),
    "GUID": frozenset(
        {
            "guid",
            "uuid",
            "replicationid",
            "replication id",
            "uniqueidentifier",
        }
    ),
    "DECIMAL": frozenset(
        {
            "decimal",
            "numeric",
            "dec",
            "number",
            "double",
            "float",
            "currency",
        }
    ),
    "COMPLEX": frozenset({"complex", "multivalued", "attachment", "long", "int32"}),
}

_NAME_TO_TYPE_CODE: dict[str, tuple[int, bool, bool, int]] = {
    # (type_code, is_fixed, is_autonumber, default_length)
    "AUTONUMBER": (int(TYPE_INT32), True, True, 4),
    "COUNTER": (int(TYPE_INT32), True, True, 4),
    "LONG": (int(TYPE_INT32), True, False, 4),
    "LONG INTEGER": (int(TYPE_INT32), True, False, 4),
    "INT32": (int(TYPE_INT32), True, False, 4),
    "INT": (int(TYPE_INT32), True, False, 4),
    "INTEGER": (int(TYPE_INT16), True, False, 2),
    "SMALLINT": (int(TYPE_INT16), True, False, 2),
    "SHORT": (int(TYPE_INT16), True, False, 2),
    "INT16": (int(TYPE_INT16), True, False, 2),
    "BYTE": (int(TYPE_INT8), True, False, 1),
    "INT8": (int(TYPE_INT8), True, False, 1),
    "BOOLEAN": (int(TYPE_BOOLEAN), True, False, 1),
    "BOOL": (int(TYPE_BOOLEAN), True, False, 1),
    "YES/NO": (int(TYPE_BOOLEAN), True, False, 1),
    "CURRENCY": (int(TYPE_MONEY), True, False, 8),
    "MONEY": (int(TYPE_MONEY), True, False, 8),
    "SINGLE": (int(TYPE_FLOAT32), True, False, 4),
    "FLOAT": (int(TYPE_FLOAT32), True, False, 4),
    "DOUBLE": (int(TYPE_FLOAT64), True, False, 8),
    "FLOAT64": (int(TYPE_FLOAT64), True, False, 8),
    "NUMBER": (int(TYPE_FLOAT64), True, False, 8),
    "NUMERIC": (int(TYPE_96_bit_17_BYTES), False, False, 17),
    "DECIMAL": (int(TYPE_96_bit_17_BYTES), False, False, 17),
    "DATETIME": (int(TYPE_DATETIME), True, False, 8),
    "DATE/TIME": (int(TYPE_DATETIME), True, False, 8),
    "DATE": (int(TYPE_DATETIME), True, False, 8),
    "BINARY": (int(TYPE_BINARY), False, False, 255),
    "TEXT": (int(TYPE_TEXT), False, False, 255),
    "SHORT TEXT": (int(TYPE_TEXT), False, False, 255),
    "VARCHAR": (int(TYPE_TEXT), False, False, 255),
    "STRING": (int(TYPE_TEXT), False, False, 255),
    "MEMO": (int(TYPE_MEMO), False, False, 0),
    "LONG TEXT": (int(TYPE_MEMO), False, False, 0),
    "HYPERLINK": (int(TYPE_MEMO), False, False, 0),
    "OLE": (int(TYPE_OLE), False, False, 0),
    "GUID": (int(TYPE_GUID), True, False, 16),
    "UUID": (int(TYPE_GUID), True, False, 16),
}


@dataclass(frozen=True, slots=True)
class AccdbColumnSchema:
    """Метадані окремого стовпця таблиці Microsoft Access (.accdb)."""

    name: str
    type_code: int
    canonical_type: str
    aliases: frozenset[str]
    is_autonumber: bool = False
    can_be_null: bool = True
    is_fixed_length: bool = False
    length: int = 0
    is_primary_key: bool = False


@dataclass(frozen=True, slots=True)
class AccdbTableSchema:
    """Схема окремої користувацької таблиці Microsoft Access (.accdb)."""

    name: str
    columns: dict[str, AccdbColumnSchema]
    primary_keys: tuple[str, ...] = ()

    def find_column(self, column_name: str) -> AccdbColumnSchema | None:
        """Повертає стовпець таблиці за назвою (без урахування регістру)."""
        cleaned = _strip_identifiers(column_name)
        if not cleaned:
            return None
        if cleaned in self.columns:
            return self.columns[cleaned]
        cleaned_cf = cleaned.casefold()
        for col in self.columns.values():
            if col.name.casefold() == cleaned_cf:
                return col
        return None


@dataclass(frozen=True, slots=True)
class AccdbDatabaseSchema:
    """Каталог користувацьких таблиць та їхніх полів, витягнутий із файлу .accdb."""

    version: int
    tables: dict[str, AccdbTableSchema]

    def find_table(self, table_name: str) -> AccdbTableSchema | None:
        """Повертає схему таблиці за її назвою (без урахування регістру)."""
        cleaned = _strip_identifiers(table_name)
        if not cleaned:
            return None
        if cleaned in self.tables:
            return self.tables[cleaned]
        cleaned_cf = cleaned.casefold()
        for table in self.tables.values():
            if table.name.casefold() == cleaned_cf:
                return table
        return None


class AccdbGrader(BaseGrader):
    """Стратегія детермінованої автоперевірки баз даних Microsoft Access (.accdb)."""

    format_type: PracticalFormat = PracticalFormat.ACCDB

    def evaluate(
        self,
        *,
        file_path: Path | None = None,
        raw_code: str | None = None,
        rules: list[GradingRule],
        variant_data: dict[str, object],
    ) -> GradingReport:
        """Виконує інспекцію таблиць, стовпців та їхніх типів даних у файлі .accdb."""
        resolved_path = self.require_file_path(file_path, expected_suffix=".accdb")
        schema = self._extract_database_schema(resolved_path)

        results: list[CriterionResult] = []
        for rule in rules:
            resolved_expected = self.resolve_expected(rule.expected, variant_data)
            resolved_target = self.resolve_expected(rule.target, variant_data)
            result = self._evaluate_rule(
                schema=schema,
                rule=rule,
                target=resolved_target,
                expected=resolved_expected,
            )
            results.append(result)

        return self.build_report(results)

    def _extract_database_schema(self, file_path: Path) -> AccdbDatabaseSchema:
        """Зчитує схему таблиць та полів .accdb через access-parser (або mdbtools CLI)."""
        try:
            raw_bytes = file_path.read_bytes()
        except OSError as exc:
            raise InvalidFileFormatError(
                f"Не вдалося прочитати файл бази даних Access '{file_path.name}'.",
                context={"file_name": file_path.name, "error": str(exc)},
            ) from exc

        if len(raw_bytes) < 32 or not raw_bytes.startswith(_ACCESS_HEADER_MAGIC):
            raise InvalidFileFormatError(
                f"Файл '{file_path.name}' не є коректною базою даних Microsoft Access (.accdb): "
                "відсутній заголовок Jet/ACE.",
                context={"file_name": file_path.name},
            )

        try:
            return self._parse_with_access_parser(file_path)
        except InvalidFileFormatError:
            raise
        except Exception as primary_exc:
            fallback_schema = self._try_parse_with_mdbtools(file_path)
            if fallback_schema is not None:
                return fallback_schema

            raise InvalidFileFormatError(
                f"Не вдалося розібрати структуру бази даних Access '{file_path.name}': "
                "файл пошкоджений або має непідтримуваний формат сторінок.",
                context={"file_name": file_path.name, "error": str(primary_exc)},
            ) from primary_exc

    def _parse_with_access_parser(self, file_path: Path) -> AccdbDatabaseSchema:
        """Витягує таблиці, стовпці, типи даних та первинні ключі через access-parser."""
        try:
            parser = AccessParser(str(file_path))
        except (
            ConstructError,
            ValueError,
            KeyError,
            IndexError,
            TypeError,
            struct.error,
            OSError,
        ) as exc:
            raise InvalidFileFormatError(
                f"Не вдалося відкрити базу даних Access '{file_path.name}': {exc}",
                context={"file_name": file_path.name, "error": str(exc)},
            ) from exc

        if not isinstance(getattr(parser, "extra_props", None), dict):
            parser.extra_props = {}

        catalog_obj: object = getattr(parser, "catalog", None)
        if not isinstance(catalog_obj, dict):
            raise InvalidFileFormatError(
                f"Каталог MSysObjects у файлі '{file_path.name}' відсутній або пошкоджений.",
                context={"file_name": file_path.name},
            )

        version_raw: object = getattr(parser, "version", 4)
        version = int(version_raw) if isinstance(version_raw, int) else 4
        page_size_raw: object = getattr(parser, "page_size", PAGE_SIZE_V4)
        page_size = int(page_size_raw) if isinstance(page_size_raw, int) else int(PAGE_SIZE_V4)
        table_defs_obj: object = getattr(parser, "_table_defs", {})
        table_defs: dict[int, bytes] = (
            table_defs_obj if isinstance(table_defs_obj, dict) else {}
        )
        extra_props: dict[str, object] = (
            parser.extra_props if isinstance(parser.extra_props, dict) else {}
        )

        tables: dict[str, AccdbTableSchema] = {}
        for raw_name, raw_page_id in catalog_obj.items():
            if not isinstance(raw_name, str):
                continue
            table_name = raw_name.strip()
            if not table_name or _is_system_table_name(table_name):
                continue

            page_id = int(raw_page_id) if isinstance(raw_page_id, int) else None
            table_schema = self._extract_single_table_schema(
                parser=parser,
                table_name=table_name,
                page_id=page_id,
                version=version,
                page_size=page_size,
                table_defs=table_defs,
                extra_props=extra_props,
            )
            if table_schema is not None:
                tables[table_name] = table_schema

        return AccdbDatabaseSchema(version=version, tables=tables)

    def _extract_single_table_schema(
        self,
        *,
        parser: AccessParser,
        table_name: str,
        page_id: int | None,
        version: int,
        page_size: int,
        table_defs: dict[int, bytes],
        extra_props: dict[str, object],
    ) -> AccdbTableSchema | None:
        """Безпечно зчитує метадані стовпців окремої таблиці Access."""
        # Спроба 1: Прямий розбір сторінки визначення таблиці (TDEF), стійкий до помилок індексів
        if page_id is not None:
            page_offset = page_id * page_size
            tdef_bytes = table_defs.get(page_offset)
            if isinstance(tdef_bytes, (bytes, bytearray)):
                direct_schema = self._parse_tdef_bytes(
                    table_name=table_name,
                    tdef_bytes=bytes(tdef_bytes),
                    version=version,
                    page_size=page_size,
                    table_defs=table_defs,
                    table_props=extra_props.get(table_name),
                )
                if direct_schema is not None:
                    return direct_schema

        # Спроба 2: Через стандартний метод parser.get_table(table_name)
        try:
            access_table: object = parser.get_table(table_name)
        except Exception:
            access_table = None

        if access_table is None:
            return None

        raw_columns: object = getattr(access_table, "columns", None)
        if not isinstance(raw_columns, dict):
            return None

        raw_pks: object = getattr(access_table, "primary_keys", ())
        pk_names: tuple[str, ...] = (
            tuple(str(pk) for pk in raw_pks if isinstance(pk, str))
            if isinstance(raw_pks, (list, tuple))
            else ()
        )
        pk_casefold = {pk.casefold() for pk in pk_names}

        columns: dict[str, AccdbColumnSchema] = {}
        for col_obj in raw_columns.values():
            col_schema = self._build_column_schema(col_obj, pk_casefold)
            if col_schema is not None:
                columns[col_schema.name] = col_schema

        return AccdbTableSchema(
            name=table_name,
            columns=columns,
            primary_keys=pk_names,
        )

    def _parse_tdef_bytes(
        self,
        *,
        table_name: str,
        tdef_bytes: bytes,
        version: int,
        page_size: int,
        table_defs: dict[int, bytes],
        table_props: object,
    ) -> AccdbTableSchema | None:
        """Розбирає заголовок та масив стовпців TDEF-сторінки таблиці."""
        try:
            table_header = parse_table_head(tdef_bytes, version=version)
            header_end = int(table_header.tdef_header_end)
            merged_data = tdef_bytes[header_end:]

            next_ptr = int(table_header.TDEF_header.next_page_ptr)
            visited_ptrs: set[int] = set()
            while next_ptr and next_ptr not in visited_ptrs:
                visited_ptrs.add(next_ptr)
                next_page = table_defs.get(next_ptr * page_size)
                if not isinstance(next_page, (bytes, bytearray)):
                    break
                parsed_next = TDEF_HEADER.parse(bytes(next_page))
                merged_data += bytes(next_page)[int(parsed_next.header_end) :]
                next_ptr = int(parsed_next.next_page_ptr)

            parsed_data = parse_table_data(
                merged_data,
                int(table_header.index_count),
                int(table_header.real_index_count),
                int(table_header.column_count),
                version=version,
            )
        except Exception:
            return None

        raw_cols: object = parsed_data.get("column")
        raw_names: object = parsed_data.get("column_names")
        if not isinstance(raw_cols, Sequence) or not isinstance(raw_names, Sequence):
            return None

        _ = table_props
        col_by_id: dict[int, str] = {}
        ordered_entries: list[tuple[object, str]] = []

        for idx, col_obj in enumerate(raw_cols):
            name_str = ""
            if idx < len(raw_names):
                raw_name_val: object = getattr(raw_names[idx], "col_name_str", "")
                if isinstance(raw_name_val, str):
                    name_str = raw_name_val.strip("\x00").strip()
            if not name_str:
                continue

            col_id_raw: object = getattr(col_obj, "column_id", idx)
            col_id = int(col_id_raw) if isinstance(col_id_raw, int) else idx
            col_by_id[col_id] = name_str
            ordered_entries.append((col_obj, name_str))

        pk_list: list[str] = []
        raw_all_indexes: object = parsed_data.get("all_indexes")
        raw_real_index_2: object = parsed_data.get("real_index_2")
        if isinstance(raw_all_indexes, Sequence) and isinstance(raw_real_index_2, Sequence):
            for idx_entry in raw_all_indexes:
                idx_type: object = getattr(idx_entry, "idx_type", 0)
                idx_col_num: object = getattr(idx_entry, "idx_col_num", -1)
                if (
                    idx_type == 1
                    and isinstance(idx_col_num, int)
                    and 0 <= idx_col_num < len(raw_real_index_2)
                ):
                    real_idx = raw_real_index_2[idx_col_num]
                    unk_struct: object = getattr(real_idx, "unk_struct", ())
                    if isinstance(unk_struct, Sequence):
                        for col_ref in unk_struct:
                            ref_id: object = getattr(col_ref, "col_id", 0xFFFF)
                            if isinstance(ref_id, int) and (ref_id ^ 0xFFFF) != 0:
                                pk_col_name = col_by_id.get(ref_id)
                                if pk_col_name is not None and pk_col_name not in pk_list:
                                    pk_list.append(pk_col_name)

        pk_casefold = {pk.casefold() for pk in pk_list}
        columns: dict[str, AccdbColumnSchema] = {}
        for col_obj, col_name_str in ordered_entries:
            col_schema = self._build_column_schema(
                col_obj,
                pk_casefold,
                explicit_name=col_name_str,
            )
            if col_schema is not None:
                columns[col_schema.name] = col_schema

        return AccdbTableSchema(
            name=table_name,
            columns=columns,
            primary_keys=tuple(pk_list),
        )

    def _build_column_schema(
        self,
        col_obj: object,
        pk_casefold: set[str],
        *,
        explicit_name: str | None = None,
    ) -> AccdbColumnSchema | None:
        """Конвертує внутрішню структуру стовпця access-parser у AccdbColumnSchema."""
        raw_name: object = (
            explicit_name
            if explicit_name is not None
            else getattr(col_obj, "col_name_str", None)
        )
        if not isinstance(raw_name, str) or not raw_name.strip():
            return None
        col_name = raw_name.strip("\x00").strip()

        raw_type: object = getattr(col_obj, "type", 0)
        type_code = int(raw_type) if isinstance(raw_type, int) else 0

        flags_obj: object = getattr(col_obj, "column_flags", None)
        is_autonumber = bool(getattr(flags_obj, "autonumber", False))
        can_be_null = bool(getattr(flags_obj, "can_be_null", True))
        is_fixed = bool(getattr(flags_obj, "fixed_length", False))

        raw_len: object = getattr(col_obj, "length", 0)
        col_length = int(raw_len) if isinstance(raw_len, int) else 0

        canonical_type = _resolve_canonical_type(type_code, is_autonumber=is_autonumber)
        aliases = _CANONICAL_TYPE_ALIASES.get(
            canonical_type,
            frozenset({canonical_type.lower()}),
        )
        is_pk = col_name.casefold() in pk_casefold or is_autonumber

        return AccdbColumnSchema(
            name=col_name,
            type_code=type_code,
            canonical_type=canonical_type,
            aliases=aliases,
            is_autonumber=is_autonumber,
            can_be_null=can_be_null,
            is_fixed_length=is_fixed,
            length=col_length,
            is_primary_key=is_pk,
        )

    def _try_parse_with_mdbtools(self, file_path: Path) -> AccdbDatabaseSchema | None:
        """Резервний парсинг схеми .accdb через утиліту mdb-schema (mdbtools на Linux)."""
        mdb_schema_bin = shutil.which("mdb-schema")
        if mdb_schema_bin is None:
            return None

        try:
            proc = subprocess.run(
                [mdb_schema_bin, str(file_path)],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except OSError:
            return None

        if proc.returncode != 0 or not proc.stdout.strip():
            return None

        tables: dict[str, AccdbTableSchema] = {}
        for match in _MDB_CREATE_TABLE_PATTERN.finditer(proc.stdout):
            table_name = _strip_identifiers(match.group(1))
            if not table_name or _is_system_table_name(table_name):
                continue

            body_lines = [
                line.strip().rstrip(",")
                for line in match.group(2).splitlines()
                if line.strip() and not line.strip().startswith("--")
            ]
            columns: dict[str, AccdbColumnSchema] = {}
            for line in body_lines:
                upper_line = line.upper()
                if upper_line.startswith(("PRIMARY KEY", "CONSTRAINT", "FOREIGN KEY", "UNIQUE")):
                    continue

                if line.startswith("[") and "]" in line:
                    end_bracket = line.find("]")
                    col_name = line[1:end_bracket].strip()
                    rest = line[end_bracket + 1 :].strip()
                else:
                    parts = line.split(None, 1)
                    if len(parts) < 2:
                        continue
                    col_name = _strip_identifiers(parts[0])
                    rest = parts[1].strip()

                if not col_name:
                    continue

                canonical_type, type_code, is_auto, length = _parse_ddl_column_type(rest)
                aliases = _CANONICAL_TYPE_ALIASES.get(
                    canonical_type,
                    frozenset({canonical_type.lower()}),
                )
                columns[col_name] = AccdbColumnSchema(
                    name=col_name,
                    type_code=type_code,
                    canonical_type=canonical_type,
                    aliases=aliases,
                    is_autonumber=is_auto,
                    can_be_null="NOT NULL" not in rest.upper(),
                    is_fixed_length=canonical_type not in {"TEXT", "MEMO", "BINARY", "OLE"},
                    length=length,
                    is_primary_key=is_auto,
                )

            tables[table_name] = AccdbTableSchema(name=table_name, columns=columns)

        return AccdbDatabaseSchema(version=4, tables=tables) if tables else None

    def _evaluate_rule(
        self,
        *,
        schema: AccdbDatabaseSchema,
        rule: GradingRule,
        target: str,
        expected: str,
    ) -> CriterionResult:
        """Маршрутизує перевірку правила Access (.accdb) за його типом."""
        if rule.type == GradingRuleType.ACCDB_TABLE_EXISTS:
            return self._evaluate_table_exists(
                schema=schema,
                rule=rule,
                target=target,
                expected=expected,
            )
        if rule.type == GradingRuleType.ACCDB_COLUMN_EXISTS:
            return self._evaluate_column_exists(
                schema=schema,
                rule=rule,
                target=target,
                expected=expected,
            )
        if rule.type == GradingRuleType.ACCDB_COLUMN_TYPE:
            return self._evaluate_column_type(
                schema=schema,
                rule=rule,
                target=target,
                expected=expected,
            )

        raise GradingError(
            f"AccdbGrader не підтримує правило типу '{rule.type.value}'.",
            context={"rule_id": rule.id, "rule_type": rule.type.value},
        )

    def _evaluate_table_exists(
        self,
        *,
        schema: AccdbDatabaseSchema,
        rule: GradingRule,
        target: str,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє наявність або кількість таблиць (чи кількість стовпців таблиці) у БД."""
        target_clean = target.strip()
        expected_clean = expected.strip()
        expected_lower = expected_clean.lower()

        # Режим 1: Перевірка кількості стовпців таблиці ('Students.columns' -> '>=3')
        col_count_match = _TABLE_COLUMN_COUNT_SUFFIX_PATTERN.match(target_clean)
        if col_count_match is not None:
            tbl_name = _strip_identifiers(col_count_match.group(1))
            table_schema = schema.find_table(tbl_name)
            if table_schema is None:
                return self.build_criterion_result(
                    rule,
                    passed=False,
                    actual="0",
                    feedback=f"Таблицю '{tbl_name}' не знайдено у базі даних Access.",
                    resolved_expected=expected,
                )
            col_count = len(table_schema.columns)
            passed = self.compare_numeric_condition(col_count, expected_clean)
            feedback = (
                f"Кількість полів у таблиці '{table_schema.name}' ({col_count}) "
                f"відповідає умові '{expected}'."
                if passed
                else (
                    f"Кількість полів у таблиці '{table_schema.name}' ({col_count}) "
                    f"не відповідає умові '{expected}'."
                )
            )
            return self.build_criterion_result(
                rule,
                passed=passed,
                actual=str(col_count),
                feedback=feedback,
                resolved_expected=expected,
            )

        # Режим 2: Загальна кількість таблиць у БД (target='database' або '*')
        if target_clean.lower() in _DB_WIDE_TARGETS:
            table_count = len(schema.tables)
            if expected_lower in {"true", "false", "1", "0", "yes", "no"} and not any(
                expected_clean.startswith(op) for op in (">=", "<=", "==", "!=", ">", "<", "=")
            ):
                if expected_lower in {"true", "false", "yes", "no"}:
                    expected_bool = self.parse_bool_expected(expected_clean)
                    actual_bool = table_count > 0
                    passed = actual_bool == expected_bool
                    actual_str = "true" if actual_bool else "false"
                else:
                    passed = self.compare_numeric_condition(table_count, expected_clean)
                    actual_str = str(table_count)
            else:
                passed = self.compare_numeric_condition(table_count, expected_clean)
                actual_str = str(table_count)

            feedback = (
                f"Кількість користувацьких таблиць у базі даних ({table_count}) "
                f"відповідає умові '{expected}'."
                if passed
                else (
                    f"Кількість користувацьких таблиць у базі даних ({table_count}) "
                    f"не відповідає умові '{expected}'."
                )
            )
            return self.build_criterion_result(
                rule,
                passed=passed,
                actual=actual_str,
                feedback=feedback,
                resolved_expected=expected,
            )

        # Режим 3: Конкретна таблиця або список таблиць ('Students' або 'Students,Grades')
        requested_tables = [
            _strip_identifiers(part)
            for part in target_clean.split(",")
            if _strip_identifiers(part)
        ]
        if not requested_tables:
            raise GradingError(
                f"Не вказано цільову назву таблиці Access у правилі '{rule.id}'.",
                context={"rule_id": rule.id, "target": target},
            )

        found_tables: list[str] = []
        missing_tables: list[str] = []
        for req_name in requested_tables:
            matched_tbl = schema.find_table(req_name)
            if matched_tbl is not None:
                found_tables.append(matched_tbl.name)
            else:
                missing_tables.append(req_name)

        all_exist = len(missing_tables) == 0

        if expected_lower in {"true", "false", "yes", "no"}:
            expected_bool = self.parse_bool_expected(expected_clean)
            passed = all_exist == expected_bool
            actual_str = "true" if all_exist else "false"
        else:
            passed = self.compare_numeric_condition(len(found_tables), expected_clean)
            actual_str = str(len(found_tables))

        available_list = ", ".join(schema.tables.keys()) if schema.tables else "немає таблиць"
        if len(requested_tables) == 1:
            req_single = requested_tables[0]
            if passed:
                feedback = (
                    f"Таблиця '{found_tables[0]}' присутня у схемі бази даних Access."
                    if all_exist
                    else f"Таблиця '{req_single}' відсутня у базі даних, як і очікувалося."
                )
            else:
                feedback = (
                    f"Таблицю '{req_single}' не знайдено у базі даних Access "
                    f"(наявні таблиці: {available_list})."
                    if not all_exist
                    else (
                        f"Таблиця '{req_single}' присутня у базі даних, "
                        f"хоча очікувалося '{expected}'."
                    )
                )
        else:
            if passed:
                feedback = (
                    f"Усі цільові таблиці ({', '.join(found_tables)}) присутні у базі даних."
                )
            else:
                feedback = (
                    f"Не знайдено таблиці: {', '.join(missing_tables)} "
                    f"(наявні таблиці: {available_list})."
                )

        return self.build_criterion_result(
            rule,
            passed=passed,
            actual=actual_str,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _evaluate_column_exists(
        self,
        *,
        schema: AccdbDatabaseSchema,
        rule: GradingRule,
        target: str,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє наявність стовпця у цільовій таблиці Access ('Students.FullName')."""
        table_name, column_name = self._parse_table_column_target(rule, target, expected)
        table_schema = schema.find_table(table_name)
        expected_clean = expected.strip()
        expected_lower = expected_clean.lower()

        is_bool_or_num_expected = expected_lower in {
            "true",
            "false",
            "yes",
            "no",
        } or _is_numeric_condition(expected_clean)

        if table_schema is None:
            available_tables = (
                ", ".join(schema.tables.keys()) if schema.tables else "немає таблиць"
            )
            return self.build_criterion_result(
                rule,
                passed=False,
                actual="false" if is_bool_or_num_expected else None,
                feedback=(
                    f"Таблицю '{table_name}' для перевірки поля '{column_name}' "
                    f"не знайдено у базі даних (наявні таблиці: {available_tables})."
                ),
                resolved_expected=expected,
            )

        requested_cols = [
            _strip_identifiers(part)
            for part in column_name.split(",")
            if _strip_identifiers(part)
        ]
        found_cols: list[str] = []
        missing_cols: list[str] = []
        for req_col in requested_cols:
            col_schema = table_schema.find_column(req_col)
            if col_schema is not None:
                found_cols.append(col_schema.name)
            else:
                missing_cols.append(req_col)

        all_cols_exist = len(missing_cols) == 0 and len(found_cols) > 0

        if expected_lower in {"true", "false", "yes", "no"}:
            expected_bool = self.parse_bool_expected(expected_clean)
            passed = all_cols_exist == expected_bool
            actual_str = "true" if all_cols_exist else "false"
        elif _is_numeric_condition(expected_clean):
            passed = self.compare_numeric_condition(len(found_cols), expected_clean)
            actual_str = str(len(found_cols))
        else:
            # Якщо expected задавав ім'я стовпця при target='TableName'
            passed = all_cols_exist
            actual_str = (
                ", ".join(found_cols)
                if found_cols
                else (", ".join(table_schema.columns.keys()) or "none")
            )

        available_cols = (
            ", ".join(table_schema.columns.keys())
            if table_schema.columns
            else "немає полів"
        )
        if passed:
            if all_cols_exist:
                feedback = (
                    f"Поле '{', '.join(found_cols)}' присутнє у таблиці '{table_schema.name}'."
                )
            else:
                feedback = (
                    f"Поле '{column_name}' відсутнє у таблиці '{table_schema.name}', "
                    "як і очікувалося."
                )
        else:
            if not all_cols_exist:
                feedback = (
                    f"У таблиці '{table_schema.name}' не знайдено поле "
                    f"'{', '.join(missing_cols)}' (наявні поля: {available_cols})."
                )
            else:
                feedback = (
                    f"Поле '{', '.join(found_cols)}' присутнє у таблиці '{table_schema.name}', "
                    f"хоча очікувалося '{expected}'."
                )

        return self.build_criterion_result(
            rule,
            passed=passed,
            actual=actual_str,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _evaluate_column_type(
        self,
        *,
        schema: AccdbDatabaseSchema,
        rule: GradingRule,
        target: str,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє відповідність типу даних стовпця у таблиці Access ('Grades.Score')."""
        table_name, column_name = self._parse_table_column_target(
            rule,
            target,
            expected,
            require_explicit_column=True,
        )
        table_schema = schema.find_table(table_name)
        if table_schema is None:
            return self.build_criterion_result(
                rule,
                passed=False,
                actual=None,
                feedback=(
                    f"Таблицю '{table_name}' для перевірки типу поля '{column_name}' "
                    "не знайдено у базі даних Access."
                ),
                resolved_expected=expected,
            )

        col_schema = table_schema.find_column(column_name)
        if col_schema is None:
            available_cols = (
                ", ".join(table_schema.columns.keys())
                if table_schema.columns
                else "немає полів"
            )
            return self.build_criterion_result(
                rule,
                passed=False,
                actual=None,
                feedback=(
                    f"Поле '{column_name}' не знайдено у таблиці '{table_schema.name}' "
                    f"(наявні поля: {available_cols})."
                ),
                resolved_expected=expected,
            )

        passed = self._column_matches_expected_type(col_schema, expected)
        actual_type = col_schema.canonical_type

        if passed:
            feedback = (
                f"Тип даних поля '{table_schema.name}.{col_schema.name}' ({actual_type}) "
                f"відповідає очікуваному '{expected}'."
            )
        else:
            feedback = (
                f"Тип даних поля '{table_schema.name}.{col_schema.name}' є '{actual_type}', "
                f"але очікувався '{expected}'."
            )

        return self.build_criterion_result(
            rule,
            passed=passed,
            actual=actual_type,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _parse_table_column_target(
        self,
        rule: GradingRule,
        target: str,
        expected: str,
        *,
        require_explicit_column: bool = False,
    ) -> tuple[str, str]:
        """Розбирає цільовий ідентифікатор 'TableName.ColumnName' на назву таблиці та стовпця."""
        cleaned = target.strip()

        # Підтримка синтаксису [Table].[Column]
        bracket_parts = re.findall(r"\[([^\]]+)\]", cleaned)
        if len(bracket_parts) == 2:
            t_name, c_name = bracket_parts[0].strip(), bracket_parts[1].strip()
            if t_name and c_name:
                return t_name, c_name

        parts = [
            _strip_identifiers(p)
            for p in _COLUMN_TARGET_SPLIT_PATTERN.split(cleaned, maxsplit=1)
        ]
        if len(parts) == 2 and parts[0] and parts[1]:
            return parts[0], parts[1]

        if not require_explicit_column:
            expected_clean = expected.strip()
            if (
                cleaned
                and expected_clean
                and expected_clean.lower() not in {"true", "false", "1", "0", "yes", "no"}
                and not _is_numeric_condition(expected_clean)
            ):
                return _strip_identifiers(cleaned), _strip_identifiers(expected_clean)

        raise GradingError(
            f"Некоректний формат цілі '{target}' у правилі '{rule.id}'. "
            "Очікується формат 'TableName.ColumnName'.",
            context={"rule_id": rule.id, "target": target},
        )

    def _column_matches_expected_type(
        self,
        col_schema: AccdbColumnSchema,
        expected: str,
    ) -> bool:
        """Перевіряє, чи відповідає тип стовпця очікуваному типу (включно з аліасами Access/SQL)."""
        raw_candidates = [
            token.strip()
            for token in re.split(r"[|,;]", expected)
            if token.strip()
        ]
        if not raw_candidates:
            raise GradingError(
                "Порожній вираз очікуваного типу даних стовпця у правилі Access.",
                context={"expected": expected},
            )

        for candidate in raw_candidates:
            match = _EXPECTED_TYPE_SIZE_PATTERN.match(candidate)
            type_token = (
                match.group(1).strip().lower()
                if match is not None
                else candidate.strip().lower()
            )
            size_token = (
                int(match.group(2))
                if match is not None and match.group(2) is not None
                else None
            )
            normalized_token = " ".join(type_token.replace("_", " ").split())

            type_matched = False
            if normalized_token.isdigit():
                type_matched = col_schema.type_code == int(normalized_token)
            elif (
                normalized_token == col_schema.canonical_type.lower()
                or normalized_token in col_schema.aliases
                or type_token in col_schema.aliases
            ):
                type_matched = True
            elif normalized_token in {"pk", "primary key", "primary"}:
                type_matched = col_schema.is_primary_key

            if type_matched:
                # У Access UTF-16 текстові поля мають довжину в байтах (2 * символи) або символах
                if (
                    size_token is not None
                    and col_schema.length > 0
                    and col_schema.length not in {size_token, size_token * 2}
                ):
                    continue
                return True

        return False


def _strip_identifiers(value: str) -> str:
    """Видаляє обрамлюючі лапки та квадратні дужки з ідентифікатора таблиці/поля."""
    cleaned = value.strip()
    if (
        len(cleaned) >= 2
        and (
            (cleaned[0] == "[" and cleaned[-1] == "]")
            or (cleaned[0] in {"'", '"', "`"} and cleaned[-1] == cleaned[0])
        )
    ):
        cleaned = cleaned[1:-1].strip()
    return cleaned


def _is_system_table_name(table_name: str) -> bool:
    """Визначає, чи є таблиця системною таблицею Microsoft Access (MSys*, USys*, ~*)."""
    lowered = table_name.strip().lower()
    return lowered.startswith(_SYSTEM_TABLE_PREFIXES)


def _is_numeric_condition(expr: str) -> bool:
    """Перевіряє, чи є рядок числовим виразом умови ('>=1', '2', '==3')."""
    return bool(
        re.match(r"^\s*(>=|<=|!=|==|>|<|=)?\s*[+-]?\d+(?:[.,]\d+)?\s*$", expr)
    )


def _resolve_canonical_type(type_code: int, *, is_autonumber: bool = False) -> str:
    """Визначає канонічну назву типу даних Access за числовим кодом та прапорцем AutoNumber."""
    if type_code == int(TYPE_INT32) and is_autonumber:
        return "AUTONUMBER"
    return _TYPE_CODE_TO_CANONICAL.get(type_code, f"TYPE_{type_code}")


def _parse_ddl_column_type(ddl_rest: str) -> tuple[str, int, bool, int]:
    """Розбирає SQL/DDL опис типу стовпця з виводу mdb-schema."""
    upper = ddl_rest.upper()
    is_auto = "AUTOINCREMENT" in upper or "COUNTER" in upper or "IDENTITY" in upper
    size_match = re.search(r"\((\d+)\)", upper)
    length = int(size_match.group(1)) if size_match is not None else 0

    if is_auto:
        return "AUTONUMBER", int(TYPE_INT32), True, 4
    if any(k in upper for k in ("LONG INTEGER", "LONGINT", "INT32")):
        return "LONG", int(TYPE_INT32), False, 4
    if any(k in upper for k in ("SMALLINT", "INTEGER", "INT16", "SHORT")):
        if "LONG" not in upper:
            return "INTEGER", int(TYPE_INT16), False, 2
        return "LONG", int(TYPE_INT32), False, 4
    if "BYTE" in upper or "TINYINT" in upper:
        return "BYTE", int(TYPE_INT8), False, 1
    if any(k in upper for k in ("BOOLEAN", "BOOL", "BIT", "YESNO")):
        return "BOOLEAN", int(TYPE_BOOLEAN), False, 1
    if "CURRENCY" in upper or "MONEY" in upper:
        return "CURRENCY", int(TYPE_MONEY), False, 8
    if "DOUBLE" in upper or "FLOAT8" in upper:
        return "DOUBLE", int(TYPE_FLOAT64), False, 8
    if "SINGLE" in upper or "FLOAT4" in upper or "REAL" in upper:
        return "SINGLE", int(TYPE_FLOAT32), False, 4
    if "NUMERIC" in upper or "DECIMAL" in upper:
        return "DECIMAL", int(TYPE_96_bit_17_BYTES), False, 17
    if "DATETIME" in upper or "TIMESTAMP" in upper or "DATE" in upper:
        return "DATETIME", int(TYPE_DATETIME), False, 8
    if "MEMO" in upper or "LONGTEXT" in upper:
        return "MEMO", int(TYPE_MEMO), False, 0
    if "OLE" in upper or "LONGBINARY" in upper or "BLOB" in upper:
        return "OLE", int(TYPE_OLE), False, 0
    if "GUID" in upper or "UUID" in upper or "UNIQUEIDENTIFIER" in upper:
        return "GUID", int(TYPE_GUID), False, 16
    if "BINARY" in upper:
        return "BINARY", int(TYPE_BINARY), False, length or 255
    return "TEXT", int(TYPE_TEXT), False, length or 255


def build_accdb_bytes(
    tables: Mapping[str, Sequence[tuple[str, str | int]]],
) -> bytes:
    """Конструює валідний бінарний образ бази даних Microsoft Access (.accdb, ACE v4/2010).

    Використовується для детермінованої генерації еталонних та тестових .accdb файлів,
    які повноцінно парсяться бібліотекою access-parser на будь-якій ОС без MS Access.
    """
    page_size = int(PAGE_SIZE_V4)

    # Сторінка 0: Заголовок бази даних ACE (VERSION_2010 = 0x03)
    page_0 = (
        _ACCESS_HEADER_MAGIC
        + b"Standard ACE DB\x00"
        + struct.pack("<I", 0x03)
        + (b"\x00" * 126)
    ).ljust(page_size, b"\x00")

    # Сторінка 1: Системна сторінка карти вільного місця
    page_1 = b"\x00" * page_size

    # Сторінка 2: TDEF системного каталогу MSysObjects
    msys_columns: list[tuple[str, int, int, bool, bool]] = [
        ("Id", int(TYPE_INT32), 4, True, False),
        ("Type", int(TYPE_INT16), 2, True, False),
        ("Flags", int(TYPE_INT32), 4, True, False),
        ("Name", int(TYPE_TEXT), 255, False, False),
    ]
    page_2 = _encode_tdef_page(msys_columns, page_size=page_size)

    # Сторінки 4..N: TDEF користувацьких таблиць
    catalog_records: list[bytes] = [
        _encode_msys_catalog_record(
            obj_id=2,
            obj_type=1,
            obj_flags=int(SYSTEM_TABLE_FLAGS[0]),
            name="MSysObjects",
        )
    ]
    user_tdef_pages: list[bytes] = []
    next_page_id = 4

    for table_name, raw_cols in tables.items():
        encoded_cols: list[tuple[str, int, int, bool, bool]] = []
        for col_name, col_type_spec in raw_cols:
            if isinstance(col_type_spec, int):
                type_code = col_type_spec
                is_fixed = type_code not in {
                    int(TYPE_TEXT),
                    int(TYPE_MEMO),
                    int(TYPE_OLE),
                    int(TYPE_BINARY),
                    int(TYPE_96_bit_17_BYTES),
                }
                is_auto = False
                col_len = 4 if is_fixed else 255
            else:
                spec_upper = " ".join(col_type_spec.strip().upper().replace("_", " ").split())
                size_m = _EXPECTED_TYPE_SIZE_PATTERN.match(spec_upper)
                base_name = (
                    size_m.group(1).strip() if size_m is not None else spec_upper
                )
                custom_len = (
                    int(size_m.group(2))
                    if size_m is not None and size_m.group(2) is not None
                    else None
                )
                type_code, is_fixed, is_auto, default_len = _NAME_TO_TYPE_CODE.get(
                    base_name,
                    (int(TYPE_TEXT), False, False, 255),
                )
                col_len = custom_len if custom_len is not None else default_len

            encoded_cols.append((col_name, type_code, col_len, is_fixed, is_auto))

        user_tdef_pages.append(_encode_tdef_page(encoded_cols, page_size=page_size))
        catalog_records.append(
            _encode_msys_catalog_record(
                obj_id=next_page_id,
                obj_type=1,
                obj_flags=0,
                name=table_name,
            )
        )
        next_page_id += 1

    # Сторінка 3: Сторінка даних MSysObjects (owner = 2)
    page_3 = _encode_data_page(owner_page=2, records=catalog_records, page_size=page_size)

    return b"".join([page_0, page_1, page_2, page_3, *user_tdef_pages])


def _encode_tdef_page(
    columns: Sequence[tuple[str, int, int, bool, bool]],
    *,
    page_size: int,
) -> bytes:
    """Кодує бінарну сторінку визначення таблиці (TDEF, magic 0x02 0x01) для Access v4."""
    col_count = len(columns)
    var_cols = sum(1 for _, _, _, is_fixed, _ in columns if not is_fixed)
    col_blobs = bytearray()
    name_blobs = bytearray()
    var_idx = 0
    fix_offset = 0

    for idx, (name, ctype, clen, is_fixed, is_auto) in enumerate(columns):
        if is_fixed:
            v_col_num = 0
            cur_fix = fix_offset
            fix_offset += clen
        else:
            v_col_num = var_idx
            var_idx += 1
            cur_fix = 0

        flag_byte_0 = (
            (0x01 if is_fixed else 0x00)
            | 0x02
            | (0x04 if is_auto else 0x00)
        )
        flags_bytes = bytes([flag_byte_0, 0x00])
        col_blobs += struct.pack(
            "<BIHHH4s2sIHH",
            ctype,
            0,
            idx,
            v_col_num,
            idx,
            b"\x00" * 4,
            flags_bytes,
            0,
            cur_fix,
            clen,
        )
        name_utf16 = name.encode("utf-16le")
        name_blobs += struct.pack("<H", len(name_utf16)) + name_utf16

    body = bytes(col_blobs + name_blobs)
    tdef_len = 8 + 43 + len(body)
    head = struct.pack(
        "<2sHI IIIIIIII BHHH IIII",
        b"\x02\x01",
        0,
        0,
        tdef_len,
        0,
        0,
        1,
        1,
        0,
        0,
        0,
        0x4E,
        col_count,
        var_cols,
        col_count,
        0,
        0,
        0,
        0,
    )
    return (head + body).ljust(page_size, b"\x00")


def _encode_msys_catalog_record(
    *,
    obj_id: int,
    obj_type: int,
    obj_flags: int,
    name: str,
) -> bytes:
    """Кодує запис рядка таблиці системного каталогу MSysObjects."""
    name_bytes = b"\xff\xfe" + name.encode("utf-8")
    fixed_part = struct.pack("<ihi", obj_id, obj_type, obj_flags)
    var_start = 2 + len(fixed_part)
    var_end = var_start + len(name_bytes)
    meta_reversed = struct.pack(">HHH", 1, var_start, var_end)
    meta_forward = meta_reversed[::-1]
    null_bitmap = b"\x0f"
    return struct.pack("<h", 4) + fixed_part + name_bytes + meta_forward + null_bitmap


def _encode_data_page(
    *,
    owner_page: int,
    records: Sequence[bytes],
    page_size: int,
) -> bytes:
    """Кодує сторінку даних Access (magic 0x01 0x01) зі списком записів."""
    page = bytearray(page_size)
    cursor = page_size
    offsets: list[int] = []
    for rec in records:
        cursor -= len(rec)
        page[cursor : cursor + len(rec)] = rec
        offsets.append(cursor)

    header = struct.pack(
        f"<2sHIIH{len(offsets)}H",
        b"\x01\x01",
        0,
        owner_page,
        0,
        len(offsets),
        *offsets,
    )
    page[: len(header)] = header
    return bytes(page)
