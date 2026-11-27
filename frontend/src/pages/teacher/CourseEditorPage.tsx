import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
  type ComponentType,
  type FormEvent,
  type ReactElement,
} from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import {
  AlertCircle,
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  BookOpen,
  BookOpenCheck,
  CheckCircle2,
  Code2,
  Database,
  Download,
  Eye,
  FileEdit,
  FileSpreadsheet,
  FileText,
  HelpCircle,
  ImagePlus,
  Layers,
  Loader2,
  Paperclip,
  Pencil,
  Plus,
  RefreshCw,
  Save,
  SlidersHorizontal,
  Sparkles,
  Trash2,
  Upload,
  Wrench,
  X,
} from "lucide-react";
import apiClient from "../../api/client";
import { MarkdownRenderer } from "../../components/common/MarkdownRenderer";
import { extractApiErrorMessage } from "../../context/AuthContext";
import {
  COURSE_SLUGS,
  type CourseCreate,
  type CourseMediaUploadRead,
  type CourseRead,
  type CourseSlug,
  type CourseUpdate,
  type ModuleCreate,
  type ModuleDetailRead,
  type ModuleReorderRequest,
  type ModuleSummaryRead,
  type ModuleUpdate,
  type PracticalCreate,
  type PracticalTeacherRead,
  type PracticalVariant,
  type QuizQuestionCreate,
  type QuizQuestionTeacherRead,
  type QuizQuestionUpdate,
} from "../../types/course";
import {
  PRACTICAL_FORMATS,
  type PracticalFormat,
} from "../../types/grading";

type EditorTab = "lecture" | "quiz" | "practical";

interface DisciplineMeta {
  label: string;
  shortLabel: string;
  defaultFormat: PracticalFormat;
  icon: ComponentType<{ className?: string }>;
  badgeClass: string;
}

const DISCIPLINE_META: Record<CourseSlug, DisciplineMeta> = {
  word: {
    label: "Microsoft Word",
    shortLabel: "Word (.docx)",
    defaultFormat: "docx",
    icon: FileText,
    badgeClass: "border-blue-200 bg-blue-50 text-blue-700",
  },
  excel: {
    label: "Microsoft Excel",
    shortLabel: "Excel (.xlsx)",
    defaultFormat: "xlsx",
    icon: FileSpreadsheet,
    badgeClass: "border-emerald-200 bg-emerald-50 text-emerald-700",
  },
  access: {
    label: "Microsoft Access",
    shortLabel: "Access (.accdb)",
    defaultFormat: "accdb",
    icon: Database,
    badgeClass: "border-amber-200 bg-amber-50 text-amber-800",
  },
  html: {
    label: "HTML5 & DOM",
    shortLabel: "HTML5",
    defaultFormat: "html",
    icon: Code2,
    badgeClass: "border-violet-200 bg-violet-50 text-violet-700",
  },
};

const FORMAT_LABELS: Record<PracticalFormat, string> = {
  docx: "Microsoft Word (.docx)",
  xlsx: "Microsoft Excel (.xlsx)",
  accdb: "Microsoft Access (.accdb)",
  html: "HTML5 & DOM (Пісочниця)",
};

interface VariantDraft {
  variant_number: number;
  title: string;
  task_description: string;
  parametersJson: string;
}

type DeleteTarget =
  | {
      kind: "module";
      courseId: string;
      moduleId: string;
      orderIndex: number;
      title: string;
      practicalId: string | null;
      hasPractical: boolean;
    }
  | {
      kind: "practical";
      courseId: string;
      moduleId: string;
      practicalId: string;
      title: string;
      moduleTitle: string;
    };

async function fetchCourses(): Promise<CourseRead[]> {
  const response = await apiClient.get<CourseRead[]>("/courses");
  return response.data;
}

async function fetchModuleDetail(moduleId: string): Promise<ModuleDetailRead> {
  const response = await apiClient.get<ModuleDetailRead>(
    `/modules/${moduleId}`
  );
  return response.data;
}

async function fetchModuleQuizQuestions(
  moduleId: string
): Promise<QuizQuestionTeacherRead[]> {
  const response = await apiClient.get<QuizQuestionTeacherRead[]>(
    `/modules/${moduleId}/quiz/questions`
  );
  return response.data;
}

async function fetchPracticalTeacher(
  practicalId: string
): Promise<PracticalTeacherRead> {
  const response = await apiClient.get<PracticalTeacherRead>(
    `/practicals/${practicalId}/teacher`
  );
  return response.data;
}

async function deleteModuleById(moduleId: string): Promise<void> {
  await apiClient.delete(`/modules/${moduleId}`);
}

async function deletePracticalById(practicalId: string): Promise<void> {
  await apiClient.delete(`/practicals/${practicalId}`);
}

const ALLOWED_MEDIA_IMAGE_EXTENSIONS = [
  ".png",
  ".jpg",
  ".jpeg",
  ".webp",
  ".gif",
] as const;
const MAX_MEDIA_UPLOAD_BYTES = 5 * 1024 * 1024;
const ALLOWED_TEMPLATE_FILE_ACCEPT = ".docx,.xlsx,.accdb,.zip,.txt,.csv";

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

export function CourseEditorPage(): ReactElement {
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();

  const [selectedCourseId, setSelectedCourseId] = useState<string | null>(() =>
    searchParams.get("courseId")
  );
  const [selectedModuleId, setSelectedModuleId] = useState<string | null>(() =>
    searchParams.get("moduleId")
  );
  const [activeTab, setActiveTab] = useState<EditorTab>("lecture");
  const [showLecturePreview, setShowLecturePreview] = useState<boolean>(true);

  const [feedbackBanner, setFeedbackBanner] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null);
  const [deleteModalError, setDeleteModalError] = useState<string | null>(null);

  // Стан редагування поточного курсу
  const [courseTitle, setCourseTitle] = useState<string>("");
  const [courseDescription, setCourseDescription] = useState<string>("");
  const [isCreatingCourse, setIsCreatingCourse] = useState<boolean>(false);
  const [newCourseSlug, setNewCourseSlug] = useState<CourseSlug>("word");
  const [newCourseTitle, setNewCourseTitle] = useState<string>("");
  const [newCourseDescription, setNewCourseDescription] = useState<string>("");

  // Стан створення нового модуля
  const [isAddingModule, setIsAddingModule] = useState<boolean>(false);
  const [newModuleOrder, setNewModuleOrder] = useState<number>(1);
  const [newModuleTitle, setNewModuleTitle] = useState<string>("");
  const [newModuleLecture, setNewModuleLecture] = useState<string>(
    "# Назва теми лекції\n\n## 1. Теоретичні відомості\nОпишіть ключові поняття та алгоритми роботи."
  );

  // Стан редагування обраного модуля (лекції)
  const [moduleOrderIndex, setModuleOrderIndex] = useState<number>(1);
  const [moduleTitle, setModuleTitle] = useState<string>("");
  const [moduleLectureContent, setModuleLectureContent] = useState<string>("");
  const lectureTextareaRef = useRef<HTMLTextAreaElement | null>(null);
  const mediaFileInputRef = useRef<HTMLInputElement | null>(null);
  const templateFileInputRef = useRef<HTMLInputElement | null>(null);

  // Стан додавання нового питання тесту-допуску
  const [questionText, setQuestionText] = useState<string>("");
  const [questionOptions, setQuestionOptions] = useState<string[]>([
    "",
    "",
    "",
    "",
  ]);
  const [correctOptionIndex, setCorrectOptionIndex] = useState<number>(0);

  // Стан inline-редагування існуючого питання тесту-допуску
  const [editingQuestionId, setEditingQuestionId] = useState<string | null>(
    null
  );
  const [editQuestionText, setEditQuestionText] = useState<string>("");
  const [editQuestionOptions, setEditQuestionOptions] = useState<string[]>([]);
  const [editCorrectOptionIndex, setEditCorrectOptionIndex] =
    useState<number>(0);

  // Стан редагування практичної роботи, варіантів та файлу-заготовки
  const [practicalTitle, setPracticalTitle] = useState<string>("");
  const [practicalFormat, setPracticalFormat] =
    useState<PracticalFormat>("docx");
  const [practicalMaxScore, setPracticalMaxScore] = useState<number>(12);
  const [practicalInstructions, setPracticalInstructions] =
    useState<string>("");
  const [variantDrafts, setVariantDrafts] = useState<VariantDraft[]>([]);
  const [isDownloadingTemplate, setIsDownloadingTemplate] =
    useState<boolean>(false);

  const {
    data: courses,
    isLoading: isLoadingCourses,
    isError: isCoursesError,
    error: coursesError,
    refetch: refetchCourses,
  } = useQuery<CourseRead[]>({
    queryKey: ["courses"],
    queryFn: fetchCourses,
  });

  // Автоматичний вибір першого курсу
  useEffect(() => {
    const list = courses ?? [];
    if (list.length === 0) {
      setSelectedCourseId(null);
      return;
    }
    const exists = list.some((item) => item.id === selectedCourseId);
    if (!exists) {
      setSelectedCourseId(list[0]?.id ?? null);
    }
  }, [courses, selectedCourseId]);

  const activeCourse = useMemo<CourseRead | null>(() => {
    const list = courses ?? [];
    if (selectedCourseId === null) {
      return list[0] ?? null;
    }
    return (
      list.find((item) => item.id === selectedCourseId) ?? list[0] ?? null
    );
  }, [courses, selectedCourseId]);

  // Синхронізація полів курсу та вибір першого модуля
  useEffect(() => {
    if (activeCourse === null) {
      setCourseTitle("");
      setCourseDescription("");
      setSelectedModuleId(null);
      return;
    }
    setCourseTitle(activeCourse.title);
    setCourseDescription(activeCourse.description);

    const modules = activeCourse.modules;
    setNewModuleOrder(modules.length + 1);
    if (modules.length === 0) {
      setSelectedModuleId(null);
      return;
    }
    const moduleExists = modules.some((mod) => mod.id === selectedModuleId);
    if (!moduleExists) {
      setSelectedModuleId(modules[0]?.id ?? null);
    }
  }, [activeCourse, selectedModuleId]);

  // Завантаження деталей обраного модуля
  const {
    data: moduleDetail,
    isLoading: isLoadingModule,
  } = useQuery<ModuleDetailRead>({
    queryKey: ["module-detail", selectedModuleId],
    queryFn: () => fetchModuleDetail(selectedModuleId ?? ""),
    enabled: selectedModuleId !== null,
  });

  // Завантаження питань тесту-допуску для викладача
  const {
    data: quizQuestions,
    isLoading: isLoadingQuizQuestions,
  } = useQuery<QuizQuestionTeacherRead[]>({
    queryKey: ["module-quiz-teacher", selectedModuleId],
    queryFn: () => fetchModuleQuizQuestions(selectedModuleId ?? ""),
    enabled: selectedModuleId !== null,
  });

  const activePracticalId = moduleDetail?.practical?.id ?? null;

  // Завантаження повних налаштувань практичної роботи для викладача
  const {
    data: practicalTeacher,
    isLoading: isLoadingPractical,
  } = useQuery<PracticalTeacherRead>({
    queryKey: ["practical-teacher", activePracticalId],
    queryFn: () => fetchPracticalTeacher(activePracticalId ?? ""),
    enabled: activePracticalId !== null,
  });

  // Синхронізація полів модуля після завантаження
  useEffect(() => {
    if (moduleDetail === undefined) {
      return;
    }
    setModuleOrderIndex(moduleDetail.order_index);
    setModuleTitle(moduleDetail.title);
    setModuleLectureContent(moduleDetail.lecture_content);
  }, [moduleDetail]);

  // Скидання активного редагування питання при зміні модуля
  useEffect(() => {
    setEditingQuestionId(null);
  }, [selectedModuleId]);

  // Синхронізація полів практичної роботи після завантаження
  useEffect(() => {
    if (practicalTeacher !== undefined && activePracticalId !== null) {
      setPracticalTitle(practicalTeacher.title);
      setPracticalFormat(practicalTeacher.format_type);
      setPracticalMaxScore(practicalTeacher.max_score);
      setPracticalInstructions(practicalTeacher.instructions);
      setVariantDrafts(
        practicalTeacher.variants.map((item) => ({
          variant_number: item.variant_number,
          title: item.title,
          task_description: item.task_description,
          parametersJson: JSON.stringify(item.parameters, null, 2),
        }))
      );
      return;
    }

    if (activePracticalId === null && activeCourse !== null) {
      const defaultFormat = DISCIPLINE_META[activeCourse.slug].defaultFormat;
      setPracticalTitle(
        `Практична робота: ${moduleDetail?.title ?? activeCourse.title}`
      );
      setPracticalFormat(defaultFormat);
      setPracticalMaxScore(12);
      setPracticalInstructions(
        "Виконайте завдання згідно з індивідуальним варіантом та завантажте результат на перевірку."
      );
      setVariantDrafts([
        {
          variant_number: 1,
          title: "Варіант 1: Базове індивідуальне завдання",
          task_description:
            "Оформіть практичну роботу відповідно до методичних вказівок для варіанта №1.",
          parametersJson: JSON.stringify({ variant: 1 }, null, 2),
        },
      ]);
    }
  }, [practicalTeacher, activePracticalId, activeCourse, moduleDetail]);

  const missingCourseSlugs = useMemo<CourseSlug[]>(() => {
    const existingSlugs = new Set((courses ?? []).map((c) => c.slug));
    return COURSE_SLUGS.filter((slug) => !existingSlugs.has(slug));
  }, [courses]);

  // Мутація створення курсу
  const createCourseMutation = useMutation<CourseRead, unknown, CourseCreate>({
    mutationFn: async (payload: CourseCreate) => {
      const response = await apiClient.post<CourseRead>("/courses", payload);
      return response.data;
    },
    onSuccess: (created) => {
      void queryClient.invalidateQueries({ queryKey: ["courses"] });
      setSelectedCourseId(created.id);
      setIsCreatingCourse(false);
      setNewCourseTitle("");
      setNewCourseDescription("");
      setFeedbackBanner({
        type: "success",
        text: `Навчальний курс «${created.title}» успішно створено.`,
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(err, "Не вдалося створити курс."),
      });
    },
  });

  // Мутація оновлення курсу
  const updateCourseMutation = useMutation<CourseRead, unknown, CourseUpdate>({
    mutationFn: async (payload: CourseUpdate) => {
      if (activeCourse === null) {
        throw new Error("Курс не обрано");
      }
      const response = await apiClient.patch<CourseRead>(
        `/courses/${activeCourse.id}`,
        payload
      );
      return response.data;
    },
    onSuccess: (updated) => {
      void queryClient.invalidateQueries({ queryKey: ["courses"] });
      setFeedbackBanner({
        type: "success",
        text: `Параметри курсу «${updated.title}» збережено.`,
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(err, "Не вдалося оновити курс."),
      });
    },
  });

  // Мутація створення модуля
  const createModuleMutation = useMutation<
    ModuleDetailRead,
    unknown,
    ModuleCreate
  >({
    mutationFn: async (payload: ModuleCreate) => {
      if (activeCourse === null) {
        throw new Error("Курс не обрано");
      }
      const response = await apiClient.post<ModuleDetailRead>(
        `/courses/${activeCourse.id}/modules`,
        payload
      );
      return response.data;
    },
    onSuccess: (created) => {
      void queryClient.invalidateQueries({ queryKey: ["courses"] });
      setSelectedModuleId(created.id);
      setIsAddingModule(false);
      setNewModuleTitle("");
      setFeedbackBanner({
        type: "success",
        text: `Модуль №${created.order_index} «${created.title}» додано до курсу.`,
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(err, "Не вдалося створити модуль."),
      });
    },
  });

  // Мутація оновлення модуля та лекції
  const updateModuleMutation = useMutation<
    ModuleDetailRead,
    unknown,
    ModuleUpdate
  >({
    mutationFn: async (payload: ModuleUpdate) => {
      if (selectedModuleId === null) {
        throw new Error("Модуль не обрано");
      }
      const response = await apiClient.patch<ModuleDetailRead>(
        `/modules/${selectedModuleId}`,
        payload
      );
      return response.data;
    },
    onSuccess: (updated) => {
      void queryClient.invalidateQueries({ queryKey: ["courses"] });
      void queryClient.invalidateQueries({
        queryKey: ["module-detail", updated.id],
      });
      setFeedbackBanner({
        type: "success",
        text: `Лекцію та параметри модуля «${updated.title}» успішно збережено.`,
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(err, "Не вдалося зберегти модуль."),
      });
    },
  });

  // Мутація додавання тестового питання
  const createQuizQuestionMutation = useMutation<
    QuizQuestionTeacherRead,
    unknown,
    QuizQuestionCreate
  >({
    mutationFn: async (payload: QuizQuestionCreate) => {
      if (selectedModuleId === null) {
        throw new Error("Модуль не обрано");
      }
      const response = await apiClient.post<QuizQuestionTeacherRead>(
        `/modules/${selectedModuleId}/quiz/questions`,
        payload
      );
      return response.data;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ["module-quiz-teacher", selectedModuleId],
      });
      void queryClient.invalidateQueries({
        queryKey: ["module-detail", selectedModuleId],
      });
      setQuestionText("");
      setQuestionOptions(["", "", "", ""]);
      setCorrectOptionIndex(0);
      setFeedbackBanner({
        type: "success",
        text: "Питання тесту-допуску додано до модуля.",
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(
          err,
          "Не вдалося додати тестове питання."
        ),
      });
    },
  });

  // Мутація видалення тестового питання
  const deleteQuizQuestionMutation = useMutation<void, unknown, string>({
    mutationFn: async (questionId: string) => {
      await apiClient.delete(`/quiz/questions/${questionId}`);
    },
    onSuccess: (_data, deletedQuestionId) => {
      if (editingQuestionId === deletedQuestionId) {
        setEditingQuestionId(null);
      }
      void queryClient.invalidateQueries({
        queryKey: ["module-quiz-teacher", selectedModuleId],
      });
      void queryClient.invalidateQueries({
        queryKey: ["module-detail", selectedModuleId],
      });
      setFeedbackBanner({
        type: "success",
        text: "Тестове питання видалено.",
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(
          err,
          "Не вдалося видалити тестове питання."
        ),
      });
    },
  });

  // Мутація редагування існуючого питання тесту-допуску (PATCH)
  const updateQuizQuestionMutation = useMutation<
    QuizQuestionTeacherRead,
    unknown,
    { questionId: string; payload: QuizQuestionUpdate }
  >({
    mutationFn: async ({ questionId, payload }) => {
      const response = await apiClient.patch<QuizQuestionTeacherRead>(
        `/quiz/questions/${questionId}`,
        payload
      );
      return response.data;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ["module-quiz-teacher", selectedModuleId],
      });
      void queryClient.invalidateQueries({
        queryKey: ["module-detail", selectedModuleId],
      });
      setEditingQuestionId(null);
      setFeedbackBanner({
        type: "success",
        text: "Зміни до тестового питання збережено.",
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(
          err,
          "Не вдалося оновити тестове питання."
        ),
      });
    },
  });

  // Мутація зміни порядку модулів курсу (PUT /courses/{id}/modules/reorder)
  const reorderModulesMutation = useMutation<
    ModuleSummaryRead[],
    unknown,
    { courseId: string; moduleIds: string[] }
  >({
    mutationFn: async ({ courseId, moduleIds }) => {
      const payload: ModuleReorderRequest = { module_ids: moduleIds };
      const response = await apiClient.put<ModuleSummaryRead[]>(
        `/courses/${courseId}/modules/reorder`,
        payload
      );
      return response.data;
    },
    onSuccess: (reorderedModules, variables) => {
      queryClient.setQueryData<CourseRead[]>(["courses"], (previous) => {
        if (previous === undefined) {
          return previous;
        }
        return previous.map((course) =>
          course.id === variables.courseId
            ? {
                ...course,
                modules: reorderedModules,
              }
            : course
        );
      });
      if (selectedModuleId !== null) {
        const updatedSelected = reorderedModules.find(
          (item) => item.id === selectedModuleId
        );
        if (updatedSelected !== undefined) {
          setModuleOrderIndex(updatedSelected.order_index);
        }
        void queryClient.invalidateQueries({
          queryKey: ["module-detail", selectedModuleId],
        });
      }
      void queryClient.invalidateQueries({ queryKey: ["courses"] });
      setFeedbackBanner({
        type: "success",
        text: "Порядок модулів курсу оновлено.",
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(
          err,
          "Не вдалося змінити порядок модулів курсу."
        ),
      });
    },
  });

  // Мутація завантаження растрової ілюстрації для лекції (POST /courses/{id}/media)
  const uploadCourseMediaMutation = useMutation<
    CourseMediaUploadRead,
    unknown,
    { courseId: string; file: File }
  >({
    mutationFn: async ({ courseId, file }) => {
      const formData = new FormData();
      formData.append("file", file);
      const response = await apiClient.post<CourseMediaUploadRead>(
        `/courses/${courseId}/media`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return response.data;
    },
    onSuccess: (uploaded) => {
      insertTextAtLectureCursor(uploaded.markdown);
      setFeedbackBanner({
        type: "success",
        text: `Ілюстрацію завантажено та вставлено у текст лекції (${uploaded.filename}).`,
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(
          err,
          "Не вдалося завантажити ілюстрацію до лекції."
        ),
      });
    },
  });

  // Мутація завантаження файлу-заготовки практичної (POST /practicals/{id}/template)
  const uploadPracticalTemplateMutation = useMutation<
    PracticalTeacherRead,
    unknown,
    { practicalId: string; file: File }
  >({
    mutationFn: async ({ practicalId, file }) => {
      const formData = new FormData();
      formData.append("file", file);
      const response = await apiClient.post<PracticalTeacherRead>(
        `/practicals/${practicalId}/template`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return response.data;
    },
    onSuccess: (updated) => {
      queryClient.setQueryData<PracticalTeacherRead>(
        ["practical-teacher", updated.id],
        updated
      );
      void queryClient.invalidateQueries({
        queryKey: ["module-detail", selectedModuleId],
      });
      void queryClient.invalidateQueries({
        queryKey: ["practical-student", updated.id],
      });
      setFeedbackBanner({
        type: "success",
        text: `Файл-заготовку «${updated.template_file_name ?? "шаблон"}» прикріплено до практичної роботи.`,
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(
          err,
          "Не вдалося завантажити файл-заготовку практичної роботи."
        ),
      });
    },
  });

  // Мутація видалення файлу-заготовки практичної (DELETE /practicals/{id}/template)
  const deletePracticalTemplateMutation = useMutation<void, unknown, string>({
    mutationFn: async (practicalId: string) => {
      await apiClient.delete(`/practicals/${practicalId}/template`);
    },
    onSuccess: (_data, practicalId) => {
      queryClient.setQueryData<PracticalTeacherRead>(
        ["practical-teacher", practicalId],
        (previous) => {
          if (previous === undefined) {
            return previous;
          }
          return {
            ...previous,
            has_template_file: false,
            template_file_name: null,
          };
        }
      );
      void queryClient.invalidateQueries({
        queryKey: ["practical-teacher", practicalId],
      });
      void queryClient.invalidateQueries({
        queryKey: ["module-detail", selectedModuleId],
      });
      void queryClient.invalidateQueries({
        queryKey: ["practical-student", practicalId],
      });
      setFeedbackBanner({
        type: "success",
        text: "Файл-заготовку видалено з практичної роботи.",
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(
          err,
          "Не вдалося видалити файл-заготовку."
        ),
      });
    },
  });

  // Мутація збереження практичної роботи та варіантів
  const upsertPracticalMutation = useMutation<
    PracticalTeacherRead,
    unknown,
    PracticalCreate
  >({
    mutationFn: async (payload: PracticalCreate) => {
      if (selectedModuleId === null) {
        throw new Error("Модуль не обрано");
      }
      const response = await apiClient.post<PracticalTeacherRead>(
        `/modules/${selectedModuleId}/practical`,
        payload
      );
      return response.data;
    },
    onSuccess: (saved) => {
      void queryClient.invalidateQueries({ queryKey: ["courses"] });
      void queryClient.invalidateQueries({
        queryKey: ["module-detail", selectedModuleId],
      });
      void queryClient.invalidateQueries({
        queryKey: ["practical-teacher", saved.id],
      });
      setFeedbackBanner({
        type: "success",
        text: `Практичну роботу «${saved.title}» та ${saved.variants.length} варіант(и) збережено.`,
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(
          err,
          "Не вдалося зберегти практичну роботу."
        ),
      });
    },
  });

  // Мутація видалення модуля курсу
  const deleteModuleMutation = useMutation<
    void,
    unknown,
    Extract<DeleteTarget, { kind: "module" }>
  >({
    mutationFn: async (target) => {
      await deleteModuleById(target.moduleId);
    },
    onSuccess: (_data, target) => {
      const currentCourses =
        queryClient.getQueryData<CourseRead[]>(["courses"]) ?? [];
      const targetCourse = currentCourses.find(
        (course) => course.id === target.courseId
      );

      if (selectedModuleId === target.moduleId) {
        const currentModules = targetCourse?.modules ?? [];
        const deletedIndex = currentModules.findIndex(
          (item) => item.id === target.moduleId
        );
        const remainingModules = currentModules.filter(
          (item) => item.id !== target.moduleId
        );
        if (remainingModules.length === 0) {
          setSelectedModuleId(null);
        } else {
          const nextIndex = Math.min(
            Math.max(deletedIndex, 0),
            remainingModules.length - 1
          );
          setSelectedModuleId(remainingModules[nextIndex]?.id ?? null);
        }
      }

      queryClient.setQueryData<CourseRead[]>(["courses"], (previous) => {
        if (previous === undefined) {
          return previous;
        }
        return previous.map((course) => {
          if (course.id !== target.courseId) {
            return course;
          }
          const renumberedModules = course.modules
            .filter((item) => item.id !== target.moduleId)
            .map((item, index) => ({
              ...item,
              order_index: index + 1,
            }));
          return {
            ...course,
            total_modules: renumberedModules.length,
            modules: renumberedModules,
          };
        });
      });

      queryClient.removeQueries({
        queryKey: ["module-detail", target.moduleId],
        exact: true,
      });
      queryClient.removeQueries({
        queryKey: ["module-quiz-teacher", target.moduleId],
        exact: true,
      });
      queryClient.removeQueries({
        queryKey: ["module", target.moduleId],
        exact: true,
      });
      if (target.practicalId !== null) {
        queryClient.removeQueries({
          queryKey: ["practical-teacher", target.practicalId],
          exact: true,
        });
        queryClient.removeQueries({
          queryKey: ["practical-student", target.practicalId],
          exact: true,
        });
      }

      void queryClient.invalidateQueries({ queryKey: ["courses"] });
      void queryClient.invalidateQueries({
        queryKey: ["module"],
        predicate: (query) => query.queryKey[1] !== target.moduleId,
      });
      void queryClient.invalidateQueries({
        queryKey: ["module-detail"],
        predicate: (query) => query.queryKey[1] !== target.moduleId,
      });
      void queryClient.invalidateQueries({
        queryKey: ["module-quiz-teacher"],
        predicate: (query) => query.queryKey[1] !== target.moduleId,
      });
      void queryClient.invalidateQueries({
        queryKey: ["practical-teacher"],
        predicate: (query) =>
          target.practicalId === null ||
          query.queryKey[1] !== target.practicalId,
      });
      void queryClient.invalidateQueries({
        queryKey: ["practical-student"],
        predicate: (query) =>
          target.practicalId === null ||
          query.queryKey[1] !== target.practicalId,
      });
      void queryClient.invalidateQueries({ queryKey: ["group-journal"] });
      void queryClient.invalidateQueries({ queryKey: ["submission-detail"] });
      void queryClient.invalidateQueries({ queryKey: ["submissions-my"] });

      setDeleteTarget(null);
      setDeleteModalError(null);
      setFeedbackBanner({
        type: "success",
        text: `Модуль «${target.title}» видалено, нумерацію решти тем оновлено.`,
      });
    },
    onError: (err) => {
      setDeleteModalError(
        extractApiErrorMessage(err, "Не вдалося видалити модуль курсу.")
      );
    },
  });

  // Мутація видалення практичної роботи модуля
  const deletePracticalMutation = useMutation<
    void,
    unknown,
    Extract<DeleteTarget, { kind: "practical" }>
  >({
    mutationFn: async (target) => {
      await deletePracticalById(target.practicalId);
    },
    onSuccess: (_data, target) => {
      queryClient.setQueryData<CourseRead[]>(["courses"], (previous) => {
        if (previous === undefined) {
          return previous;
        }
        return previous.map((course) => {
          if (course.id !== target.courseId) {
            return course;
          }
          return {
            ...course,
            modules: course.modules.map((item) =>
              item.id === target.moduleId
                ? {
                    ...item,
                    practical_id: null,
                    practical_format: null,
                    practical_score: null,
                    practical_max_score: null,
                  }
                : item
            ),
          };
        });
      });

      queryClient.setQueryData<ModuleDetailRead>(
        ["module-detail", target.moduleId],
        (previous) => {
          if (previous === undefined) {
            return previous;
          }
          return {
            ...previous,
            practical: null,
          };
        }
      );

      queryClient.removeQueries({
        queryKey: ["practical-teacher", target.practicalId],
        exact: true,
      });
      queryClient.removeQueries({
        queryKey: ["practical-student", target.practicalId],
        exact: true,
      });

      void queryClient.invalidateQueries({ queryKey: ["courses"] });
      void queryClient.invalidateQueries({ queryKey: ["module"] });
      void queryClient.invalidateQueries({
        queryKey: ["module-detail", target.moduleId],
      });
      void queryClient.invalidateQueries({
        queryKey: ["practical-teacher"],
        predicate: (query) => query.queryKey[1] !== target.practicalId,
      });
      void queryClient.invalidateQueries({
        queryKey: ["practical-student"],
        predicate: (query) => query.queryKey[1] !== target.practicalId,
      });
      void queryClient.invalidateQueries({ queryKey: ["group-journal"] });
      void queryClient.invalidateQueries({ queryKey: ["submission-detail"] });
      void queryClient.invalidateQueries({ queryKey: ["submissions-my"] });

      setDeleteTarget(null);
      setDeleteModalError(null);
      setFeedbackBanner({
        type: "success",
        text: `Практичну роботу «${target.title}» видалено. Лекція та тест-допуск модуля збережені.`,
      });
    },
    onError: (err) => {
      setDeleteModalError(
        extractApiErrorMessage(err, "Не вдалося видалити практичну роботу.")
      );
    },
  });

  const isDeleting =
    deleteModuleMutation.isPending || deletePracticalMutation.isPending;

  useEffect(() => {
    if (deleteTarget === null) {
      return;
    }
    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key === "Escape" && !isDeleting) {
        setDeleteTarget(null);
        setDeleteModalError(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [deleteTarget, isDeleting]);

  const openDeleteModal = (target: DeleteTarget): void => {
    setDeleteModalError(null);
    setDeleteTarget(target);
  };

  const closeDeleteModal = (): void => {
    if (isDeleting) {
      return;
    }
    setDeleteTarget(null);
    setDeleteModalError(null);
  };

  const handleConfirmDelete = (): void => {
    if (deleteTarget === null || isDeleting) {
      return;
    }
    setDeleteModalError(null);
    if (deleteTarget.kind === "module") {
      deleteModuleMutation.mutate(deleteTarget);
    } else {
      deletePracticalMutation.mutate(deleteTarget);
    }
  };

  const handleSaveCourse = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (courseTitle.trim().length < 3 || courseDescription.trim().length < 3) {
      setFeedbackBanner({
        type: "error",
        text: "Заповніть назву та опис курсу (щонайменше 3 символи).",
      });
      return;
    }
    updateCourseMutation.mutate({
      title: courseTitle.trim(),
      description: courseDescription.trim(),
    });
  };

  const handleCreateCourse = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (
      newCourseTitle.trim().length < 3 ||
      newCourseDescription.trim().length < 3
    ) {
      setFeedbackBanner({
        type: "error",
        text: "Вкажіть коректну назву та опис нового курсу.",
      });
      return;
    }
    createCourseMutation.mutate({
      slug: newCourseSlug,
      title: newCourseTitle.trim(),
      description: newCourseDescription.trim(),
    });
  };

  const handleCreateModule = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (newModuleTitle.trim().length < 3) {
      setFeedbackBanner({
        type: "error",
        text: "Введіть назву нового модуля (щонайменше 3 символи).",
      });
      return;
    }
    createModuleMutation.mutate({
      order_index: Math.max(1, newModuleOrder),
      title: newModuleTitle.trim(),
      lecture_content:
        newModuleLecture.trim().length > 0
          ? newModuleLecture
          : `# ${newModuleTitle.trim()}`,
    });
  };

  const handleSaveModuleLecture = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (moduleTitle.trim().length < 3) {
      setFeedbackBanner({
        type: "error",
        text: "Назва модуля повинна містити щонайменше 3 символи.",
      });
      return;
    }
    updateModuleMutation.mutate({
      order_index: Math.max(1, moduleOrderIndex),
      title: moduleTitle.trim(),
      lecture_content: moduleLectureContent,
    });
  };

  const handleAddQuizQuestion = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    const cleanedOptions = questionOptions.map((opt) => opt.trim());
    if (questionText.trim().length < 5) {
      setFeedbackBanner({
        type: "error",
        text: "Введіть формулювання тестового питання (мінімум 5 символів).",
      });
      return;
    }
    if (cleanedOptions.some((opt) => opt.length === 0)) {
      setFeedbackBanner({
        type: "error",
        text: "Усі варіанти відповідей повинні бути заповнені.",
      });
      return;
    }
    createQuizQuestionMutation.mutate({
      question_text: questionText.trim(),
      options: cleanedOptions,
      correct_option_index: correctOptionIndex,
    });
  };

  const handleAddVariantDraft = (): void => {
    const nextNumber = variantDrafts.length + 1;
    setVariantDrafts((prev) => [
      ...prev,
      {
        variant_number: nextNumber,
        title: `Варіант ${nextNumber}: Індивідуальне завдання`,
        task_description: `Виконайте практичне завдання згідно з вхідними даними варіанта №${nextNumber}.`,
        parametersJson: JSON.stringify({ variant_number: nextNumber }, null, 2),
      },
    ]);
  };

  const handleRemoveVariantDraft = (index: number): void => {
    setVariantDrafts((prev) =>
      prev
        .filter((_, idx) => idx !== index)
        .map((item, idx) => ({
          ...item,
          variant_number: idx + 1,
        }))
    );
  };

  const handleUpdateVariantDraft = (
    index: number,
    patch: Partial<VariantDraft>
  ): void => {
    setVariantDrafts((prev) =>
      prev.map((item, idx) => (idx === index ? { ...item, ...patch } : item))
    );
  };

  const handleSavePractical = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (practicalTitle.trim().length < 3) {
      setFeedbackBanner({
        type: "error",
        text: "Вкажіть назву практичної роботи.",
      });
      return;
    }
    if (practicalInstructions.trim().length < 5) {
      setFeedbackBanner({
        type: "error",
        text: "Заповніть методичні вказівки до практичної роботи.",
      });
      return;
    }

    const parsedVariants: PracticalVariant[] = [];
    for (let idx = 0; idx < variantDrafts.length; idx += 1) {
      const draft = variantDrafts[idx];
      if (draft === undefined) {
        continue;
      }
      let parsedParams: Record<string, unknown> = {};
      if (draft.parametersJson.trim().length > 0) {
        try {
          const rawParsed: unknown = JSON.parse(draft.parametersJson);
          if (
            typeof rawParsed === "object" &&
            rawParsed !== null &&
            !Array.isArray(rawParsed)
          ) {
            parsedParams = rawParsed as Record<string, unknown>;
          } else {
            setFeedbackBanner({
              type: "error",
              text: `Параметри варіанта №${idx + 1} мають бути JSON-об'єктом {}.`,
            });
            return;
          }
        } catch {
          setFeedbackBanner({
            type: "error",
            text: `Некоректний JSON у параметрах варіанта №${idx + 1}.`,
          });
          return;
        }
      }
      parsedVariants.push({
        variant_number: idx + 1,
        title: draft.title.trim() || `Варіант ${idx + 1}`,
        task_description: draft.task_description.trim(),
        parameters: parsedParams,
      });
    }

    upsertPracticalMutation.mutate({
      title: practicalTitle.trim(),
      instructions: practicalInstructions.trim(),
      format_type: practicalFormat,
      max_score: Math.max(1, practicalMaxScore),
      variants: parsedVariants,
      grading_rules: practicalTeacher?.grading_rules ?? [],
    });
  };

  const insertTextAtLectureCursor = (snippet: string): void => {
    const textarea = lectureTextareaRef.current;
    if (textarea === null) {
      setModuleLectureContent((prev) =>
        prev.endsWith("\n") || prev.length === 0
          ? `${prev}${snippet}`
          : `${prev}\n\n${snippet}`
      );
      return;
    }

    const start = textarea.selectionStart ?? moduleLectureContent.length;
    const end = textarea.selectionEnd ?? start;
    const before = moduleLectureContent.slice(0, start);
    const after = moduleLectureContent.slice(end);
    const leadingPrefix =
      before.length === 0 || before.endsWith("\n\n")
        ? ""
        : before.endsWith("\n")
          ? "\n"
          : "\n\n";
    const trailingSuffix =
      after.length === 0 || after.startsWith("\n\n")
        ? ""
        : after.startsWith("\n")
          ? "\n"
          : "\n\n";

    const nextValue = `${before}${leadingPrefix}${snippet}${trailingSuffix}${after}`;
    const nextCaretPos =
      before.length + leadingPrefix.length + snippet.length;
    setModuleLectureContent(nextValue);

    window.requestAnimationFrame(() => {
      if (lectureTextareaRef.current !== null) {
        lectureTextareaRef.current.focus();
        lectureTextareaRef.current.setSelectionRange(
          nextCaretPos,
          nextCaretPos
        );
      }
    });
  };

  const insertMarkdownSnippet = (snippet: string): void => {
    insertTextAtLectureCursor(snippet);
  };

  const handleMediaFileSelected = (
    event: ChangeEvent<HTMLInputElement>
  ): void => {
    const pickedFile = event.target.files?.[0];
    event.target.value = "";
    if (!pickedFile || activeCourse === null) {
      return;
    }

    const lowerName = pickedFile.name.toLowerCase();
    const isAllowedExt = ALLOWED_MEDIA_IMAGE_EXTENSIONS.some((ext) =>
      lowerName.endsWith(ext)
    );
    if (!isAllowedExt) {
      setFeedbackBanner({
        type: "error",
        text: "Дозволено завантажувати лише растрові зображення: .png, .jpg, .jpeg, .webp, .gif.",
      });
      return;
    }

    if (pickedFile.size === 0) {
      setFeedbackBanner({
        type: "error",
        text: "Обраний файл зображення порожній.",
      });
      return;
    }

    if (pickedFile.size > MAX_MEDIA_UPLOAD_BYTES) {
      setFeedbackBanner({
        type: "error",
        text: "Розмір зображення перевищує максимально допустимі 5 МБ.",
      });
      return;
    }

    uploadCourseMediaMutation.mutate({
      courseId: activeCourse.id,
      file: pickedFile,
    });
  };

  const handleMoveModule = (index: number, direction: -1 | 1): void => {
    if (activeCourse === null || reorderModulesMutation.isPending) {
      return;
    }
    const targetIndex = index + direction;
    const modules = activeCourse.modules;
    if (targetIndex < 0 || targetIndex >= modules.length) {
      return;
    }

    const nextIds = modules.map((item) => item.id);
    const currentId = nextIds[index];
    const swapId = nextIds[targetIndex];
    if (currentId === undefined || swapId === undefined) {
      return;
    }
    nextIds[index] = swapId;
    nextIds[targetIndex] = currentId;

    reorderModulesMutation.mutate({
      courseId: activeCourse.id,
      moduleIds: nextIds,
    });
  };

  const startEditingQuizQuestion = (question: QuizQuestionTeacherRead): void => {
    setEditingQuestionId(question.id);
    setEditQuestionText(question.question_text);
    setEditQuestionOptions([...question.options]);
    setEditCorrectOptionIndex(question.correct_option_index);
  };

  const cancelEditingQuizQuestion = (): void => {
    setEditingQuestionId(null);
  };

  const handleAddEditOption = (): void => {
    setEditQuestionOptions((prev) => [...prev, ""]);
  };

  const handleRemoveEditOption = (optionIndex: number): void => {
    setEditQuestionOptions((prev) => {
      if (prev.length <= 2) {
        return prev;
      }
      const next = prev.filter((_, idx) => idx !== optionIndex);
      setEditCorrectOptionIndex((currentCorrect) => {
        if (currentCorrect === optionIndex) {
          return 0;
        }
        if (currentCorrect > optionIndex) {
          return currentCorrect - 1;
        }
        return Math.min(currentCorrect, next.length - 1);
      });
      return next;
    });
  };

  const handleSaveEditedQuizQuestion = (
    event: FormEvent<HTMLFormElement>,
    questionId: string
  ): void => {
    event.preventDefault();
    const trimmedText = editQuestionText.trim();
    const cleanedOptions = editQuestionOptions.map((opt) => opt.trim());
    if (trimmedText.length < 3) {
      setFeedbackBanner({
        type: "error",
        text: "Введіть формулювання тестового питання (мінімум 3 символи).",
      });
      return;
    }
    if (cleanedOptions.length < 2 || cleanedOptions.some((opt) => opt.length === 0)) {
      setFeedbackBanner({
        type: "error",
        text: "Необхідно вказати щонайменше 2 непорожні варіанти відповіді.",
      });
      return;
    }
    if (
      editCorrectOptionIndex < 0 ||
      editCorrectOptionIndex >= cleanedOptions.length
    ) {
      setFeedbackBanner({
        type: "error",
        text: "Оберіть коректну правильну відповідь зі списку варіантів.",
      });
      return;
    }

    updateQuizQuestionMutation.mutate({
      questionId,
      payload: {
        question_text: trimmedText,
        options: cleanedOptions,
        correct_option_index: editCorrectOptionIndex,
      },
    });
  };

  const handleTemplateFileSelected = (
    event: ChangeEvent<HTMLInputElement>
  ): void => {
    const pickedFile = event.target.files?.[0];
    event.target.value = "";
    if (!pickedFile || activePracticalId === null) {
      return;
    }
    if (pickedFile.size === 0) {
      setFeedbackBanner({
        type: "error",
        text: "Обраний файл-заготовка порожній.",
      });
      return;
    }
    uploadPracticalTemplateMutation.mutate({
      practicalId: activePracticalId,
      file: pickedFile,
    });
  };

  const handleDownloadPracticalTemplate = async (): Promise<void> => {
    if (activePracticalId === null) {
      return;
    }
    setIsDownloadingTemplate(true);
    try {
      const response = await apiClient.get<Blob>(
        `/practicals/${activePracticalId}/template`,
        {
          responseType: "blob",
        }
      );
      const fallbackFilename =
        practicalTeacher?.template_file_name ?? "template.bin";
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
        "Не вдалося завантажити файл-заготовку."
      );
      setFeedbackBanner({
        type: "error",
        text: errorMessage,
      });
    } finally {
      setIsDownloadingTemplate(false);
    }
  };

  if (isLoadingCourses) {
    return (
      <div className="flex min-h-[55vh] flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8">
        <Loader2 className="h-9 w-9 animate-spin text-blue-600" />
        <p className="mt-3 text-sm font-medium text-slate-700">
          Завантаження конструктора навчальних курсів та модулів...
        </p>
      </div>
    );
  }

  if (isCoursesError) {
    return (
      <div className="mx-auto max-w-2xl rounded-2xl border border-rose-200 bg-white p-6 text-center shadow-xs">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose-600">
          <AlertCircle className="h-6 w-6" />
        </div>
        <h2 className="mt-4 text-lg font-bold text-slate-900">
          Не вдалося завантажити навчальні курси
        </h2>
        <p className="mt-1.5 text-sm text-slate-600">
          {extractApiErrorMessage(
            coursesError,
            "Сталася помилка під час звернення до сервера."
          )}
        </p>
        <button
          type="button"
          onClick={() => void refetchCourses()}
          className="mt-5 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
        >
          <RefreshCw className="h-4 w-4" />
          Спробувати знову
        </button>
      </div>
    );
  }

  const courseList = courses ?? [];

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Шапка конструктора курсів */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div className="space-y-1.5">
            <div className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
              <BookOpenCheck className="h-3.5 w-3.5" />
              Кабінет викладача • Конструктор навчального контенту
            </div>
            <h1 className="text-xl font-bold text-slate-900 sm:text-2xl">
              Курси, лекції, тести-допуски та індивідуальні варіанти
            </h1>
            <p className="max-w-3xl text-sm text-slate-600">
              Керуйте структурою електронних посібників із дисциплін{" "}
              <span className="font-semibold text-slate-800">
                Word, Excel, Access та HTML
              </span>
              : редагуйте Markdown-лекції, формуйте банк питань тесту-допуску
              (поріг ≥ 70%) та налаштовуйте варіанти практичних робіт.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            {missingCourseSlugs.length > 0 && (
              <button
                type="button"
                onClick={() => {
                  const firstMissing = missingCourseSlugs[0];
                  if (firstMissing !== undefined) {
                    setNewCourseSlug(firstMissing);
                  }
                  setIsCreatingCourse((prev) => !prev);
                }}
                className="inline-flex items-center gap-1.5 rounded-xl border border-blue-200 bg-blue-50 px-3.5 py-2 text-xs font-semibold text-blue-700 hover:bg-blue-100"
              >
                <Plus className="h-4 w-4" />
                <span>Новий курс</span>
              </button>
            )}

            <Link
              to={
                activePracticalId !== null
                  ? `/teacher/rules?practicalId=${activePracticalId}`
                  : "/teacher/rules"
              }
              className="inline-flex items-center gap-1.5 rounded-xl bg-slate-900 px-4 py-2.5 text-xs font-semibold text-white shadow-2xs hover:bg-slate-800"
            >
              <SlidersHorizontal className="h-4 w-4" />
              <span>Редактор правил перевірки</span>
            </Link>
          </div>
        </div>

        {/* Повідомлення про результат збереження */}
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

        {/* Форма створення нового курсу (якщо є вільні дисципліни) */}
        {isCreatingCourse && missingCourseSlugs.length > 0 && (
          <form
            onSubmit={handleCreateCourse}
            className="mt-5 rounded-2xl border border-blue-200 bg-blue-50/40 p-4 sm:p-5"
          >
            <h3 className="text-sm font-bold text-slate-900">
              Створення нового навчального курсу
            </h3>
            <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700">
                  Дисципліна (slug)
                </label>
                <select
                  value={newCourseSlug}
                  onChange={(e) =>
                    setNewCourseSlug(e.target.value as CourseSlug)
                  }
                  className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-xs font-semibold text-slate-900"
                >
                  {missingCourseSlugs.map((slug) => (
                    <option key={slug} value={slug}>
                      {DISCIPLINE_META[slug].label} ({slug})
                    </option>
                  ))}
                </select>
              </div>
              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold text-slate-700">
                  Назва курсу
                </label>
                <input
                  type="text"
                  required
                  value={newCourseTitle}
                  onChange={(e) => setNewCourseTitle(e.target.value)}
                  placeholder="Напр.: Microsoft Word: Оформлення текстових документів"
                  className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900"
                />
              </div>
              <div className="sm:col-span-3">
                <label className="block text-xs font-semibold text-slate-700">
                  Анотація курсу
                </label>
                <textarea
                  rows={2}
                  required
                  value={newCourseDescription}
                  onChange={(e) => setNewCourseDescription(e.target.value)}
                  placeholder="Короткий опис навчальної програми..."
                  className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900"
                />
              </div>
            </div>
            <div className="mt-3 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsCreatingCourse(false)}
                className="rounded-xl border border-slate-300 bg-white px-3.5 py-1.5 text-xs font-semibold text-slate-700"
              >
                Скасувати
              </button>
              <button
                type="submit"
                disabled={createCourseMutation.isPending}
                className="inline-flex items-center gap-1.5 rounded-xl bg-blue-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
              >
                <Save className="h-3.5 w-3.5" />
                <span>Створити курс</span>
              </button>
            </div>
          </form>
        )}

        {/* Вкладки вибору курсу */}
        <div
          className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4"
          role="tablist"
          aria-label="Навчальні курси"
        >
          {courseList.map((course) => {
            const meta = DISCIPLINE_META[course.slug];
            const Icon = meta.icon;
            const isSelected = activeCourse?.id === course.id;

            return (
              <button
                key={course.id}
                type="button"
                role="tab"
                aria-selected={isSelected}
                onClick={() => setSelectedCourseId(course.id)}
                className={`flex items-start gap-3 rounded-2xl border p-4 text-left transition-all ${
                  isSelected
                    ? "border-blue-600 bg-blue-50/50 shadow-xs ring-1 ring-blue-600"
                    : "border-slate-200 bg-slate-50/60 hover:border-blue-300 hover:bg-white"
                }`}
              >
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-slate-200 bg-white text-blue-600">
                  <Icon className="h-5 w-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <span
                    className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-bold ${meta.badgeClass}`}
                  >
                    {meta.shortLabel}
                  </span>
                  <h2 className="mt-1.5 truncate text-sm font-bold text-slate-900">
                    {course.title}
                  </h2>
                  <p className="mt-0.5 text-xs text-slate-500">
                    Модулів: {course.modules.length}
                  </p>
                </div>
              </button>
            );
          })}
        </div>
      </section>

      {activeCourse !== null && (
        <>
          {/* Редагування заголовка та опису обраного курсу */}
          <form
            onSubmit={handleSaveCourse}
            className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs"
          >
            <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
              <div className="grid flex-1 grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label
                    htmlFor="course-title-input"
                    className="block text-xs font-semibold text-slate-700"
                  >
                    Назва обраного курсу ({DISCIPLINE_META[activeCourse.slug].label})
                  </label>
                  <input
                    id="course-title-input"
                    type="text"
                    value={courseTitle}
                    onChange={(e) => setCourseTitle(e.target.value)}
                    className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs font-semibold text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
                  />
                </div>
                <div>
                  <label
                    htmlFor="course-desc-input"
                    className="block text-xs font-semibold text-slate-700"
                  >
                    Опис курсу для студентів
                  </label>
                  <input
                    id="course-desc-input"
                    type="text"
                    value={courseDescription}
                    onChange={(e) => setCourseDescription(e.target.value)}
                    className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={updateCourseMutation.isPending}
                className="inline-flex shrink-0 items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-800 shadow-2xs hover:bg-slate-50 disabled:opacity-60"
              >
                <Save className="h-3.5 w-3.5 text-blue-600" />
                <span>Оновити паспорт курсу</span>
              </button>
            </div>
          </form>

          {/* Основна робоча область: Список модулів (ліворуч) + Редактор контенту (праворуч) */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
            {/* Ліва панель: Модулі курсу */}
            <aside className="space-y-3 lg:col-span-4">
              <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-4 shadow-xs">
                <div>
                  <h2 className="text-sm font-bold text-slate-900">
                    Модулі курсу ({activeCourse.modules.length})
                  </h2>
                  <p className="text-xs text-slate-500">
                    Лекція + тест + практична
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setIsAddingModule((prev) => !prev)}
                  className="inline-flex items-center gap-1 rounded-xl bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-700"
                >
                  <Plus className="h-3.5 w-3.5" />
                  <span>Додати модуль</span>
                </button>
              </div>

              {isAddingModule && (
                <form
                  onSubmit={handleCreateModule}
                  className="rounded-2xl border border-blue-200 bg-blue-50/50 p-4 shadow-xs space-y-3"
                >
                  <h3 className="text-xs font-bold uppercase tracking-wider text-blue-900">
                    Новий навчальний модуль
                  </h3>
                  <div className="grid grid-cols-3 gap-2">
                    <div>
                      <label className="block text-[11px] font-semibold text-slate-700">
                        Порядок №
                      </label>
                      <input
                        type="number"
                        min={1}
                        value={newModuleOrder}
                        onChange={(e) =>
                          setNewModuleOrder(Number(e.target.value) || 1)
                        }
                        className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs text-slate-900"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-[11px] font-semibold text-slate-700">
                        Назва теми модуля
                      </label>
                      <input
                        type="text"
                        required
                        value={newModuleTitle}
                        onChange={(e) => setNewModuleTitle(e.target.value)}
                        placeholder="Назва теми..."
                        className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs text-slate-900"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-700">
                      Початковий текст лекції (Markdown)
                    </label>
                    <textarea
                      rows={3}
                      value={newModuleLecture}
                      onChange={(e) => setNewModuleLecture(e.target.value)}
                      className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2 font-mono text-xs text-slate-900"
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <button
                      type="button"
                      onClick={() => setIsAddingModule(false)}
                      className="rounded-lg border border-slate-300 bg-white px-3 py-1 text-xs font-semibold text-slate-700"
                    >
                      Скасувати
                    </button>
                    <button
                      type="submit"
                      disabled={createModuleMutation.isPending}
                      className="rounded-lg bg-blue-600 px-3 py-1 text-xs font-semibold text-white hover:bg-blue-700"
                    >
                      Створити
                    </button>
                  </div>
                </form>
              )}

              <div className="space-y-2.5">
                {activeCourse.modules.map((mod, modIndex) => {
                  const isSelected = selectedModuleId === mod.id;
                  const isFirstModule = modIndex === 0;
                  const isLastModule =
                    modIndex === activeCourse.modules.length - 1;
                  return (
                    <div
                      key={mod.id}
                      className={`group relative rounded-2xl border transition-all ${
                        isSelected
                          ? "border-blue-600 bg-blue-50/40 shadow-xs ring-1 ring-blue-600"
                          : "border-slate-200 bg-white hover:border-blue-300"
                      }`}
                    >
                      <button
                        type="button"
                        onClick={() => setSelectedModuleId(mod.id)}
                        className="w-full p-4 pr-24 text-left"
                      >
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="inline-flex items-center rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-bold text-slate-700">
                            Тема №{mod.order_index}
                          </span>
                          {mod.practical_format !== null ? (
                            <span className="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 font-mono text-[10px] font-bold uppercase text-emerald-700">
                              .{mod.practical_format}
                            </span>
                          ) : (
                            <span className="rounded-full border border-amber-200 bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-800">
                              Без практичної
                            </span>
                          )}
                        </div>
                        <h3 className="mt-2 text-sm font-bold text-slate-900">
                          {mod.title}
                        </h3>
                        {mod.practical_id !== null &&
                          mod.practical_needs_rules_review && (
                            <span
                              title="Потребує перевірки правил / ручного дооцінювання"
                              className="mt-1.5 inline-flex items-center gap-1 rounded-full border border-amber-300 bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-800"
                            >
                              <AlertTriangle className="h-3 w-3 shrink-0 text-amber-600" />
                              <span>
                                Потребує перевірки правил / ручного
                                дооцінювання
                              </span>
                            </span>
                          )}
                      </button>

                      <div className="absolute right-2 top-3 flex items-center gap-0.5">
                        <button
                          type="button"
                          disabled={
                            isFirstModule || reorderModulesMutation.isPending
                          }
                          onClick={() => handleMoveModule(modIndex, -1)}
                          title="Перемістити вище"
                          aria-label={`Перемістити модуль «${mod.title}» вище`}
                          className="inline-flex h-7 w-7 items-center justify-center rounded-lg border border-transparent text-slate-400 transition-colors hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 disabled:cursor-not-allowed disabled:opacity-30"
                        >
                          <ArrowUp className="h-3.5 w-3.5" />
                        </button>
                        <button
                          type="button"
                          disabled={
                            isLastModule || reorderModulesMutation.isPending
                          }
                          onClick={() => handleMoveModule(modIndex, 1)}
                          title="Перемістити нижче"
                          aria-label={`Перемістити модуль «${mod.title}» нижче`}
                          className="inline-flex h-7 w-7 items-center justify-center rounded-lg border border-transparent text-slate-400 transition-colors hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 disabled:cursor-not-allowed disabled:opacity-30"
                        >
                          <ArrowDown className="h-3.5 w-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={() =>
                            openDeleteModal({
                              kind: "module",
                              courseId: activeCourse.id,
                              moduleId: mod.id,
                              orderIndex: mod.order_index,
                              title: mod.title,
                              practicalId: mod.practical_id,
                              hasPractical: mod.practical_id !== null,
                            })
                          }
                          title="Видалити модуль"
                          aria-label={`Видалити модуль «${mod.title}»`}
                          className="inline-flex h-7 w-7 items-center justify-center rounded-lg border border-transparent text-slate-400 transition-colors hover:border-rose-200 hover:bg-rose-50 hover:text-rose-600 focus:border-rose-300 focus:bg-rose-50 focus:text-rose-600 focus:outline-none"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </aside>

            {/* Права панель: Редактор лекції, тесту-допуску та практичної роботи */}
            <div className="lg:col-span-8">
              {selectedModuleId === null ? (
                <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-xs">
                  <Layers className="mx-auto h-10 w-10 text-slate-400" />
                  <h3 className="mt-3 text-base font-bold text-slate-900">
                    Оберіть або створіть навчальний модуль
                  </h3>
                  <p className="mt-1 text-xs text-slate-500">
                    Для редагування лекції, тестових питань та практичної роботи
                    оберіть тему у списку ліворуч.
                  </p>
                </div>
              ) : isLoadingModule ? (
                <div className="flex min-h-[40vh] flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8">
                  <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                  <p className="mt-2.5 text-xs font-medium text-slate-600">
                    Завантаження матеріалів модуля...
                  </p>
                </div>
              ) : (
                <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs">
                  {/* Перемикач вкладок модуля */}
                  <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-slate-50/80 px-5 py-3.5">
                    <div
                      className="inline-flex flex-wrap items-center gap-1.5 rounded-xl border border-slate-200 bg-white p-1"
                      role="tablist"
                    >
                      <button
                        type="button"
                        role="tab"
                        aria-selected={activeTab === "lecture"}
                        onClick={() => setActiveTab("lecture")}
                        className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                          activeTab === "lecture"
                            ? "bg-blue-600 text-white"
                            : "text-slate-600 hover:bg-slate-100"
                        }`}
                      >
                        <BookOpen className="h-3.5 w-3.5" />
                        <span>1. Лекція (Markdown)</span>
                      </button>

                      <button
                        type="button"
                        role="tab"
                        aria-selected={activeTab === "quiz"}
                        onClick={() => setActiveTab("quiz")}
                        className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                          activeTab === "quiz"
                            ? "bg-blue-600 text-white"
                            : "text-slate-600 hover:bg-slate-100"
                        }`}
                      >
                        <HelpCircle className="h-3.5 w-3.5" />
                        <span>
                          2. Тест-допуск ({quizQuestions?.length ?? 0})
                        </span>
                      </button>

                      <button
                        type="button"
                        role="tab"
                        aria-selected={activeTab === "practical"}
                        onClick={() => setActiveTab("practical")}
                        className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                          activeTab === "practical"
                            ? "bg-blue-600 text-white"
                            : "text-slate-600 hover:bg-slate-100"
                        }`}
                      >
                        <Wrench className="h-3.5 w-3.5" />
                        <span>
                          3. Практична та варіанти ({variantDrafts.length})
                        </span>
                      </button>
                    </div>

                    <div className="flex flex-wrap items-center gap-2">
                      {activeCourse !== null && selectedModuleId !== null && (
                        <Link
                          to={`/teacher/courses/${activeCourse.id}/modules/${selectedModuleId}/preview`}
                          className="inline-flex items-center gap-1.5 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-800 transition-colors hover:bg-emerald-100"
                          title="Відкрити цей модуль у режимі попереднього перегляду очима студента"
                        >
                          <Eye className="h-3.5 w-3.5 text-emerald-600" />
                          <span>Очима студента</span>
                        </Link>
                      )}
                      {activePracticalId !== null && (
                        <>
                          {practicalTeacher?.needs_rules_review === true && (
                            <span
                              title="Стартові правила потребують перевірки викладачем або додаткової ручної оцінки"
                              className="inline-flex items-center gap-1 rounded-full border border-amber-300 bg-amber-50 px-2.5 py-1 text-[11px] font-semibold text-amber-800"
                            >
                              <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-amber-600" />
                              <span>
                                Потребує перевірки правил / ручного дооцінювання
                              </span>
                            </span>
                          )}
                          <Link
                            to={`/teacher/rules?practicalId=${activePracticalId}`}
                            className="inline-flex items-center gap-1.5 rounded-xl border border-indigo-200 bg-indigo-50 px-3 py-1.5 text-xs font-semibold text-indigo-700 hover:bg-indigo-100"
                          >
                            <SlidersHorizontal className="h-3.5 w-3.5" />
                            <span>
                              Правила автоперевірки (
                              {practicalTeacher?.grading_rules.length ?? 0})
                            </span>
                          </Link>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Вкладка 1: Редактор лекції */}
                  {activeTab === "lecture" && (
                    <form
                      onSubmit={handleSaveModuleLecture}
                      className="space-y-5 p-5 sm:p-6"
                    >
                      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
                        <div>
                          <label className="block text-xs font-semibold text-slate-700">
                            Номер теми
                          </label>
                          <input
                            type="number"
                            min={1}
                            value={moduleOrderIndex}
                            onChange={(e) =>
                              setModuleOrderIndex(Number(e.target.value) || 1)
                            }
                            className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
                          />
                        </div>
                        <div className="sm:col-span-3">
                          <label className="block text-xs font-semibold text-slate-700">
                            Заголовок модуля (теми)
                          </label>
                          <input
                            type="text"
                            required
                            value={moduleTitle}
                            onChange={(e) => setModuleTitle(e.target.value)}
                            className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs font-semibold text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
                          />
                        </div>
                      </div>

                      {/* Панель форматування Markdown та перемикач прев'ю */}
                      <div className="space-y-2">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="flex flex-wrap items-center gap-1.5">
                            <span className="text-xs font-semibold text-slate-700">
                              Текст лекції (Markdown):
                            </span>
                            <button
                              type="button"
                              onClick={() =>
                                insertMarkdownSnippet("## Новий розділ лекції\n")
                              }
                              className="rounded-lg border border-slate-200 bg-slate-50 px-2 py-1 text-[11px] font-semibold text-slate-700 hover:bg-slate-100"
                            >
                              + Заголовок H2
                            </button>
                            <button
                              type="button"
                              onClick={() =>
                                insertMarkdownSnippet(
                                  "- Перший пункт\n- Другий пункт"
                                )
                              }
                              className="rounded-lg border border-slate-200 bg-slate-50 px-2 py-1 text-[11px] font-semibold text-slate-700 hover:bg-slate-100"
                            >
                              + Список
                            </button>
                            <button
                              type="button"
                              onClick={() =>
                                insertMarkdownSnippet(
                                  "**Важливе визначення** — пояснення терміна."
                                )
                              }
                              className="rounded-lg border border-slate-200 bg-slate-50 px-2 py-1 text-[11px] font-semibold text-slate-700 hover:bg-slate-100"
                            >
                              + Визначення
                            </button>
                            <input
                              ref={mediaFileInputRef}
                              type="file"
                              accept=".png,.jpg,.jpeg,.webp,.gif,image/png,image/jpeg,image/webp,image/gif"
                              onChange={handleMediaFileSelected}
                              className="sr-only"
                            />
                            <button
                              type="button"
                              disabled={uploadCourseMediaMutation.isPending}
                              onClick={() => mediaFileInputRef.current?.click()}
                              title="Завантажити ілюстрацію (PNG, JPG, WebP, GIF до 5 МБ)"
                              className="inline-flex items-center gap-1 rounded-lg border border-blue-200 bg-blue-50 px-2.5 py-1 text-[11px] font-semibold text-blue-700 hover:bg-blue-100 disabled:opacity-60"
                            >
                              {uploadCourseMediaMutation.isPending ? (
                                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                              ) : (
                                <ImagePlus className="h-3.5 w-3.5" />
                              )}
                              <span>
                                {uploadCourseMediaMutation.isPending
                                  ? "Завантаження..."
                                  : "Вставити зображення"}
                              </span>
                            </button>
                          </div>

                          <button
                            type="button"
                            onClick={() =>
                              setShowLecturePreview((prev) => !prev)
                            }
                            className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                          >
                            {showLecturePreview ? (
                              <>
                                <FileEdit className="h-3.5 w-3.5 text-blue-600" />
                                <span>Лише редактор</span>
                              </>
                            ) : (
                              <>
                                <Eye className="h-3.5 w-3.5 text-blue-600" />
                                <span>Показати прев&apos;ю</span>
                              </>
                            )}
                          </button>
                        </div>

                        <div
                          className={`grid grid-cols-1 gap-4 ${
                            showLecturePreview ? "lg:grid-cols-2" : ""
                          }`}
                        >
                          <textarea
                            ref={lectureTextareaRef}
                            rows={16}
                            value={moduleLectureContent}
                            onChange={(e) =>
                              setModuleLectureContent(e.target.value)
                            }
                            placeholder="# Заголовок лекції..."
                            className="w-full rounded-xl border border-slate-200 bg-slate-900 p-4 font-mono text-xs leading-relaxed text-slate-100 focus:border-blue-500 focus:outline-none"
                          />

                          {showLecturePreview && (
                            <div className="max-h-[460px] overflow-y-auto rounded-xl border border-slate-200 bg-white p-4">
                              <div className="mb-2.5 flex items-center justify-between border-b border-slate-200 pb-2">
                                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                                  Живе прев&apos;ю для студента (1-в-1)
                                </span>
                                <Eye className="h-3.5 w-3.5 text-slate-400" />
                              </div>
                              <MarkdownRenderer
                                content={moduleLectureContent}
                                compact
                                emptyFallback="Текст лекції порожній. Введіть Markdown-розмітку ліворуч."
                              />
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center justify-end border-t border-slate-100 pt-4">
                        <button
                          type="submit"
                          disabled={updateModuleMutation.isPending}
                          className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-xs font-semibold text-white shadow-2xs hover:bg-blue-700 disabled:opacity-60"
                        >
                          <Save className="h-4 w-4" />
                          <span>
                            {updateModuleMutation.isPending
                              ? "Збереження..."
                              : "Зберегти лекцію та тему"}
                          </span>
                        </button>
                      </div>
                    </form>
                  )}

                  {/* Вкладка 2: Питання тесту-допуску */}
                  {activeTab === "quiz" && (
                    <div className="space-y-6 p-5 sm:p-6">
                      <div className="rounded-xl border border-blue-200 bg-blue-50/60 p-4 text-xs text-blue-950">
                        <p className="font-bold">
                          Правило допуску до практичної роботи (FR-2):
                        </p>
                        <p className="mt-0.5 text-blue-800">
                          Студент повинен надати щонайменше{" "}
                          <span className="font-bold">70% правильних відповідей</span>{" "}
                          на ці тестові питання, щоб система розблокувала
                          індивідуальний варіант та форму здачі практичної роботи.
                        </p>
                      </div>

                      {/* Список наявних питань */}
                      {isLoadingQuizQuestions ? (
                        <div className="flex items-center justify-center py-8">
                          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
                        </div>
                      ) : (quizQuestions ?? []).length === 0 ? (
                        <div className="rounded-xl border border-dashed border-slate-200 p-6 text-center text-xs text-slate-500">
                          У цьому модулі ще немає тестових питань. Додайте
                          перше питання за допомогою форми нижче.
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {(quizQuestions ?? []).map((q, qIdx) => {
                            const isEditingThisQuestion =
                              editingQuestionId === q.id;
                            return (
                              <article
                                key={q.id}
                                className={`rounded-xl border p-4 ${
                                  isEditingThisQuestion
                                    ? "border-blue-300 bg-blue-50/40"
                                    : "border-slate-200 bg-slate-50/50"
                                }`}
                              >
                                {isEditingThisQuestion ? (
                                  <form
                                    onSubmit={(event) =>
                                      handleSaveEditedQuizQuestion(event, q.id)
                                    }
                                    className="space-y-3.5"
                                  >
                                    <div className="flex items-center justify-between gap-2">
                                      <span className="text-xs font-bold text-blue-800">
                                        Редагування питання №{qIdx + 1}
                                      </span>
                                      <button
                                        type="button"
                                        onClick={cancelEditingQuizQuestion}
                                        className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                                      >
                                        <X className="h-3.5 w-3.5" />
                                        <span>Скасувати</span>
                                      </button>
                                    </div>

                                    <div>
                                      <label className="block text-xs font-semibold text-slate-700">
                                        Текст питання
                                      </label>
                                      <input
                                        type="text"
                                        required
                                        value={editQuestionText}
                                        onChange={(e) =>
                                          setEditQuestionText(e.target.value)
                                        }
                                        className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-xs text-slate-900 focus:border-blue-500 focus:outline-none"
                                      />
                                    </div>

                                    <div className="space-y-2">
                                      <div className="flex items-center justify-between gap-2">
                                        <label className="block text-xs font-semibold text-slate-700">
                                          Варіанти відповідей (позначте правильний)
                                        </label>
                                        <button
                                          type="button"
                                          onClick={handleAddEditOption}
                                          className="inline-flex items-center gap-1 rounded-lg border border-blue-200 bg-white px-2 py-1 text-[11px] font-semibold text-blue-700 hover:bg-blue-50"
                                        >
                                          <Plus className="h-3 w-3" />
                                          <span>Додати варіант</span>
                                        </button>
                                      </div>

                                      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                                        {editQuestionOptions.map(
                                          (optionValue, optIdx) => (
                                            <div
                                              key={optIdx}
                                              className={`flex items-center gap-2 rounded-xl border p-2 ${
                                                editCorrectOptionIndex ===
                                                optIdx
                                                  ? "border-emerald-400 bg-emerald-50/70"
                                                  : "border-slate-200 bg-white"
                                              }`}
                                            >
                                              <input
                                                type="radio"
                                                name={`edit-correct-${q.id}`}
                                                checked={
                                                  editCorrectOptionIndex ===
                                                  optIdx
                                                }
                                                onChange={() =>
                                                  setEditCorrectOptionIndex(
                                                    optIdx
                                                  )
                                                }
                                                className="h-4 w-4 accent-emerald-600"
                                                title="Позначити як правильну відповідь"
                                              />
                                              <input
                                                type="text"
                                                required
                                                value={optionValue}
                                                onChange={(e) => {
                                                  const next = [
                                                    ...editQuestionOptions,
                                                  ];
                                                  next[optIdx] = e.target.value;
                                                  setEditQuestionOptions(next);
                                                }}
                                                placeholder={`Варіант №${optIdx + 1}`}
                                                className="w-full bg-transparent text-xs text-slate-900 focus:outline-none"
                                              />
                                              {editQuestionOptions.length >
                                                2 && (
                                                <button
                                                  type="button"
                                                  onClick={() =>
                                                    handleRemoveEditOption(
                                                      optIdx
                                                    )
                                                  }
                                                  title="Видалити варіант"
                                                  className="rounded p-1 text-slate-400 hover:bg-rose-50 hover:text-rose-600"
                                                >
                                                  <X className="h-3.5 w-3.5" />
                                                </button>
                                              )}
                                            </div>
                                          )
                                        )}
                                      </div>
                                    </div>

                                    <div className="flex justify-end gap-2">
                                      <button
                                        type="button"
                                        onClick={cancelEditingQuizQuestion}
                                        className="rounded-xl border border-slate-300 bg-white px-3.5 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                                      >
                                        Скасувати
                                      </button>
                                      <button
                                        type="submit"
                                        disabled={
                                          updateQuizQuestionMutation.isPending
                                        }
                                        className="inline-flex items-center gap-1.5 rounded-xl bg-blue-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
                                      >
                                        <Save className="h-3.5 w-3.5" />
                                        <span>
                                          {updateQuizQuestionMutation.isPending
                                            ? "Збереження..."
                                            : "Зберегти зміни"}
                                        </span>
                                      </button>
                                    </div>
                                  </form>
                                ) : (
                                  <>
                                    <div className="flex items-start justify-between gap-3">
                                      <h4 className="text-sm font-bold text-slate-900">
                                        <span className="mr-1.5 text-blue-600">
                                          Питання №{qIdx + 1}.
                                        </span>
                                        {q.question_text}
                                      </h4>
                                      <div className="flex shrink-0 items-center gap-1.5">
                                        <button
                                          type="button"
                                          onClick={() =>
                                            startEditingQuizQuestion(q)
                                          }
                                          className="inline-flex items-center gap-1 rounded-lg border border-blue-200 bg-white px-2.5 py-1 text-xs font-semibold text-blue-700 hover:bg-blue-50"
                                          title="Редагувати питання"
                                        >
                                          <Pencil className="h-3.5 w-3.5" />
                                          <span>Редагувати</span>
                                        </button>
                                        <button
                                          type="button"
                                          disabled={
                                            deleteQuizQuestionMutation.isPending
                                          }
                                          onClick={() =>
                                            deleteQuizQuestionMutation.mutate(
                                              q.id
                                            )
                                          }
                                          className="inline-flex items-center gap-1 rounded-lg border border-rose-200 bg-white px-2.5 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-50"
                                          title="Видалити питання"
                                        >
                                          <Trash2 className="h-3.5 w-3.5" />
                                          <span>Видалити</span>
                                        </button>
                                      </div>
                                    </div>

                                    <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
                                      {q.options.map((opt, optIdx) => {
                                        const isCorrect =
                                          optIdx === q.correct_option_index;
                                        return (
                                          <div
                                            key={optIdx}
                                            className={`flex items-center justify-between rounded-lg border px-3 py-2 text-xs ${
                                              isCorrect
                                                ? "border-emerald-300 bg-emerald-50 font-bold text-emerald-950"
                                                : "border-slate-200 bg-white text-slate-700"
                                            }`}
                                          >
                                            <span>
                                              {optIdx + 1}. {opt}
                                            </span>
                                            {isCorrect && (
                                              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
                                                <CheckCircle2 className="h-3 w-3" />
                                                Правильна
                                              </span>
                                            )}
                                          </div>
                                        );
                                      })}
                                    </div>
                                  </>
                                )}
                              </article>
                            );
                          })}
                        </div>
                      )}

                      {/* Форма додавання нового питання */}
                      <form
                        onSubmit={handleAddQuizQuestion}
                        className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 sm:p-5 space-y-4"
                      >
                        <h3 className="text-sm font-bold text-slate-900">
                          Додати нове питання до тесту-допуску
                        </h3>

                        <div>
                          <label className="block text-xs font-semibold text-slate-700">
                            Текст питання
                          </label>
                          <input
                            type="text"
                            required
                            value={questionText}
                            onChange={(e) => setQuestionText(e.target.value)}
                            placeholder="Напр.: Яка функція Excel обчислює суму діапазону комірок?"
                            className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-xs text-slate-900 focus:border-blue-500 focus:outline-none"
                          />
                        </div>

                        <div className="space-y-2">
                          <label className="block text-xs font-semibold text-slate-700">
                            Варіанти відповідей (позначте правильний варіант)
                          </label>
                          <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                            {questionOptions.map((optionValue, idx) => (
                              <div
                                key={idx}
                                className={`flex items-center gap-2 rounded-xl border p-2 ${
                                  correctOptionIndex === idx
                                    ? "border-emerald-400 bg-emerald-50/60"
                                    : "border-slate-200 bg-white"
                                }`}
                              >
                                <input
                                  type="radio"
                                  name="correctOptionIndex"
                                  checked={correctOptionIndex === idx}
                                  onChange={() => setCorrectOptionIndex(idx)}
                                  className="h-4 w-4 accent-emerald-600"
                                  title="Позначити як правильну відповідь"
                                />
                                <input
                                  type="text"
                                  required
                                  value={optionValue}
                                  onChange={(e) => {
                                    const next = [...questionOptions];
                                    next[idx] = e.target.value;
                                    setQuestionOptions(next);
                                  }}
                                  placeholder={`Варіант відповіді №${idx + 1}`}
                                  className="w-full bg-transparent text-xs text-slate-900 focus:outline-none"
                                />
                              </div>
                            ))}
                          </div>
                        </div>

                        <div className="flex justify-end">
                          <button
                            type="submit"
                            disabled={createQuizQuestionMutation.isPending}
                            className="inline-flex items-center gap-1.5 rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
                          >
                            <Plus className="h-4 w-4" />
                            <span>Додати питання в тест</span>
                          </button>
                        </div>
                      </form>
                    </div>
                  )}

                  {/* Вкладка 3: Практична робота та індивідуальні варіанти */}
                  {activeTab === "practical" && (
                    <form
                      onSubmit={handleSavePractical}
                      className="space-y-6 p-5 sm:p-6"
                    >
                      {isLoadingPractical ? (
                        <div className="flex items-center justify-center py-8">
                          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
                        </div>
                      ) : (
                        <>
                          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                            <div className="sm:col-span-2">
                              <label className="block text-xs font-semibold text-slate-700">
                                Назва практичної роботи
                              </label>
                              <input
                                type="text"
                                required
                                value={practicalTitle}
                                onChange={(e) =>
                                  setPracticalTitle(e.target.value)
                                }
                                className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs font-semibold text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
                              />
                            </div>

                            <div>
                              <label className="block text-xs font-semibold text-slate-700">
                                Максимальний бал
                              </label>
                              <input
                                type="number"
                                step="0.5"
                                min={1}
                                max={100}
                                value={practicalMaxScore}
                                onChange={(e) =>
                                  setPracticalMaxScore(
                                    Number(e.target.value) || 12
                                  )
                                }
                                className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs font-semibold text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
                              />
                              <p className="mt-1 text-[11px] text-slate-500">
                                12-бальна шкала: до 10 б. автоперевірка + до 2 б.
                                творче завдання
                              </p>
                            </div>

                            <div>
                              <label className="block text-xs font-semibold text-slate-700">
                                Цільовий формат автоперевірки
                              </label>
                              <select
                                value={practicalFormat}
                                onChange={(e) =>
                                  setPracticalFormat(
                                    e.target.value as PracticalFormat
                                  )
                                }
                                className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
                              >
                                {PRACTICAL_FORMATS.map((fmt) => (
                                  <option key={fmt} value={fmt}>
                                    {FORMAT_LABELS[fmt]}
                                  </option>
                                ))}
                              </select>
                            </div>

                            <div className="sm:col-span-2">
                              <label className="block text-xs font-semibold text-slate-700">
                                Загальні методичні вказівки
                              </label>
                              <textarea
                                rows={3}
                                required
                                value={practicalInstructions}
                                onChange={(e) =>
                                  setPracticalInstructions(e.target.value)
                                }
                                className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
                              />
                            </div>
                          </div>

                          {/* Файл-заготовка (шаблон) для студентів */}
                          <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4 space-y-3">
                            <div className="flex flex-wrap items-start justify-between gap-3">
                              <div className="space-y-1">
                                <h3 className="inline-flex items-center gap-1.5 text-sm font-bold text-slate-900">
                                  <Paperclip className="h-4 w-4 text-blue-600" />
                                  <span>
                                    Файл-заготовка (шаблон) для студентів
                                  </span>
                                </h3>
                                <p className="text-xs text-slate-500">
                                  Підтримуються формати{" "}
                                  <span className="font-mono font-semibold text-slate-700">
                                    .docx, .xlsx, .accdb, .zip, .txt, .csv
                                  </span>
                                  . Система автоматично блокує спроби здати
                                  незмінений шаблон.
                                </p>
                              </div>

                              <input
                                ref={templateFileInputRef}
                                type="file"
                                accept={ALLOWED_TEMPLATE_FILE_ACCEPT}
                                onChange={handleTemplateFileSelected}
                                className="sr-only"
                              />

                              {activePracticalId !== null &&
                                !practicalTeacher?.has_template_file && (
                                  <button
                                    type="button"
                                    disabled={
                                      uploadPracticalTemplateMutation.isPending
                                    }
                                    onClick={() =>
                                      templateFileInputRef.current?.click()
                                    }
                                    className="inline-flex items-center gap-1.5 rounded-xl border border-blue-200 bg-blue-50 px-3.5 py-2 text-xs font-semibold text-blue-700 hover:bg-blue-100 disabled:opacity-60"
                                  >
                                    {uploadPracticalTemplateMutation.isPending ? (
                                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                    ) : (
                                      <Upload className="h-3.5 w-3.5" />
                                    )}
                                    <span>
                                      {uploadPracticalTemplateMutation.isPending
                                        ? "Завантаження..."
                                        : "Прикріпити файл-заготовку"}
                                    </span>
                                  </button>
                                )}
                            </div>

                            {activePracticalId === null ? (
                              <p className="text-xs italic text-slate-500">
                                Спочатку збережіть практичну роботу, щоб
                                прикріпити файл-заготовку для студентів.
                              </p>
                            ) : practicalTeacher?.has_template_file ? (
                              <div className="flex flex-col justify-between gap-3 rounded-xl border border-emerald-200 bg-white p-3.5 sm:flex-row sm:items-center">
                                <div className="flex min-w-0 items-center gap-2.5">
                                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
                                    <FileText className="h-4 w-4" />
                                  </div>
                                  <div className="min-w-0">
                                    <p className="truncate text-xs font-bold text-slate-900">
                                      {practicalTeacher.template_file_name ??
                                        "Прикріплений файл-заготовка"}
                                    </p>
                                    <p className="text-[11px] text-emerald-700">
                                      Доступний студентам для завантаження у
                                      картці практичної роботи
                                    </p>
                                  </div>
                                </div>

                                <div className="flex flex-wrap shrink-0 items-center gap-2">
                                  <button
                                    type="button"
                                    disabled={isDownloadingTemplate}
                                    onClick={() =>
                                      void handleDownloadPracticalTemplate()
                                    }
                                    className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
                                  >
                                    {isDownloadingTemplate ? (
                                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                    ) : (
                                      <Download className="h-3.5 w-3.5 text-blue-600" />
                                    )}
                                    <span>Завантажити</span>
                                  </button>
                                  <button
                                    type="button"
                                    disabled={
                                      uploadPracticalTemplateMutation.isPending
                                    }
                                    onClick={() =>
                                      templateFileInputRef.current?.click()
                                    }
                                    className="inline-flex items-center gap-1 rounded-lg border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700 hover:bg-blue-100 disabled:opacity-60"
                                  >
                                    <Upload className="h-3.5 w-3.5" />
                                    <span>Замінити</span>
                                  </button>
                                  <button
                                    type="button"
                                    disabled={
                                      deletePracticalTemplateMutation.isPending
                                    }
                                    onClick={() =>
                                      deletePracticalTemplateMutation.mutate(
                                        activePracticalId
                                      )
                                    }
                                    className="inline-flex items-center gap-1 rounded-lg border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-700 hover:bg-rose-100 disabled:opacity-60"
                                  >
                                    <Trash2 className="h-3.5 w-3.5" />
                                    <span>Видалити шаблон</span>
                                  </button>
                                </div>
                              </div>
                            ) : null}
                          </div>

                          {/* Індивідуальні варіанти завдань */}
                          <div className="space-y-3 border-t border-slate-200 pt-5">
                            <div className="flex flex-wrap items-center justify-between gap-2">
                              <div>
                                <h3 className="inline-flex items-center gap-1.5 text-sm font-bold text-slate-900">
                                  <Sparkles className="h-4 w-4 text-indigo-600" />
                                  <span>
                                    Індивідуальні варіанти завдання (
                                    {variantDrafts.length})
                                  </span>
                                </h3>
                                <p className="text-xs text-slate-500">
                                  Розподіляються автоматично за номером студента у
                                  списку групи:{" "}
                                  <code>
                                    ((list_number - 1) % total_variants)
                                  </code>
                                </p>
                              </div>

                              <button
                                type="button"
                                onClick={handleAddVariantDraft}
                                className="inline-flex items-center gap-1.5 rounded-xl border border-indigo-200 bg-indigo-50 px-3 py-1.5 text-xs font-semibold text-indigo-700 hover:bg-indigo-100"
                              >
                                <Plus className="h-3.5 w-3.5" />
                                <span>Додати варіант</span>
                              </button>
                            </div>

                            <div className="space-y-3">
                              {variantDrafts.map((variant, idx) => (
                                <div
                                  key={idx}
                                  className="rounded-xl border border-slate-200 bg-slate-50/70 p-4 space-y-3"
                                >
                                  <div className="flex items-center justify-between gap-2">
                                    <span className="inline-flex items-center gap-1 rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-0.5 text-xs font-bold text-indigo-800">
                                      Варіант №{idx + 1}
                                    </span>
                                    {variantDrafts.length > 1 && (
                                      <button
                                        type="button"
                                        onClick={() =>
                                          handleRemoveVariantDraft(idx)
                                        }
                                        className="inline-flex items-center gap-1 text-xs font-semibold text-rose-600 hover:text-rose-800"
                                      >
                                        <Trash2 className="h-3.5 w-3.5" />
                                        <span>Видалити</span>
                                      </button>
                                    )}
                                  </div>

                                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                                    <div>
                                      <label className="block text-[11px] font-semibold text-slate-700">
                                        Заголовок варіанта
                                      </label>
                                      <input
                                        type="text"
                                        value={variant.title}
                                        onChange={(e) =>
                                          handleUpdateVariantDraft(idx, {
                                            title: e.target.value,
                                          })
                                        }
                                        className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-900"
                                      />
                                    </div>

                                    <div>
                                      <label className="block text-[11px] font-semibold text-slate-700">
                                        Вхідні параметри (JSONB parameters)
                                      </label>
                                      <input
                                        type="text"
                                        value={variant.parametersJson}
                                        onChange={(e) =>
                                          handleUpdateVariantDraft(idx, {
                                            parametersJson: e.target.value,
                                          })
                                        }
                                        className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 font-mono text-xs text-slate-900"
                                      />
                                    </div>

                                    <div className="sm:col-span-2">
                                      <label className="block text-[11px] font-semibold text-slate-700">
                                        Опис індивідуального завдання
                                      </label>
                                      <textarea
                                        rows={2}
                                        value={variant.task_description}
                                        onChange={(e) =>
                                          handleUpdateVariantDraft(idx, {
                                            task_description: e.target.value,
                                          })
                                        }
                                        className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2 text-xs text-slate-900"
                                      />
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>

                          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-4">
                            {activePracticalId !== null ? (
                              <div className="flex flex-wrap items-center gap-2">
                                <Link
                                  to={`/teacher/rules?practicalId=${activePracticalId}`}
                                  className="inline-flex items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-800 hover:bg-slate-50"
                                >
                                  <SlidersHorizontal className="h-3.5 w-3.5 text-blue-600" />
                                  <span>
                                    Перейти до візуального редактора правил (
                                    {practicalTeacher?.grading_rules.length ?? 0})
                                  </span>
                                </Link>

                                <button
                                  type="button"
                                  disabled={isDeleting}
                                  onClick={() => {
                                    if (
                                      selectedModuleId === null ||
                                      activeCourse === null
                                    ) {
                                      return;
                                    }
                                    openDeleteModal({
                                      kind: "practical",
                                      courseId: activeCourse.id,
                                      moduleId: selectedModuleId,
                                      practicalId: activePracticalId,
                                      title:
                                        practicalTeacher?.title ??
                                        moduleDetail?.practical?.title ??
                                        practicalTitle,
                                      moduleTitle:
                                        moduleDetail?.title ?? moduleTitle,
                                    });
                                  }}
                                  className="inline-flex items-center gap-1.5 rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-2 text-xs font-semibold text-rose-700 transition-colors hover:bg-rose-100 disabled:opacity-60"
                                >
                                  <Trash2 className="h-3.5 w-3.5" />
                                  <span>Видалити практичну роботу</span>
                                </button>
                              </div>
                            ) : (
                              <span className="text-xs text-slate-500">
                                Збережіть практичну роботу, щоб налаштувати
                                критерії автоперевірки.
                              </span>
                            )}

                            <button
                              type="submit"
                              disabled={upsertPracticalMutation.isPending}
                              className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-xs font-semibold text-white shadow-2xs hover:bg-blue-700 disabled:opacity-60"
                            >
                              <Save className="h-4 w-4" />
                              <span>
                                {upsertPracticalMutation.isPending
                                  ? "Збереження..."
                                  : "Зберегти практичну роботу та варіанти"}
                              </span>
                            </button>
                          </div>
                        </>
                      )}
                    </form>
                  )}
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* Модальне вікно підтвердження видалення модуля або практичної роботи */}
      {deleteTarget !== null && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-xs"
          role="dialog"
          aria-modal="true"
          aria-labelledby="course-delete-modal-title"
          onClick={(event) => {
            if (event.target === event.currentTarget) {
              closeDeleteModal();
            }
          }}
        >
          <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-50 text-rose-600">
                  <Trash2 className="h-5 w-5" />
                </div>
                <div>
                  <h3
                    id="course-delete-modal-title"
                    className="text-base font-bold text-slate-900"
                  >
                    {deleteTarget.kind === "module"
                      ? "Видалити модуль курсу?"
                      : "Видалити практичну роботу?"}
                  </h3>
                  <p className="mt-1 text-sm font-semibold text-slate-800">
                    {deleteTarget.kind === "module"
                      ? `Тема №${deleteTarget.orderIndex}: «${deleteTarget.title}»`
                      : `«${deleteTarget.title}»`}
                  </p>
                  {deleteTarget.kind === "practical" && (
                    <p className="mt-0.5 text-xs text-slate-500">
                      Модуль: {deleteTarget.moduleTitle}
                    </p>
                  )}
                </div>
              </div>
              <button
                type="button"
                onClick={closeDeleteModal}
                disabled={isDeleting}
                aria-label="Закрити вікно підтвердження"
                className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 disabled:opacity-50"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-amber-200 bg-amber-50 p-3.5 text-xs leading-relaxed text-amber-950">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
              <span>
                {deleteTarget.kind === "module"
                  ? `Дія незворотна. Буде остаточно видалено текст лекції, питання й спроби тесту-допуску${
                      deleteTarget.hasPractical
                        ? ", прикріплену практичну роботу"
                        : ""
                    }, а також усі пов'язані здачі, файли та оцінки студентів. Решта модулів курсу буде автоматично перенумерована.`
                  : "Дія незворотна. Буде остаточно видалено практичну роботу, її варіанти, правила автоперевірки, а також усі пов'язані здачі, завантажені файли та оцінки студентів. Лекція та тест-допуск цього модуля залишаться недоторканими."}
              </span>
            </div>

            {deleteModalError !== null && (
              <div
                role="alert"
                className="mt-3 flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-900"
              >
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" />
                <span className="font-medium">{deleteModalError}</span>
              </div>
            )}

            <div className="mt-6 flex items-center justify-end gap-2.5">
              <button
                type="button"
                onClick={closeDeleteModal}
                disabled={isDeleting}
                className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
              >
                Скасувати
              </button>
              <button
                type="button"
                onClick={handleConfirmDelete}
                disabled={isDeleting}
                className="inline-flex items-center gap-1.5 rounded-xl bg-rose-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-rose-700 disabled:opacity-60"
              >
                {isDeleting ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    <span>Видалення...</span>
                  </>
                ) : (
                  <>
                    <Trash2 className="h-3.5 w-3.5" />
                    <span>Підтвердити видалення</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CourseEditorPage;
