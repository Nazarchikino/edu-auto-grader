import {
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
  Copy,
  Database,
  FileCheck2,
  FileCode2,
  FileSpreadsheet,
  FileText,
  HardDriveUpload,
  HelpCircle,
  KeyRound,
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
import { HtmlSandbox } from "../../components/sandbox/HtmlSandbox";
import { extractApiErrorMessage, useAuth } from "../../context/AuthContext";
import type { HtmlSubmissionRequest, SubmissionRead } from "../../types/api";
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

async function fetchModuleDetail(moduleId: string): Promise<ModuleDetailRead> {
  const response = await apiClient.get<ModuleDetailRead>(
    `/modules/${moduleId}`
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
};

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

export function ModuleViewPage(): ReactElement {
  const { moduleId } = useParams<{ moduleId: string }>();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const copyResetTimerRef = useRef<number | null>(null);

  const [activeTab, setActiveTab] = useState<ModuleSectionTab>("lecture");
  const [selectedAnswers, setSelectedAnswers] = useState<
    Record<string, number>
  >({});
  const [lastQuizResult, setLastQuizResult] =
    useState<QuizSubmitResponse | null>(null);
  const [quizError, setQuizError] = useState<string | null>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragActive, setIsDragActive] = useState<boolean>(false);
  const [submissionError, setSubmissionError] = useState<string | null>(null);
  const [lastSubmissionResult, setLastSubmissionResult] =
    useState<SubmissionRead | null>(null);
  const [copiedRawText, setCopiedRawText] = useState<boolean>(false);

  const resolvedModuleId = moduleId ?? "";

  const {
    data: module,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<ModuleDetailRead>({
    queryKey: ["module", resolvedModuleId],
    queryFn: () => fetchModuleDetail(resolvedModuleId),
    enabled: resolvedModuleId.length > 0,
  });

  const practicalId = module?.practical?.id ?? null;
  const isPracticalUnlocked = module?.practical_unlocked ?? false;

  const {
    data: practicalDetail,
    isLoading: isLoadingPractical,
    isError: isPracticalError,
    error: practicalError,
  } = useQuery<PracticalStudentRead>({
    queryKey: ["practical-student", practicalId],
    queryFn: () => fetchStudentPractical(practicalId ?? ""),
    enabled:
      practicalId !== null &&
      isPracticalUnlocked &&
      user?.role === "student",
  });

  useEffect(() => {
    setSelectedAnswers({});
    setLastQuizResult(null);
    setQuizError(null);
    setSelectedFile(null);
    setIsDragActive(false);
    setSubmissionError(null);
    setLastSubmissionResult(null);
    setCopiedRawText(false);
    setActiveTab("lecture");
  }, [resolvedModuleId]);

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
      await invalidateSubmissionRelatedQueries();
    },
    onError: (err) => {
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

  const isSubmittingPractical =
    submitHtmlMutation.isPending || submitFileMutation.isPending;

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
  };

  const handleQuizSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (!module) {
      return;
    }

    if (!allQuestionsAnswered) {
      setQuizError(
        `Будь ласка, дайте відповідь на всі питання тесту (${answeredCount} із ${totalQuestions}).`
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
            to="/student/courses"
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            <ArrowLeft className="h-4 w-4" />
            Повернутися до курсів
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
      {/* Верхня навігація та статус модуля */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link
            to="/student/courses"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-800"
          >
            <ArrowLeft className="h-4 w-4" />
            Назад до переліку навчальних курсів
          </Link>

          <div className="flex flex-wrap items-center gap-2">
            {module.quiz_passed ? (
              <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                <CheckCircle2 className="h-3.5 w-3.5" />
                {hasPractical
                  ? "Тест-допуск складено"
                  : "Тест самоперевірки пройдено"}
                {module.best_quiz_score !== null
                  ? ` (${module.best_quiz_score.toFixed(0)}%)`
                  : ""}
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">
                <HelpCircle className="h-3.5 w-3.5" />
                {hasPractical
                  ? "Тест-допуск: потрібен результат ≥ 70%"
                  : "Тест самоперевірки: рекомендовано ≥ 70%"}
                {module.best_quiz_score !== null
                  ? ` (найкращий: ${module.best_quiz_score.toFixed(0)}%)`
                  : ""}
              </span>
            )}

            {hasPractical ? (
              module.practical_unlocked ? (
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
                  : module.quiz_passed
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
                    : module.practical_unlocked
                      ? "bg-indigo-100 text-indigo-700"
                      : "bg-slate-200 text-slate-500"
                }`}
              >
                {module.practical_unlocked ? (
                  <FileCode2 className="h-4 w-4" />
                ) : (
                  <Lock className="h-4 w-4" />
                )}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Крок 3 •{" "}
                  {module.practical_unlocked ? "Розблоковано" : "Заблоковано"}
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
                    className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                  >
                    <RotateCcw className="h-3.5 w-3.5" />
                    Пройти ще раз
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

              <div className="flex items-center gap-3">
                <div className="rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs">
                  <span className="text-slate-500">Обрано відповідей: </span>
                  <span className="font-bold text-slate-900">
                    {answeredCount} / {totalQuestions}
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
                {quizError !== null && (
                  <div className="flex items-center gap-2.5 rounded-xl border border-rose-200 bg-rose-50 p-3.5 text-xs font-medium text-rose-800">
                    <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
                    <span>{quizError}</span>
                  </div>
                )}

                <div className="space-y-5">
                  {module.quiz_questions.map((question, qIndex) => {
                    const selectedIdx = selectedAnswers[question.id];

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
                          {question.options.map((optionText, optIndex) => {
                            const isSelected = selectedIdx === optIndex;
                            const inputId = `q-${question.id}-opt-${optIndex}`;

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
                                    handleSelectOption(question.id, optIndex)
                                  }
                                  className="h-4 w-4 shrink-0 border-slate-300 text-blue-600 focus:ring-blue-500"
                                />
                                <span className="min-w-0 leading-snug">
                                  {renderInlineMarkdown(optionText)}
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

                  <button
                    type="submit"
                    disabled={
                      !allQuestionsAnswered || submitQuizMutation.isPending
                    }
                    className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {submitQuizMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Перевірка відповідей...</span>
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4" />
                        <span>
                          {hasPractical
                            ? "Завершити тест та перевірити допуск"
                            : "Завершити тест самоперевірки"}
                        </span>
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
          ) : !module.practical_unlocked ? (
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
                        Призначено за списком групи (№{user?.list_number ?? 1})
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
                    <HtmlSandbox
                      practicalId={practicalDetail.id}
                      practicalTitle={practicalDetail.title}
                      variant={practicalDetail.variant}
                      variantNumber={practicalDetail.variant_number}
                      userId={user?.id}
                      isSubmitting={isSubmittingPractical}
                      onSubmitCode={handleHtmlSandboxSubmit}
                    />
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
                              Перевірка виконується автоматично за{" "}
                              <span className="font-semibold text-slate-700">
                                варіантом №{practicalDetail.variant_number}
                              </span>{" "}
                              протягом 1–3 секунд.
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
                                  <span>Автоперевірка файлу...</span>
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

                  {/* Миттєвий звіт результату автоперевірки та контролю авторства */}
                  {lastSubmissionResult !== null && (
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
