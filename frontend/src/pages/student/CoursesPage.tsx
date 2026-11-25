import { useMemo, useState, type ComponentType, type ReactElement } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  AlertCircle,
  ArrowRight,
  Award,
  BookOpen,
  CheckCircle2,
  Clock,
  Code2,
  Database,
  FileSpreadsheet,
  FileText,
  Layers,
  Loader2,
  Lock,
  RefreshCw,
  Sparkles,
  Unlock,
} from "lucide-react";
import apiClient from "../../api/client";
import { extractApiErrorMessage, useAuth } from "../../context/AuthContext";
import {
  COURSE_SLUGS,
  type CourseRead,
  type CourseSlug,
  type ModuleSummaryRead,
  type PracticalFormat,
} from "../../types/course";

interface CourseVisualMeta {
  label: string;
  shortTag: string;
  formatBadge: string;
  icon: ComponentType<{ className?: string }>;
  accentBorderClass: string;
  iconBgClass: string;
  badgeClass: string;
  progressBarClass: string;
}

const COURSE_VISUAL_META: Record<CourseSlug, CourseVisualMeta> = {
  word: {
    label: "Microsoft Word",
    shortTag: "Текстовий процесор",
    formatBadge: ".docx • python-docx",
    icon: FileText,
    accentBorderClass: "border-t-4 border-t-blue-600",
    iconBgClass: "bg-blue-50 text-blue-600 border-blue-200",
    badgeClass: "bg-blue-50 text-blue-700 border-blue-200",
    progressBarClass: "bg-blue-600",
  },
  excel: {
    label: "Microsoft Excel",
    shortTag: "Електронні таблиці",
    formatBadge: ".xlsx • openpyxl",
    icon: FileSpreadsheet,
    accentBorderClass: "border-t-4 border-t-emerald-600",
    iconBgClass: "bg-emerald-50 text-emerald-600 border-emerald-200",
    badgeClass: "bg-emerald-50 text-emerald-700 border-emerald-200",
    progressBarClass: "bg-emerald-600",
  },
  access: {
    label: "Microsoft Access",
    shortTag: "Реляційні бази даних",
    formatBadge: ".accdb • access-parser",
    icon: Database,
    accentBorderClass: "border-t-4 border-t-amber-500",
    iconBgClass: "bg-amber-50 text-amber-600 border-amber-200",
    badgeClass: "bg-amber-50 text-amber-700 border-amber-200",
    progressBarClass: "bg-amber-500",
  },
  html: {
    label: "HTML5 & DOM",
    shortTag: "Вебверстка та DOM",
    formatBadge: "HTML5 • BeautifulSoup4",
    icon: Code2,
    accentBorderClass: "border-t-4 border-t-violet-600",
    iconBgClass: "bg-violet-50 text-violet-600 border-violet-200",
    badgeClass: "bg-violet-50 text-violet-700 border-violet-200",
    progressBarClass: "bg-violet-600",
  },
};

const PRACTICAL_FORMAT_LABELS: Record<PracticalFormat, string> = {
  docx: "Файл Word (.docx)",
  xlsx: "Книга Excel (.xlsx)",
  accdb: "База Access (.accdb)",
  html: "HTML5-пісочниця",
};

type FilterOption = "all" | CourseSlug;

async function fetchCourses(): Promise<CourseRead[]> {
  const response = await apiClient.get<CourseRead[]>("/courses");
  return response.data;
}

function ModuleRowCard({
  module,
}: {
  module: ModuleSummaryRead;
}): ReactElement {
  const isCompleted =
    module.quiz_passed &&
    (module.practical_id === null || module.practical_score !== null);

  return (
    <div className="flex flex-col justify-between gap-3 rounded-xl border border-slate-200 bg-slate-50/70 p-4 transition-colors hover:border-blue-300 hover:bg-white sm:flex-row sm:items-center">
      <div className="min-w-0 flex-1 space-y-1.5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center rounded-md bg-slate-200/80 px-2 py-0.5 text-xs font-bold text-slate-700">
            Тема №{module.order_index}
          </span>
          <h4 className="text-sm font-semibold text-slate-900">
            {module.title}
          </h4>
        </div>

        <div className="flex flex-wrap items-center gap-2 pt-0.5">
          {module.quiz_passed ? (
            <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-xs font-medium text-emerald-700">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Тест-допуск складено
              {module.best_quiz_score !== null
                ? ` (${module.best_quiz_score.toFixed(0)}%)`
                : ""}
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 rounded-full border border-amber-200 bg-amber-50 px-2.5 py-0.5 text-xs font-medium text-amber-700">
              <Clock className="h-3.5 w-3.5" />
              {module.best_quiz_score !== null
                ? `Тест: ${module.best_quiz_score.toFixed(0)}% (поріг ≥ 70%)`
                : "Очікує проходження тесту-допуску"}
            </span>
          )}

          {module.practical_id !== null && (
            <>
              {module.practical_format !== null && (
                <span className="inline-flex items-center rounded-full border border-slate-200 bg-white px-2.5 py-0.5 text-xs font-medium text-slate-600">
                  {PRACTICAL_FORMAT_LABELS[module.practical_format]}
                </span>
              )}

              {module.practical_score !== null ? (
                <span className="inline-flex items-center gap-1 rounded-full border border-blue-200 bg-blue-50 px-2.5 py-0.5 text-xs font-semibold text-blue-700">
                  <Award className="h-3.5 w-3.5" />
                  Оцінка: {module.practical_score.toFixed(1)}
                  {module.practical_max_score !== null
                    ? ` / ${
                        Number.isInteger(module.practical_max_score)
                          ? module.practical_max_score.toFixed(0)
                          : module.practical_max_score.toFixed(1)
                      }`
                    : ""}{" "}
                  б.
                </span>
              ) : module.quiz_passed ? (
                <span className="inline-flex items-center gap-1 rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700">
                  <Unlock className="h-3.5 w-3.5" />
                  Практичну розблоковано
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 rounded-full border border-slate-200 bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-500">
                  <Lock className="h-3.5 w-3.5" />
                  Практичну заблоковано
                </span>
              )}
            </>
          )}
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-2">
        <Link
          to={`/student/modules/${module.id}`}
          className={`inline-flex w-full items-center justify-center gap-1.5 rounded-lg px-4 py-2 text-xs font-semibold shadow-2xs transition-colors sm:w-auto ${
            isCompleted
              ? "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
              : "bg-blue-600 text-white hover:bg-blue-700"
          }`}
        >
          <span>{isCompleted ? "Переглянути модуль" : "Відкрити модуль"}</span>
          <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>
    </div>
  );
}

export function CoursesPage(): ReactElement {
  const { user } = useAuth();
  const [selectedSlug, setSelectedSlug] = useState<FilterOption>("all");

  const {
    data: courses,
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
  } = useQuery<CourseRead[]>({
    queryKey: ["courses"],
    queryFn: fetchCourses,
  });

  const summaryStats = useMemo(() => {
    const courseList = courses ?? [];
    const totalCourses = courseList.length;
    let totalModules = 0;
    let completedModules = 0;
    let passedQuizzes = 0;
    let gradedPracticals = 0;

    for (const course of courseList) {
      totalModules += course.total_modules;
      completedModules += course.completed_modules;
      for (const mod of course.modules) {
        if (mod.quiz_passed) {
          passedQuizzes += 1;
        }
        if (mod.practical_score !== null) {
          gradedPracticals += 1;
        }
      }
    }

    const overallProgress =
      totalModules > 0
        ? Math.round((completedModules / totalModules) * 100)
        : 0;

    return {
      totalCourses,
      totalModules,
      completedModules,
      passedQuizzes,
      gradedPracticals,
      overallProgress,
    };
  }, [courses]);

  const filteredCourses = useMemo<CourseRead[]>(() => {
    const courseList = courses ?? [];
    if (selectedSlug === "all") {
      return courseList;
    }
    return courseList.filter((course) => course.slug === selectedSlug);
  }, [courses, selectedSlug]);

  if (isLoading) {
    return (
      <div className="flex min-h-[55vh] flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8">
        <Loader2 className="h-9 w-9 animate-spin text-blue-600" />
        <p className="mt-3 text-sm font-medium text-slate-700">
          Завантаження навчальних курсів та вашого прогресу...
        </p>
      </div>
    );
  }

  if (isError) {
    const errorMessage = extractApiErrorMessage(
      error,
      "Не вдалося завантажити список навчальних курсів."
    );
    return (
      <div className="mx-auto max-w-2xl rounded-2xl border border-rose-200 bg-white p-6 text-center shadow-xs">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose-600">
          <AlertCircle className="h-6 w-6" />
        </div>
        <h2 className="mt-4 text-lg font-bold text-slate-900">
          Помилка завантаження курсів
        </h2>
        <p className="mt-1.5 text-sm text-slate-600">{errorMessage}</p>
        <button
          type="button"
          onClick={() => void refetch()}
          className="mt-5 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-2xs hover:bg-blue-700"
        >
          <RefreshCw className="h-4 w-4" />
          Спробувати знову
        </button>
      </div>
    );
  }

  const studentListNumber = user?.list_number ?? 1;

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      {/* Шапка-огляд успішності студента */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div className="space-y-1.5">
            <div className="inline-flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
              <Sparkles className="h-3.5 w-3.5" />
              Електронні навчально-методичні посібники
            </div>
            <h2 className="text-xl font-bold text-slate-900 sm:text-2xl">
              Вітаємо, {user?.full_name ?? "студенте"}!
            </h2>
            <p className="max-w-2xl text-sm text-slate-600">
              Оберіть дисципліну, опрацюйте теоретичну лекцію та складіть
              тест-допуск (мінімум 70% правильних відповідей), щоб відкрити
              індивідуальний варіант практичної роботи з миттєвою
              автоперевіркою.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-xs">
              <span className="block text-slate-500">Академічна група</span>
              <span className="mt-0.5 block text-sm font-bold text-slate-900">
                {user?.group_code ?? "КН-31"}
              </span>
            </div>
            <div className="rounded-xl border border-blue-200 bg-blue-50/70 px-4 py-2.5 text-xs">
              <span className="block text-blue-700">Номер у списку групи</span>
              <span className="mt-0.5 block text-sm font-bold text-blue-900">
                №{studentListNumber} (формула варіанта:{" "}
                <code>((N - 1) mod V) + 1</code>)
              </span>
            </div>
          </div>
        </div>

        {/* Картки зведених показників */}
        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
            <div className="flex items-center justify-between text-xs font-medium text-slate-500">
              <span>Загальний прогрес</span>
              <Layers className="h-4 w-4 text-blue-600" />
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              {summaryStats.overallProgress}%
            </p>
            <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
              <div
                className="h-full rounded-full bg-blue-600 transition-all duration-300"
                style={{ width: `${summaryStats.overallProgress}%` }}
              />
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
            <div className="flex items-center justify-between text-xs font-medium text-slate-500">
              <span>Завершені модулі</span>
              <BookOpen className="h-4 w-4 text-emerald-600" />
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              {summaryStats.completedModules}{" "}
              <span className="text-sm font-normal text-slate-500">
                / {summaryStats.totalModules}
              </span>
            </p>
            <p className="mt-1 text-xs text-slate-500">
              У межах {summaryStats.totalCourses} дисциплін
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
            <div className="flex items-center justify-between text-xs font-medium text-slate-500">
              <span>Складені тести-допуски</span>
              <CheckCircle2 className="h-4 w-4 text-indigo-600" />
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              {summaryStats.passedQuizzes}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Прохідний поріг ≥ 70%
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
            <div className="flex items-center justify-between text-xs font-medium text-slate-500">
              <span>Оцінені практичні</span>
              <Award className="h-4 w-4 text-amber-600" />
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              {summaryStats.gradedPracticals}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Звіти доступні в заліковці
            </p>
          </div>
        </div>
      </section>

      {/* Фільтр за дисциплінами */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div
          className="inline-flex flex-wrap items-center gap-1.5 rounded-xl border border-slate-200 bg-white p-1.5 shadow-2xs"
          role="tablist"
          aria-label="Фільтр дисциплін"
        >
          <button
            type="button"
            onClick={() => setSelectedSlug("all")}
            className={`rounded-lg px-3.5 py-1.5 text-xs font-semibold transition-colors ${
              selectedSlug === "all"
                ? "bg-slate-900 text-white"
                : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            }`}
          >
            Усі дисципліни ({courses?.length ?? 0})
          </button>

          {COURSE_SLUGS.map((slug) => {
            const meta = COURSE_VISUAL_META[slug];
            const isSelected = selectedSlug === slug;
            return (
              <button
                key={slug}
                type="button"
                onClick={() => setSelectedSlug(slug)}
                className={`rounded-lg px-3.5 py-1.5 text-xs font-semibold transition-colors ${
                  isSelected
                    ? "bg-blue-600 text-white"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                {meta.label}
              </button>
            );
          })}
        </div>

        <button
          type="button"
          onClick={() => void refetch()}
          disabled={isFetching}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-2xs hover:bg-slate-50 disabled:opacity-60"
        >
          <RefreshCw
            className={`h-3.5 w-3.5 ${isFetching ? "animate-spin" : ""}`}
          />
          Оновити прогрес
        </button>
      </div>

      {/* Перелік карток курсів */}
      {filteredCourses.length === 0 ? (
        <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center">
          <BookOpen className="mx-auto h-10 w-10 text-slate-400" />
          <h3 className="mt-3 text-base font-bold text-slate-900">
            Навчальні курси не знайдено
          </h3>
          <p className="mt-1 text-sm text-slate-500">
            Для обраного фільтра наразі немає доступних курсів.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {filteredCourses.map((course) => {
            const meta = COURSE_VISUAL_META[course.slug];
            const CourseIcon = meta.icon;
            const sortedModules = [...course.modules].sort(
              (a, b) => a.order_index - b.order_index
            );

            return (
              <article
                key={course.id}
                className={`overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs ${meta.accentBorderClass}`}
              >
                <div className="p-6">
                  <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
                    <div className="flex items-start gap-4">
                      <div
                        className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border ${meta.iconBgClass}`}
                      >
                        <CourseIcon className="h-6 w-6" />
                      </div>
                      <div className="space-y-1.5">
                        <div className="flex flex-wrap items-center gap-2">
                          <span
                            className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${meta.badgeClass}`}
                          >
                            {meta.label}
                          </span>
                          <span className="inline-flex items-center rounded-full border border-slate-200 bg-slate-50 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                            {meta.formatBadge}
                          </span>
                        </div>
                        <h3 className="text-lg font-bold text-slate-900">
                          {course.title}
                        </h3>
                        <p className="max-w-3xl text-sm leading-relaxed text-slate-600">
                          {course.description}
                        </p>
                      </div>
                    </div>

                    {/* Прогрес-блок курсу */}
                    <div className="w-full shrink-0 rounded-xl border border-slate-200 bg-slate-50 p-3.5 md:w-64">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-slate-700">
                          Прогрес курсу
                        </span>
                        <span className="font-bold text-slate-900">
                          {course.progress_percent.toFixed(0)}%
                        </span>
                      </div>
                      <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-200">
                        <div
                          className={`h-full rounded-full transition-all duration-300 ${meta.progressBarClass}`}
                          style={{
                            width: `${Math.min(100, Math.max(0, course.progress_percent))}%`,
                          }}
                        />
                      </div>
                      <p className="mt-2 text-xs text-slate-500">
                        Завершено модулів:{" "}
                        <span className="font-semibold text-slate-800">
                          {course.completed_modules} із {course.total_modules}
                        </span>
                      </p>
                    </div>
                  </div>

                  {/* Модулі курсу */}
                  <div className="mt-6 space-y-3 border-t border-slate-100 pt-5">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                        Модулі курсу ({sortedModules.length})
                      </h4>
                      <span className="text-xs text-slate-400">
                        Лекція → Тест-допуск (≥ 70%) → Практична робота
                      </span>
                    </div>

                    {sortedModules.length === 0 ? (
                      <p className="rounded-xl border border-dashed border-slate-200 p-4 text-center text-xs text-slate-500">
                        У цьому курсі ще немає опублікованих модулів.
                      </p>
                    ) : (
                      <div className="space-y-2.5">
                        {sortedModules.map((module) => (
                          <ModuleRowCard key={module.id} module={module} />
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default CoursesPage;
