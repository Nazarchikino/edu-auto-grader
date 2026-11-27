import {
  Suspense,
  lazy,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
  type FormEvent,
  type ReactElement,
} from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import {
  AlertCircle,
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Award,
  BookOpen,
  Check,
  CheckCircle2,
  ClipboardCheck,
  Clock,
  Copy,
  Database,
  Download,
  Eye,
  FileCheck2,
  FileCode2,
  FileDown,
  FileSpreadsheet,
  FileText,
  FlaskConical,
  HardDriveUpload,
  HelpCircle,
  Info,
  KeyRound,
  ListChecks,
  Loader2,
  Lock,
  RefreshCw,
  RotateCcw,
  Send,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Table2,
  Trash2,
  Unlock,
  UploadCloud,
  XCircle,
} from "lucide-react";
import apiClient from "../../api/client";
import {
  MarkdownRenderer,
  renderInlineMarkdown,
} from "../../components/common/MarkdownRenderer";
import { DryRunResultPanel } from "../../components/grading/DryRunResultPanel";
import { extractApiErrorMessage, useAuth } from "../../context/AuthContext";
import type {
  DryRunGradingResponse,
  ErrorResponse,
  HtmlDryRunRequest,
  HtmlSubmissionRequest,
  SubmissionRead,
} from "../../types/api";
import type {
  ModuleDetailRead,
  PracticalFormat,
  PracticalStudentRead,
  QuizAnswerItem,
  QuizSubmitRequest,
  QuizSubmitResponse,
} from "../../types/course";

type ModuleSectionTab = "lecture" | "quiz" | "practical";
type BinaryPracticalFormat = Exclude<PracticalFormat, "html">;

const HtmlSandbox = lazy(
  () => import("../../components/sandbox/HtmlSandbox")
);

interface FileUploadFormatMeta {
  extension: string;
  acceptAttr: string;
  applicationLabel: string;
  hintText: string;
}

const FORMAT_BADGE_LABELS: Record<PracticalFormat, string> = {
  docx: "Microsoft Word (.docx)",
  xlsx: "Microsoft Excel (.xlsx)",
  accdb: "Microsoft Access (.accdb)",
  html: "HTML5 & DOM (Пісочниця)",
};

const FILE_UPLOAD_FORMAT_META: Record<
  BinaryPracticalFormat,
  FileUploadFormatMeta
> = {
  docx: {
    extension: ".docx",
    acceptAttr:
      ".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    applicationLabel: "Документ Microsoft Word (.docx)",
    hintText:
      "Перевіряються поля сторінки, шрифти, міжрядковий інтервал, вирівнювання абзаців, таблиці, списки та метадані docProps/core.xml.",
  },
  xlsx: {
    extension: ".xlsx",
    acceptAttr:
      ".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    applicationLabel: "Книга Microsoft Excel (.xlsx)",
    hintText:
      "Перевіряються формули в цільових комірках (data_only=False), обчислені значення (data_only=True), наявність діаграм та метадані docProps/core.xml.",
  },
  accdb: {
    extension: ".accdb",
    acceptAttr: ".accdb,application/msaccess,application/x-msaccess",
    applicationLabel: "База даних Microsoft Access (.accdb)",
    hintText:
      "Перевіряються наявність таблиць у схемі БД, назви стовпців, їхні типи даних та контрольна сума SHA-256.",
  },
};

function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} Б`;
  }
  const kilobytes = bytes / 1024;
  if (kilobytes < 1024) {
    return `${kilobytes.toFixed(1)} КБ`;
  }
  const megabytes = kilobytes / 1024;
  return `${megabytes.toFixed(2)} МБ`;
}

interface ShuffledQuizOption {
  text: string;
  originalIndex: number;
}

/**
 * Перемішує варіанти відповідей алгоритмом Фішера–Єйтса зі збереженням
 * оригінального індексу (`originalIndex`) для коректної перевірки на бекенді.
 */
function shuffleQuizOptions(options: readonly string[]): ShuffledQuizOption[] {
  const items: ShuffledQuizOption[] = options.map((text, index) => ({
    text,
    originalIndex: index,
  }));
  for (let idx = items.length - 1; idx > 0; idx -= 1) {
    const swapIdx = Math.floor(Math.random() * (idx + 1));
    const currentItem = items[idx];
    const targetItem = items[swapIdx];
    if (currentItem !== undefined && targetItem !== undefined) {
      items[idx] = targetItem;
      items[swapIdx] = currentItem;
    }
  }
  return items;
}

function formatCountdownMmSs(totalSeconds: number): string {
  const safeSeconds = Math.max(0, Math.floor(totalSeconds));
  const minutes = Math.floor(safeSeconds / 60);
  const seconds = safeSeconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

function extractRetryAfterSeconds(error: unknown): number | null {
  if (!axios.isAxiosError<ErrorResponse>(error) || error.response?.status !== 429) {
    return null;
  }

  const rawHeaders: unknown = error.response.headers;
  if (isPlainRecord(rawHeaders)) {
    const retryHeader = rawHeaders["retry-after"] ?? rawHeaders["Retry-After"];
    if (typeof retryHeader === "string" || typeof retryHeader === "number") {
      const parsedHeader = Number.parseInt(String(retryHeader), 10);
      if (Number.isFinite(parsedHeader) && parsedHeader > 0) {
        return parsedHeader;
      }
    }
  }

  const responseContext = error.response.data?.context;
  if (isPlainRecord(responseContext)) {
    const rawContextSeconds = responseContext["retry_after_seconds"];
    if (
      typeof rawContextSeconds === "number" &&
      Number.isFinite(rawContextSeconds) &&
      rawContextSeconds > 0
    ) {
      return Math.ceil(rawContextSeconds);
    }
  }

  return null;
}

function sanitizeDownloadFilename(rawName: string): string {
  const trimmed = rawName.trim().replace(/^["']|["']$/g, "");
  const baseName = trimmed.split(/[/\\]/).pop() ?? "";
  return baseName.trim();
}

function parseFilenameFromContentDisposition(
  headerValue: unknown,
  fallbackFilename: string
): string {
  if (typeof headerValue !== "string" || headerValue.trim().length === 0) {
    return fallbackFilename;
  }

  const utf8Match = /filename\*\s*=\s*UTF-8''([^;\r\n]+)/i.exec(headerValue);
  if (utf8Match?.[1] !== undefined) {
    try {
      const decoded = sanitizeDownloadFilename(
        decodeURIComponent(utf8Match[1].trim())
      );
      if (decoded.length > 0) {
        return decoded;
      }
    } catch {
      // Якщо UTF-8 послідовність пошкоджена — переходимо до ASCII filename
    }
  }

  const asciiMatch = /filename\s*=\s*(?:"([^"]+)"|([^;\r\n]+))/i.exec(
    headerValue
  );
  const rawAscii = asciiMatch?.[1] ?? asciiMatch?.[2];
  if (rawAscii !== undefined) {
    const cleaned = sanitizeDownloadFilename(rawAscii);
    if (cleaned.length > 0) {
      return cleaned;
    }
  }

  return fallbackFilename;
}

function hasStringDetail(value: unknown): value is { detail: string } {
  return (
    typeof value === "object" &&
    value !== null &&
    "detail" in value &&
    typeof (value as Record<string, unknown>).detail === "string"
  );
}

async function extractBlobApiErrorMessage(
  error: unknown,
  fallbackMessage: string
): Promise<string> {
  if (axios.isAxiosError(error)) {
    const responseData: unknown = error.response?.data;
    if (responseData instanceof Blob) {
      try {
        const rawText = await responseData.text();
        const parsed: unknown = JSON.parse(rawText);
        if (hasStringDetail(parsed) && parsed.detail.trim().length > 0) {
          return parsed.detail.trim();
        }
      } catch {
        // Тіло помилки не є валідним JSON
      }
    }
  }
  return extractApiErrorMessage(error, fallbackMessage);
}

async function fetchModuleDetail(
  moduleId: string,
  previewVariant?: number
): Promise<ModuleDetailRead> {
  const response = await apiClient.get<ModuleDetailRead>(
    `/modules/${moduleId}`,
    previewVariant !== undefined
      ? { params: { preview_variant: previewVariant } }
      : undefined
  );
  return response.data;
}

async function fetchStudentPractical(
  practicalId: string
): Promise<PracticalStudentRead> {
  const response = await apiClient.get<PracticalStudentRead>(
    `/practicals/${practicalId}`
  );
  return response.data;
}

async function submitQuizAnswers(
  moduleId: string,
  payload: QuizSubmitRequest
): Promise<QuizSubmitResponse> {
  const response = await apiClient.post<QuizSubmitResponse>(
    `/modules/${moduleId}/quiz/submit`,
    payload
  );
  return response.data;
}

async function submitHtmlPractical(
  practicalId: string,
  payload: HtmlSubmissionRequest
): Promise<SubmissionRead> {
  const response = await apiClient.post<SubmissionRead>(
    `/practicals/${practicalId}/submit`,
    payload
  );
  return response.data;
}

async function submitFilePractical(
  practicalId: string,
  file: File
): Promise<SubmissionRead> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiClient.post<SubmissionRead>(
    `/practicals/${practicalId}/submit`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );
  return response.data;
}

async function dryRunHtmlPractical(
  practicalId: string,
  payload: HtmlDryRunRequest
): Promise<DryRunGradingResponse> {
  const response = await apiClient.post<DryRunGradingResponse>(
    `/practicals/${practicalId}/dry-run`,
    payload
  );
  return response.data;
}

async function dryRunFilePractical(
  practicalId: string,
  file: File,
  variantNumber: number
): Promise<DryRunGradingResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("variant_number", String(variantNumber));
  const response = await apiClient.post<DryRunGradingResponse>(
    `/practicals/${practicalId}/dry-run`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );
  return response.data;
}

const HIDDEN_WORD_PARAMETER_KEYS = new Set<string>([
  "topic",
  "level_1_task",
  "level_2_task",
  "level_3_task",
  "raw_text_to_use",
]);

const PARAMETER_DISPLAY_LABELS: Record<string, string> = {
  database_file: "Файл БД",
  tables: "Структура таблиць БД",
  focus: "Фокус роботи",
  tasks: "Завдання",
  difficulty_level: "Рівень складності",
  tasks_count: "Кількість завдань",
  task_titles: "Перелік завдань",
  sheets_count: "Кількість аркушів",
  images: "Ілюстрації-зразки",
  body_font: "Шрифт основного тексту",
  body_size: "Розмір шрифту (пт)",
  body_alignment: "Вирівнювання тексту",
  line_spacing: "Міжрядковий інтервал",
  margins: "Поля сторінки",
  min_tables: "Таблиці в документі",
  table_1: "Головна таблиця",
  table_2: "Друга таблиця",
  table_3: "Третя таблиця",
  pk_target: "Ключове поле",
  theme: "Тема",
  required_heading: "Заголовок сторінки",
  min_items: "Мінімум елементів",
};

const ALIGNMENT_DISPLAY_LABELS: Record<string, string> = {
  justify: "по ширині",
  both: "по ширині",
  center: "по центру",
  left: "по лівому краю",
  right: "по правому краю",
  distribute: "рівномірно за шириною",
};

const MARGIN_SIDE_DISPLAY_LABELS: Record<string, string> = {
  left: "ліве",
  right: "праве",
  top: "верхнє",
  bottom: "нижнє",
};

function formatPointsValue(points: number): string {
  const rounded = Math.round(points * 100) / 100;
  return Number.isInteger(rounded)
    ? String(rounded)
    : rounded.toFixed(2).replace(/0$/, "");
}

function formatMarginsChipDisplay(raw: string): string {
  const cleaned = raw.trim();
  if (cleaned.includes("=")) {
    const parts = cleaned
      .split(/[,;]/)
      .map((chunk) => chunk.trim())
      .filter((chunk) => chunk.includes("="))
      .map((chunk) => {
        const [sideRaw, valRaw] = chunk.split("=", 2);
        const sideKey = (sideRaw ?? "").trim().toLowerCase();
        const sideLabel = MARGIN_SIDE_DISPLAY_LABELS[sideKey] ?? sideKey;
        const valueFormatted = (valRaw ?? "")
          .trim()
          .replace(/cm$/i, " см")
          .replace(/mm$/i, " мм")
          .replace(".", ",");
        return `${sideLabel} — ${valueFormatted}`;
      });
    if (parts.length > 0) {
      return parts.join(", ");
    }
  }
  const singleMatch = /^(\d+(?:[.,]\d+)?)\s*(cm|mm)$/i.exec(cleaned);
  if (singleMatch !== null) {
    const numPart = (singleMatch[1] ?? "").replace(".", ",");
    const unitPart =
      (singleMatch[2] ?? "").toLowerCase() === "cm" ? "см" : "мм";
    return `по ${numPart} ${unitPart}`;
  }
  return cleaned;
}

interface AccessFieldDescriptor {
  name: string;
  rawType: string | null;
  canonicalType: string | null;
  note: string | null;
}

interface AccessTableDescriptor {
  name: string;
  primaryKeys: string[];
  fields: AccessFieldDescriptor[];
}

function isPlainRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isPrimitiveValue(
  value: unknown
): value is string | number | boolean | null {
  return (
    value === null ||
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  );
}

function formatParameterLabel(paramKey: string): string {
  return PARAMETER_DISPLAY_LABELS[paramKey] ?? paramKey;
}

function formatScalarValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "—";
  }
  if (typeof value === "boolean") {
    return value ? "Так" : "Ні";
  }
  if (typeof value === "number" || typeof value === "string") {
    return String(value);
  }
  if (Array.isArray(value)) {
    return value.map((item) => formatScalarValue(item)).join(", ");
  }
  if (isPlainRecord(value)) {
    return Object.entries(value)
      .map(([k, v]) => `${k}: ${formatScalarValue(v)}`)
      .join("; ");
  }
  return String(value);
}

function parseAccessTableDescriptor(
  candidate: unknown
): AccessTableDescriptor | null {
  if (!isPlainRecord(candidate)) {
    return null;
  }
  if (typeof candidate.name !== "string" || candidate.name.trim().length === 0) {
    return null;
  }
  if (!Array.isArray(candidate.fields)) {
    return null;
  }

  const primaryKeys: string[] = [];
  if (Array.isArray(candidate.primary_keys)) {
    for (const pk of candidate.primary_keys) {
      if (typeof pk === "string" && pk.trim().length > 0) {
        primaryKeys.push(pk.trim());
      }
    }
  }

  const fields: AccessFieldDescriptor[] = [];
  for (const rawField of candidate.fields) {
    if (typeof rawField === "string") {
      const trimmed = rawField.trim();
      if (trimmed.length > 0) {
        fields.push({
          name: trimmed,
          rawType: null,
          canonicalType: null,
          note: null,
        });
      }
      continue;
    }

    if (isPlainRecord(rawField) && typeof rawField.name === "string") {
      const fieldName = rawField.name.trim();
      if (fieldName.length === 0) {
        continue;
      }
      const rawType =
        typeof rawField.raw_type === "string" &&
        rawField.raw_type.trim().length > 0
          ? rawField.raw_type.trim()
          : null;
      const canonicalType =
        typeof rawField.type === "string" && rawField.type.trim().length > 0
          ? rawField.type.trim()
          : null;
      const note =
        typeof rawField.note === "string" && rawField.note.trim().length > 0
          ? rawField.note.trim()
          : null;

      if (
        note !== null &&
        note.toLowerCase().includes("первинний ключ") &&
        !primaryKeys.includes(fieldName)
      ) {
        primaryKeys.push(fieldName);
      }

      fields.push({
        name: fieldName,
        rawType,
        canonicalType,
        note,
      });
    }
  }

  return {
    name: candidate.name.trim(),
    primaryKeys,
    fields,
  };
}

function parseAccessTablesList(value: unknown): AccessTableDescriptor[] | null {
  if (!Array.isArray(value) || value.length === 0) {
    return null;
  }
  const parsed: AccessTableDescriptor[] = [];
  for (const item of value) {
    const table = parseAccessTableDescriptor(item);
    if (table === null) {
      return null;
    }
    parsed.push(table);
  }
  return parsed;
}

function isLongStringArray(value: unknown): value is string[] {
  if (!Array.isArray(value) || value.length === 0) {
    return false;
  }
  if (!value.every((item): item is string => typeof item === "string")) {
    return false;
  }
  return value.some((item) => item.length > 42) || value.length >= 6;
}

function isInlineChipValue(value: unknown): boolean {
  if (isPrimitiveValue(value)) {
    return true;
  }
  if (
    Array.isArray(value) &&
    value.every((item) => isPrimitiveValue(item)) &&
    !isLongStringArray(value)
  ) {
    return true;
  }
  return false;
}

function formatInlineChipDisplay(paramKey: string, value: unknown): string {
  if (Array.isArray(value)) {
    if (paramKey === "images") {
      return value
        .map((item) => {
          const text = formatScalarValue(item);
          const parts = text.split("/");
          return parts[parts.length - 1] ?? text;
        })
        .join(", ");
    }
    return value.map((item) => formatScalarValue(item)).join(", ");
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    const lowered = trimmed.toLowerCase();
    if (paramKey === "body_alignment" && lowered in ALIGNMENT_DISPLAY_LABELS) {
      return ALIGNMENT_DISPLAY_LABELS[lowered] ?? trimmed;
    }
    if (paramKey === "margins") {
      return formatMarginsChipDisplay(trimmed);
    }
    if (paramKey === "line_spacing") {
      return trimmed.replace(".", ",");
    }
    if (paramKey === "min_tables") {
      if (trimmed === ">=0") {
        return "не обов'язково";
      }
      if (trimmed === ">=1") {
        return "не менше 1";
      }
    }
  }
  return formatScalarValue(value);
}

function renderGenericObjectCard(
  record: Record<string, unknown>,
  cardKey: string
): ReactElement {
  return (
    <div
      key={cardKey}
      className="rounded-lg border border-indigo-200/80 bg-white p-3 text-xs shadow-2xs"
    >
      <dl className="space-y-1.5">
        {Object.entries(record).map(([nestedKey, nestedVal]) => (
          <div
            key={`${cardKey}-${nestedKey}`}
            className="flex flex-col gap-0.5 sm:flex-row sm:gap-2"
          >
            <dt className="shrink-0 font-semibold text-indigo-800">
              {formatParameterLabel(nestedKey)}:
            </dt>
            <dd className="min-w-0 text-slate-700">
              {formatScalarValue(nestedVal)}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

interface VariantParametersSectionProps {
  parameters: Record<string, unknown>;
  copiedRawText: boolean;
  onCopyRawText: (text: string) => void;
}

function VariantParametersSection({
  parameters,
  copiedRawText,
  onCopyRawText,
}: VariantParametersSectionProps): ReactElement | null {
  const rawTextCandidate = parameters.raw_text_to_use;
  const rawTextToUse =
    typeof rawTextCandidate === "string" && rawTextCandidate.trim().length > 0
      ? rawTextCandidate
      : null;

  const visibleEntries = Object.entries(parameters).filter(
    ([paramKey]) => !HIDDEN_WORD_PARAMETER_KEYS.has(paramKey)
  );

  const inlineChipEntries = visibleEntries.filter(([, value]) =>
    isInlineChipValue(value)
  );
  const structuredEntries = visibleEntries.filter(
    ([, value]) => !isInlineChipValue(value)
  );

  if (rawTextToUse === null && visibleEntries.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 space-y-4 border-t border-indigo-200/70 pt-4">
      {rawTextToUse !== null && (
        <div className="rounded-xl border border-indigo-200 bg-white/90 p-4 shadow-2xs">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-indigo-600" />
              <p className="text-xs font-bold uppercase tracking-wider text-indigo-900">
                Текст/Дані для копіювання
              </p>
            </div>
            <button
              type="button"
              onClick={() => onCopyRawText(rawTextToUse)}
              className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold transition-colors ${
                copiedRawText
                  ? "border-emerald-300 bg-emerald-50 text-emerald-800"
                  : "border-indigo-200 bg-indigo-50 text-indigo-800 hover:border-indigo-300 hover:bg-indigo-100"
              }`}
            >
              {copiedRawText ? (
                <>
                  <Check className="h-3.5 w-3.5 text-emerald-600" />
                  <span>Скопійовано!</span>
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5" />
                  <span>Скопіювати текст у буфер</span>
                </>
              )}
            </button>
          </div>
          <pre className="mt-2.5 max-h-64 overflow-y-auto whitespace-pre-wrap break-words rounded-lg border border-slate-200 bg-slate-50/80 p-3.5 font-sans text-xs leading-relaxed text-slate-800 sm:text-sm">
            {rawTextToUse}
          </pre>
        </div>
      )}

      {visibleEntries.length > 0 && (
        <div className="space-y-3">
          <p className="text-xs font-semibold text-indigo-900">
            Контрольні параметри варіанта:
          </p>

          {inlineChipEntries.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {inlineChipEntries.map(([paramKey, paramValue]) => (
                <span
                  key={paramKey}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-indigo-200 bg-white px-2.5 py-1 font-mono text-xs text-slate-800"
                >
                  <span className="font-semibold text-indigo-700">
                    {formatParameterLabel(paramKey)}:
                  </span>
                  <span>{formatInlineChipDisplay(paramKey, paramValue)}</span>
                </span>
              ))}
            </div>
          )}

          {structuredEntries.map(([paramKey, paramValue]) => {
            const accessTables = parseAccessTablesList(paramValue);
            if (accessTables !== null) {
              return (
                <div key={paramKey} className="space-y-2">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-indigo-900">
                    <Database className="h-3.5 w-3.5 text-indigo-600" />
                    <span>{formatParameterLabel(paramKey)}:</span>
                  </div>
                  <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                    {accessTables.map((table) => {
                      const pkSet = new Set(
                        table.primaryKeys.map((pk) => pk.toLowerCase())
                      );
                      return (
                        <div
                          key={table.name}
                          className="rounded-xl border border-indigo-200/80 bg-white p-3.5 shadow-2xs"
                        >
                          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-2">
                            <div className="flex items-center gap-1.5 text-sm font-bold text-slate-900">
                              <Table2 className="h-4 w-4 text-indigo-600" />
                              <span>{table.name}</span>
                            </div>
                            <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">
                              {table.fields.length} полів
                            </span>
                          </div>

                          {table.primaryKeys.length > 0 && (
                            <div className="mt-2 flex flex-wrap items-center gap-1.5">
                              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-800">
                                <KeyRound className="h-3 w-3 text-amber-600" />
                                Ключові поля:
                              </span>
                              {table.primaryKeys.map((pk) => (
                                <span
                                  key={`${table.name}-pk-${pk}`}
                                  className="rounded-md border border-amber-200 bg-amber-50 px-2 py-0.5 text-[11px] font-semibold text-amber-900"
                                >
                                  {pk}
                                </span>
                              ))}
                            </div>
                          )}

                          <ul className="mt-2.5 space-y-1.5 text-xs text-slate-700">
                            {table.fields.map((field, fieldIdx) => {
                              const isPrimaryKey = pkSet.has(
                                field.name.toLowerCase()
                              );
                              const typeLabel =
                                field.rawType !== null &&
                                field.canonicalType !== null
                                  ? `${field.rawType} (${field.canonicalType})`
                                  : (field.rawType ?? field.canonicalType);

                              return (
                                <li
                                  key={`${table.name}-f-${fieldIdx}-${field.name}`}
                                  className="flex flex-wrap items-baseline justify-between gap-x-2 gap-y-0.5 rounded-md bg-slate-50/80 px-2.5 py-1"
                                >
                                  <span className="inline-flex items-center gap-1.5 font-medium text-slate-800">
                                    {isPrimaryKey && (
                                      <KeyRound
                                        className="h-3 w-3 shrink-0 text-amber-600"
                                        aria-label="Ключове поле"
                                      />
                                    )}
                                    <span>{field.name}</span>
                                  </span>
                                  {typeLabel !== null && (
                                    <span className="font-mono text-[11px] text-indigo-700">
                                      {typeLabel}
                                    </span>
                                  )}
                                  {field.note !== null && (
                                    <span className="w-full text-[11px] italic text-slate-500">
                                      {field.note}
                                    </span>
                                  )}
                                </li>
                              );
                            })}
                          </ul>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            }

            if (isLongStringArray(paramValue)) {
              return (
                <div
                  key={paramKey}
                  className="rounded-xl border border-indigo-200/80 bg-white p-3.5 shadow-2xs"
                >
                  <p className="text-xs font-semibold text-indigo-900">
                    {formatParameterLabel(paramKey)}:
                  </p>
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-xs leading-relaxed text-slate-700">
                    {paramValue.map((entry, idx) => (
                      <li key={`${paramKey}-item-${idx}`}>
                        {renderInlineMarkdown(entry)}
                      </li>
                    ))}
                  </ul>
                </div>
              );
            }

            if (Array.isArray(paramValue)) {
              return (
                <div key={paramKey} className="space-y-2">
                  <p className="text-xs font-semibold text-indigo-900">
                    {formatParameterLabel(paramKey)}:
                  </p>
                  <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                    {paramValue.map((item, idx) =>
                      isPlainRecord(item) ? (
                        renderGenericObjectCard(item, `${paramKey}-${idx}`)
                      ) : (
                        <div
                          key={`${paramKey}-${idx}`}
                          className="rounded-lg border border-indigo-200/80 bg-white px-3 py-2 text-xs text-slate-700"
                        >
                          {formatScalarValue(item)}
                        </div>
                      )
                    )}
                  </div>
                </div>
              );
            }

            if (isPlainRecord(paramValue)) {
              return (
                <div key={paramKey} className="space-y-1.5">
                  <p className="text-xs font-semibold text-indigo-900">
                    {formatParameterLabel(paramKey)}:
                  </p>
                  {renderGenericObjectCard(paramValue, paramKey)}
                </div>
              );
            }

            return (
              <div
                key={paramKey}
                className="rounded-lg border border-indigo-200 bg-white px-3 py-2 text-xs text-slate-800"
              >
                <span className="font-semibold text-indigo-700">
                  {formatParameterLabel(paramKey)}:{" "}
                </span>
                <span>{formatScalarValue(paramValue)}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export interface ModuleViewPageProps {
  previewMode?: boolean;
}

export function ModuleViewPage({
  previewMode = false,
}: ModuleViewPageProps): ReactElement {
  const { courseId, moduleId } = useParams<{
    courseId?: string;
    moduleId: string;
  }>();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const copyResetTimerRef = useRef<number | null>(null);

  const [activeTab, setActiveTab] = useState<ModuleSectionTab>("lecture");
  const [previewVariant, setPreviewVariant] = useState<number>(1);
  const [simulateQuizPassed, setSimulateQuizPassed] = useState<boolean>(true);
  const [selectedAnswers, setSelectedAnswers] = useState<
    Record<string, number>
  >({});
  const [lastQuizResult, setLastQuizResult] =
    useState<QuizSubmitResponse | null>(null);
  const [quizError, setQuizError] = useState<string | null>(null);

  const [shuffleSeed, setShuffleSeed] = useState<number>(0);
  const [shuffledOptionsMap, setShuffledOptionsMap] = useState<
    Record<string, ShuffledQuizOption[]>
  >({});
  const lastShuffledSignatureRef = useRef<string>("");

  const [cooldownSeconds, setCooldownSeconds] = useState<number>(0);
  const cooldownDeadlineRef = useRef<number | null>(null);
  const prevCooldownActiveRef = useRef<boolean>(false);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragActive, setIsDragActive] = useState<boolean>(false);
  const [submissionError, setSubmissionError] = useState<string | null>(null);
  const [lastSubmissionResult, setLastSubmissionResult] =
    useState<SubmissionRead | null>(null);
  const [lastDryRunResult, setLastDryRunResult] =
    useState<DryRunGradingResponse | null>(null);
  const [copiedRawText, setCopiedRawText] = useState<boolean>(false);
  const [isDownloadingTemplate, setIsDownloadingTemplate] =
    useState<boolean>(false);
  const [templateDownloadError, setTemplateDownloadError] = useState<
    string | null
  >(null);

  const startQuizCooldown = useCallback((seconds: number): void => {
    const normalized = Math.max(0, Math.ceil(seconds));
    if (normalized <= 0) {
      cooldownDeadlineRef.current = null;
      setCooldownSeconds(0);
      return;
    }
    cooldownDeadlineRef.current = Date.now() + normalized * 1000;
    setCooldownSeconds(normalized);
  }, []);

  const resolvedModuleId = moduleId ?? "";

  const {
    data: module,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<ModuleDetailRead>({
    queryKey: previewMode
      ? ["module-preview", resolvedModuleId, previewVariant]
      : ["module", resolvedModuleId],
    queryFn: () =>
      fetchModuleDetail(
        resolvedModuleId,
        previewMode ? previewVariant : undefined
      ),
    enabled: resolvedModuleId.length > 0,
  });

  const practicalId = module?.practical?.id ?? null;
  const effectiveQuizPassed = previewMode
    ? simulateQuizPassed
    : (module?.quiz_passed ?? false);
  const effectivePracticalUnlocked = previewMode
    ? simulateQuizPassed
    : (module?.practical_unlocked ?? false);

  const {
    data: fetchedStudentPractical,
    isLoading: isLoadingStudentPractical,
    isError: isStudentPracticalError,
    error: studentPracticalError,
  } = useQuery<PracticalStudentRead>({
    queryKey: ["practical-student", practicalId],
    queryFn: () => fetchStudentPractical(practicalId ?? ""),
    enabled:
      !previewMode &&
      practicalId !== null &&
      effectivePracticalUnlocked &&
      user?.role === "student",
  });

  const practicalDetail = useMemo<PracticalStudentRead | undefined>(() => {
    if (!previewMode) {
      return fetchedStudentPractical;
    }
    const summary = module?.practical;
    if (summary === null || summary === undefined) {
      return undefined;
    }
    const variantNum = summary.assigned_variant_number;
    const totalVars = Math.max(1, summary.total_variants);
    const resolvedVariant = summary.variant ?? {
      variant_number: variantNum,
      title: summary.title,
      task_description: summary.instructions ?? "",
      parameters: {},
    };
    return {
      id: summary.id,
      module_id: summary.module_id,
      title: summary.title,
      instructions: summary.instructions ?? "",
      format_type: summary.format_type,
      max_score: summary.max_score,
      auto_max_score: summary.auto_max_score,
      manual_bonus_max: summary.manual_bonus_max,
      needs_rules_review: summary.needs_rules_review,
      has_template_file: summary.has_template_file,
      template_file_name: summary.template_file_name,
      variant_index: Math.max(0, variantNum - 1),
      variant_number: variantNum,
      total_variants: totalVars,
      variant: resolvedVariant,
      grading_criteria: summary.grading_criteria,
    };
  }, [previewMode, fetchedStudentPractical, module]);

  const isLoadingPractical = previewMode ? false : isLoadingStudentPractical;
  const isPracticalError = previewMode ? false : isStudentPracticalError;
  const practicalError = previewMode ? null : studentPracticalError;

  const totalVariants = Math.max(
    1,
    module?.practical?.total_variants ?? practicalDetail?.total_variants ?? 1
  );

  useEffect(() => {
    setSelectedAnswers({});
    setLastQuizResult(null);
    setQuizError(null);
    setSelectedFile(null);
    setIsDragActive(false);
    setSubmissionError(null);
    setLastSubmissionResult(null);
    setLastDryRunResult(null);
    setPreviewVariant(1);
    setSimulateQuizPassed(true);
    setCopiedRawText(false);
    setTemplateDownloadError(null);
    setActiveTab("lecture");
    prevCooldownActiveRef.current = false;
    cooldownDeadlineRef.current = null;
    setCooldownSeconds(0);
    lastShuffledSignatureRef.current = "";
    setShuffledOptionsMap({});
  }, [resolvedModuleId]);

  useEffect(() => {
    if (!module) {
      return;
    }
    const signature = `${module.id}|${shuffleSeed}|${module.quiz_questions
      .map((question) => `${question.id}:${question.options.join("\u001f")}`)
      .join("\u001e")}`;
    if (lastShuffledSignatureRef.current === signature) {
      return;
    }
    lastShuffledSignatureRef.current = signature;

    const nextShuffledMap: Record<string, ShuffledQuizOption[]> = {};
    for (const question of module.quiz_questions) {
      nextShuffledMap[question.id] = shuffleQuizOptions(question.options);
    }
    setShuffledOptionsMap(nextShuffledMap);
  }, [module, shuffleSeed]);

  useEffect(() => {
    if (!module) {
      return;
    }
    if (module.quiz_passed) {
      prevCooldownActiveRef.current = false;
      startQuizCooldown(0);
      return;
    }

    const serverRemaining = Math.max(
      0,
      Math.ceil(module.quiz_cooldown_remaining_seconds ?? 0)
    );
    if (serverRemaining > 0) {
      const currentDeadline = cooldownDeadlineRef.current;
      const currentRemaining =
        currentDeadline === null
          ? 0
          : Math.max(0, Math.ceil((currentDeadline - Date.now()) / 1000));
      if (
        currentRemaining <= 0 ||
        Math.abs(currentRemaining - serverRemaining) > 2
      ) {
        startQuizCooldown(serverRemaining);
      }
    }
  }, [module, startQuizCooldown]);

  const isQuizOnCooldown = cooldownSeconds > 0;

  useEffect(() => {
    if (!isQuizOnCooldown) {
      if (prevCooldownActiveRef.current) {
        setSelectedAnswers({});
        setQuizError(null);
        setShuffleSeed((prev) => prev + 1);
      }
      prevCooldownActiveRef.current = false;
      return;
    }

    prevCooldownActiveRef.current = true;
    const intervalId = window.setInterval(() => {
      const deadline = cooldownDeadlineRef.current;
      if (deadline === null) {
        setCooldownSeconds(0);
        return;
      }
      const nextRemaining = Math.max(
        0,
        Math.ceil((deadline - Date.now()) / 1000)
      );
      setCooldownSeconds(nextRemaining);
    }, 500);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [isQuizOnCooldown]);

  useEffect(() => {
    return () => {
      if (copyResetTimerRef.current !== null) {
        window.clearTimeout(copyResetTimerRef.current);
      }
    };
  }, []);

  const handleCopyRawText = (text: string): void => {
    const triggerConfirmation = (): void => {
      setCopiedRawText(true);
      if (copyResetTimerRef.current !== null) {
        window.clearTimeout(copyResetTimerRef.current);
      }
      copyResetTimerRef.current = window.setTimeout(() => {
        setCopiedRawText(false);
        copyResetTimerRef.current = null;
      }, 2500);
    };

    if (
      typeof navigator !== "undefined" &&
      navigator.clipboard !== undefined &&
      typeof navigator.clipboard.writeText === "function"
    ) {
      void navigator.clipboard
        .writeText(text)
        .then(() => {
          triggerConfirmation();
        })
        .catch(() => {
          const fallbackTextarea = document.createElement("textarea");
          fallbackTextarea.value = text;
          fallbackTextarea.setAttribute("readonly", "true");
          fallbackTextarea.style.position = "fixed";
          fallbackTextarea.style.opacity = "0";
          document.body.appendChild(fallbackTextarea);
          fallbackTextarea.select();
          document.execCommand("copy");
          document.body.removeChild(fallbackTextarea);
          triggerConfirmation();
        });
      return;
    }

    const fallbackTextarea = document.createElement("textarea");
    fallbackTextarea.value = text;
    fallbackTextarea.setAttribute("readonly", "true");
    fallbackTextarea.style.position = "fixed";
    fallbackTextarea.style.opacity = "0";
    document.body.appendChild(fallbackTextarea);
    fallbackTextarea.select();
    document.execCommand("copy");
    document.body.removeChild(fallbackTextarea);
    triggerConfirmation();
  };

  const invalidateSubmissionRelatedQueries = async (): Promise<void> => {
    await Promise.all([
      queryClient.invalidateQueries({
        queryKey: ["module", resolvedModuleId],
      }),
      queryClient.invalidateQueries({
        queryKey: ["courses"],
      }),
      queryClient.invalidateQueries({
        queryKey: ["practical-student"],
      }),
      queryClient.invalidateQueries({
        queryKey: ["submissions-my"],
      }),
    ]);
  };

  const submitQuizMutation = useMutation<
    QuizSubmitResponse,
    unknown,
    QuizSubmitRequest
  >({
    mutationFn: (payload) => submitQuizAnswers(resolvedModuleId, payload),
    onSuccess: async (result) => {
      setLastQuizResult(result);
      setQuizError(null);
      if (result.passed) {
        prevCooldownActiveRef.current = false;
        startQuizCooldown(0);
      } else if (result.retry_after_seconds > 0) {
        startQuizCooldown(result.retry_after_seconds);
      } else {
        setSelectedAnswers({});
        setShuffleSeed((prev) => prev + 1);
      }
      await invalidateSubmissionRelatedQueries();
    },
    onError: (err) => {
      const retryAfter = extractRetryAfterSeconds(err);
      if (retryAfter !== null) {
        startQuizCooldown(retryAfter);
      }
      setQuizError(
        extractApiErrorMessage(
          err,
          "Не вдалося надіслати відповіді тесту-допуску. Перевірте з'єднання."
        )
      );
    },
  });

  const submitHtmlMutation = useMutation<
    SubmissionRead,
    unknown,
    HtmlSubmissionRequest
  >({
    mutationFn: (payload) => submitHtmlPractical(practicalId ?? "", payload),
    onSuccess: async (result) => {
      setLastSubmissionResult(result);
      setSubmissionError(null);
      await invalidateSubmissionRelatedQueries();
    },
    onError: (err) => {
      setSubmissionError(
        extractApiErrorMessage(
          err,
          "Не вдалося виконати перевірку HTML-коду. Спробуйте ще раз."
        )
      );
    },
  });

  const submitFileMutation = useMutation<SubmissionRead, unknown, File>({
    mutationFn: (file) => submitFilePractical(practicalId ?? "", file),
    onSuccess: async (result) => {
      setLastSubmissionResult(result);
      setSubmissionError(null);
      await invalidateSubmissionRelatedQueries();
    },
    onError: (err) => {
      setSubmissionError(
        extractApiErrorMessage(
          err,
          "Помилка завантаження або автоперевірки файлу практичної роботи."
        )
      );
    },
  });

  const dryRunHtmlMutation = useMutation<
    DryRunGradingResponse,
    unknown,
    HtmlDryRunRequest
  >({
    mutationFn: (payload) => dryRunHtmlPractical(practicalId ?? "", payload),
    onSuccess: (result) => {
      setLastDryRunResult(result);
      setSubmissionError(null);
    },
    onError: (err) => {
      setLastDryRunResult(null);
      setSubmissionError(
        extractApiErrorMessage(
          err,
          "Не вдалося виконати тестову перевірку HTML-коду (Dry-Run)."
        )
      );
    },
  });

  const dryRunFileMutation = useMutation<
    DryRunGradingResponse,
    unknown,
    { file: File; variantNumber: number }
  >({
    mutationFn: ({ file, variantNumber }) =>
      dryRunFilePractical(practicalId ?? "", file, variantNumber),
    onSuccess: (result) => {
      setLastDryRunResult(result);
      setSubmissionError(null);
    },
    onError: (err) => {
      setLastDryRunResult(null);
      setSubmissionError(
        extractApiErrorMessage(
          err,
          "Помилка тестової перевірки файлу практичної роботи (Dry-Run)."
        )
      );
    },
  });

  const isSubmittingPractical =
    submitHtmlMutation.isPending ||
    submitFileMutation.isPending ||
    dryRunHtmlMutation.isPending ||
    dryRunFileMutation.isPending;

  const totalQuestions = module?.quiz_questions.length ?? 0;
  const answeredCount = useMemo(() => {
    if (!module) {
      return 0;
    }
    return module.quiz_questions.filter(
      (q) => selectedAnswers[q.id] !== undefined
    ).length;
  }, [module, selectedAnswers]);

  const allQuestionsAnswered =
    totalQuestions > 0 && answeredCount === totalQuestions;

  const handleSelectOption = (
    questionId: string,
    optionIndex: number
  ): void => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: optionIndex,
    }));
    if (quizError !== null) {
      setQuizError(null);
    }
  };

  const handleResetQuizSelection = (): void => {
    setSelectedAnswers({});
    setLastQuizResult(null);
    setQuizError(null);
    setShuffleSeed((prev) => prev + 1);
  };

  const handleQuizSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (!module || previewMode) {
      return;
    }

    if (isQuizOnCooldown) {
      setQuizError(
        `Повторна спроба буде доступна через ${formatCountdownMmSs(cooldownSeconds)}. Перечитайте конспект лекції.`
      );
      return;
    }

    if (!allQuestionsAnswered) {
      setQuizError(
        `Будь ласка, дайте відповідь на всі питання тесту (${answeredCount} з ${totalQuestions}).`
      );
      return;
    }

    const answers: QuizAnswerItem[] = module.quiz_questions.map((question) => ({
      question_id: question.id,
      selected_option_index: selectedAnswers[question.id] ?? 0,
    }));

    submitQuizMutation.mutate({ answers });
  };

  const validateAndSelectFile = (
    candidate: File,
    expectedFormat: BinaryPracticalFormat
  ): void => {
    const formatMeta = FILE_UPLOAD_FORMAT_META[expectedFormat];
    const lowerName = candidate.name.toLowerCase();

    if (!lowerName.endsWith(formatMeta.extension)) {
      setSelectedFile(null);
      setSubmissionError(
        `Невірний формат файлу "${candidate.name}". Для цієї практичної роботи очікується файл із розширенням ${formatMeta.extension}.`
      );
      return;
    }

    if (candidate.size === 0) {
      setSelectedFile(null);
      setSubmissionError(
        `Обраний файл "${candidate.name}" порожній (0 байтів). Оберіть збережений документ.`
      );
      return;
    }

    setSelectedFile(candidate);
    setSubmissionError(null);
  };

  const handleFileInputChange = (
    event: ChangeEvent<HTMLInputElement>,
    expectedFormat: BinaryPracticalFormat
  ): void => {
    const pickedFile = event.target.files?.[0];
    if (!pickedFile) {
      return;
    }
    validateAndSelectFile(pickedFile, expectedFormat);
  };

  const handleDragOver = (event: DragEvent<HTMLDivElement>): void => {
    event.preventDefault();
    event.stopPropagation();
    if (!isDragActive) {
      setIsDragActive(true);
    }
  };

  const handleDragLeave = (event: DragEvent<HTMLDivElement>): void => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragActive(false);
  };

  const handleDrop = (
    event: DragEvent<HTMLDivElement>,
    expectedFormat: BinaryPracticalFormat
  ): void => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragActive(false);

    const droppedFile = event.dataTransfer.files?.[0];
    if (!droppedFile) {
      return;
    }
    validateAndSelectFile(droppedFile, expectedFormat);
  };

  const handleRemoveSelectedFile = (): void => {
    setSelectedFile(null);
    setSubmissionError(null);
    if (fileInputRef.current !== null) {
      fileInputRef.current.value = "";
    }
  };

  const handleDownloadPracticalTemplate = async (
    targetPracticalId: string,
    fallbackName: string | null
  ): Promise<void> => {
    setIsDownloadingTemplate(true);
    setTemplateDownloadError(null);
    try {
      const response = await apiClient.get<Blob>(
        `/practicals/${targetPracticalId}/template`,
        {
          responseType: "blob",
        }
      );
      const filename = parseFilenameFromContentDisposition(
        response.headers["content-disposition"],
        fallbackName ?? "template.bin"
      );

      const blobUrl = window.URL.createObjectURL(response.data);
      const anchor = document.createElement("a");
      anchor.href = blobUrl;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (err: unknown) {
      const errorMessage = await extractBlobApiErrorMessage(
        err,
        "Не вдалося завантажити файл-заготовку практичної роботи."
      );
      setTemplateDownloadError(errorMessage);
    } finally {
      setIsDownloadingTemplate(false);
    }
  };

  const handleFileFormSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (practicalId === null) {
      return;
    }
    if (selectedFile === null) {
      setSubmissionError(
        "Будь ласка, оберіть або перетягніть виконаний файл практичної роботи перед відправкою."
      );
      return;
    }
    setSubmissionError(null);
    if (previewMode) {
      dryRunFileMutation.mutate({
        file: selectedFile,
        variantNumber: practicalDetail?.variant_number ?? previewVariant,
      });
      return;
    }
    submitFileMutation.mutate(selectedFile);
  };

  const handleHtmlSandboxSubmit = (rawCode: string): void => {
    if (practicalId === null) {
      return;
    }
    if (rawCode.trim().length === 0) {
      setSubmissionError("HTML-код не може бути порожнім.");
      return;
    }
    setSubmissionError(null);
    if (previewMode) {
      dryRunHtmlMutation.mutate({
        raw_code: rawCode,
        variant_number: practicalDetail?.variant_number ?? previewVariant,
      });
      return;
    }
    submitHtmlMutation.mutate({ raw_code: rawCode });
  };

  const renderBinaryFormatIcon = (
    formatType: BinaryPracticalFormat
  ): ReactElement => {
    switch (formatType) {
      case "docx":
        return <FileText className="h-6 w-6 text-blue-600" />;
      case "xlsx":
        return <FileSpreadsheet className="h-6 w-6 text-emerald-600" />;
      case "accdb":
        return <HardDriveUpload className="h-6 w-6 text-rose-600" />;
    }
  };

  const resolvedCourseId = courseId ?? module?.course_id;
  const teacherEditorReturnTo =
    resolvedCourseId !== undefined
      ? `/teacher/courses?courseId=${resolvedCourseId}&moduleId=${resolvedModuleId}`
      : "/teacher/courses";
  const backLinkTo = previewMode ? teacherEditorReturnTo : "/student/courses";
  const backLinkLabel = previewMode
    ? "Повернутися до редактора курсу"
    : "Назад до переліку навчальних курсів";

  if (isLoading) {
    return (
      <div className="flex min-h-[55vh] flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8">
        <Loader2 className="h-9 w-9 animate-spin text-blue-600" />
        <p className="mt-3 text-sm font-medium text-slate-700">
          Завантаження лекції та тесту-допуску модуля...
        </p>
      </div>
    );
  }

  if (isError || !module) {
    const errorMessage = extractApiErrorMessage(
      error,
      "Не вдалося завантажити навчальний модуль."
    );
    return (
      <div className="mx-auto max-w-2xl rounded-2xl border border-rose-200 bg-white p-6 text-center shadow-xs">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose-600">
          <AlertCircle className="h-6 w-6" />
        </div>
        <h2 className="mt-4 text-lg font-bold text-slate-900">
          Модуль не вдалося відкрити
        </h2>
        <p className="mt-1.5 text-sm text-slate-600">{errorMessage}</p>
        <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
          <Link
            to={backLinkTo}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            <ArrowLeft className="h-4 w-4" />
            {previewMode ? "Повернутися до редактора курсу" : "Повернутися до курсів"}
          </Link>
          <button
            type="button"
            onClick={() => void refetch()}
            className="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
          >
            <RefreshCw className="h-4 w-4" />
            Повторити спробу
          </button>
        </div>
      </div>
    );
  }

  const hasPractical = module.practical !== null;

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      {/* Контрастна панель попереднього перегляду очима студента */}
      {previewMode && (
        <div
          className="rounded-2xl border border-indigo-400/50 bg-slate-900 p-4 text-white shadow-md sm:p-5"
          role="region"
          aria-label="Панель керування режимом попереднього перегляду очима студента"
        >
          <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-500 text-white shadow-xs">
                <Eye className="h-5 w-5" />
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="text-sm font-bold text-white sm:text-base">
                    Режим попереднього перегляду очима студента
                  </h2>
                  <span className="inline-flex items-center gap-1 rounded-full border border-amber-400/40 bg-amber-400/15 px-2.5 py-0.5 text-[11px] font-semibold text-amber-200">
                    <FlaskConical className="h-3 w-3" />
                    Dry-Run / Без запису в журнал
                  </span>
                </div>
                <p className="mt-0.5 text-xs text-slate-300">
                  Перевіряйте відображення лекції, ілюстрацій, тесту-допуску,
                  індивідуальних варіантів, україномовних критеріїв та 12-бальної
                  шкали без створення студентського акаунта.
                </p>
              </div>
            </div>

            <Link
              to={teacherEditorReturnTo}
              className="inline-flex shrink-0 items-center justify-center gap-1.5 rounded-xl border border-slate-600 bg-slate-800 px-3.5 py-2 text-xs font-semibold text-white transition-colors hover:border-slate-500 hover:bg-slate-700"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              <span>Повернутися до редактора курсу</span>
            </Link>
          </div>

          <div className="mt-4 flex flex-col flex-wrap gap-3 border-t border-slate-800 pt-3.5 sm:flex-row sm:items-center sm:justify-between">
            {/* Перемикач варіанта 1..N */}
            {hasPractical && (
              <div className="flex flex-wrap items-center gap-2">
                <label
                  htmlFor="preview-variant-select"
                  className="text-xs font-semibold text-slate-200"
                >
                  Варіант студента:
                </label>
                <select
                  id="preview-variant-select"
                  value={Math.min(previewVariant, totalVariants)}
                  onChange={(event) => {
                    const nextVariant = Number(event.target.value) || 1;
                    setPreviewVariant(nextVariant);
                    setLastDryRunResult(null);
                    setSubmissionError(null);
                  }}
                  className="rounded-xl border border-slate-600 bg-slate-800 px-3 py-1.5 text-xs font-semibold text-white focus:border-indigo-400 focus:outline-none"
                >
                  {Array.from({ length: totalVariants }, (_, idx) => {
                    const num = idx + 1;
                    return (
                      <option key={num} value={num}>
                        Варіант {num} із {totalVariants}
                      </option>
                    );
                  })}
                </select>
              </div>
            )}

            {/* Перемикач симуляції статусу тесту-допуску */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold text-slate-300">
                Симуляція допуску:
              </span>
              <div
                className="inline-flex rounded-xl border border-slate-700 bg-slate-800 p-0.5"
                role="group"
                aria-label="Симуляція статусу тесту-допуску"
              >
                <button
                  type="button"
                  onClick={() => setSimulateQuizPassed(false)}
                  className={`inline-flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-semibold transition-colors ${
                    !simulateQuizPassed
                      ? "bg-amber-500 text-slate-950"
                      : "text-slate-300 hover:text-white"
                  }`}
                >
                  <Lock className="h-3 w-3" />
                  <span>Тест ще не складено (заблоковано)</span>
                </button>
                <button
                  type="button"
                  onClick={() => setSimulateQuizPassed(true)}
                  className={`inline-flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-semibold transition-colors ${
                    simulateQuizPassed
                      ? "bg-emerald-500 text-slate-950"
                      : "text-slate-300 hover:text-white"
                  }`}
                >
                  <Unlock className="h-3 w-3" />
                  <span>Тест складено (доступ відкрито)</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Верхня навігація та статус модуля */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link
            to={backLinkTo}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-800"
          >
            <ArrowLeft className="h-4 w-4" />
            {backLinkLabel}
          </Link>

          <div className="flex flex-wrap items-center gap-2">
            {effectiveQuizPassed ? (
              <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                <CheckCircle2 className="h-3.5 w-3.5" />
                {hasPractical
                  ? "Тест-допуск складено"
                  : "Тест самоперевірки пройдено"}
                {!previewMode && module.best_quiz_score !== null
                  ? ` (${module.best_quiz_score.toFixed(0)}%)`
                  : ""}
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">
                <HelpCircle className="h-3.5 w-3.5" />
                {hasPractical
                  ? "Тест-допуск: потрібен результат ≥ 70%"
                  : "Тест самоперевірки: рекомендовано ≥ 70%"}
                {!previewMode && module.best_quiz_score !== null
                  ? ` (найкращий: ${module.best_quiz_score.toFixed(0)}%)`
                  : ""}
              </span>
            )}

            {hasPractical ? (
              effectivePracticalUnlocked ? (
                <span className="inline-flex items-center gap-1 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                  <Unlock className="h-3.5 w-3.5" />
                  Практична робота відкрита
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                  <Lock className="h-3.5 w-3.5" />
                  Практична заблокована
                </span>
              )
            ) : (
              <span className="inline-flex items-center gap-1 rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">
                <BookOpen className="h-3.5 w-3.5" />
                Теоретичний модуль
              </span>
            )}
          </div>
        </div>

        <div className="mt-4">
          <span className="inline-flex items-center rounded-md bg-slate-100 px-2.5 py-0.5 text-xs font-bold text-slate-700">
            Тема №{module.order_index}
          </span>
          <h1 className="mt-2 text-xl font-bold text-slate-900 sm:text-2xl">
            {module.title}
          </h1>
        </div>

        {/* Перемикач вкладок модуля */}
        <div
          className={`mt-6 grid grid-cols-1 gap-2 border-t border-slate-100 pt-4 ${
            hasPractical ? "sm:grid-cols-3" : "sm:grid-cols-2"
          }`}
          role="tablist"
          aria-label="Етапи навчального модуля"
        >
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === "lecture"}
            onClick={() => setActiveTab("lecture")}
            className={`flex items-center gap-3 rounded-xl border p-3.5 text-left transition-colors ${
              activeTab === "lecture"
                ? "border-blue-600 bg-blue-50/70 text-blue-900"
                : "border-slate-200 bg-slate-50/60 text-slate-700 hover:bg-slate-100"
            }`}
          >
            <div
              className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
                activeTab === "lecture"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-slate-600 border border-slate-200"
              }`}
            >
              <BookOpen className="h-4 w-4" />
            </div>
            <div className="min-w-0">
              <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Крок 1
              </p>
              <p className="truncate text-sm font-semibold">
                Теоретична лекція
              </p>
            </div>
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={activeTab === "quiz"}
            onClick={() => setActiveTab("quiz")}
            className={`flex items-center gap-3 rounded-xl border p-3.5 text-left transition-colors ${
              activeTab === "quiz"
                ? "border-blue-600 bg-blue-50/70 text-blue-900"
                : "border-slate-200 bg-slate-50/60 text-slate-700 hover:bg-slate-100"
            }`}
          >
            <div
              className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
                activeTab === "quiz"
                  ? "bg-blue-600 text-white"
                  : effectiveQuizPassed
                    ? "bg-emerald-100 text-emerald-700"
                    : "bg-white text-slate-600 border border-slate-200"
              }`}
            >
              <ClipboardCheck className="h-4 w-4" />
            </div>
            <div className="min-w-0">
              <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Крок 2 • {totalQuestions} питань
              </p>
              <p className="truncate text-sm font-semibold">
                {hasPractical ? "Тест-допуск (≥ 70%)" : "Тест самоперевірки"}
              </p>
            </div>
          </button>

          {hasPractical && (
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "practical"}
              onClick={() => setActiveTab("practical")}
              className={`flex items-center gap-3 rounded-xl border p-3.5 text-left transition-colors ${
                activeTab === "practical"
                  ? "border-blue-600 bg-blue-50/70 text-blue-900"
                  : "border-slate-200 bg-slate-50/60 text-slate-700 hover:bg-slate-100"
              }`}
            >
              <div
                className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
                  activeTab === "practical"
                    ? "bg-blue-600 text-white"
                    : effectivePracticalUnlocked
                      ? "bg-indigo-100 text-indigo-700"
                      : "bg-slate-200 text-slate-500"
                }`}
              >
                {effectivePracticalUnlocked ? (
                  <FileCode2 className="h-4 w-4" />
                ) : (
                  <Lock className="h-4 w-4" />
                )}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Крок 3 •{" "}
                  {effectivePracticalUnlocked ? "Розблоковано" : "Заблоковано"}
                </p>
                <p className="truncate text-sm font-semibold">
                  Практична робота
                </p>
              </div>
            </button>
          )}
        </div>
      </div>

      {/* Вкладка 1: Теоретична лекція */}
      {activeTab === "lecture" && (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs sm:p-8">
          <div className="mb-6 flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-4">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-blue-700">
              <BookOpen className="h-4 w-4" />
              <span>Лекційний конспект модуля</span>
            </div>
            <span className="text-xs text-slate-500">
              {hasPractical
                ? "Ознайомтеся з матеріалом перед складанням тесту-допуску"
                : "Ознайомтеся з теоретичним матеріалом та перевірте знання у тесті самоперевірки"}
            </span>
          </div>

          <MarkdownRenderer
            content={module.lecture_content}
            emptyFallback="Текст лекції для цього модуля ще не додано."
          />

          <div className="mt-8 flex flex-col items-start justify-between gap-4 rounded-xl border border-blue-200 bg-blue-50/60 p-5 sm:flex-row sm:items-center">
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                Готові перевірити засвоєння теорії?
              </h3>
              <p className="mt-0.5 text-xs text-slate-600">
                {hasPractical
                  ? "Для отримання індивідуального варіанта практичної роботи необхідно набрати щонайменше 70% у тесті-допуску."
                  : "Цей модуль є теоретичним і не передбачає практичної роботи. Пройдіть тест самоперевірки (рекомендовано ≥ 70%), щоб закріпити знання."}
              </p>
            </div>
            <button
              type="button"
              onClick={() => setActiveTab("quiz")}
              className="inline-flex shrink-0 items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white shadow-2xs hover:bg-blue-700"
            >
              <span>
                {hasPractical
                  ? "Перейти до тесту-допуску"
                  : "Перейти до тесту самоперевірки"}
              </span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </section>
      )}

      {/* Вкладка 2: Інтерактивний тест-допуск / тест самоперевірки */}
      {activeTab === "quiz" && (
        <section className="space-y-6">
          {/* Картка результату останньої спроби (якщо щойно надіслано) */}
          {lastQuizResult !== null && (
            <div
              className={`rounded-2xl border p-6 shadow-xs ${
                lastQuizResult.passed
                  ? "border-emerald-300 bg-emerald-50/80"
                  : "border-rose-300 bg-rose-50/80"
              }`}
              role="status"
            >
              <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                <div className="flex items-start gap-3.5">
                  {lastQuizResult.passed ? (
                    <CheckCircle2 className="mt-0.5 h-7 w-7 shrink-0 text-emerald-600" />
                  ) : (
                    <XCircle className="mt-0.5 h-7 w-7 shrink-0 text-rose-600" />
                  )}
                  <div>
                    <h3
                      className={`text-base font-bold ${
                        lastQuizResult.passed
                          ? "text-emerald-950"
                          : "text-rose-950"
                      }`}
                    >
                      {lastQuizResult.passed
                        ? hasPractical
                          ? "Тест-допуск успішно складено! Практичну роботу розблоковано."
                          : "Тест самоперевірки успішно пройдено!"
                        : hasPractical
                          ? "Прохідний поріг (70%) не досягнуто. Спробуйте ще раз."
                          : "Результат нижче 70%. Рекомендуємо повторити лекцію та спробувати ще раз."}
                    </h3>
                    <p
                      className={`mt-1 text-sm ${
                        lastQuizResult.passed
                          ? "text-emerald-800"
                          : "text-rose-800"
                      }`}
                    >
                      Ваш результат:{" "}
                      <span className="font-bold">
                        {lastQuizResult.score_percent.toFixed(1)}%
                      </span>{" "}
                      ({lastQuizResult.correct_count} правильних відповідей із{" "}
                      {lastQuizResult.total_questions}).
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2.5">
                  {lastQuizResult.passed && hasPractical && (
                    <button
                      type="button"
                      onClick={() => setActiveTab("practical")}
                      className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white shadow-2xs hover:bg-emerald-700"
                    >
                      <span>Відкрити практичну роботу</span>
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  )}
                  {lastQuizResult.passed && !hasPractical && (
                    <Link
                      to="/student/courses"
                      className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white shadow-2xs hover:bg-emerald-700"
                    >
                      <span>Повернутися до курсів</span>
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  )}
                  <button
                    type="button"
                    onClick={handleResetQuizSelection}
                    disabled={isQuizOnCooldown}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {isQuizOnCooldown ? (
                      <>
                        <Clock className="h-3.5 w-3.5 text-amber-600" />
                        <span>
                          Доступно через {formatCountdownMmSs(cooldownSeconds)}
                        </span>
                      </>
                    ) : (
                      <>
                        <RotateCcw className="h-3.5 w-3.5" />
                        <span>Пройти ще раз</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs sm:p-8">
            <div className="flex flex-col justify-between gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-center">
              <div>
                <h2 className="text-lg font-bold text-slate-900">
                  {hasPractical
                    ? "Тест-допуск до практичної роботи"
                    : "Тест самоперевірки за матеріалами лекції"}
                </h2>
                <p className="mt-1 text-xs text-slate-600">
                  {hasPractical ? (
                    <>
                      Оберіть одну правильну відповідь для кожного питання.
                      Прохідний бал для відкриття індивідуального варіанта —{" "}
                      <span className="font-semibold text-slate-900">
                        ≥ 70%
                      </span>
                      .
                    </>
                  ) : (
                    <>
                      Оберіть одну правильну відповідь для кожного питання, щоб
                      перевірити засвоєння теоретичного матеріалу (цільовий
                      рівень —{" "}
                      <span className="font-semibold text-slate-900">
                        ≥ 70%
                      </span>
                      ).
                    </>
                  )}
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <div className="rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs">
                  <span className="text-slate-500">Відповіли: </span>
                  <span className="font-bold text-slate-900">
                    {answeredCount} з {totalQuestions}
                  </span>
                </div>
                {module.best_quiz_score !== null && (
                  <div className="rounded-xl border border-blue-200 bg-blue-50 px-3.5 py-2 text-xs font-semibold text-blue-800">
                    Найкращий бал: {module.best_quiz_score.toFixed(0)}%
                  </div>
                )}
              </div>
            </div>

            {totalQuestions === 0 ? (
              <div className="py-8 text-center">
                <p className="text-sm text-slate-600">
                  {hasPractical
                    ? "Для цього модуля тестові питання не налаштовані. Практична робота доступна одразу."
                    : "Для цього теоретичного модуля тестові питання ще не налаштовані."}
                </p>
              </div>
            ) : (
              <form onSubmit={handleQuizSubmit} className="mt-6 space-y-6">
                {previewMode && (
                  <div
                    className="flex items-start gap-2.5 rounded-xl border border-indigo-200 bg-indigo-50/80 p-3.5 text-xs text-indigo-950"
                    role="status"
                  >
                    <Info className="mt-0.5 h-4 w-4 shrink-0 text-indigo-600" />
                    <div>
                      <p className="font-bold">
                        У режимі перегляду спроби тесту не зберігаються в журнал
                      </p>
                      <p className="mt-0.5 text-indigo-900">
                        Ви можете локально проклікати варіанти відповідей, щоб
                        перевірити формулювання питань, зображення та
                        перемішування варіантів. Для перегляду стану
                        «заблоковано / відкрито» скористайтеся перемикачем
                        симуляції допуску у верхній панелі.
                      </p>
                    </div>
                  </div>
                )}

                {!previewMode && isQuizOnCooldown && (
                  <div
                    className="flex flex-col justify-between gap-3 rounded-xl border border-amber-300 bg-amber-50 p-4 text-xs text-amber-950 sm:flex-row sm:items-center"
                    role="status"
                  >
                    <div className="flex items-start gap-2.5">
                      <Clock className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
                      <div>
                        <p className="font-bold">
                          Тимчасова пауза перед повторною спробою:{" "}
                          <span className="font-mono text-sm text-amber-900">
                            {formatCountdownMmSs(cooldownSeconds)}
                          </span>
                        </p>
                        <p className="mt-0.5 text-amber-800">
                          Повторна спроба буде доступна після завершення
                          таймера. Перечитайте конспект лекції — після
                          розблокування варіанти відповідей перемішаються.
                        </p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => setActiveTab("lecture")}
                      className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-amber-300 bg-white px-3.5 py-2 text-xs font-semibold text-amber-900 hover:bg-amber-100"
                    >
                      <BookOpen className="h-3.5 w-3.5" />
                      <span>Перечитати лекцію</span>
                    </button>
                  </div>
                )}

                {quizError !== null && (
                  <div className="flex items-center gap-2.5 rounded-xl border border-rose-200 bg-rose-50 p-3.5 text-xs font-medium text-rose-800">
                    <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
                    <span>{quizError}</span>
                  </div>
                )}

                <div className="space-y-5">
                  {module.quiz_questions.map((question, qIndex) => {
                    const selectedIdx = selectedAnswers[question.id];
                    const displayedOptions: ShuffledQuizOption[] =
                      shuffledOptionsMap[question.id] ??
                      question.options.map((text, index) => ({
                        text,
                        originalIndex: index,
                      }));

                    return (
                      <fieldset
                        key={question.id}
                        className="rounded-xl border border-slate-200 bg-slate-50/50 p-5"
                      >
                        <legend className="sr-only">
                          Питання {qIndex + 1}
                        </legend>
                        <div className="flex items-start gap-3">
                          <span className="mt-0.5 inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">
                            {qIndex + 1}
                          </span>
                          <div className="min-w-0 flex-1 font-medium text-slate-900">
                            <MarkdownRenderer
                              content={question.question_text}
                              compact
                              className="text-slate-900"
                            />
                          </div>
                        </div>

                        <div className="mt-3.5 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                          {displayedOptions.map((option) => {
                            const isSelected =
                              selectedIdx === option.originalIndex;
                            const inputId = `q-${question.id}-opt-${option.originalIndex}`;

                            return (
                              <label
                                key={inputId}
                                htmlFor={inputId}
                                className={`flex cursor-pointer items-center gap-3 rounded-xl border p-3.5 text-sm transition-colors ${
                                  isSelected
                                    ? "border-blue-600 bg-blue-50/90 font-semibold text-blue-950 shadow-2xs"
                                    : "border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50"
                                }`}
                              >
                                <input
                                  id={inputId}
                                  type="radio"
                                  name={`question-${question.id}`}
                                  checked={isSelected}
                                  onChange={() =>
                                    handleSelectOption(
                                      question.id,
                                      option.originalIndex
                                    )
                                  }
                                  className="h-4 w-4 shrink-0 border-slate-300 text-blue-600 focus:ring-blue-500"
                                />
                                <span className="min-w-0 leading-snug">
                                  {renderInlineMarkdown(option.text, {
                                    disableLinks: true,
                                  })}
                                </span>
                              </label>
                            );
                          })}
                        </div>
                      </fieldset>
                    );
                  })}
                </div>

                <div className="flex flex-col items-stretch justify-between gap-3 border-t border-slate-100 pt-5 sm:flex-row sm:items-center">
                  <div className="flex flex-wrap items-center gap-3">
                    <button
                      type="button"
                      onClick={handleResetQuizSelection}
                      disabled={
                        answeredCount === 0 || submitQuizMutation.isPending
                      }
                      className="inline-flex items-center justify-center gap-1.5 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                    >
                      <RotateCcw className="h-3.5 w-3.5" />
                      Очистити вибір
                    </button>
                    <span className="text-xs font-medium text-slate-600">
                      Відповіли:{" "}
                      <span className="font-bold text-slate-900">
                        {answeredCount} з {totalQuestions}
                      </span>
                    </span>
                  </div>

                  <button
                    type="submit"
                    disabled={
                      previewMode ||
                      !allQuestionsAnswered ||
                      isQuizOnCooldown ||
                      submitQuizMutation.isPending
                    }
                    className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {previewMode ? (
                      <>
                        <Eye className="h-4 w-4" />
                        <span>Відправка тесту вимкнена в режимі перегляду</span>
                      </>
                    ) : submitQuizMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Перевірка відповідей...</span>
                      </>
                    ) : isQuizOnCooldown ? (
                      <>
                        <Clock className="h-4 w-4" />
                        <span>
                          Надіслати тест ({formatCountdownMmSs(cooldownSeconds)}
                          )
                        </span>
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4" />
                        <span>Надіслати тест</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            )}
          </div>
        </section>
      )}

      {/* Вкладка 3: Статус практичної роботи та індивідуальний варіант */}
      {activeTab === "practical" && (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs sm:p-8">
          {module.practical === null ? (
            <div className="mx-auto max-w-lg py-8 text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border border-indigo-200 bg-indigo-50 text-indigo-600">
                <BookOpen className="h-7 w-7" />
              </div>
              <h2 className="mt-4 text-lg font-bold text-slate-900">
                Теоретичний модуль без практичної роботи
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">
                До цього навчального модуля не прикріплено практичну роботу.
                Опрацюйте лекційний матеріал та пройдіть тест самоперевірки.
              </p>
              <button
                type="button"
                onClick={() => setActiveTab("quiz")}
                className="mt-6 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-xs font-semibold text-white shadow-2xs hover:bg-blue-700"
              >
                <ClipboardCheck className="h-4 w-4" />
                <span>Перейти до тесту самоперевірки</span>
              </button>
            </div>
          ) : !effectivePracticalUnlocked ? (
            <div className="mx-auto max-w-lg py-8 text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-amber-50 text-amber-600 border border-amber-200">
                <Lock className="h-7 w-7" />
              </div>
              <h2 className="mt-4 text-lg font-bold text-slate-900">
                Доступ до практичної роботи заблоковано
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">
                Згідно з вимогами навчального практикуму, індивідуальний варіант
                та форма здачі роботи відкриваються автоматично після успішного
                складання тесту-допуску (мінімум{" "}
                <span className="font-semibold text-slate-900">70%</span>{" "}
                правильних відповідей).
              </p>
              <button
                type="button"
                onClick={() => setActiveTab("quiz")}
                className="mt-6 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-xs font-semibold text-white shadow-2xs hover:bg-blue-700"
              >
                <ClipboardCheck className="h-4 w-4" />
                <span>Перейти до складання тесту-допуску</span>
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="flex flex-col justify-between gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-start">
                <div className="space-y-1.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">
                      <Unlock className="h-3.5 w-3.5" />
                      Допуск отримано
                    </span>
                    <span className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-2.5 py-0.5 text-xs font-semibold text-blue-700">
                      {FORMAT_BADGE_LABELS[module.practical.format_type]}
                    </span>
                  </div>
                  <h2 className="text-lg font-bold text-slate-900 sm:text-xl">
                    {module.practical.title}
                  </h2>
                </div>

                <div className="flex flex-wrap items-center gap-2.5">
                  <div className="rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs">
                    <span className="text-slate-500">Макс. бал: </span>
                    <span className="font-bold text-slate-900">
                      {module.practical.max_score.toFixed(1)} б.
                    </span>
                  </div>
                  {module.practical.best_score !== null && (
                    <div className="inline-flex items-center gap-1.5 rounded-xl border border-emerald-200 bg-emerald-50 px-3.5 py-2 text-xs font-bold text-emerald-800">
                      <Award className="h-4 w-4 text-emerald-600" />
                      <span>
                        Ваш найкращий бал:{" "}
                        {module.practical.best_score.toFixed(1)} /{" "}
                        {module.practical.max_score.toFixed(1)}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {isLoadingPractical ? (
                <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-600">
                  <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
                  <span>
                    Завантаження вашого індивідуального варіанта практичної
                    роботи...
                  </span>
                </div>
              ) : isPracticalError ? (
                <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800">
                  {extractApiErrorMessage(
                    practicalError,
                    "Не вдалося завантажити деталі індивідуального варіанта."
                  )}
                </div>
              ) : practicalDetail !== undefined ? (
                <div className="space-y-5">
                  <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-5">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                      Методичні вказівки до виконання
                    </h3>
                    <div className="mt-2.5">
                      <MarkdownRenderer
                        content={practicalDetail.instructions}
                        emptyFallback="Методичні вказівки для цієї практичної роботи ще не додано."
                      />
                    </div>
                  </div>

                  <div className="rounded-xl border border-indigo-200 bg-indigo-50/50 p-5">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span className="inline-flex items-center gap-1.5 rounded-full border border-indigo-200 bg-indigo-100/80 px-3 py-1 text-xs font-bold text-indigo-800">
                        <Sparkles className="h-3.5 w-3.5" />
                        Індивідуальний варіант №{practicalDetail.variant_number}
                      </span>
                      <span className="text-xs text-indigo-700">
                        {previewMode
                          ? `Перегляд варіанта №${practicalDetail.variant_number} із ${practicalDetail.total_variants}`
                          : `Призначено за списком групи (№${user?.list_number ?? 1})`}
                      </span>
                    </div>

                    <h3 className="mt-3 text-base font-bold text-slate-900">
                      {renderInlineMarkdown(practicalDetail.variant.title)}
                    </h3>
                    <div className="mt-2.5">
                      <MarkdownRenderer
                        content={practicalDetail.variant.task_description}
                        compact
                      />
                    </div>

                    <VariantParametersSection
                      parameters={practicalDetail.variant.parameters}
                      copiedRawText={copiedRawText}
                      onCopyRawText={handleCopyRawText}
                    />
                  </div>

                  {/* Картка прозорих україномовних критеріїв автоперевірки */}
                  {(() => {
                    const studentCriteria =
                      practicalDetail.grading_criteria.length > 0
                        ? practicalDetail.grading_criteria
                        : module.practical.grading_criteria;

                    if (studentCriteria.length === 0) {
                      return null;
                    }

                    const autoMaxScore = practicalDetail.auto_max_score;
                    const manualBonusMax = practicalDetail.manual_bonus_max;
                    const maxScoreValue = practicalDetail.max_score;

                    return (
                      <div
                        className="rounded-2xl border border-emerald-200/90 bg-emerald-50/40 p-5 shadow-xs"
                        aria-label="Критерії автоперевірки"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-emerald-200/70 pb-3.5">
                          <div className="flex items-center gap-2.5">
                            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
                              <ListChecks className="h-5 w-5" />
                            </div>
                            <div>
                              <h3 className="text-sm font-bold text-slate-900 sm:text-base">
                                Критерії автоперевірки
                              </h3>
                              <p className="text-xs text-slate-600">
                                Перелік вимог, за якими система автоматично
                                нарахує бали для вашого варіанта
                              </p>
                            </div>
                          </div>

                          <span className="inline-flex items-center rounded-full border border-emerald-300 bg-white px-3 py-1 text-xs font-bold text-emerald-800 shadow-2xs">
                            {manualBonusMax > 0
                              ? `Максимум: ${formatPointsValue(maxScoreValue)} б. (до ${formatPointsValue(autoMaxScore)} б. автоперевірка + до ${formatPointsValue(manualBonusMax)} б. творче завдання)`
                              : `Максимум: ${formatPointsValue(maxScoreValue)} б.`}
                          </span>
                        </div>

                        <ol className="mt-4 space-y-2">
                          {studentCriteria.map((criterion, index) => (
                            <li
                              key={criterion.id}
                              className="flex flex-col justify-between gap-2 rounded-xl border border-emerald-100 bg-white px-3.5 py-2.5 text-xs sm:flex-row sm:items-center sm:text-sm"
                            >
                              <div className="flex items-start gap-2.5">
                                <span className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-[11px] font-bold text-emerald-800">
                                  {index + 1}
                                </span>
                                <span className="leading-relaxed text-slate-800">
                                  {criterion.description}
                                </span>
                              </div>
                              <span className="inline-flex shrink-0 items-center self-start rounded-lg border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 font-mono text-xs font-bold text-emerald-800 sm:self-center">
                                +{formatPointsValue(criterion.weight_points)} б.
                              </span>
                            </li>
                          ))}

                          {manualBonusMax > 0 && (
                            <li className="flex flex-col justify-between gap-2 rounded-xl border border-indigo-200 bg-indigo-50/80 px-3.5 py-2.5 text-xs sm:flex-row sm:items-center sm:text-sm">
                              <div className="flex items-start gap-2.5">
                                <span className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-indigo-700">
                                  <Sparkles className="h-3 w-3" />
                                </span>
                                <span className="font-semibold leading-relaxed text-indigo-950">
                                  Творче завдання / додаткове оформлення
                                  (перевіряє викладач вручну)
                                </span>
                              </div>
                              <span className="inline-flex shrink-0 items-center self-start rounded-lg border border-indigo-200 bg-white px-2.5 py-0.5 font-mono text-xs font-bold text-indigo-800 sm:self-center">
                                +{formatPointsValue(manualBonusMax)} б.
                              </span>
                            </li>
                          )}
                        </ol>

                        {practicalDetail.needs_rules_review && (
                          <div className="mt-3.5 flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50/90 px-3.5 py-2.5 text-xs text-amber-900">
                            <Info className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
                            <span>
                              Візуальне оформлення, формули або творчу частину
                              цієї практичної роботи додатково може оцінити
                              викладач.
                            </span>
                          </div>
                        )}
                      </div>
                    );
                  })()}

                  {practicalDetail.has_template_file && (
                    <div className="rounded-xl border border-blue-200 bg-blue-50/70 p-4 sm:p-5">
                      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
                        <div className="flex items-start gap-3">
                          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-100 text-blue-700">
                            <FileDown className="h-5 w-5" />
                          </div>
                          <div>
                            <h3 className="text-sm font-bold text-slate-900">
                              Файл-заготовка для практичної роботи
                            </h3>
                            <p className="mt-0.5 text-xs text-slate-600">
                              Завантажте вхідний шаблон викладача, виконайте
                              завдання свого варіанта та здайте збережений
                              результат нижче.
                            </p>
                          </div>
                        </div>

                        <button
                          type="button"
                          disabled={isDownloadingTemplate}
                          onClick={() =>
                            void handleDownloadPracticalTemplate(
                              practicalDetail.id,
                              practicalDetail.template_file_name
                            )
                          }
                          className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white shadow-2xs transition-colors hover:bg-blue-700 disabled:opacity-60"
                        >
                          {isDownloadingTemplate ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Download className="h-4 w-4" />
                          )}
                          <span>
                            Завантажити файл-заготовку (
                            {practicalDetail.template_file_name ?? "шаблон"})
                          </span>
                        </button>
                      </div>

                      {templateDownloadError !== null && (
                        <div
                          className="mt-3 flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-medium text-rose-800"
                          role="alert"
                        >
                          <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
                          <span>{templateDownloadError}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Повідомлення про помилку здачі роботи */}
                  {submissionError !== null && (
                    <div
                      className="flex items-start gap-2.5 rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs font-medium text-rose-800"
                      role="alert"
                    >
                      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" />
                      <span>{submissionError}</span>
                    </div>
                  )}

                  {/* Гілка Б (HTML): Вбудована HTML-пісочниця (Monaco Editor + <iframe sandbox>) */}
                  {practicalDetail.format_type === "html" ? (
                    <Suspense
                      fallback={
                        <div className="flex h-[540px] items-center justify-center rounded-2xl border border-slate-200 bg-white text-sm text-slate-600 shadow-xs">
                          <Loader2 className="mr-2 h-4 w-4 animate-spin text-blue-600" />
                          Завантаження локального редактора Monaco Editor...
                        </div>
                      }
                    >
                      <HtmlSandbox
                        practicalId={practicalDetail.id}
                        practicalTitle={practicalDetail.title}
                        variant={practicalDetail.variant}
                        variantNumber={practicalDetail.variant_number}
                        userId={user?.id}
                        isSubmitting={isSubmittingPractical}
                        onSubmitCode={handleHtmlSandboxSubmit}
                        submitButtonLabel={
                          previewMode
                            ? "Перевірити (Dry-Run без запису)"
                            : undefined
                        }
                        submittingLabel={
                          previewMode
                            ? "Тестова перевірка HTML (Dry-Run)..."
                            : undefined
                        }
                      />
                    </Suspense>
                  ) : (
                    /* Гілка А (Word .docx / Excel .xlsx / Access .accdb): Drag-and-drop форма завантаження файлу */
                    (() => {
                      const binaryFormat: BinaryPracticalFormat =
                        practicalDetail.format_type;
                      const formatMeta = FILE_UPLOAD_FORMAT_META[binaryFormat];

                      return (
                        <form
                          onSubmit={handleFileFormSubmit}
                          className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs sm:p-6"
                        >
                          <div className="flex flex-col justify-between gap-3 border-b border-slate-100 pb-4 sm:flex-row sm:items-center">
                            <div className="flex items-center gap-3">
                              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-slate-200 bg-slate-50">
                                {renderBinaryFormatIcon(binaryFormat)}
                              </div>
                              <div>
                                <h3 className="text-base font-bold text-slate-900">
                                  Здача файлу практичної роботи (
                                  {formatMeta.extension})
                                </h3>
                                <p className="text-xs text-slate-600">
                                  {formatMeta.applicationLabel} • Варіант №
                                  {practicalDetail.variant_number}
                                </p>
                              </div>
                            </div>

                            <span className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-700">
                              <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
                              Контроль SHA-256 + core.xml
                            </span>
                          </div>

                          <p className="mt-3 text-xs leading-relaxed text-slate-600">
                            {formatMeta.hintText}
                          </p>

                          <input
                            ref={fileInputRef}
                            id={`file-upload-${practicalDetail.id}`}
                            type="file"
                            accept={formatMeta.acceptAttr}
                            onChange={(event) =>
                              handleFileInputChange(event, binaryFormat)
                            }
                            className="sr-only"
                          />

                          {/* Drag-and-drop зона вибору файлу */}
                          <div
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={(event) => handleDrop(event, binaryFormat)}
                            className={`mt-4 flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-6 text-center transition-colors sm:p-8 ${
                              isDragActive
                                ? "border-blue-500 bg-blue-50/70"
                                : selectedFile !== null
                                  ? "border-emerald-300 bg-emerald-50/40"
                                  : "border-slate-300 bg-slate-50/60 hover:border-blue-400 hover:bg-slate-50"
                            }`}
                          >
                            {selectedFile === null ? (
                              <>
                                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                                  <UploadCloud className="h-6 w-6" />
                                </div>
                                <p className="mt-3 text-sm font-bold text-slate-900">
                                  Перетягніть виконаний файл{" "}
                                  <span className="font-mono text-blue-700">
                                    {formatMeta.extension}
                                  </span>{" "}
                                  сюди
                                </p>
                                <p className="mt-1 text-xs text-slate-500">
                                  або оберіть збережений документ зі свого
                                  комп&apos;ютера для миттєвої автоперевірки
                                </p>
                                <label
                                  htmlFor={`file-upload-${practicalDetail.id}`}
                                  className="mt-4 inline-flex cursor-pointer items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-800 shadow-2xs hover:border-blue-400 hover:bg-blue-50"
                                >
                                  <UploadCloud className="h-4 w-4 text-blue-600" />
                                  <span>
                                    Обрати файл {formatMeta.extension}
                                  </span>
                                </label>
                              </>
                            ) : (
                              <div className="flex w-full max-w-lg flex-col items-center justify-between gap-4 rounded-xl border border-emerald-200 bg-white p-4 text-left shadow-2xs sm:flex-row">
                                <div className="flex min-w-0 items-center gap-3">
                                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-100 text-emerald-700">
                                    <FileCheck2 className="h-5 w-5" />
                                  </div>
                                  <div className="min-w-0">
                                    <p className="truncate text-sm font-bold text-slate-900">
                                      {selectedFile.name}
                                    </p>
                                    <p className="text-xs text-slate-500">
                                      Розмір:{" "}
                                      {formatFileSize(selectedFile.size)} •
                                      Формат: {formatMeta.extension}
                                    </p>
                                  </div>
                                </div>

                                <div className="flex shrink-0 items-center gap-2">
                                  <label
                                    htmlFor={`file-upload-${practicalDetail.id}`}
                                    className="cursor-pointer rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                                  >
                                    Замінити
                                  </label>
                                  <button
                                    type="button"
                                    onClick={handleRemoveSelectedFile}
                                    disabled={isSubmittingPractical}
                                    className="inline-flex items-center gap-1 rounded-lg border border-rose-200 bg-rose-50 px-2.5 py-1.5 text-xs font-semibold text-rose-700 hover:bg-rose-100 disabled:opacity-50"
                                    title="Видалити обраний файл"
                                  >
                                    <Trash2 className="h-3.5 w-3.5" />
                                    <span>Очистити</span>
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>

                          <div className="mt-5 flex flex-col items-stretch justify-between gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-center">
                            <p className="text-xs text-slate-500">
                              {previewMode ? (
                                <>
                                  Режим Dry-Run: перевірка за{" "}
                                  <span className="font-semibold text-slate-700">
                                    варіантом №{practicalDetail.variant_number}
                                  </span>{" "}
                                  без запису в журнал і без збереження файлу на
                                  диск.
                                </>
                              ) : (
                                <>
                                  Перевірка виконується автоматично за{" "}
                                  <span className="font-semibold text-slate-700">
                                    варіантом №{practicalDetail.variant_number}
                                  </span>{" "}
                                  протягом 1–3 секунд.
                                </>
                              )}
                            </p>

                            <button
                              type="submit"
                              disabled={
                                selectedFile === null || isSubmittingPractical
                              }
                              className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-xs font-semibold text-white shadow-xs transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                              {isSubmittingPractical ? (
                                <>
                                  <Loader2 className="h-4 w-4 animate-spin" />
                                  <span>
                                    {previewMode
                                      ? "Тестова перевірка (Dry-Run)..."
                                      : "Автоперевірка файлу..."}
                                  </span>
                                </>
                              ) : previewMode ? (
                                <>
                                  <FlaskConical className="h-4 w-4" />
                                  <span>
                                    Запустити Dry-Run перевірку (без запису)
                                  </span>
                                </>
                              ) : (
                                <>
                                  <Send className="h-4 w-4" />
                                  <span>Надіслати файл на перевірку</span>
                                </>
                              )}
                            </button>
                          </div>
                        </form>
                      );
                    })()
                  )}

                  {/* Результат Dry-Run перевірки у режимі попереднього перегляду */}
                  {previewMode && lastDryRunResult !== null && (
                    <DryRunResultPanel
                      result={lastDryRunResult}
                      rulesEditorLink={`/teacher/rules?practicalId=${practicalDetail.id}`}
                      onClear={() => setLastDryRunResult(null)}
                    />
                  )}

                  {/* Миттєвий звіт результату автоперевірки та контролю авторства */}
                  {!previewMode && lastSubmissionResult !== null && (
                    <div
                      className="rounded-2xl border border-slate-200 bg-slate-50/70 p-5 shadow-xs sm:p-6"
                      role="status"
                    >
                      <div className="flex flex-col justify-between gap-4 border-b border-slate-200 pb-4 sm:flex-row sm:items-center">
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="inline-flex items-center gap-1 rounded-full bg-blue-600 px-3 py-1 text-xs font-bold text-white">
                              <Award className="h-3.5 w-3.5" />
                              Результат автоперевірки:{" "}
                              {lastSubmissionResult.final_score.toFixed(1)} /{" "}
                              {lastSubmissionResult.max_score.toFixed(1)} б.
                            </span>

                            {lastSubmissionResult.is_plagiarism_flagged ? (
                              <span className="inline-flex items-center gap-1 rounded-full border border-rose-300 bg-rose-100 px-3 py-1 text-xs font-bold text-rose-800">
                                <ShieldAlert className="h-3.5 w-3.5" />
                                Підозра на плагіат
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 rounded-full border border-emerald-300 bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-800">
                                <ShieldCheck className="h-3.5 w-3.5" />
                                Авторство підтверджено
                              </span>
                            )}
                          </div>
                          <h3 className="mt-2 text-base font-bold text-slate-900">
                            Звіт перевірки за варіантом №
                            {lastSubmissionResult.variant_number}
                          </h3>
                          <p className="text-xs text-slate-600">
                            Виконано критеріїв:{" "}
                            <span className="font-bold text-emerald-700">
                              {lastSubmissionResult.grading_report.passed_count}
                            </span>{" "}
                            • Провалено:{" "}
                            <span className="font-bold text-rose-700">
                              {lastSubmissionResult.grading_report.failed_count}
                            </span>
                            {lastSubmissionResult.file_hash !== null && (
                              <span className="ml-2 font-mono text-[11px] text-slate-500">
                                • SHA-256:{" "}
                                {lastSubmissionResult.file_hash.slice(0, 12)}…
                              </span>
                            )}
                          </p>
                        </div>

                        <Link
                          to="/student/gradebook"
                          className="inline-flex shrink-0 items-center gap-1.5 rounded-xl border border-blue-200 bg-white px-4 py-2 text-xs font-semibold text-blue-700 shadow-2xs hover:bg-blue-50"
                        >
                          <span>Відкрити у заліковій книжці</span>
                          <ArrowRight className="h-3.5 w-3.5" />
                        </Link>
                      </div>

                      {lastSubmissionResult.manual_bonus_max > 0 &&
                        lastSubmissionResult.auto_max_score > 0 &&
                        lastSubmissionResult.auto_score >=
                          lastSubmissionResult.auto_max_score - 0.005 && (
                          <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-indigo-200 bg-indigo-50/80 p-3.5 text-xs text-indigo-950">
                            <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-indigo-600" />
                            <p className="leading-relaxed">
                              Усі критерії автоперевірки виконано (
                              <span className="font-bold">
                                {formatPointsValue(
                                  lastSubmissionResult.auto_score
                                )}{" "}
                                з{" "}
                                {formatPointsValue(
                                  lastSubmissionResult.max_score
                                )}{" "}
                                б.
                              </span>
                              ). Додаткові бали за творче завдання (до +
                              {formatPointsValue(
                                lastSubmissionResult.manual_bonus_max
                              )}{" "}
                              б.) виставляє викладач після перегляду роботи.
                            </p>
                          </div>
                        )}

                      {lastSubmissionResult.is_plagiarism_flagged &&
                        lastSubmissionResult.plagiarism_reason !== null && (
                          <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-amber-300 bg-amber-50 p-3.5 text-xs text-amber-900">
                            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
                            <div>
                              <p className="font-bold">
                                Спрацював модуль академічної доброчесності:
                              </p>
                              <p className="mt-0.5">
                                {lastSubmissionResult.plagiarism_reason}
                              </p>
                            </div>
                          </div>
                        )}

                      <div className="mt-4 space-y-2.5">
                        {lastSubmissionResult.grading_report.results.map(
                          (criterion) => (
                            <div
                              key={criterion.rule_id}
                              className={`flex flex-col justify-between gap-2 rounded-xl border p-3.5 text-xs sm:flex-row sm:items-center ${
                                criterion.passed
                                  ? "border-emerald-200 bg-white"
                                  : "border-rose-200 bg-rose-50/60"
                              }`}
                            >
                              <div className="flex items-start gap-2.5">
                                {criterion.passed ? (
                                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
                                ) : (
                                  <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" />
                                )}
                                <div>
                                  <p className="font-bold text-slate-900">
                                    {criterion.description}
                                  </p>
                                  <p className="mt-0.5 text-slate-600">
                                    {criterion.feedback}
                                  </p>
                                  <p className="mt-1 font-mono text-[11px] text-slate-500">
                                    Ціль: {criterion.target} • Очікувалось:{" "}
                                    {criterion.expected}
                                    {criterion.actual !== null
                                      ? ` • Фактично: ${criterion.actual}`
                                      : ""}
                                  </p>
                                </div>
                              </div>

                              <span
                                className={`inline-flex shrink-0 items-center self-start rounded-lg px-2.5 py-1 font-mono text-xs font-bold sm:self-center ${
                                  criterion.passed
                                    ? "bg-emerald-100 text-emerald-800"
                                    : "bg-rose-100 text-rose-800"
                                }`}
                              >
                                +{criterion.points_awarded.toFixed(1)} /{" "}
                                {criterion.max_points.toFixed(1)} б.
                              </span>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default ModuleViewPage;
