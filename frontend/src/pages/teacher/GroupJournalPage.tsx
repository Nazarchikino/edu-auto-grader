import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type FormEvent,
  type ReactElement,
} from "react";
import axios from "axios";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  AlertTriangle,
  Award,
  BarChart3,
  CheckCircle2,
  Clock,
  Download,
  Edit3,
  FileDown,
  FileSpreadsheet,
  FileWarning,
  Loader2,
  MessageSquareQuote,
  RefreshCw,
  RotateCcw,
  Save,
  Search,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  TableProperties,
  Users,
  X,
} from "lucide-react";
import apiClient from "../../api/client";
import { GradingReportCard } from "../../components/grading/GradingReportCard";
import { PlagiarismBadge } from "../../components/grading/PlagiarismBadge";
import { extractApiErrorMessage } from "../../context/AuthContext";
import type {
  AcademicGroupRead,
  ExportFormat,
  GroupJournalRead,
  GroupJournalRow,
  ManualGradeUpdateRequest,
  SubmissionRead,
} from "../../types/api";
import type {
  CourseRead,
  CourseSlug,
  PracticalFormat,
} from "../../types/course";

interface PracticalColumnMeta {
  practicalId: string;
  courseId: string;
  courseTitle: string;
  courseSlug: CourseSlug;
  moduleOrderIndex: number;
  moduleTitle: string;
  formatType: PracticalFormat | null;
  maxScore: number;
  needsRulesReview: boolean;
}

function formatCompactPoints(value: number): string {
  const rounded = Math.round(value * 100) / 100;
  return Number.isInteger(rounded)
    ? String(rounded)
    : rounded.toFixed(2).replace(/0$/, "");
}

function getJournalCellScoreClasses(
  score: number,
  maxScore: number
): { scoreTextClass: string; cellAccentClass: string } {
  const ratioPercent = maxScore > 0 ? (score / maxScore) * 100 : 0;
  if (ratioPercent >= 80) {
    return {
      scoreTextClass: "text-emerald-700",
      cellAccentClass:
        "border-emerald-200 bg-emerald-50/40 hover:border-emerald-300 hover:bg-emerald-50/80",
    };
  }
  if (ratioPercent >= 60) {
    return {
      scoreTextClass: "text-blue-700",
      cellAccentClass:
        "border-blue-200 bg-blue-50/30 hover:border-blue-300 hover:bg-blue-50/70",
    };
  }
  if (ratioPercent >= 40) {
    return {
      scoreTextClass: "text-amber-700",
      cellAccentClass:
        "border-amber-200 bg-amber-50/40 hover:border-amber-300 hover:bg-amber-50/80",
    };
  }
  return {
    scoreTextClass: "text-rose-700",
    cellAccentClass:
      "border-rose-200 bg-rose-50/30 hover:border-rose-300 hover:bg-rose-50/70",
  };
}

const COURSE_SLUG_BADGES: Record<
  CourseSlug,
  { shortLabel: string; badgeClass: string }
> = {
  word: {
    shortLabel: "Word",
    badgeClass: "border-blue-200 bg-blue-50 text-blue-700",
  },
  excel: {
    shortLabel: "Excel",
    badgeClass: "border-emerald-200 bg-emerald-50 text-emerald-700",
  },
  access: {
    shortLabel: "Access",
    badgeClass: "border-amber-200 bg-amber-50 text-amber-800",
  },
  html: {
    shortLabel: "HTML5",
    badgeClass: "border-violet-200 bg-violet-50 text-violet-700",
  },
};

async function fetchAcademicGroups(): Promise<AcademicGroupRead[]> {
  const response = await apiClient.get<AcademicGroupRead[]>("/analytics/groups");
  return response.data;
}

async function fetchCourses(): Promise<CourseRead[]> {
  const response = await apiClient.get<CourseRead[]>("/courses");
  return response.data;
}

async function fetchGroupJournal(
  groupId: string,
  courseId: string | null
): Promise<GroupJournalRead> {
  const params: Record<string, string> = {};
  if (courseId !== null && courseId !== "all") {
    params.course_id = courseId;
  }
  const response = await apiClient.get<GroupJournalRead>(
    `/analytics/groups/${groupId}/journal`,
    { params }
  );
  return response.data;
}

async function fetchSubmissionDetail(
  submissionId: string
): Promise<SubmissionRead> {
  const response = await apiClient.get<SubmissionRead>(
    `/submissions/${submissionId}`
  );
  return response.data;
}

function formatShortDate(isoString: string | null): string {
  if (isoString === null) {
    return "—";
  }
  const parsed = new Date(isoString);
  if (Number.isNaN(parsed.getTime())) {
    return isoString;
  }
  return parsed.toLocaleString("uk-UA", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatExpiryDate(isoString: string | null): string | null {
  if (isoString === null) {
    return null;
  }
  const parsed = new Date(isoString);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  const day = String(parsed.getDate()).padStart(2, "0");
  const month = String(parsed.getMonth() + 1).padStart(2, "0");
  const year = parsed.getFullYear();
  return `${day}.${month}.${year}`;
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
        // Тіло помилки не є валідним JSON — використовуємо резервний текст
      }
    }
    if (error.response?.status === 403) {
      return "Недостатньо прав для завантаження цієї роботи студента.";
    }
    if (error.response?.status === 404) {
      return "Файл роботи видалено за терміном зберігання або відсутній на сервері.";
    }
  }
  return extractApiErrorMessage(error, fallbackMessage);
}

export function GroupJournalPage(): ReactElement {
  const queryClient = useQueryClient();

  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
  const [selectedCourseId, setSelectedCourseId] = useState<string>("all");
  const [studentSearch, setStudentSearch] = useState<string>("");
  const [onlyPlagiarismRows, setOnlyPlagiarismRows] = useState<boolean>(false);
  const [selectedSubmissionId, setSelectedSubmissionId] = useState<
    string | null
  >(null);

  // Стан форми ручного коригування бала та коментаря
  const [manualScoreInput, setManualScoreInput] = useState<string>("");
  const [pendingScoreAdjustment, setPendingScoreAdjustment] = useState<
    number | null
  >(null);
  const [teacherCommentInput, setTeacherCommentInput] = useState<string>("");
  const teacherCommentInputRef = useRef<HTMLInputElement | null>(null);
  const [exportingFormat, setExportingFormat] = useState<ExportFormat | null>(
    null
  );
  const [isDownloadingSubmission, setIsDownloadingSubmission] =
    useState<boolean>(false);
  const [submissionDownloadError, setSubmissionDownloadError] = useState<
    string | null
  >(null);
  const [feedbackBanner, setFeedbackBanner] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const {
    data: groups,
    isLoading: isLoadingGroups,
    isError: isGroupsError,
    error: groupsError,
    refetch: refetchGroups,
  } = useQuery<AcademicGroupRead[]>({
    queryKey: ["academic-groups"],
    queryFn: fetchAcademicGroups,
  });

  const { data: courses, isLoading: isLoadingCourses } = useQuery<CourseRead[]>(
    {
      queryKey: ["courses"],
      queryFn: fetchCourses,
    }
  );

  // Автоматичний вибір першої групи
  useEffect(() => {
    const list = groups ?? [];
    if (list.length === 0) {
      setSelectedGroupId(null);
      return;
    }
    const exists = list.some((item) => item.id === selectedGroupId);
    if (!exists) {
      setSelectedGroupId(list[0]?.id ?? null);
    }
  }, [groups, selectedGroupId]);

  const {
    data: journal,
    isLoading: isLoadingJournal,
    isError: isJournalError,
    error: journalError,
    refetch: refetchJournal,
    isFetching: isFetchingJournal,
  } = useQuery<GroupJournalRead>({
    queryKey: ["group-journal", selectedGroupId, selectedCourseId],
    queryFn: () =>
      fetchGroupJournal(
        selectedGroupId ?? "",
        selectedCourseId === "all" ? null : selectedCourseId
      ),
    enabled: selectedGroupId !== null,
  });

  // Завантаження вибраної здачі для детального перегляду та ручного оцінювання
  const {
    data: activeSubmission,
    isLoading: isLoadingSubmissionDetail,
  } = useQuery<SubmissionRead>({
    queryKey: ["submission-detail", selectedSubmissionId],
    queryFn: () => fetchSubmissionDetail(selectedSubmissionId ?? ""),
    enabled: selectedSubmissionId !== null,
  });

  // Синхронізація полів форми ручного коригування оцінки
  useEffect(() => {
    if (activeSubmission === undefined) {
      setManualScoreInput("");
      setPendingScoreAdjustment(null);
      setTeacherCommentInput("");
      return;
    }
    setManualScoreInput(activeSubmission.final_score.toFixed(1));
    setPendingScoreAdjustment(null);
    setTeacherCommentInput(activeSubmission.teacher_comment ?? "");
  }, [activeSubmission]);

  // Скидання локальної помилки завантаження при зміні вибраної здачі
  useEffect(() => {
    setSubmissionDownloadError(null);
  }, [selectedSubmissionId]);

  // Мапа practical_id -> метадані модуля та курсу для заголовків стовпців
  const practicalMetaMap = useMemo<Record<string, PracticalColumnMeta>>(() => {
    const map: Record<string, PracticalColumnMeta> = {};
    for (const course of courses ?? []) {
      for (const mod of course.modules) {
        if (mod.practical_id !== null) {
          map[mod.practical_id] = {
            practicalId: mod.practical_id,
            courseId: course.id,
            courseTitle: course.title,
            courseSlug: course.slug,
            moduleOrderIndex: mod.order_index,
            moduleTitle: mod.title,
            formatType: mod.practical_format,
            maxScore: mod.practical_max_score ?? 12,
            needsRulesReview: mod.practical_needs_rules_review,
          };
        }
      }
    }
    for (const prac of journal?.practicals ?? []) {
      const existing = map[prac.practical_id];
      if (existing !== undefined) {
        map[prac.practical_id] = {
          ...existing,
          maxScore: prac.max_score,
          needsRulesReview: prac.needs_rules_review,
        };
      } else {
        map[prac.practical_id] = {
          practicalId: prac.practical_id,
          courseId: "",
          courseTitle: COURSE_SLUG_BADGES[prac.course_slug].shortLabel,
          courseSlug: prac.course_slug,
          moduleOrderIndex: prac.module_order_index,
          moduleTitle: prac.title,
          formatType: null,
          maxScore: prac.max_score,
          needsRulesReview: prac.needs_rules_review,
        };
      }
    }
    return map;
  }, [courses, journal]);

  // Перелік стовпців практичних робіт із поточного журналу
  const practicalColumnIds = useMemo<string[]>(() => {
    const firstRow = journal?.rows[0];
    if (firstRow !== undefined) {
      return firstRow.cells.map((cell) => cell.practical_id);
    }
    const fallbackIds: string[] = [];
    for (const course of courses ?? []) {
      if (selectedCourseId !== "all" && course.id !== selectedCourseId) {
        continue;
      }
      for (const mod of course.modules) {
        if (mod.practical_id !== null) {
          fallbackIds.push(mod.practical_id);
        }
      }
    }
    return fallbackIds;
  }, [journal, courses, selectedCourseId]);

  // Фільтрація рядків студентів у журналі
  const filteredRows = useMemo<GroupJournalRow[]>(() => {
    const rows = journal?.rows ?? [];
    const query = studentSearch.trim().toLowerCase();

    return rows.filter((row) => {
      if (onlyPlagiarismRows) {
        const hasFlag = row.cells.some((c) => c.is_plagiarism_flagged);
        if (!hasFlag) {
          return false;
        }
      }
      if (query.length > 0) {
        const nameMatch = row.student_full_name.toLowerCase().includes(query);
        const numberMatch = String(row.list_number ?? "").includes(query);
        if (!nameMatch && !numberMatch) {
          return false;
        }
      }
      return true;
    });
  }, [journal, studentSearch, onlyPlagiarismRows]);

  // Зведені KPI журналу групи
  const journalStats = useMemo(() => {
    const rows = journal?.rows ?? [];
    const totalStudents = rows.length;
    let totalCells = 0;
    let submittedCells = 0;
    let flaggedCells = 0;
    let totalGroupPoints = 0;

    for (const row of rows) {
      totalGroupPoints += row.total_score;
      for (const cell of row.cells) {
        totalCells += 1;
        if (cell.submission_id !== null) {
          submittedCells += 1;
        }
        if (cell.is_plagiarism_flagged) {
          flaggedCells += 1;
        }
      }
    }

    const completionPercent =
      totalCells > 0 ? Math.round((submittedCells / totalCells) * 100) : 0;
    const avgStudentScore =
      totalStudents > 0 ? totalGroupPoints / totalStudents : 0;

    return {
      totalStudents,
      totalCells,
      submittedCells,
      completionPercent,
      flaggedCells,
      avgStudentScore,
    };
  }, [journal]);

  // Мутація ручного коригування оцінки та коментаря PATCH /submissions/{id}/grade
  const updateGradeMutation = useMutation<
    SubmissionRead,
    unknown,
    { submissionId: string; payload: ManualGradeUpdateRequest }
  >({
    mutationFn: async ({ submissionId, payload }) => {
      const response = await apiClient.patch<SubmissionRead>(
        `/submissions/${submissionId}/grade`,
        payload
      );
      return response.data;
    },
    onSuccess: (updated) => {
      void queryClient.invalidateQueries({
        queryKey: ["group-journal", selectedGroupId],
      });
      void queryClient.invalidateQueries({
        queryKey: ["submission-detail", updated.id],
      });
      setFeedbackBanner({
        type: "success",
        text: `Оцінку студента «${updated.student_full_name ?? ""}» оновлено до ${updated.final_score.toFixed(1)} б.`,
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(
          err,
          "Не вдалося зберегти скориговану оцінку."
        ),
      });
    },
  });

  const handleApplyCreativeBonus = (bonusPoints: number): void => {
    if (activeSubmission === undefined) {
      return;
    }
    const clampedScore = Math.min(
      activeSubmission.max_score,
      Number((activeSubmission.auto_score + bonusPoints).toFixed(2))
    );
    const effectiveAdjustment = Number(
      (clampedScore - activeSubmission.auto_score).toFixed(2)
    );
    setManualScoreInput(clampedScore.toFixed(1));
    setPendingScoreAdjustment(effectiveAdjustment);
    teacherCommentInputRef.current?.focus();
  };

  const handleSaveManualGrade = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (activeSubmission === undefined) {
      return;
    }
    const parsedScore = Number(manualScoreInput);
    if (
      Number.isNaN(parsedScore) ||
      parsedScore < 0 ||
      parsedScore > activeSubmission.max_score
    ) {
      setFeedbackBanner({
        type: "error",
        text: `Підсумковий бал має бути в межах від 0.0 до ${activeSubmission.max_score.toFixed(1)}.`,
      });
      return;
    }

    const normalizedComment =
      teacherCommentInput.trim().length > 0
        ? teacherCommentInput.trim()
        : null;

    const useRelativeAdjustment =
      pendingScoreAdjustment !== null &&
      Math.abs(
        activeSubmission.auto_score + pendingScoreAdjustment - parsedScore
      ) < 0.01;

    updateGradeMutation.mutate({
      submissionId: activeSubmission.id,
      payload: useRelativeAdjustment
        ? {
            teacher_score_adjustment: pendingScoreAdjustment,
            teacher_comment: normalizedComment,
          }
        : {
            final_score: parsedScore,
            teacher_comment: normalizedComment,
          },
    });
  };

  // Завантаження файлу (.docx/.xlsx/.accdb/.html) обраної здачі студента
  const handleDownloadSubmission = async (
    submission: SubmissionRead
  ): Promise<void> => {
    const formatExt: PracticalFormat = submission.grading_report.format_type;
    setIsDownloadingSubmission(true);
    setSubmissionDownloadError(null);

    try {
      const response = await apiClient.get<Blob>(
        `/submissions/${submission.id}/download`,
        {
          responseType: "blob",
        }
      );

      const fallbackFilename = `submission_${submission.id.slice(0, 8)}.${formatExt}`;
      const filename = parseFilenameFromContentDisposition(
        response.headers["content-disposition"],
        fallbackFilename
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
        "Не вдалося завантажити файл роботи студента."
      );
      setSubmissionDownloadError(errorMessage);
      if (axios.isAxiosError(err) && err.response?.status === 404) {
        void queryClient.invalidateQueries({
          queryKey: ["submission-detail", submission.id],
        });
      }
    } finally {
      setIsDownloadingSubmission(false);
    }
  };

  // Експорт відомості групи у .xlsx або .pdf
  const handleExportStatement = async (format: ExportFormat): Promise<void> => {
    if (selectedGroupId === null) {
      return;
    }
    setExportingFormat(format);
    setFeedbackBanner(null);

    try {
      const params: Record<string, string> = { format };
      if (selectedCourseId !== "all") {
        params.course_id = selectedCourseId;
      }

      const response = await apiClient.get<Blob>(
        `/analytics/groups/${selectedGroupId}/export`,
        {
          params,
          responseType: "blob",
        }
      );

      const groupCode = journal?.group_code ?? "group";
      const safeCode = groupCode.replace(/\s+/g, "_");
      const filename = `vidomist_${safeCode}.${format}`;

      const blobUrl = window.URL.createObjectURL(response.data);
      const anchor = document.createElement("a");
      anchor.href = blobUrl;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(blobUrl);

      setFeedbackBanner({
        type: "success",
        text: `Відомість успішності групи ${groupCode} згенеровано та завантажено у форматі .${format.toUpperCase()}.`,
      });
    } catch (err) {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(
          err,
          `Не вдалося експортувати відомість у форматі .${format}.`
        ),
      });
    } finally {
      setExportingFormat(null);
    }
  };

  if (isLoadingGroups || isLoadingCourses) {
    return (
      <div className="flex min-h-[55vh] flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8">
        <Loader2 className="h-9 w-9 animate-spin text-blue-600" />
        <p className="mt-3 text-sm font-medium text-slate-700">
          Завантаження електронного журналу груп та аналітики...
        </p>
      </div>
    );
  }

  if (isGroupsError) {
    return (
      <div className="mx-auto max-w-2xl rounded-2xl border border-rose-200 bg-white p-6 text-center shadow-xs">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose-600">
          <AlertCircle className="h-6 w-6" />
        </div>
        <h2 className="mt-4 text-lg font-bold text-slate-900">
          Не вдалося завантажити список академічних груп
        </h2>
        <p className="mt-1.5 text-sm text-slate-600">
          {extractApiErrorMessage(
            groupsError,
            "Сталася помилка під час завантаження груп коледжу."
          )}
        </p>
        <button
          type="button"
          onClick={() => void refetchGroups()}
          className="mt-5 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
        >
          <RefreshCw className="h-4 w-4" />
          Спробувати знову
        </button>
      </div>
    );
  }

  const groupList = groups ?? [];
  const courseList = courses ?? [];

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Шапка журналу групи та кнопки експорту відомості (.xlsx / .pdf) */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div className="space-y-1.5">
            <div className="inline-flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
              <TableProperties className="h-3.5 w-3.5" />
              Електронний журнал групи • Антиплагіат • Експорт у kpefk.lcloud.in.ua
            </div>
            <h1 className="text-xl font-bold text-slate-900 sm:text-2xl">
              Зведена відомість успішності та контроль доброчесності
            </h1>
            <p className="max-w-3xl text-sm text-slate-600">
              Переглядайте автоматично виставлені оцінки студентів групи,
              контролюйте збіги SHA-256 та метаданих{" "}
              <code>docProps/core.xml</code>, виконуйте ручне коригування балів
              і завантажуйте відомості у форматах{" "}
              <span className="font-semibold text-slate-800">
                .xlsx та .pdf
              </span>
              .
            </p>
          </div>

          {/* Кнопки експорту .xlsx та .pdf */}
          <div className="flex flex-wrap items-center gap-2.5">
            <button
              type="button"
              disabled={
                selectedGroupId === null || exportingFormat !== null
              }
              onClick={() => void handleExportStatement("xlsx")}
              className="inline-flex items-center gap-2 rounded-xl border border-emerald-300 bg-emerald-50 px-4 py-2.5 text-xs font-bold text-emerald-900 shadow-2xs transition-colors hover:bg-emerald-100 disabled:opacity-60"
            >
              {exportingFormat === "xlsx" ? (
                <Loader2 className="h-4 w-4 animate-spin text-emerald-700" />
              ) : (
                <FileSpreadsheet className="h-4 w-4 text-emerald-700" />
              )}
              <span>Експорт .XLSX</span>
            </button>

            <button
              type="button"
              disabled={
                selectedGroupId === null || exportingFormat !== null
              }
              onClick={() => void handleExportStatement("pdf")}
              className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-xs font-bold text-white shadow-2xs transition-colors hover:bg-slate-800 disabled:opacity-60"
            >
              {exportingFormat === "pdf" ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <FileDown className="h-4 w-4" />
              )}
              <span>Експорт .PDF</span>
            </button>

            <button
              type="button"
              onClick={() => void refetchJournal()}
              disabled={isFetchingJournal}
              className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              title="Оновити дані журналу"
            >
              <RefreshCw
                className={`h-4 w-4 ${isFetchingJournal ? "animate-spin" : ""}`}
              />
              <span>Оновити</span>
            </button>
          </div>
        </div>

        {/* Повідомлення про результат дії */}
        {feedbackBanner !== null && (
          <div
            className={`mt-4 flex items-center justify-between gap-3 rounded-xl border px-4 py-3 text-xs ${
              feedbackBanner.type === "success"
                ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                : "border-rose-200 bg-rose-50 text-rose-900"
            }`}
            role="status"
          >
            <div className="flex items-center gap-2">
              {feedbackBanner.type === "success" ? (
                <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" />
              ) : (
                <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
              )}
              <span className="font-semibold">{feedbackBanner.text}</span>
            </div>
            <button
              type="button"
              onClick={() => setFeedbackBanner(null)}
              className="text-xs font-bold underline"
            >
              Закрити
            </button>
          </div>
        )}

        {/* 4 KPI-картки групи */}
        <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
            <div className="flex items-center justify-between text-xs font-medium text-slate-500">
              <span>Академічна група</span>
              <Users className="h-4 w-4 text-blue-600" />
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              {journal?.group_code ?? "—"}
            </p>
            <p className="mt-1 truncate text-xs text-slate-500">
              Студентів у списку: {journalStats.totalStudents}
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
            <div className="flex items-center justify-between text-xs font-medium text-slate-500">
              <span>Здача практичних робіт</span>
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              {journalStats.submittedCells}{" "}
              <span className="text-sm font-normal text-slate-500">
                / {journalStats.totalCells}
              </span>
            </p>
            <p className="mt-1 text-xs font-medium text-emerald-700">
              Заповненість відомості: {journalStats.completionPercent}%
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
            <div className="flex items-center justify-between text-xs font-medium text-slate-500">
              <span>Середній сумарний бал</span>
              <Award className="h-4 w-4 text-indigo-600" />
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              {journalStats.avgStudentScore.toFixed(1)}{" "}
              <span className="text-sm font-normal text-slate-500">б.</span>
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Середня сума балів на студента
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
            <div className="flex items-center justify-between text-xs font-medium text-slate-500">
              <span>Моніторинг антиплагіату</span>
              {journalStats.flaggedCells > 0 ? (
                <ShieldAlert className="h-4 w-4 text-rose-600" />
              ) : (
                <ShieldCheck className="h-4 w-4 text-emerald-600" />
              )}
            </div>
            <p
              className={`mt-2 text-2xl font-bold ${
                journalStats.flaggedCells > 0
                  ? "text-rose-700"
                  : "text-emerald-700"
              }`}
            >
              {journalStats.flaggedCells}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              {journalStats.flaggedCells > 0
                ? "Здач із підозрою на плагіат"
                : "Збігів SHA-256 / core.xml немає"}
            </p>
          </div>
        </div>
      </section>

      {/* Панель фільтрів журналу */}
      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs sm:p-5">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div className="flex flex-wrap items-center gap-3">
            {/* Вибір групи */}
            <div>
              <label
                htmlFor="group-select"
                className="block text-[11px] font-semibold uppercase tracking-wider text-slate-500"
              >
                Академічна група
              </label>
              <select
                id="group-select"
                value={selectedGroupId ?? ""}
                onChange={(e) => {
                  setSelectedGroupId(e.target.value);
                  setSelectedSubmissionId(null);
                }}
                className="mt-1 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs font-bold text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
              >
                {groupList.map((grp) => (
                  <option key={grp.id} value={grp.id}>
                    {grp.code} — {grp.specialty} ({grp.course_year} курс)
                  </option>
                ))}
              </select>
            </div>

            {/* Фільтр за навчальним курсом */}
            <div>
              <label
                htmlFor="course-filter-select"
                className="block text-[11px] font-semibold uppercase tracking-wider text-slate-500"
              >
                Навчальна дисципліна
              </label>
              <select
                id="course-filter-select"
                value={selectedCourseId}
                onChange={(e) => {
                  setSelectedCourseId(e.target.value);
                  setSelectedSubmissionId(null);
                }}
                className="mt-1 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs font-semibold text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
              >
                <option value="all">Усі дисципліни (Зведена відомість)</option>
                {courseList.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.title}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Пошук студента та прапорець плагіату */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative min-w-[220px]">
              <Search className="pointer-events-none absolute top-1/2 left-3 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
              <input
                type="search"
                value={studentSearch}
                onChange={(e) => setStudentSearch(e.target.value)}
                placeholder="Пошук за ПІБ або № у списку..."
                className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pr-3 pl-8 text-xs text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none"
              />
            </div>

            <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100">
              <input
                type="checkbox"
                checked={onlyPlagiarismRows}
                onChange={(e) => setOnlyPlagiarismRows(e.target.checked)}
                className="h-4 w-4 rounded accent-rose-600"
              />
              <span>Лише підозра на плагіат</span>
            </label>
          </div>
        </div>
      </section>

      {/* Матриця електронного журналу групи */}
      {isLoadingJournal ? (
        <div className="flex min-h-[35vh] flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p className="mt-2.5 text-xs font-medium text-slate-600">
            Формування зведеної відомості успішності групи...
          </p>
        </div>
      ) : isJournalError || journal === undefined ? (
        <div className="rounded-2xl border border-rose-200 bg-white p-6 text-center shadow-xs">
          <p className="text-sm font-semibold text-rose-700">
            {extractApiErrorMessage(
              journalError,
              "Не вдалося завантажити відомість групи."
            )}
          </p>
        </div>
      ) : (
        <>
          <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 bg-slate-50/70 px-5 py-3.5">
              <div>
                <h2 className="text-sm font-bold text-slate-900">
                  Відомість групи {journal.group_code} ({journal.specialty})
                </h2>
                <p className="text-xs text-slate-500">
                  Натисніть на клітинку з оцінкою, щоб відкрити звіт
                  автоперевірки, перевірити антиплагіат або вручну скоригувати
                  бал.
                </p>
              </div>
              <span className="text-xs font-semibold text-slate-500">
                Показано студентів: {filteredRows.length} із{" "}
                {journal.rows.length}
              </span>
            </div>

            <div className="relative isolate max-h-[70vh] overflow-auto">
              <table className="w-full border-separate border-spacing-0 text-left text-xs">
                <thead>
                  <tr className="text-[11px] font-bold uppercase tracking-wider text-slate-600">
                    <th className="sticky top-0 left-0 z-30 min-w-[230px] max-w-[280px] border-b border-r border-slate-200 bg-slate-50 px-4 py-3 text-left shadow-[4px_0_8px_-4px_rgba(0,0,0,0.08)]">
                      № / ПІБ студента
                    </th>
                    {practicalColumnIds.map((pracId, idx) => {
                      const meta = practicalMetaMap[pracId];
                      const slugBadge =
                        meta !== undefined
                          ? COURSE_SLUG_BADGES[meta.courseSlug]
                          : null;

                      return (
                        <th
                          key={pracId}
                          className="sticky top-0 z-20 min-w-[160px] border-b border-r border-slate-200 bg-slate-50 px-3.5 py-3 text-left"
                        >
                          <div className="flex items-center justify-between gap-1">
                            {slugBadge !== null ? (
                              <span
                                className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-bold ${slugBadge.badgeClass}`}
                              >
                                {slugBadge.shortLabel}
                              </span>
                            ) : (
                              <span className="text-[10px] text-slate-500">
                                ПР №{idx + 1}
                              </span>
                            )}
                            <div className="flex items-center gap-1.5">
                              {meta !== undefined && (
                                <span className="font-mono text-[10px] font-semibold normal-case text-slate-500">
                                  /{formatCompactPoints(meta.maxScore)} б.
                                </span>
                              )}
                              {meta?.formatType !== null &&
                                meta?.formatType !== undefined && (
                                  <span className="font-mono text-[10px] lowercase text-slate-400">
                                    .{meta.formatType}
                                  </span>
                                )}
                            </div>
                          </div>
                          <p className="mt-1 line-clamp-1 font-bold normal-case text-slate-800">
                            {meta?.moduleTitle ?? `Практична №${idx + 1}`}
                          </p>
                          {meta?.needsRulesReview && (
                            <span
                              title="Потребує перевірки правил / ручного дооцінювання"
                              className="mt-1 inline-flex items-center gap-1 rounded-full border border-amber-300 bg-amber-50 px-2 py-0.5 text-[10px] font-semibold normal-case text-amber-800"
                            >
                              <AlertTriangle className="h-3 w-3 shrink-0 text-amber-600" />
                              <span>Потребує дооцінювання</span>
                            </span>
                          )}
                        </th>
                      );
                    })}
                    <th className="sticky top-0 z-20 w-36 min-w-[9rem] border-b border-slate-200 bg-slate-50 px-4 py-3 text-center">
                      Антиплагіат
                    </th>
                    <th className="sticky top-0 right-0 z-30 w-28 min-w-[7rem] border-b border-l border-slate-200 bg-slate-50 px-4 py-3 text-center shadow-[-4px_0_8px_-4px_rgba(0,0,0,0.08)]">
                      Сума балів
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {filteredRows.length === 0 ? (
                    <tr>
                      <td
                        colSpan={practicalColumnIds.length + 3}
                        className="bg-white px-6 py-10 text-center text-xs text-slate-500"
                      >
                        Студентів за обраними критеріями пошуку не знайдено.
                      </td>
                    </tr>
                  ) : (
                    filteredRows.map((row) => {
                      const rowFlaggedCell = row.cells.find(
                        (c) => c.is_plagiarism_flagged
                      );
                      const isRowFlagged = rowFlaggedCell !== undefined;
                      const hasAnySubmission = row.cells.some(
                        (c) => c.submission_id !== null
                      );
                      const rowSurfaceClass = isRowFlagged
                        ? "bg-rose-50 group-hover:bg-rose-100"
                        : "bg-white group-hover:bg-slate-50";

                      return (
                        <tr
                          key={row.student_id}
                          className={`group transition-colors ${
                            isRowFlagged
                              ? "bg-rose-50 hover:bg-rose-100"
                              : "bg-white hover:bg-slate-50"
                          }`}
                        >
                          <td
                            className={`sticky left-0 z-10 min-w-[230px] max-w-[280px] border-b border-r border-slate-200 px-4 py-3 align-middle shadow-[4px_0_8px_-4px_rgba(0,0,0,0.08)] transition-colors group-last:border-b-0 ${rowSurfaceClass}`}
                          >
                            <div className="flex items-center gap-3">
                              <span className="inline-flex h-6 min-w-[1.75rem] shrink-0 items-center justify-center rounded-md border border-slate-200 bg-slate-100 px-1.5 font-mono text-[11px] font-bold text-slate-700">
                                {row.list_number ?? "—"}
                              </span>
                              <div className="min-w-0">
                                <p className="font-bold text-slate-900">
                                  {row.student_full_name}
                                </p>
                                <p className="text-[11px] text-slate-400">
                                  Варіант за списком: №{row.list_number ?? 1}
                                </p>
                              </div>
                            </div>
                          </td>

                          {row.cells.map((cell, cellIdx) => {
                            const isLastPracticalCell =
                              cellIdx === row.cells.length - 1;
                            const isSelectedCell =
                              cell.submission_id !== null &&
                              cell.submission_id === selectedSubmissionId;
                            const cellMaxScore =
                              practicalMetaMap[cell.practical_id]?.maxScore ??
                              12;
                            const isManuallyAdjusted =
                              cell.final_score !== null &&
                              cell.auto_score !== null &&
                              Math.abs(cell.final_score - cell.auto_score) >=
                                0.01;
                            const isCreativeBonusAdded =
                              cell.final_score !== null &&
                              cell.auto_score !== null &&
                              cell.final_score - cell.auto_score >= 0.01;
                            const scoreTone =
                              cell.final_score !== null
                                ? getJournalCellScoreClasses(
                                    cell.final_score,
                                    cellMaxScore
                                  )
                                : null;

                            return (
                              <td
                                key={cell.practical_id}
                                className={`border-b border-b-slate-200 border-r px-3 py-2.5 align-middle group-last:border-b-0 ${
                                  isLastPracticalCell
                                    ? "border-r-slate-200"
                                    : "border-r-slate-100"
                                }`}
                              >
                                {cell.submission_id === null ? (
                                  <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50/60 px-3 py-2 text-center text-[11px] text-slate-400">
                                    Не здано
                                  </div>
                                ) : (
                                  <button
                                    type="button"
                                    onClick={() =>
                                      setSelectedSubmissionId(
                                        cell.submission_id
                                      )
                                    }
                                    className={`w-full rounded-xl border p-2.5 text-left transition-all ${
                                      isSelectedCell
                                        ? "border-blue-600 bg-blue-50/70 ring-1 ring-blue-600"
                                        : cell.is_plagiarism_flagged
                                          ? "border-rose-300 bg-rose-50/70 hover:border-rose-400"
                                          : (scoreTone?.cellAccentClass ??
                                            "border-slate-200 bg-white hover:border-blue-300 hover:bg-slate-50")
                                    }`}
                                  >
                                    <div className="flex items-center justify-between gap-1.5">
                                      <span
                                        className={`font-mono text-sm font-extrabold ${
                                          cell.is_plagiarism_flagged
                                            ? "text-rose-800"
                                            : (scoreTone?.scoreTextClass ??
                                              "text-slate-900")
                                        }`}
                                      >
                                        {cell.final_score?.toFixed(1) ?? "0.0"}{" "}
                                        <span className="text-[10px] font-normal text-slate-500">
                                          / {formatCompactPoints(cellMaxScore)}
                                        </span>
                                      </span>
                                      <PlagiarismBadge
                                        isFlagged={cell.is_plagiarism_flagged}
                                        reason={cell.plagiarism_reason}
                                        variant="compact"
                                      />
                                    </div>

                                    <div className="mt-1 flex items-center justify-between text-[10px] text-slate-500">
                                      {isCreativeBonusAdded &&
                                      cell.final_score !== null &&
                                      cell.auto_score !== null ? (
                                        <span className="font-semibold text-indigo-700">
                                          +
                                          {formatCompactPoints(
                                            cell.final_score - cell.auto_score
                                          )}{" "}
                                          творч.
                                        </span>
                                      ) : isManuallyAdjusted ? (
                                        <span className="font-semibold text-amber-700">
                                          Авто: {cell.auto_score?.toFixed(1)}
                                        </span>
                                      ) : (
                                        <span>Автобал</span>
                                      )}
                                      <span>
                                        {formatShortDate(cell.submitted_at)}
                                      </span>
                                    </div>
                                  </button>
                                )}
                              </td>
                            );
                          })}

                          <td className="w-36 min-w-[9rem] border-b border-slate-200 px-4 py-3 text-center align-middle group-last:border-b-0">
                            {rowFlaggedCell !== undefined ? (
                              <PlagiarismBadge
                                isFlagged={true}
                                reason={rowFlaggedCell.plagiarism_reason}
                                variant="pill"
                              />
                            ) : hasAnySubmission ? (
                              <PlagiarismBadge
                                isFlagged={false}
                                variant="pill"
                              />
                            ) : (
                              <span className="text-[11px] text-slate-400">
                                Немає здач
                              </span>
                            )}
                          </td>

                          <td
                            className={`sticky right-0 z-10 w-28 min-w-[7rem] border-b border-l border-slate-200 px-4 py-3 text-center align-middle shadow-[-4px_0_8px_-4px_rgba(0,0,0,0.08)] transition-colors group-last:border-b-0 ${rowSurfaceClass}`}
                          >
                            <span className="inline-flex items-center rounded-xl bg-slate-900 px-3 py-1 font-mono text-xs font-bold text-white">
                              {row.total_score.toFixed(1)}
                            </span>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* Панель інспекції обраної здачі та ручного коригування бала */}
          {selectedSubmissionId !== null && (
            <section
              className="rounded-2xl border-2 border-blue-600 bg-white p-5 shadow-md sm:p-6 space-y-5"
              aria-label="Панель перевірки здачі та ручного коригування оцінки"
            >
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-4">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="inline-flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-2.5 py-0.5 text-xs font-bold text-blue-700">
                      <Edit3 className="h-3.5 w-3.5" />
                      Інспекція роботи та ручне коригування оцінки
                    </span>
                    {activeSubmission !== undefined &&
                      practicalMetaMap[activeSubmission.practical_id]
                        ?.needsRulesReview && (
                        <span
                          title="Стартові правила цієї практичної потребують перевірки викладачем або додаткової ручної оцінки"
                          className="inline-flex items-center gap-1 rounded-full border border-amber-300 bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-amber-800"
                        >
                          <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-amber-600" />
                          <span>
                            Потребує перевірки правил / ручного дооцінювання
                          </span>
                        </span>
                      )}
                  </div>
                  <h3 className="mt-1.5 text-lg font-bold text-slate-900">
                    {activeSubmission?.student_full_name ?? "Студент"} —{" "}
                    {activeSubmission?.practical_title ?? "Практична робота"}
                  </h3>
                </div>

                <button
                  type="button"
                  onClick={() => setSelectedSubmissionId(null)}
                  className="inline-flex items-center gap-1 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100"
                >
                  <X className="h-4 w-4" />
                  <span>Закрити інспектор</span>
                </button>
              </div>

              {isLoadingSubmissionDetail || activeSubmission === undefined ? (
                <div className="flex items-center justify-center py-10">
                  <Loader2 className="h-7 w-7 animate-spin text-blue-600" />
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Блок завантаження файлу зданої роботи та інформації про термін зберігання */}
                  <div className="rounded-2xl border border-slate-200 bg-slate-50/80 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="space-y-1">
                        <p className="text-xs font-bold text-slate-900">
                          Файл зданої роботи (
                          <span className="font-mono lowercase">
                            .{activeSubmission.grading_report.format_type}
                          </span>
                          )
                        </p>
                        {activeSubmission.is_file_available ? (
                          <p className="inline-flex items-center gap-1.5 text-xs text-slate-600">
                            <Clock className="h-3.5 w-3.5 shrink-0 text-slate-400" />
                            <span>
                              {formatExpiryDate(activeSubmission.file_expires_at) !==
                              null
                                ? `Зберігається на сервері до ${formatExpiryDate(activeSubmission.file_expires_at)}`
                                : "Файл доступний для завантаження"}
                            </span>
                          </p>
                        ) : (
                          <div className="inline-flex items-center gap-1.5 rounded-lg border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-800">
                            <FileWarning className="h-3.5 w-3.5 shrink-0 text-amber-600" />
                            <span>
                              Файл роботи видалено за терміном зберігання (90
                              днів) або недоступний
                            </span>
                          </div>
                        )}
                      </div>

                      {activeSubmission.is_file_available && (
                        <button
                          type="button"
                          disabled={isDownloadingSubmission}
                          onClick={() =>
                            void handleDownloadSubmission(activeSubmission)
                          }
                          className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2 text-xs font-bold text-white shadow-2xs transition-colors hover:bg-slate-800 disabled:opacity-60"
                        >
                          {isDownloadingSubmission ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Download className="h-4 w-4" />
                          )}
                          <span>
                            {isDownloadingSubmission
                              ? "Завантаження..."
                              : `Завантажити роботу (.${activeSubmission.grading_report.format_type})`}
                          </span>
                        </button>
                      )}
                    </div>

                    {submissionDownloadError !== null && (
                      <div
                        className="mt-3 flex items-center justify-between gap-3 rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-2.5 text-xs text-rose-900"
                        role="alert"
                      >
                        <div className="flex items-center gap-2">
                          <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
                          <span className="font-semibold">
                            {submissionDownloadError}
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => setSubmissionDownloadError(null)}
                          className="shrink-0 font-bold underline"
                        >
                          Закрити
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Банер антиплагіату PlagiarismBadge */}
                  <PlagiarismBadge
                    isFlagged={activeSubmission.is_plagiarism_flagged}
                    reason={activeSubmission.plagiarism_reason}
                    fileHash={activeSubmission.file_hash}
                    variant="banner"
                  />

                  {/* Форма ручного коригування оцінки та коментаря викладача */}
                  <form
                    onSubmit={handleSaveManualGrade}
                    className="rounded-2xl border border-slate-200 bg-slate-50/80 p-4 sm:p-5 space-y-4"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div className="space-y-1">
                        <h4 className="text-sm font-bold text-slate-900">
                          Ручне коригування бала та рецензія викладача
                        </h4>
                        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-600">
                          <span>
                            Автооцінка:{" "}
                            <span className="font-mono font-bold text-slate-900">
                              {activeSubmission.auto_score.toFixed(1)} /{" "}
                              {activeSubmission.auto_max_score.toFixed(1)} б.
                            </span>
                          </span>
                          <span>
                            Підсумковий бал:{" "}
                            <span className="font-mono font-bold text-blue-700">
                              {activeSubmission.final_score.toFixed(1)} /{" "}
                              {activeSubmission.max_score.toFixed(1)} б.
                            </span>
                          </span>
                          {activeSubmission.manual_bonus_max > 0 && (
                            <span className="inline-flex items-center gap-1 rounded-md border border-indigo-200 bg-indigo-50 px-2 py-0.5 text-[11px] font-semibold text-indigo-800">
                              <Sparkles className="h-3 w-3" />
                              Творче завдання: до +
                              {formatCompactPoints(
                                activeSubmission.manual_bonus_max
                              )}{" "}
                              б.
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center gap-2">
                        {activeSubmission.max_score >
                          activeSubmission.auto_score && (
                          <>
                            <button
                              type="button"
                              onClick={() => handleApplyCreativeBonus(1)}
                              className={`inline-flex items-center gap-1 rounded-lg border px-2.5 py-1 text-xs font-bold transition-colors ${
                                pendingScoreAdjustment !== null &&
                                Math.abs(
                                  activeSubmission.auto_score +
                                    pendingScoreAdjustment -
                                    Math.min(
                                      activeSubmission.max_score,
                                      activeSubmission.auto_score + 1
                                    )
                                ) < 0.01
                                  ? "border-indigo-500 bg-indigo-600 text-white"
                                  : "border-indigo-300 bg-indigo-50 text-indigo-800 hover:bg-indigo-100"
                              }`}
                              title="Додати +1 б. за творче завдання (не вище максимального бала)"
                            >
                              <Sparkles className="h-3 w-3" />
                              <span>+1 б. за творче</span>
                            </button>

                            <button
                              type="button"
                              onClick={() => handleApplyCreativeBonus(2)}
                              className={`inline-flex items-center gap-1 rounded-lg border px-2.5 py-1 text-xs font-bold transition-colors ${
                                pendingScoreAdjustment !== null &&
                                Math.abs(
                                  activeSubmission.auto_score +
                                    pendingScoreAdjustment -
                                    Math.min(
                                      activeSubmission.max_score,
                                      activeSubmission.auto_score + 2
                                    )
                                ) < 0.01
                                  ? "border-indigo-500 bg-indigo-600 text-white"
                                  : "border-indigo-300 bg-indigo-50 text-indigo-800 hover:bg-indigo-100"
                              }`}
                              title="Додати +2 б. за творче завдання (не вище максимального бала)"
                            >
                              <Sparkles className="h-3 w-3" />
                              <span>+2 б. за творче</span>
                            </button>
                          </>
                        )}

                        <button
                          type="button"
                          onClick={() => {
                            setManualScoreInput(
                              activeSubmission.auto_score.toFixed(1)
                            );
                            setPendingScoreAdjustment(0);
                          }}
                          className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                        >
                          <RotateCcw className="h-3 w-3" />
                          <span>Повернути автобал</span>
                        </button>

                        {activeSubmission.is_plagiarism_flagged && (
                          <button
                            type="button"
                            onClick={() => {
                              setManualScoreInput("0.0");
                              setPendingScoreAdjustment(null);
                              if (teacherCommentInput.trim().length === 0) {
                                setTeacherCommentInput(
                                  "Роботу анульовано (0 балів) через виявлений збіг SHA-256 / метаданих docProps/core.xml."
                                );
                              }
                            }}
                            className="inline-flex items-center gap-1 rounded-lg border border-rose-300 bg-rose-50 px-2.5 py-1 text-xs font-bold text-rose-800 hover:bg-rose-100"
                          >
                            <ShieldAlert className="h-3 w-3" />
                            <span>Анулювати (0.0 б. за плагіат)</span>
                          </button>
                        )}
                      </div>
                    </div>

                    {pendingScoreAdjustment !== null &&
                      pendingScoreAdjustment > 0 && (
                        <div className="flex items-center gap-2 rounded-xl border border-indigo-200 bg-indigo-50/70 px-3 py-2 text-xs text-indigo-900">
                          <Sparkles className="h-3.5 w-3.5 shrink-0 text-indigo-600" />
                          <span>
                            Підставлено коригування{" "}
                            <strong className="font-mono">
                              +{formatCompactPoints(pendingScoreAdjustment)} б.
                            </strong>{" "}
                            до автооцінки (підсумковий бал:{" "}
                            <strong className="font-mono">
                              {manualScoreInput} /{" "}
                              {activeSubmission.max_score.toFixed(1)} б.
                            </strong>
                            ). Додайте коментар і натисніть «Зберегти
                            скориговану оцінку».
                          </span>
                        </div>
                      )}

                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
                      <div>
                        <label
                          htmlFor="manual-score-input"
                          className="block text-xs font-semibold text-slate-700"
                        >
                          Підсумковий бал (макс.{" "}
                          {activeSubmission.max_score.toFixed(1)})
                        </label>
                        <input
                          id="manual-score-input"
                          type="number"
                          step="0.5"
                          min={0}
                          max={activeSubmission.max_score}
                          required
                          value={manualScoreInput}
                          onChange={(e) => {
                            setManualScoreInput(e.target.value);
                            setPendingScoreAdjustment(null);
                          }}
                          className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 font-mono text-sm font-bold text-slate-900 focus:border-blue-500 focus:outline-none"
                        />
                      </div>

                      <div className="sm:col-span-3">
                        <label
                          htmlFor="teacher-comment-input"
                          className="block text-xs font-semibold text-slate-700"
                        >
                          <span className="inline-flex items-center gap-1">
                            <MessageSquareQuote className="h-3.5 w-3.5 text-blue-600" />
                            <span>
                              Коментар викладача (відображається у заліковці
                              студента)
                            </span>
                          </span>
                        </label>
                        <input
                          ref={teacherCommentInputRef}
                          id="teacher-comment-input"
                          type="text"
                          value={teacherCommentInput}
                          onChange={(e) =>
                            setTeacherCommentInput(e.target.value)
                          }
                          placeholder="Напр.: Додано +2 б. за творче оформлення та акуратну структуру..."
                          className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-xs text-slate-900 focus:border-blue-500 focus:outline-none"
                        />
                      </div>
                    </div>

                    <div className="flex justify-end">
                      <button
                        type="submit"
                        disabled={updateGradeMutation.isPending}
                        className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2 text-xs font-semibold text-white shadow-2xs hover:bg-blue-700 disabled:opacity-60"
                      >
                        <Save className="h-4 w-4" />
                        <span>
                          {updateGradeMutation.isPending
                            ? "Збереження..."
                            : "Зберегти скориговану оцінку"}
                        </span>
                      </button>
                    </div>
                  </form>

                  {/* Повний протокол автоперевірки GradingReportCard */}
                  <GradingReportCard submission={activeSubmission} />
                </div>
              )}
            </section>
          )}

          {/* Аналітика помилок групи по критеріях перевірки (FR-8) */}
          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs sm:p-6">
            <div className="flex flex-col justify-between gap-3 border-b border-slate-100 pb-4 sm:flex-row sm:items-center">
              <div>
                <h2 className="inline-flex items-center gap-2 text-base font-bold text-slate-900">
                  <BarChart3 className="h-5 w-5 text-blue-600" />
                  <span>
                    Аналітика типових помилок студентів групи по критеріях
                  </span>
                </h2>
                <p className="mt-0.5 text-xs text-slate-500">
                  Рейтинг правил автоперевірки з найвищим відсотком невиконання
                  серед усіх здач групи {journal.group_code}.
                </p>
              </div>

              <button
                type="button"
                disabled={exportingFormat !== null}
                onClick={() => void handleExportStatement("xlsx")}
                className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100"
              >
                <Download className="h-3.5 w-3.5 text-blue-600" />
                <span>Вивантажити аналітику в .XLSX</span>
              </button>
            </div>

            {journal.error_stats.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-500">
                Для обраної групи ще немає достатньої кількості здач для
                побудови статистики помилок.
              </div>
            ) : (
              <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
                {journal.error_stats.map((stat) => {
                  const isHighFailure = stat.failure_rate_percent >= 50;

                  return (
                    <div
                      key={stat.rule_id}
                      className="rounded-xl border border-slate-200 bg-slate-50/60 p-4"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0">
                          <span className="inline-block rounded bg-slate-200/80 px-2 py-0.5 font-mono text-[11px] font-bold text-slate-800">
                            {stat.rule_id}
                          </span>
                          <h3 className="mt-1 text-xs font-bold text-slate-900">
                            {stat.description}
                          </h3>
                        </div>
                        <span
                          className={`shrink-0 rounded-full px-2.5 py-0.5 font-mono text-xs font-bold ${
                            isHighFailure
                              ? "bg-rose-100 text-rose-800"
                              : stat.failure_rate_percent > 0
                                ? "bg-amber-100 text-amber-800"
                                : "bg-emerald-100 text-emerald-800"
                          }`}
                        >
                          {stat.failure_rate_percent.toFixed(1)}% помилок
                        </span>
                      </div>

                      <div className="mt-2.5 h-2 w-full overflow-hidden rounded-full bg-slate-200">
                        <div
                          className={`h-full transition-all ${
                            isHighFailure
                              ? "bg-rose-500"
                              : stat.failure_rate_percent > 0
                                ? "bg-amber-500"
                                : "bg-emerald-500"
                          }`}
                          style={{
                            width: `${Math.min(100, stat.failure_rate_percent)}%`,
                          }}
                        />
                      </div>

                      <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500">
                        <span>
                          Провалено спроб:{" "}
                          <strong className="text-slate-700">
                            {stat.failure_count}
                          </strong>
                        </span>
                        <span>
                          Усього перевірок:{" "}
                          <strong className="text-slate-700">
                            {stat.total_attempts}
                          </strong>
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}

export default GroupJournalPage;
