import sys
import xml.etree.ElementTree as ET
import zipfile
from collections.abc import AsyncGenerator, Iterable, Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

import docx
import openpyxl  # type: ignore[import-untyped]
import pytest
import pytest_asyncio
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm, Pt
from httpx import ASGITransport, AsyncClient
from openpyxl.chart import BarChart, Reference  # type: ignore[import-untyped]
from openpyxl.worksheet.worksheet import Worksheet  # type: ignore[import-untyped]
from sqlalchemy import Column, Engine, create_engine, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Result
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import Executable
from sqlalchemy.sql.schema import FetchedValue

_BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app import models as _app_models  # noqa: E402, F401
from app import seed as seed_module  # noqa: E402
from app.api.deps import get_db  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.database import Base  # noqa: E402
from app.core.security import create_access_token, hash_password  # noqa: E402
from app.graders.accdb_grader import build_accdb_bytes  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402
from app.models.user import UserRole  # noqa: E402


@compiles(JSONB, "sqlite")
def _compile_jsonb_for_sqlite(
    _type: JSONB,
    _compiler: object,
    **_kw: object,
) -> str:
    """Компілює PostgreSQL-тип JSONB у стандартний JSON для тестової БД SQLite."""
    return "JSON"


_PRECOMPUTED_PASSWORD_HASHES: dict[str, str] = {
    "Admin123!": hash_password("Admin123!"),
    "Teacher123!": hash_password("Teacher123!"),
    "Student123!": hash_password("Student123!"),
}


def _fast_seed_hash_password(plain_password: str) -> str:
    """Повертає попередньо обчислений bcrypt-хеш для стандартних тестових паролів."""
    cached = _PRECOMPUTED_PASSWORD_HASHES.get(plain_password)
    if cached is not None:
        return cached
    return hash_password(plain_password)


class SqliteAsyncSessionAdapter:
    """Асинхронний адаптер поверх синхронної SQLAlchemy Session для тестів на SQLite."""

    def __init__(self, sync_session: Session) -> None:
        self._session = sync_session

    # justified Any: SQLAlchemy Executable generic Tuple result signature varies by query
    async def execute(
        self,
        statement: Executable,
        *args: Any,
        **kwargs: Any,
    ) -> Result[Any]:
        return self._session.execute(statement, *args, **kwargs)

    def add(self, instance: object) -> None:
        self._session.add(instance)

    def add_all(self, instances: Iterable[object]) -> None:
        self._session.add_all(instances)

    async def delete(self, instance: object) -> None:
        self._session.delete(instance)

    async def flush(self, objects: Sequence[object] | None = None) -> None:
        self._session.flush(objects)

    async def commit(self) -> None:
        self._session.commit()

    async def rollback(self) -> None:
        self._session.rollback()

    async def refresh(
        self,
        instance: object,
        attribute_names: Iterable[str] | None = None,
    ) -> None:
        self._session.refresh(instance, attribute_names=attribute_names)

    async def close(self) -> None:
        self._session.close()


def _create_sqlite_test_engine() -> Engine:
    """Створює ізольований in-memory SQLite Engine з підтримкою зовнішніх ключів."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection: object, _connection_record: object) -> None:
        cursor_factory: object = getattr(dbapi_connection, "cursor", None)
        if callable(cursor_factory):
            cursor = cursor_factory()
            execute_fn: object = getattr(cursor, "execute", None)
            close_fn: object = getattr(cursor, "close", None)
            if callable(execute_fn):
                execute_fn("PRAGMA foreign_keys=ON")
            if callable(close_fn):
                close_fn()

    saved_server_defaults: list[tuple[Column[Any], FetchedValue]] = []
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if column.server_default is not None and "::jsonb" in str(
                getattr(column.server_default, "arg", "")
            ):
                saved_server_defaults.append((column, column.server_default))
                column.server_default = None

    try:
        Base.metadata.create_all(engine)
    finally:
        for col_obj, original_default in saved_server_defaults:
            col_obj.server_default = original_default

    return engine


@pytest_asyncio.fixture
async def db_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[SqliteAsyncSessionAdapter, None]:
    """Фікстура ізольованої тестової БД з початковими курсами, групою та користувачами."""
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(settings, "UPLOADS_DIR", uploads_dir)
    monkeypatch.setattr(seed_module, "hash_password", _fast_seed_hash_password)

    engine = _create_sqlite_test_engine()
    session_factory = sessionmaker(
        bind=engine,
        class_=Session,
        expire_on_commit=False,
        autoflush=False,
    )

    with session_factory() as sync_session:
        adapter = SqliteAsyncSessionAdapter(sync_session)
        # justified Any: SqliteAsyncSessionAdapter structural duck-typing for AsyncSession
        typed_db: Any = adapter
        await seed_module.seed_database(typed_db)
        yield adapter

    engine.dispose()


@pytest_asyncio.fixture
async def async_client(
    db_session: SqliteAsyncSessionAdapter,
) -> AsyncGenerator[AsyncClient, None]:
    """Асинхронний HTTP-клієнт FastAPI з підміною залежності get_db на тестову сесію."""

    async def _override_get_db() -> AsyncGenerator[SqliteAsyncSessionAdapter, None]:
        yield db_session

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=fastapi_app)
    try:
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            yield client
    finally:
        fastapi_app.dependency_overrides.clear()


def make_auth_headers(user_id: object, role: UserRole) -> dict[str, str]:
    """Генерує HTTP-заголовок Authorization із валідним JWT access-токеном."""
    token = create_access_token(subject=str(user_id), role=role)
    return {"Authorization": f"Bearer {token}"}


def rewrite_openxml_core_metadata(
    file_path: Path,
    *,
    creator: str | None = None,
    last_modified_by: str | None = None,
    created: str | None = None,
    modified: str | None = None,
    revision: str | None = None,
) -> None:
    """Перезаписує `docProps/core.xml` в OpenXML-архіві (.docx/.xlsx) заданими метаданими."""
    cp_ns = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
    dc_ns = "http://purl.org/dc/elements/1.1/"
    dcterms_ns = "http://purl.org/dc/terms/"
    xsi_ns = "http://www.w3.org/2001/XMLSchema-instance"

    ET.register_namespace("cp", cp_ns)
    ET.register_namespace("dc", dc_ns)
    ET.register_namespace("dcterms", dcterms_ns)
    ET.register_namespace("xsi", xsi_ns)

    root = ET.Element(f"{{{cp_ns}}}coreProperties")
    if creator is not None:
        el = ET.SubElement(root, f"{{{dc_ns}}}creator")
        el.text = creator
    if last_modified_by is not None:
        el = ET.SubElement(root, f"{{{cp_ns}}}lastModifiedBy")
        el.text = last_modified_by
    if revision is not None:
        el = ET.SubElement(root, f"{{{cp_ns}}}revision")
        el.text = revision
    if created is not None:
        el = ET.SubElement(
            root,
            f"{{{dcterms_ns}}}created",
            {f"{{{xsi_ns}}}type": "dcterms:W3CDTF"},
        )
        el.text = created
    if modified is not None:
        el = ET.SubElement(
            root,
            f"{{{dcterms_ns}}}modified",
            {f"{{{xsi_ns}}}type": "dcterms:W3CDTF"},
        )
        el.text = modified

    core_xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    _replace_zip_member(file_path, "docProps/core.xml", core_xml_bytes)


def _replace_zip_member(
    archive_path: Path,
    member_name: str,
    member_bytes: bytes,
) -> None:
    """Замінює або додає файл усередині ZIP-архіву."""
    existing_entries: list[tuple[zipfile.ZipInfo, bytes]] = []
    with zipfile.ZipFile(archive_path, mode="r") as src_zip:
        for info in src_zip.infolist():
            if info.filename != member_name:
                existing_entries.append((info, src_zip.read(info.filename)))

    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED) as dst_zip:
        for info, data in existing_entries:
            dst_zip.writestr(info, data)
        dst_zip.writestr(member_name, member_bytes)


def build_sample_docx(
    target_path: Path,
    *,
    left_mm: float = 30.0,
    right_mm: float = 15.0,
    top_mm: float = 20.0,
    bottom_mm: float = 20.0,
    font_name: str = "Times New Roman",
    font_size_pt: float = 14.0,
    line_spacing: float = 1.5,
    alignment: WD_ALIGN_PARAGRAPH = WD_ALIGN_PARAGRAPH.JUSTIFY,
    include_table: bool = True,
    table_rows: int = 4,
    table_cols: int = 3,
    include_list: bool = True,
    creator: str = "Student One",
    created_iso: str = "2026-11-18T10:00:00Z",
    modified_iso: str = "2026-11-18T10:30:00Z",
) -> Path:
    """Генерує тестовий документ Word (.docx) із заданими параметрами форматування."""
    doc = docx.Document()
    section = doc.sections[0]
    section.left_margin = Mm(left_mm)
    section.right_margin = Mm(right_mm)
    section.top_margin = Mm(top_mm)
    section.bottom_margin = Mm(bottom_mm)

    normal_style = doc.styles["Normal"]
    normal_style.font.name = font_name
    normal_style.font.size = Pt(font_size_pt)

    paragraphs_text = [
        "Звіт про виконання практичної роботи з дисципліни Microsoft Word.",
        "Основний текст оформлено відповідно до вимог методичних вказівок коледжу.",
    ]
    for text in paragraphs_text:
        p = doc.add_paragraph()
        p.alignment = alignment
        p.paragraph_format.line_spacing = line_spacing
        run = p.add_run(text)
        run.font.name = font_name
        run.font.size = Pt(font_size_pt)

    if include_list:
        list_p = doc.add_paragraph(style="List Bullet")
        list_p.alignment = alignment
        list_p.paragraph_format.line_spacing = line_spacing
        list_run = list_p.add_run("Перший пункт маркованого списку звіту")
        list_run.font.name = font_name
        list_run.font.size = Pt(font_size_pt)

    if include_table and table_rows > 0 and table_cols > 0:
        table = doc.add_table(rows=table_rows, cols=table_cols)
        for r_idx in range(table_rows):
            for c_idx in range(table_cols):
                table.cell(r_idx, c_idx).text = f"R{r_idx + 1}C{c_idx + 1}"

    core_props = doc.core_properties
    core_props.author = creator
    core_props.last_modified_by = creator
    core_props.created = datetime.fromisoformat(created_iso.replace("Z", "+00:00"))
    core_props.modified = datetime.fromisoformat(modified_iso.replace("Z", "+00:00"))

    doc.save(str(target_path))
    rewrite_openxml_core_metadata(
        target_path,
        creator=creator,
        last_modified_by=creator,
        created=created_iso,
        modified=modified_iso,
        revision="1",
    )
    return target_path


def build_sample_xlsx(
    target_path: Path,
    *,
    sheet_title: str = "Sheet1",
    values: Sequence[float] = (
        1850.0,
        1850.0,
        1850.0,
        1850.0,
        1850.0,
        1850.0,
        1850.0,
        1850.0,
        1850.0,
        1850.0,
    ),
    sum_formula: str | None = "=SUM(D2:D11)",
    avg_formula: str | None = "=AVERAGE(D2:D11)",
    include_chart: bool = True,
    creator: str = "Student One",
    created_iso: str = "2026-11-18T11:00:00Z",
    modified_iso: str = "2026-11-18T11:30:00Z",
) -> Path:
    """Генерує тестову книгу Excel (.xlsx) із даними, формулами, діаграмою та core.xml."""
    wb = openpyxl.Workbook()
    ws = wb.active
    assert isinstance(ws, Worksheet)
    ws.title = sheet_title

    ws["C1"] = "Студент"
    ws["D1"] = "Сума"
    for idx, val in enumerate(values, start=2):
        ws[f"C{idx}"] = f"Запис {idx - 1}"
        ws[f"D{idx}"] = val

    if sum_formula is not None:
        ws["D12"] = sum_formula
    else:
        ws["D12"] = float(sum(values))

    if avg_formula is not None:
        ws["D13"] = avg_formula
    elif values:
        ws["D13"] = float(sum(values) / len(values))

    if include_chart:
        chart = BarChart()
        chart.title = "Відомість показників"
        data_ref = Reference(ws, min_col=4, min_row=1, max_row=11)
        cats_ref = Reference(ws, min_col=3, min_row=2, max_row=11)
        chart.add_data(data_ref, titles_from_data=True)
        chart.set_categories(cats_ref)
        ws.add_chart(chart, "F2")

    wb.save(str(target_path))
    wb.close()

    rewrite_openxml_core_metadata(
        target_path,
        creator=creator,
        last_modified_by=creator,
        created=created_iso,
        modified=modified_iso,
        revision="1",
    )
    return target_path


def build_sample_accdb(
    target_path: Path,
    *,
    tables: Mapping[str, Sequence[tuple[str, str | int]]] | None = None,
) -> Path:
    """Генерує валідний бінарний файл бази даних Access (.accdb) із заданою схемою таблиць."""
    default_tables: dict[str, list[tuple[str, str | int]]] = {
        "Students": [
            ("ID", "AUTONUMBER"),
            ("FullName", "TEXT(150)"),
            ("GroupCode", "TEXT(32)"),
        ],
        "Grades": [
            ("ID", "AUTONUMBER"),
            ("StudentID", "LONG"),
            ("SubjectName", "TEXT(100)"),
            ("Score", "DOUBLE"),
        ],
    }
    schema_to_write = tables if tables is not None else default_tables
    raw_bytes = build_accdb_bytes(schema_to_write)
    target_path.write_bytes(raw_bytes)
    return target_path


__all__ = [
    "SqliteAsyncSessionAdapter",
    "async_client",
    "build_sample_accdb",
    "build_sample_docx",
    "build_sample_xlsx",
    "db_session",
    "make_auth_headers",
    "rewrite_openxml_core_metadata",
]
