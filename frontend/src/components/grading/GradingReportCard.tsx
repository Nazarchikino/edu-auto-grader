import { useMemo, useState, type ReactElement } from "react";
import {
  AlertTriangle,
  Award,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Clock,
  Code2,
  Database,
  FileCode2,
  FileSpreadsheet,
  FileText,
  Filter,
  Fingerprint,
  Info,
  MessageSquareQuote,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Target,
  UserCheck,
  XCircle,
} from "lucide-react";
import type { SubmissionRead } from "../../types/api";
import type { CourseSlug } from "../../types/course";
import type {
  CriterionResult,
  GradingRuleType,
  PracticalFormat,
} from "../../types/grading";

export type CriterionFilterMode = "all" | "failed" | "passed";

export interface GradingReportCardProps {
  submission: SubmissionRead;
  attemptNumber?: number;
  isLatestAttempt?: boolean;
  defaultFilter?: CriterionFilterMode;
}

interface RuleTypeMeta {
  label: string;
  engineLabel: string;
}

const RULE_TYPE_META: Record<GradingRuleType, RuleTypeMeta> = {
  docx_page_margins: {
    label: "Поля сторінки документа",
    engineLabel: "Word • python-docx",
  },
  docx_font: {
    label: "Гарнітура та кегль шрифту",
    engineLabel: "Word • python-docx",
  },
  docx_line_spacing: {
    label: "Міжрядковий інтервал",
    engineLabel: "Word • python-docx",
  },
  docx_alignment: {
    label: "Вирівнювання абзацу",
    engineLabel: "Word • python-docx",
  },
  docx_table_exists: {
    label: "Наявність та структура таблиці",
    engineLabel: "Word • python-docx",
  },
  docx_list_exists: {
    label: "Маркований або нумерований список",
    engineLabel: "Word • python-docx",
  },
  xlsx_formula: {
    label: "Формула у цільовій комірці",
    engineLabel: "Excel • openpyxl (data_only=False)",
  },
  xlsx_value: {
    label: "Обчислене значення комірки",
    engineLabel: "Excel • openpyxl (data_only=True)",
  },
  xlsx_chart_exists: {
    label: "Діаграма на аркуші книги",
    engineLabel: "Excel • openpyxl (_charts)",
  },
  accdb_table_exists: {
    label: "Наявність таблиці у схемі БД",
    engineLabel: "Access • access-parser",
  },
  accdb_column_exists: {
    label: "Наявність поля (стовпця) таблиці",
    engineLabel: "Access • access-parser",
  },
  accdb_column_type: {
    label: "Тип даних поля таблиці",
    engineLabel: "Access • access-parser",
  },
  accdb_query_exists: {
    label: "Наявність запиту у БД",
    engineLabel: "Access • MSysObjects",
  },
  accdb_form_exists: {
    label: "Наявність форми у БД",
    engineLabel: "Access • MSysObjects",
  },
  accdb_report_exists: {
    label: "Наявність звіту у БД",
    engineLabel: "Access • MSysObjects",
  },
  accdb_relationship_exists: {
    label: "Зв'язок між таблицями БД",
    engineLabel: "Access • MSysRelationships",
  },
  html_tag_exists: {
    label: "Наявність HTML-тегу за селектором",
    engineLabel: "HTML5 • BeautifulSoup4 DOM",
  },
  html_tag_count: {
    label: "Кількість HTML-елементів у DOM",
    engineLabel: "HTML5 • BeautifulSoup4 DOM",
  },
  html_attribute_exists: {
    label: "Атрибут HTML-елемента",
    engineLabel: "HTML5 • BeautifulSoup4 DOM",
  },
};

const FORMAT_META: Record<
  PracticalFormat,
  {
    label: string;
    badgeClass: string;
  }
> = {
  docx: {
    label: "Microsoft Word (.docx)",
    badgeClass: "border-blue-200 bg-blue-50 text-blue-700",
  },
  xlsx: {
    label: "Microsoft Excel (.xlsx)",
    badgeClass: "border-emerald-200 bg-emerald-50 text-emerald-700",
  },
  accdb: {
    label: "Microsoft Access (.accdb)",
    badgeClass: "border-amber-200 bg-amber-50 text-amber-800",
  },
  html: {
    label: "HTML5 & DOM",
    badgeClass: "border-violet-200 bg-violet-50 text-violet-700",
  },
};

const COURSE_SLUG_LABELS: Record<CourseSlug, string> = {
  word: "Microsoft Word",
  excel: "Microsoft Excel",
  access: "Microsoft Access",
  html: "HTML5 & DOM",
};

function renderFormatIcon(formatType: PracticalFormat): ReactElement {
  switch (formatType) {
    case "docx":
      return <FileText className="h-4 w-4 text-blue-600" />;
    case "xlsx":
      return <FileSpreadsheet className="h-4 w-4 text-emerald-600" />;
    case "accdb":
      return <Database className="h-4 w-4 text-amber-600" />;
    case "html":
      return <Code2 className="h-4 w-4 text-violet-600" />;
  }
}

function formatDateTime(isoString: string): string {
  const parsed = new Date(isoString);
  if (Number.isNaN(parsed.getTime())) {
    return isoString;
  }
  return parsed.toLocaleString("uk-UA", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function extractFileNameFromPath(filePath: string | null): string | null {
  if (filePath === null || filePath.trim().length === 0) {
    return null;
  }
  const normalized = filePath.replace(/\\/g, "/");
  const segments = normalized.split("/");
  return segments[segments.length - 1] ?? filePath;
}

function CriterionBreakdownItem({
  criterion,
  index,
}: {
  criterion: CriterionResult;
  index: number;
}): ReactElement {
  const ruleMeta = RULE_TYPE_META[criterion.rule_type];

  return (
    <article
      className={`rounded-2xl border p-4 transition-colors sm:p-5 ${
        criterion.passed
          ? "border-emerald-200 bg-white"
          : "border-rose-200 bg-rose-50/40"
      }`}
    >
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
        <div className="flex items-start gap-3">
          <div
            className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border ${
              criterion.passed
                ? "border-emerald-200 bg-emerald-50 text-emerald-600"
                : "border-rose-200 bg-rose-100 text-rose-600"
            }`}
          >
            {criterion.passed ? (
              <CheckCircle2 className="h-4 w-4" />
            ) : (
              <XCircle className="h-4 w-4" />
            )}
          </div>

          <div className="min-w-0 space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[11px] font-bold text-slate-700">
                #{index + 1} • {criterion.rule_id}
              </span>
              <span className="inline-flex items-center rounded-md border border-slate-200 bg-white px-2 py-0.5 text-[11px] font-semibold text-slate-600">
                {ruleMeta.label}
              </span>
              <span className="text-[11px] text-slate-400">
                {ruleMeta.engineLabel}
              </span>
            </div>

            <h4 className="text-sm font-bold text-slate-900">
              {criterion.description}
            </h4>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2 self-start">
          <span
            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${
              criterion.passed
                ? "bg-emerald-100 text-emerald-800"
                : "bg-rose-100 text-rose-800"
            }`}
          >
            {criterion.passed ? "Виконано" : "Помилка"}
          </span>
          <span
            className={`inline-flex items-center rounded-xl border px-3 py-1 font-mono text-xs font-bold ${
              criterion.passed
                ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                : "border-rose-200 bg-white text-rose-900"
            }`}
          >
            +{criterion.points_awarded.toFixed(1)} /{" "}
            {criterion.max_points.toFixed(1)} б.
          </span>
        </div>
      </div>

      {/* Пояснення автоперевірки (feedback) */}
      <div
        className={`mt-3 rounded-xl border px-3.5 py-2.5 text-xs leading-relaxed ${
          criterion.passed
            ? "border-slate-200 bg-slate-50/80 text-slate-700"
            : "border-rose-200/80 bg-white text-rose-950"
        }`}
      >
        <span className="font-semibold">Висновок парсера: </span>
        <span>{criterion.feedback}</span>
      </div>

      {/* Технічне порівняння: Ціль -> Очікувалось -> Фактично */}
      <div className="mt-3 grid grid-cols-1 gap-2.5 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-2.5">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            <Target className="h-3.5 w-3.5 text-blue-600" />
            <span>Ціль інспекції (target)</span>
          </div>
          <p className="mt-1 break-all font-mono text-xs font-semibold text-slate-900">
            {criterion.target}
          </p>
        </div>

        <div className="rounded-xl border border-emerald-200/80 bg-emerald-50/40 p-2.5">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-emerald-700">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
            <span>Очікуване значення</span>
          </div>
          <p className="mt-1 break-all font-mono text-xs font-semibold text-emerald-950">
            {criterion.expected}
          </p>
        </div>

        <div
          className={`rounded-xl border p-2.5 ${
            criterion.passed
              ? "border-slate-200 bg-slate-50/70"
              : "border-rose-300 bg-rose-100/60"
          }`}
        >
          <div
            className={`flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider ${
              criterion.passed ? "text-slate-500" : "text-rose-700"
            }`}
          >
            {criterion.passed ? (
              <Info className="h-3.5 w-3.5 text-slate-500" />
            ) : (
              <AlertTriangle className="h-3.5 w-3.5 text-rose-600" />
            )}
            <span>Фактичне значення у роботі</span>
          </div>
          <p
            className={`mt-1 break-all font-mono text-xs font-semibold ${
              criterion.passed ? "text-slate-900" : "text-rose-950"
            }`}
          >
            {criterion.actual !== null && criterion.actual.trim().length > 0
              ? criterion.actual
              : "Не виявлено (null)"}
          </p>
        </div>
      </div>
    </article>
  );
}

export function GradingReportCard({
  submission,
  attemptNumber,
  isLatestAttempt = false,
  defaultFilter = "all",
}: GradingReportCardProps): ReactElement {
  const [filterMode, setFilterMode] =
    useState<CriterionFilterMode>(defaultFilter);
  const [isMetadataExpanded, setIsMetadataExpanded] = useState<boolean>(false);
  const [isCodePreviewExpanded, setIsCodePreviewExpanded] =
    useState<boolean>(false);

  const report = submission.grading_report;
  const formatMeta = FORMAT_META[report.format_type];
  const totalCriteria = report.results.length;
  const scorePercent =
    submission.max_score > 0
      ? Math.min(
          100,
          Math.max(0, Math.round((submission.final_score / submission.max_score) * 100))
        )
      : 0;

  const isManuallyAdjusted =
    Math.abs(submission.final_score - submission.auto_score) >= 0.01;

  const filteredResults = useMemo<CriterionResult[]>(() => {
    if (filterMode === "failed") {
      return report.results.filter((item) => !item.passed);
    }
    if (filterMode === "passed") {
      return report.results.filter((item) => item.passed);
    }
    return report.results;
  }, [report.results, filterMode]);

  const metadataEntries = useMemo<Array<{ label: string; value: string }>>(() => {
    const meta = submission.extracted_metadata;
    const entries: Array<{ label: string; value: string }> = [];

    if (typeof meta.creator === "string" && meta.creator.trim().length > 0) {
      entries.push({ label: "Автор документа (dc:creator)", value: meta.creator });
    }
    if (
      typeof meta.last_modified_by === "string" &&
      meta.last_modified_by.trim().length > 0
    ) {
      entries.push({
        label: "Останнє редагування (cp:lastModifiedBy)",
        value: meta.last_modified_by,
      });
    }
    if (typeof meta.created === "string" && meta.created.trim().length > 0) {
      entries.push({
        label: "Час створення (dcterms:created)",
        value: formatDateTime(meta.created),
      });
    }
    if (typeof meta.modified === "string" && meta.modified.trim().length > 0) {
      entries.push({
        label: "Час модифікації (dcterms:modified)",
        value: formatDateTime(meta.modified),
      });
    }
    if (typeof meta.revision === "string" && meta.revision.trim().length > 0) {
      entries.push({
        label: "Номер ревізії (cp:revision)",
        value: meta.revision,
      });
    }

    return entries;
  }, [submission.extracted_metadata]);

  const uploadedFileName = extractFileNameFromPath(submission.file_path);

  return (
    <section
      className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs"
      aria-label="Детальний звіт автоперевірки практичної роботи"
    >
      {/* Шапка звіту автоперевірки */}
      <div className="border-b border-slate-200 bg-slate-50/70 p-5 sm:p-6">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              {submission.course_slug !== null && (
                <span className="inline-flex items-center rounded-full border border-slate-300 bg-white px-2.5 py-0.5 text-xs font-bold text-slate-800">
                  {COURSE_SLUG_LABELS[submission.course_slug]}
                </span>
              )}

              <span
                className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${formatMeta.badgeClass}`}
              >
                {renderFormatIcon(report.format_type)}
                <span>{formatMeta.label}</span>
              </span>

              <span className="inline-flex items-center gap-1 rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-0.5 text-xs font-bold text-indigo-800">
                <Sparkles className="h-3 w-3" />
                Варіант №{submission.variant_number}
              </span>

              {attemptNumber !== undefined && (
                <span className="inline-flex items-center rounded-full border border-slate-200 bg-white px-2.5 py-0.5 text-xs font-semibold text-slate-600">
                  Спроба №{attemptNumber}
                  {isLatestAttempt ? " (актуальна)" : ""}
                </span>
              )}
            </div>

            <h3 className="text-lg font-bold text-slate-900 sm:text-xl">
              {submission.practical_title ?? "Звіт автоперевірки практичної роботи"}
            </h3>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
              <span className="inline-flex items-center gap-1">
                <Clock className="h-3.5 w-3.5 text-slate-400" />
                Здано: {formatDateTime(submission.submitted_at)}
              </span>
              {uploadedFileName !== null && (
                <span className="inline-flex items-center gap-1 font-mono text-[11px] text-slate-600">
                  Файл: {uploadedFileName}
                </span>
              )}
              <span className="font-mono text-[11px] text-slate-400">
                ID: {submission.id.slice(0, 8)}
              </span>
            </div>
          </div>

          {/* Картка підсумкового бала */}
          <div className="flex shrink-0 flex-wrap items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-2xs">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600 text-white">
              <Award className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Підсумковий бал
              </p>
              <div className="flex items-baseline gap-1.5">
                <span className="text-2xl font-extrabold text-slate-900">
                  {submission.final_score.toFixed(1)}
                </span>
                <span className="text-sm font-semibold text-slate-500">
                  / {submission.max_score.toFixed(1)} б.
                </span>
                <span
                  className={`ml-1 rounded-md px-1.5 py-0.5 text-xs font-bold ${
                    scorePercent >= 80
                      ? "bg-emerald-50 text-emerald-700"
                      : scorePercent >= 60
                        ? "bg-blue-50 text-blue-700"
                        : scorePercent >= 40
                          ? "bg-amber-50 text-amber-700"
                          : "bg-rose-50 text-rose-700"
                  }`}
                >
                  {scorePercent}%
                </span>
              </div>
              {isManuallyAdjusted ? (
                <p className="mt-0.5 text-[11px] font-medium text-amber-700">
                  Автооцінка: {submission.auto_score.toFixed(1)} /{" "}
                  {submission.auto_max_score.toFixed(1)} б. (скориговано
                  викладачем)
                </p>
              ) : submission.manual_bonus_max > 0 ? (
                <p className="mt-0.5 text-[11px] text-slate-500">
                  Автооцінка: {submission.auto_score.toFixed(1)} /{" "}
                  {submission.auto_max_score.toFixed(1)} б. (+ до{" "}
                  {Number.isInteger(submission.manual_bonus_max)
                    ? submission.manual_bonus_max.toFixed(0)
                    : submission.manual_bonus_max.toFixed(1)}{" "}
                  б. творче завдання)
                </p>
              ) : (
                <p className="mt-0.5 text-[11px] text-slate-500">
                  Нараховано автоматично за правилами
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Статус академічної доброчесності та коментар викладача */}
        <div className="mt-4 space-y-3">
          {submission.is_plagiarism_flagged ? (
            <div
              className="flex flex-col justify-between gap-3 rounded-xl border border-rose-300 bg-rose-50/90 p-4 text-xs text-rose-950 sm:flex-row sm:items-center"
              role="alert"
            >
              <div className="flex items-start gap-3">
                <ShieldAlert className="mt-0.5 h-5 w-5 shrink-0 text-rose-600" />
                <div>
                  <p className="font-bold text-rose-900">
                    Зафіксовано підозру на порушення академічної доброчесності
                  </p>
                  <p className="mt-0.5 leading-relaxed text-rose-800">
                    {submission.plagiarism_reason ??
                      "Виявлено збіг контрольної суми SHA-256 або метаданих docProps/core.xml із роботою іншого студента."}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsMetadataExpanded((prev) => !prev)}
                className="inline-flex shrink-0 items-center gap-1 self-start rounded-lg border border-rose-300 bg-white px-3 py-1.5 text-xs font-semibold text-rose-800 hover:bg-rose-100 sm:self-center"
              >
                <Fingerprint className="h-3.5 w-3.5" />
                <span>Технічні метадані</span>
                {isMetadataExpanded ? (
                  <ChevronUp className="h-3.5 w-3.5" />
                ) : (
                  <ChevronDown className="h-3.5 w-3.5" />
                )}
              </button>
            </div>
          ) : (
            <div className="flex flex-col justify-between gap-3 rounded-xl border border-emerald-200 bg-emerald-50/70 px-4 py-3 text-xs text-emerald-950 sm:flex-row sm:items-center">
              <div className="flex items-center gap-2.5">
                <ShieldCheck className="h-5 w-5 shrink-0 text-emerald-600" />
                <div>
                  <span className="font-bold text-emerald-900">
                    Перевірка авторства успішна:
                  </span>{" "}
                  <span className="text-emerald-800">
                    збігів SHA-256 та метаданих <code>docProps/core.xml</code> з
                    іншими студентами не виявлено.
                  </span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsMetadataExpanded((prev) => !prev)}
                className="inline-flex shrink-0 items-center gap-1 self-start rounded-lg border border-emerald-300 bg-white px-3 py-1.5 text-xs font-semibold text-emerald-800 hover:bg-emerald-100 sm:self-center"
              >
                <Fingerprint className="h-3.5 w-3.5" />
                <span>Цифровий відбиток</span>
                {isMetadataExpanded ? (
                  <ChevronUp className="h-3.5 w-3.5" />
                ) : (
                  <ChevronDown className="h-3.5 w-3.5" />
                )}
              </button>
            </div>
          )}

          {/* Розгорнута панель SHA-256 та метаданих docProps/core.xml */}
          {isMetadataExpanded && (
            <div className="rounded-xl border border-slate-200 bg-white p-4 text-xs">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
                <span className="font-bold text-slate-800">
                  Цифровий паспорт зданої роботи (SHA-256 & OpenXML Metadata)
                </span>
                <span className="text-[11px] text-slate-500">
                  Модуль контролю академічної доброчесності
                </span>
              </div>

              <div className="mt-3 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-2.5 sm:col-span-2">
                  <span className="block text-[11px] font-semibold text-slate-500">
                    Контрольна сума SHA-256:
                  </span>
                  <code className="mt-0.5 block break-all font-mono text-xs text-slate-800">
                    {submission.file_hash ?? "Не обчислено"}
                  </code>
                </div>

                {metadataEntries.length > 0 ? (
                  metadataEntries.map((entry) => (
                    <div
                      key={entry.label}
                      className="rounded-lg border border-slate-200 bg-slate-50 p-2.5"
                    >
                      <span className="block text-[11px] font-semibold text-slate-500">
                        {entry.label}:
                      </span>
                      <span className="mt-0.5 block font-mono text-xs font-medium text-slate-900">
                        {entry.value}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-2.5 text-slate-500 sm:col-span-2">
                    Для формату <code>{report.format_type}</code> додаткові поля{" "}
                    <code>docProps/core.xml</code> відсутні або не заповнені.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Коментар викладача (якщо є) */}
          {submission.teacher_comment !== null &&
            submission.teacher_comment.trim().length > 0 && (
              <div className="flex items-start gap-3 rounded-xl border border-blue-200 bg-blue-50/80 p-4 text-xs text-blue-950">
                <MessageSquareQuote className="mt-0.5 h-5 w-5 shrink-0 text-blue-600" />
                <div className="space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-blue-900">
                    <UserCheck className="h-3.5 w-3.5" />
                    <span>Рецензія та коментар викладача:</span>
                  </div>
                  <p className="leading-relaxed text-blue-900">
                    {submission.teacher_comment}
                  </p>
                </div>
              </div>
            )}
        </div>
      </div>

      {/* Зведена шкала виконання критеріїв та фільтри */}
      <div className="border-b border-slate-100 bg-white px-5 py-4 sm:px-6">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-3 text-xs">
              <span className="font-bold text-slate-800">
                Виконання критеріїв перевірки:
              </span>
              <span className="inline-flex items-center gap-1 font-semibold text-emerald-700">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Успішно: {report.passed_count}
              </span>
              <span className="inline-flex items-center gap-1 font-semibold text-rose-700">
                <XCircle className="h-3.5 w-3.5" />
                Помилок: {report.failed_count}
              </span>
              <span className="text-slate-500">
                (Усього правил: {totalCriteria})
              </span>
            </div>

            <div className="flex h-2 w-full max-w-md overflow-hidden rounded-full bg-slate-100">
              {totalCriteria > 0 && (
                <>
                  <div
                    className="h-full bg-emerald-500 transition-all duration-300"
                    style={{
                      width: `${(report.passed_count / totalCriteria) * 100}%`,
                    }}
                  />
                  <div
                    className="h-full bg-rose-500 transition-all duration-300"
                    style={{
                      width: `${(report.failed_count / totalCriteria) * 100}%`,
                    }}
                  />
                </>
              )}
            </div>
          </div>

          {/* Кнопки фільтрації критеріїв */}
          <div
            className="inline-flex flex-wrap items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 p-1"
            role="tablist"
            aria-label="Фільтр критеріїв автоперевірки"
          >
            <span className="hidden items-center gap-1 px-2 text-[11px] font-semibold text-slate-500 sm:inline-flex">
              <Filter className="h-3 w-3" />
              Показати:
            </span>
            <button
              type="button"
              role="tab"
              aria-selected={filterMode === "all"}
              onClick={() => setFilterMode("all")}
              className={`rounded-lg px-2.5 py-1 text-xs font-semibold transition-colors ${
                filterMode === "all"
                  ? "bg-slate-900 text-white"
                  : "text-slate-600 hover:bg-white hover:text-slate-900"
              }`}
            >
              Усі ({totalCriteria})
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={filterMode === "failed"}
              onClick={() => setFilterMode("failed")}
              className={`rounded-lg px-2.5 py-1 text-xs font-semibold transition-colors ${
                filterMode === "failed"
                  ? "bg-rose-600 text-white"
                  : "text-rose-700 hover:bg-white"
              }`}
            >
              Помилки ({report.failed_count})
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={filterMode === "passed"}
              onClick={() => setFilterMode("passed")}
              className={`rounded-lg px-2.5 py-1 text-xs font-semibold transition-colors ${
                filterMode === "passed"
                  ? "bg-emerald-600 text-white"
                  : "text-emerald-700 hover:bg-white"
              }`}
            >
              Виконані ({report.passed_count})
            </button>
          </div>
        </div>
      </div>

      {/* Список карток розбору критеріїв */}
      <div className="space-y-3 p-5 sm:p-6">
        {filteredResults.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50/50 p-8 text-center">
            {filterMode === "failed" ? (
              <>
                <CheckCircle2 className="mx-auto h-9 w-9 text-emerald-500" />
                <h4 className="mt-2.5 text-sm font-bold text-slate-900">
                  Помилок не виявлено!
                </h4>
                <p className="mt-1 text-xs text-slate-500">
                  Усі критерії автоперевірки для цієї здачі виконані бездоганно.
                </p>
              </>
            ) : (
              <>
                <Info className="mx-auto h-9 w-9 text-slate-400" />
                <h4 className="mt-2.5 text-sm font-bold text-slate-900">
                  Критерії за обраним фільтром відсутні
                </h4>
                <p className="mt-1 text-xs text-slate-500">
                  Перемкніть фільтр на «Усі», щоб переглянути повний протокол
                  перевірки.
                </p>
              </>
            )}
          </div>
        ) : (
          filteredResults.map((criterion, idx) => (
            <CriterionBreakdownItem
              key={criterion.rule_id}
              criterion={criterion}
              index={idx}
            />
          ))
        )}

        {/* Перегляд зданого HTML-коду (якщо робота формату HTML) */}
        {submission.raw_code !== null &&
          submission.raw_code.trim().length > 0 && (
            <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50/70">
              <button
                type="button"
                onClick={() => setIsCodePreviewExpanded((prev) => !prev)}
                className="flex w-full items-center justify-between px-4 py-3 text-left text-xs font-semibold text-slate-800 hover:bg-slate-100/80"
              >
                <span className="inline-flex items-center gap-2">
                  <FileCode2 className="h-4 w-4 text-violet-600" />
                  <span>
                    Переглянути надісланий вихідний HTML-код (
                    {submission.raw_code.length} символів)
                  </span>
                </span>
                {isCodePreviewExpanded ? (
                  <ChevronUp className="h-4 w-4 text-slate-500" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-slate-500" />
                )}
              </button>

              {isCodePreviewExpanded && (
                <div className="border-t border-slate-200 p-4">
                  <pre className="max-h-80 overflow-auto rounded-xl border border-slate-800 bg-slate-900 p-4 font-mono text-xs leading-relaxed text-slate-100">
                    <code>{submission.raw_code}</code>
                  </pre>
                </div>
              )}
            </div>
          )}
      </div>
    </section>
  );
}

export default GradingReportCard;
