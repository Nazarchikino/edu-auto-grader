import {
  useEffect,
  useMemo,
  useState,
  type ComponentType,
  type ReactElement,
} from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  AlertCircle,
  ArrowRight,
  Award,
  BookOpen,
  CheckCircle2,
  ClipboardList,
  Clock,
  Code2,
  Database,
  FileSpreadsheet,
  FileText,
  History,
  Loader2,
  Lock,
  MessageSquareQuote,
  RefreshCw,
  Search,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Unlock,
  XCircle,
} from "lucide-react";
import apiClient from "../../api/client";
import { GradingReportCard } from "../../components/grading/GradingReportCard";
import { extractApiErrorMessage, useAuth } from "../../context/AuthContext";
import type { SubmissionRead } from "../../types/api";
import {
  COURSE_SLUGS,
  type CourseRead,
  type CourseSlug,
} from "../../types/course";

type CourseFilterOption = "all" | CourseSlug;
type SubmissionStatusFilter =
  | "all"
  | "latest_only"
  | "with_errors"
  | "with_comment"
  | "plagiarism_flagged";

interface CourseBadgeMeta {
  label: string;
  shortLabel: string;
  icon: ComponentType<{ className?: string }>;
  pillClass: string;
  iconBgClass: string;
}

const COURSE_BADGE_META: Record<CourseSlug, CourseBadgeMeta> = {
  word: {
    label: "Microsoft Word",
    shortLabel: "Word (.docx)",
    icon: FileText,
    pillClass: "border-blue-200 bg-blue-50 text-blue-700",
    iconBgClass: "bg-blue-50 text-blue-600 border-blue-200",
  },
  excel: {
    label: "Microsoft Excel",
    shortLabel: "Excel (.xlsx)",
    icon: FileSpreadsheet,
    pillClass: "border-emerald-200 bg-emerald-50 text-emerald-700",
    iconBgClass: "bg-emerald-50 text-emerald-600 border-emerald-200",
  },
  access: {
    label: "Microsoft Access",
    shortLabel: "Access (.accdb)",
    icon: Database,
    pillClass: "border-amber-200 bg-amber-50 text-amber-800",
    iconBgClass: "bg-amber-50 text-amber-600 border-amber-200",
  },
  html: {
    label: "HTML5 & DOM",
    shortLabel: "HTML5",
    icon: Code2,
    pillClass: "border-violet-200 bg-violet-50 text-violet-700",
    iconBgClass: "bg-violet-50 text-violet-600 border-violet-200",
  },
};

interface PracticalModuleContext {
  practicalId: string;
  moduleId: string;
  moduleTitle: string;
  moduleOrderIndex: number;
  courseId: string;
  courseTitle: string;
  courseSlug: CourseSlug;
}

interface AttemptMeta {
  attemptNumber: number;
  totalAttemptsForPractical: number;
  isLatestAttempt: boolean;
  isBestAttempt: boolean;
}

async function fetchMySubmissions(): Promise<SubmissionRead[]> {
  const response = await apiClient.get<SubmissionRead[]>("/submissions/me");
  return response.data;
}

async function fetchCourses(): Promise<CourseRead[]> {
  const response = await apiClient.get<CourseRead[]>("/courses");
  return response.data;
}

function formatCompactScore(value: number): string {
  const rounded = Math.round(value * 100) / 100;
  return Number.isInteger(rounded)
    ? String(rounded)
    : rounded.toFixed(1);
}

function getScoreBadgeClasses(score: number, maxScore: number): string {
  const ratioPercent = maxScore > 0 ? (score / maxScore) * 100 : 0;
  if (ratioPercent >= 80) {
    return "bg-emerald-600 text-white";
  }
  if (ratioPercent >= 60) {
    return "bg-blue-600 text-white";
  }
  if (ratioPercent >= 40) {
    return "bg-amber-600 text-white";
  }
  return "bg-rose-600 text-white";
}

function getSoftScoreBadgeClasses(score: number, maxScore: number): string {
  const ratioPercent = maxScore > 0 ? (score / maxScore) * 100 : 0;
  if (ratioPercent >= 80) {
    return "bg-emerald-50 text-emerald-800 border border-emerald-200";
  }
  if (ratioPercent >= 60) {
    return "bg-blue-50 text-blue-800 border border-blue-200";
  }
  if (ratioPercent >= 40) {
    return "bg-amber-50 text-amber-800 border border-amber-200";
  }
  return "bg-rose-50 text-rose-800 border border-rose-200";
}

function formatShortDateTime(isoString: string): string {
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

export function GradebookPage(): ReactElement {
  const { user } = useAuth();

  const [selectedCourse, setSelectedCourse] =
    useState<CourseFilterOption>("all");
  const [statusFilter, setStatusFilter] =
    useState<SubmissionStatusFilter>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedSubmissionId, setSelectedSubmissionId] = useState<
    string | null
  >(null);

  const {
    data: submissions,
    isLoading: isLoadingSubmissions,
    isError: isSubmissionsError,
    error: submissionsError,
    refetch: refetchSubmissions,
    isFetching: isFetchingSubmissions,
  } = useQuery<SubmissionRead[]>({
    queryKey: ["submissions-my"],
    queryFn: fetchMySubmissions,
  });

  const {
    data: courses,
    isLoading: isLoadingCourses,
    refetch: refetchCourses,
    isFetching: isFetchingCourses,
  } = useQuery<CourseRead[]>({
    queryKey: ["courses"],
    queryFn: fetchCourses,
  });

  const handleRefreshAll = (): void => {
    void refetchSubmissions();
    void refetchCourses();
  };

  // Мапа practical_id -> інформація про модуль та курс для навігації
  const practicalContextMap = useMemo<
    Record<string, PracticalModuleContext>
  >(() => {
    const map: Record<string, PracticalModuleContext> = {};
    for (const course of courses ?? []) {
      for (const mod of course.modules) {
        if (mod.practical_id !== null) {
          map[mod.practical_id] = {
            practicalId: mod.practical_id,
            moduleId: mod.id,
            moduleTitle: mod.title,
            moduleOrderIndex: mod.order_index,
            courseId: course.id,
            courseTitle: course.title,
            courseSlug: course.slug,
          };
        }
      }
    }
    return map;
  }, [courses]);

  // Обчислення номера спроби, ознаки актуальної та найкращої здачі для кожної практичної роботи
  const attemptMetaMap = useMemo<Record<string, AttemptMeta>>(() => {
    const list = submissions ?? [];
    const groupedByPractical: Record<string, SubmissionRead[]> = {};

    for (const item of list) {
      const group = groupedByPractical[item.practical_id] ?? [];
      group.push(item);
      groupedByPractical[item.practical_id] = group;
    }

    const metaMap: Record<string, AttemptMeta> = {};

    for (const group of Object.values(groupedByPractical)) {
      const chronological = [...group].sort((a, b) => {
        const timeDiff =
          new Date(a.submitted_at).getTime() -
          new Date(b.submitted_at).getTime();
        if (timeDiff !== 0) {
          return timeDiff;
        }
        if (a.submitted_at !== b.submitted_at) {
          return a.submitted_at < b.submitted_at ? -1 : 1;
        }
        return a.id < b.id ? -1 : a.id > b.id ? 1 : 0;
      });
      const totalAttempts = chronological.length;
      const latestId = chronological[totalAttempts - 1]?.id ?? "";

      let bestItem: SubmissionRead | null = null;
      for (const item of chronological) {
        if (bestItem === null || item.final_score >= bestItem.final_score) {
          bestItem = item;
        }
      }
      const bestId = bestItem?.id ?? latestId;

      chronological.forEach((item, index) => {
        metaMap[item.id] = {
          attemptNumber: index + 1,
          totalAttemptsForPractical: totalAttempts,
          isLatestAttempt: item.id === latestId,
          isBestAttempt: item.id === bestId,
        };
      });
    }

    return metaMap;
  }, [submissions]);

  // Зведені показники залікової книжки
  const gradebookStats = useMemo(() => {
    const allSubmissions = submissions ?? [];
    const allCourses = courses ?? [];

    let totalPracticalsInCurriculum = 0;
    for (const course of allCourses) {
      for (const mod of course.modules) {
        if (mod.practical_id !== null) {
          totalPracticalsInCurriculum += 1;
        }
      }
    }

    const bestByPractical: Record<string, SubmissionRead> = {};
    const latestByPractical: Record<string, SubmissionRead> = {};

    for (const sub of allSubmissions) {
      const meta = attemptMetaMap[sub.id];
      if (meta?.isBestAttempt) {
        bestByPractical[sub.practical_id] = sub;
      }
      if (meta?.isLatestAttempt) {
        latestByPractical[sub.practical_id] = sub;
      }
    }

    const bestSubmissions = Object.values(bestByPractical);
    const latestSubmissions = Object.values(latestByPractical);

    const submittedPracticalsCount = bestSubmissions.length;
    const totalEarnedPoints = bestSubmissions.reduce(
      (acc, item) => acc + item.final_score,
      0
    );
    const totalMaxPoints = bestSubmissions.reduce(
      (acc, item) => acc + item.max_score,
      0
    );
    const averageScorePercent =
      totalMaxPoints > 0
        ? Math.round((totalEarnedPoints / totalMaxPoints) * 100)
        : 0;

    const totalPassedCriteria = latestSubmissions.reduce(
      (acc, item) => acc + item.grading_report.passed_count,
      0
    );
    const totalFailedCriteria = latestSubmissions.reduce(
      (acc, item) => acc + item.grading_report.failed_count,
      0
    );

    const flaggedCount = allSubmissions.filter(
      (item) => item.is_plagiarism_flagged
    ).length;
    const cleanCount = allSubmissions.length - flaggedCount;

    return {
      totalAttempts: allSubmissions.length,
      submittedPracticalsCount,
      totalPracticalsInCurriculum,
      totalEarnedPoints,
      totalMaxPoints,
      averageScorePercent,
      totalPassedCriteria,
      totalFailedCriteria,
      flaggedCount,
      cleanCount,
    };
  }, [submissions, courses, attemptMetaMap]);

  // Фільтрація списку здач
  const filteredSubmissions = useMemo<SubmissionRead[]>(() => {
    const list = submissions ?? [];
    const normalizedQuery = searchQuery.trim().toLowerCase();

    return list.filter((item) => {
      const resolvedSlug =
        item.course_slug ??
        practicalContextMap[item.practical_id]?.courseSlug ??
        null;

      if (selectedCourse !== "all" && resolvedSlug !== selectedCourse) {
        return false;
      }

      const attemptMeta = attemptMetaMap[item.id];
      if (statusFilter === "latest_only" && !attemptMeta?.isLatestAttempt) {
        return false;
      }
      if (
        statusFilter === "with_errors" &&
        item.grading_report.failed_count === 0
      ) {
        return false;
      }
      if (
        statusFilter === "with_comment" &&
        (item.teacher_comment === null ||
          item.teacher_comment.trim().length === 0)
      ) {
        return false;
      }
      if (
        statusFilter === "plagiarism_flagged" &&
        !item.is_plagiarism_flagged
      ) {
        return false;
      }

      if (normalizedQuery.length > 0) {
        const titleText = (
          item.practical_title ??
          practicalContextMap[item.practical_id]?.moduleTitle ??
          ""
        ).toLowerCase();
        const commentText = (item.teacher_comment ?? "").toLowerCase();
        const criteriaMatch = item.grading_report.results.some(
          (res) =>
            res.description.toLowerCase().includes(normalizedQuery) ||
            res.feedback.toLowerCase().includes(normalizedQuery) ||
            res.target.toLowerCase().includes(normalizedQuery)
        );

        if (
          !titleText.includes(normalizedQuery) &&
          !commentText.includes(normalizedQuery) &&
          !criteriaMatch
        ) {
          return false;
        }
      }

      return true;
    });
  }, [
    submissions,
    selectedCourse,
    statusFilter,
    searchQuery,
    practicalContextMap,
    attemptMetaMap,
  ]);

  // Автоматичний вибір першої здачі зі списку відфільтрованих
  useEffect(() => {
    if (filteredSubmissions.length === 0) {
      setSelectedSubmissionId(null);
      return;
    }
    const stillExists = filteredSubmissions.some(
      (item) => item.id === selectedSubmissionId
    );
    if (!stillExists) {
      setSelectedSubmissionId(filteredSubmissions[0]?.id ?? null);
    }
  }, [filteredSubmissions, selectedSubmissionId]);

  const activeSubmission = useMemo<SubmissionRead | null>(() => {
    if (selectedSubmissionId === null) {
      return filteredSubmissions[0] ?? null;
    }
    return (
      filteredSubmissions.find((item) => item.id === selectedSubmissionId) ??
      filteredSubmissions[0] ??
      null
    );
  }, [filteredSubmissions, selectedSubmissionId]);

  if (isLoadingSubmissions || isLoadingCourses) {
    return (
      <div className="flex min-h-[55vh] flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8">
        <Loader2 className="h-9 w-9 animate-spin text-blue-600" />
        <p className="mt-3 text-sm font-medium text-slate-700">
          Завантаження електронної залікової книжки та звітів автоперевірки...
        </p>
      </div>
    );
  }

  if (isSubmissionsError) {
    const errorMessage = extractApiErrorMessage(
      submissionsError,
      "Не вдалося завантажити дані електронної залікової книжки."
    );
    return (
      <div className="mx-auto max-w-2xl rounded-2xl border border-rose-200 bg-white p-6 text-center shadow-xs">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose-600">
          <AlertCircle className="h-6 w-6" />
        </div>
        <h2 className="mt-4 text-lg font-bold text-slate-900">
          Помилка завантаження залікової книжки
        </h2>
        <p className="mt-1.5 text-sm text-slate-600">{errorMessage}</p>
        <button
          type="button"
          onClick={handleRefreshAll}
          className="mt-5 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-2xs hover:bg-blue-700"
        >
          <RefreshCw className="h-4 w-4" />
          Спробувати знову
        </button>
      </div>
    );
  }

  const allSubmissions = submissions ?? [];
  const isFetchingAny = isFetchingSubmissions || isFetchingCourses;
  const activeContext =
    activeSubmission !== null
      ? practicalContextMap[activeSubmission.practical_id]
      : undefined;
  const activeAttemptMeta =
    activeSubmission !== null ? attemptMetaMap[activeSubmission.id] : undefined;

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Верхній блок: паспорт студента та зведені KPI заліковки */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div className="space-y-1.5">
            <div className="inline-flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
              <ClipboardList className="h-3.5 w-3.5" />
              Електронна залікова книжка студента
            </div>
            <h1 className="text-xl font-bold text-slate-900 sm:text-2xl">
              Журнал здач та розбір помилок автоперевірки
            </h1>
            <p className="max-w-3xl text-sm text-slate-600">
              Переглядайте підсумкові бали за практичні роботи з{" "}
              <span className="font-semibold text-slate-800">
                Word, Excel, Access та HTML
              </span>
              , аналізуйте протоколи виконання кожного критерію та перевіряйте
              статус авторства (SHA-256 / <code>docProps/core.xml</code>).
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-xs">
              <span className="block text-slate-500">Студент / Група</span>
              <span className="mt-0.5 block text-sm font-bold text-slate-900">
                {user?.full_name ?? "Студент"} • {user?.group_code ?? "КН-31"}
              </span>
            </div>
            <div className="rounded-xl border border-indigo-200 bg-indigo-50/70 px-4 py-2.5 text-xs">
              <span className="block text-indigo-700">Номер у списку</span>
              <span className="mt-0.5 block text-sm font-bold text-indigo-950">
                №{user?.list_number ?? 1}
              </span>
            </div>
            <button
              type="button"
              onClick={handleRefreshAll}
              disabled={isFetchingAny}
              className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-xs font-semibold text-slate-700 shadow-2xs hover:bg-slate-50 disabled:opacity-60"
            >
              <RefreshCw
                className={`h-4 w-4 ${isFetchingAny ? "animate-spin" : ""}`}
              />
              <span>Оновити</span>
            </button>
          </div>
        </div>

        {/* 4 KPI-картки успішності */}
        <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
            <div className="flex items-center justify-between text-xs font-medium text-slate-500">
              <span>Набрано балів (найкращі здачі)</span>
              <Award className="h-4 w-4 text-blue-600" />
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              {gradebookStats.totalEarnedPoints.toFixed(1)}{" "}
              <span className="text-sm font-normal text-slate-500">
                / {gradebookStats.totalMaxPoints.toFixed(1)} б.
              </span>
            </p>
            <p className="mt-1 text-xs font-medium text-blue-700">
              Середня результативність: {gradebookStats.averageScorePercent}%
            </p>
            <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
              <div
                className={`h-full rounded-full transition-all duration-300 ${
                  gradebookStats.averageScorePercent >= 80
                    ? "bg-emerald-500"
                    : gradebookStats.averageScorePercent >= 60
                      ? "bg-blue-600"
                      : gradebookStats.averageScorePercent >= 40
                        ? "bg-amber-500"
                        : "bg-rose-500"
                }`}
                style={{
                  width: `${Math.min(100, Math.max(0, gradebookStats.averageScorePercent))}%`,
                }}
              />
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
            <div className="flex items-center justify-between text-xs font-medium text-slate-500">
              <span>Здані практичні роботи</span>
              <TrendingUp className="h-4 w-4 text-emerald-600" />
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              {gradebookStats.submittedPracticalsCount}{" "}
              <span className="text-sm font-normal text-slate-500">
                / {gradebookStats.totalPracticalsInCurriculum}
              </span>
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Усього спроб перевірки: {gradebookStats.totalAttempts}
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
            <div className="flex items-center justify-between text-xs font-medium text-slate-500">
              <span>Баланс критеріїв (актуальні)</span>
              <CheckCircle2 className="h-4 w-4 text-indigo-600" />
            </div>
            <div className="mt-2 flex items-baseline gap-3">
              <span className="text-2xl font-bold text-emerald-700">
                {gradebookStats.totalPassedCriteria} ✓
              </span>
              <span className="text-base font-bold text-rose-600">
                {gradebookStats.totalFailedCriteria} ✗
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Виконано / провалено правил автоперевірки
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
            <div className="flex items-center justify-between text-xs font-medium text-slate-500">
              <span>Контроль доброчесності</span>
              {gradebookStats.flaggedCount > 0 ? (
                <ShieldAlert className="h-4 w-4 text-rose-600" />
              ) : (
                <ShieldCheck className="h-4 w-4 text-emerald-600" />
              )}
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              {gradebookStats.cleanCount}{" "}
              <span className="text-sm font-normal text-slate-500">
                підтверджено
              </span>
            </p>
            <p
              className={`mt-1 text-xs font-medium ${
                gradebookStats.flaggedCount > 0
                  ? "text-rose-700"
                  : "text-emerald-700"
              }`}
            >
              {gradebookStats.flaggedCount > 0
                ? `Потребують уваги (плагіат): ${gradebookStats.flaggedCount}`
                : "Порушень авторства не зафіксовано"}
            </p>
          </div>
        </div>
      </section>

      {/* Панель фільтрів та пошуку по заліковці */}
      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs sm:p-5">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          {/* Вкладки дисциплін */}
          <div
            className="inline-flex flex-wrap items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 p-1"
            role="tablist"
            aria-label="Фільтр заліковки за дисципліною"
          >
            <button
              type="button"
              role="tab"
              aria-selected={selectedCourse === "all"}
              onClick={() => setSelectedCourse("all")}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                selectedCourse === "all"
                  ? "bg-slate-900 text-white"
                  : "text-slate-600 hover:bg-white hover:text-slate-900"
              }`}
            >
              Усі дисципліни ({allSubmissions.length})
            </button>

            {COURSE_SLUGS.map((slug) => {
              const meta = COURSE_BADGE_META[slug];
              const isSelected = selectedCourse === slug;
              return (
                <button
                  key={slug}
                  type="button"
                  role="tab"
                  aria-selected={isSelected}
                  onClick={() => setSelectedCourse(slug)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                    isSelected
                      ? "bg-blue-600 text-white"
                      : "text-slate-600 hover:bg-white hover:text-slate-900"
                  }`}
                >
                  {meta.label}
                </button>
              );
            })}
          </div>

          {/* Пошук та фільтр за статусом */}
          <div className="flex flex-col gap-2.5 sm:flex-row sm:items-center">
            <div className="relative min-w-[230px]">
              <Search className="pointer-events-none absolute top-1/2 left-3 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
              <input
                type="search"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="Пошук за назвою або правилом..."
                className="w-full rounded-xl border border-slate-200 bg-slate-50 py-1.5 pr-3 pl-8 text-xs text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none"
              />
            </div>

            <select
              aria-label="Фільтр статусу здачі"
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(event.target.value as SubmissionStatusFilter)
              }
              className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:bg-white focus:outline-none"
            >
              <option value="all">Усі спроби здачі</option>
              <option value="latest_only">Лише актуальні спроби</option>
              <option value="with_errors">Із помилками критеріїв</option>
              <option value="with_comment">З коментарем викладача</option>
              <option value="plagiarism_flagged">Підозра на плагіат</option>
            </select>
          </div>
        </div>
      </section>

      {/* Основна робоча область: Список здач (ліворуч) + Детальний розбір GradingReportCard (праворуч) */}
      {allSubmissions.length === 0 ? (
        <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-xs">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-blue-50 text-blue-600">
            <BookOpen className="h-7 w-7" />
          </div>
          <h2 className="mt-4 text-lg font-bold text-slate-900">
            У заліковій книжці ще немає зданих практичних робіт
          </h2>
          <p className="mx-auto mt-1.5 max-w-lg text-sm text-slate-600">
            Щоб отримати перший деталізований звіт автоперевірки, відкрийте
            навчальний модуль, складіть тест-допуск на ≥ 70% та надішліть
            виконаний файл (<code>.docx</code>, <code>.xlsx</code>,{" "}
            <code>.accdb</code>) або HTML-код.
          </p>
          <Link
            to="/student/courses"
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-xs font-semibold text-white shadow-2xs hover:bg-blue-700"
          >
            <span>Перейти до навчальних курсів</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      ) : filteredSubmissions.length === 0 ? (
        <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-xs">
          <Search className="mx-auto h-9 w-9 text-slate-400" />
          <h3 className="mt-3 text-base font-bold text-slate-900">
            За обраними фільтрами здач не знайдено
          </h3>
          <p className="mt-1 text-xs text-slate-500">
            Спробуйте скинути параметри пошуку або перемкнути вкладку
            дисципліни.
          </p>
          <button
            type="button"
            onClick={() => {
              setSelectedCourse("all");
              setStatusFilter("all");
              setSearchQuery("");
            }}
            className="mt-4 inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3.5 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
          >
            Скинути всі фільтри
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
          {/* Ліва колонка: Історія здач студента */}
          <aside
            className="space-y-3 lg:col-span-4"
            aria-label="Історія здач практичних робіт"
          >
            <div className="flex items-center justify-between px-1">
              <h2 className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-500">
                <History className="h-3.5 w-3.5" />
                <span>Історія перевірок ({filteredSubmissions.length})</span>
              </h2>
              <span className="text-[11px] text-slate-400">
                Оберіть запис для розбору
              </span>
            </div>

            <div className="max-h-[78vh] space-y-2.5 overflow-y-auto pr-1">
              {filteredSubmissions.map((item) => {
                const isSelected = activeSubmission?.id === item.id;
                const context = practicalContextMap[item.practical_id];
                const resolvedSlug =
                  item.course_slug ?? context?.courseSlug ?? "word";
                const courseMeta = COURSE_BADGE_META[resolvedSlug];
                const attemptMeta = attemptMetaMap[item.id];
                const hasFailedCriteria =
                  item.grading_report.failed_count > 0;

                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setSelectedSubmissionId(item.id)}
                    className={`w-full rounded-2xl border p-4 text-left transition-all ${
                      isSelected
                        ? "border-blue-600 bg-blue-50/50 shadow-xs ring-1 ring-blue-600"
                        : "border-slate-200 bg-white hover:border-blue-300 hover:bg-slate-50/70"
                    }`}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-1.5">
                      <span
                        className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-semibold ${courseMeta.pillClass}`}
                      >
                        {courseMeta.shortLabel}
                      </span>

                      <div className="flex items-center gap-1.5">
                        {attemptMeta !== undefined && (
                          <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-600">
                            Спроба №{attemptMeta.attemptNumber}
                            {attemptMeta.isLatestAttempt ? " • акт." : ""}
                          </span>
                        )}
                        <span
                          className={`inline-flex items-center gap-1 rounded-lg px-2 py-0.5 font-mono text-xs font-bold ${getScoreBadgeClasses(
                            item.final_score,
                            item.max_score
                          )}`}
                        >
                          {item.final_score.toFixed(1)}/
                          {formatCompactScore(item.max_score)}
                        </span>
                      </div>
                    </div>

                    <h3 className="mt-2 line-clamp-2 text-sm font-bold text-slate-900">
                      {item.practical_title ??
                        context?.moduleTitle ??
                        "Практична робота"}
                    </h3>

                    <div className="mt-2 flex flex-wrap items-center gap-1.5 text-[11px]">
                      <span className="inline-flex items-center gap-0.5 rounded-md border border-indigo-200 bg-indigo-50 px-1.5 py-0.5 font-semibold text-indigo-800">
                        <Sparkles className="h-3 w-3" />В №{item.variant_number}
                      </span>

                      <span className="inline-flex items-center gap-0.5 rounded-md border border-emerald-200 bg-emerald-50 px-1.5 py-0.5 font-semibold text-emerald-800">
                        <CheckCircle2 className="h-3 w-3" />
                        {item.grading_report.passed_count}
                      </span>

                      {hasFailedCriteria && (
                        <span className="inline-flex items-center gap-0.5 rounded-md border border-rose-200 bg-rose-50 px-1.5 py-0.5 font-semibold text-rose-800">
                          <XCircle className="h-3 w-3" />
                          {item.grading_report.failed_count} пом.
                        </span>
                      )}

                      {item.is_plagiarism_flagged ? (
                        <span className="inline-flex items-center gap-0.5 rounded-md border border-rose-300 bg-rose-100 px-1.5 py-0.5 font-bold text-rose-900">
                          <ShieldAlert className="h-3 w-3" />
                          Плагіат
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-0.5 rounded-md border border-slate-200 bg-slate-50 px-1.5 py-0.5 font-medium text-slate-600">
                          <ShieldCheck className="h-3 w-3 text-emerald-600" />
                          Ок
                        </span>
                      )}

                      {item.teacher_comment !== null &&
                        item.teacher_comment.trim().length > 0 && (
                          <span
                            className="inline-flex items-center gap-0.5 rounded-md border border-blue-200 bg-blue-50 px-1.5 py-0.5 font-semibold text-blue-800"
                            title="Є коментар викладача"
                          >
                            <MessageSquareQuote className="h-3 w-3" />
                            Відгук
                          </span>
                        )}
                    </div>

                    <div className="mt-2.5 flex items-center justify-between border-t border-slate-100 pt-2 text-[11px] text-slate-500">
                      <span className="inline-flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatShortDateTime(item.submitted_at)}
                      </span>
                      <span className="font-semibold text-blue-600">
                        {isSelected ? "Відкрито →" : "Детальніше"}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </aside>

          {/* Права колонка: Повний протокол автоперевірки обраної здачі */}
          <div className="space-y-4 lg:col-span-8">
            {activeSubmission !== null && (
              <>
                {/* Верхня панель швидкого переходу до модуля для виправлення помилок */}
                <div className="flex flex-col justify-between gap-3 rounded-2xl border border-slate-200 bg-white px-5 py-3.5 shadow-xs sm:flex-row sm:items-center">
                  <div className="text-xs text-slate-600">
                    {activeContext !== undefined ? (
                      <span>
                        Дисципліна:{" "}
                        <strong className="text-slate-900">
                          {activeContext.courseTitle}
                        </strong>{" "}
                        • Тема №{activeContext.moduleOrderIndex}:{" "}
                        <strong className="text-slate-900">
                          {activeContext.moduleTitle}
                        </strong>
                      </span>
                    ) : (
                      <span>
                        Протокол автоматичної перевірки здачі практичної роботи
                      </span>
                    )}
                  </div>

                  {activeContext !== undefined && (
                    <Link
                      to={`/student/modules/${activeContext.moduleId}`}
                      className="inline-flex shrink-0 items-center gap-1.5 rounded-xl bg-blue-600 px-3.5 py-2 text-xs font-semibold text-white shadow-2xs hover:bg-blue-700"
                    >
                      <span>
                        {activeSubmission.grading_report.failed_count > 0
                          ? "Виправити помилки та перездати"
                          : "Відкрити сторінку модуля"}
                      </span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  )}
                </div>

                <GradingReportCard
                  key={activeSubmission.id}
                  submission={activeSubmission}
                  attemptNumber={activeAttemptMeta?.attemptNumber}
                  isLatestAttempt={activeAttemptMeta?.isLatestAttempt}
                />
              </>
            )}
          </div>
        </div>
      )}

      {/* Зведена відомість успішності за всіма модулями навчального плану */}
      {(courses ?? []).length > 0 && (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex flex-col justify-between gap-2 border-b border-slate-100 pb-4 sm:flex-row sm:items-center">
            <div>
              <h2 className="text-base font-bold text-slate-900">
                Зведена відомість модулів за навчальним планом
              </h2>
              <p className="text-xs text-slate-500">
                Статус складання тестів-допусків та найкращі оцінки практичних
                робіт по кожній дисципліні
              </p>
            </div>
            <Link
              to="/student/courses"
              className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800"
            >
              <span>До каталогу курсів</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
            {(courses ?? []).map((course) => {
              const meta = COURSE_BADGE_META[course.slug];
              const CourseIcon = meta.icon;
              const sortedModules = [...course.modules].sort(
                (a, b) => a.order_index - b.order_index
              );

              return (
                <div
                  key={course.id}
                  className="rounded-xl border border-slate-200 bg-slate-50/50 p-4"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div
                        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border ${meta.iconBgClass}`}
                      >
                        <CourseIcon className="h-4 w-4" />
                      </div>
                      <div>
                        <span
                          className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-semibold ${meta.pillClass}`}
                        >
                          {meta.label}
                        </span>
                        <h3 className="mt-0.5 text-sm font-bold text-slate-900">
                          {course.title}
                        </h3>
                      </div>
                    </div>

                    <span className="rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs font-bold text-slate-800">
                      {course.progress_percent.toFixed(0)}%
                    </span>
                  </div>

                  <div className="mt-3 space-y-2 border-t border-slate-200/70 pt-3">
                    {sortedModules.map((mod) => (
                      <div
                        key={mod.id}
                        className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-200/80 bg-white px-3 py-2 text-xs"
                      >
                        <div className="min-w-0 flex-1">
                          <span className="font-semibold text-slate-900">
                            Тема №{mod.order_index}. {mod.title}
                          </span>
                        </div>

                        <div className="flex shrink-0 items-center gap-2">
                          {mod.quiz_passed ? (
                            <span className="inline-flex items-center gap-1 rounded-md bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700">
                              <CheckCircle2 className="h-3 w-3" />
                              Тест:{" "}
                              {mod.best_quiz_score !== null
                                ? `${mod.best_quiz_score.toFixed(0)}%`
                                : "ОК"}
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 rounded-md bg-amber-50 px-2 py-0.5 text-[11px] font-medium text-amber-700">
                              <Lock className="h-3 w-3" />
                              Тест &lt; 70%
                            </span>
                          )}

                          {mod.practical_score !== null ? (
                            <span
                              className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 font-mono text-[11px] font-bold ${getSoftScoreBadgeClasses(
                                mod.practical_score,
                                mod.practical_max_score ?? 12
                              )}`}
                            >
                              <Award className="h-3 w-3" />
                              {mod.practical_score.toFixed(1)}
                              {mod.practical_max_score !== null
                                ? ` / ${formatCompactScore(mod.practical_max_score)}`
                                : ""}{" "}
                              б.
                            </span>
                          ) : mod.quiz_passed ? (
                            <span className="inline-flex items-center gap-1 rounded-md bg-indigo-50 px-2 py-0.5 text-[11px] font-medium text-indigo-700">
                              <Unlock className="h-3 w-3" />
                              Доступно
                            </span>
                          ) : null}

                          <Link
                            to={`/student/modules/${mod.id}`}
                            className="font-semibold text-blue-600 hover:underline"
                          >
                            Відкрити
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}

export default GradebookPage;
