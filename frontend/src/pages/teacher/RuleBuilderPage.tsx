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
import { Link, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  BookOpenCheck,
  CheckCircle2,
  Code2,
  Copy,
  Database,
  Eye,
  FileCheck2,
  FileCode2,
  FileSpreadsheet,
  FileText,
  FlaskConical,
  Info,
  Loader2,
  Play,
  Plus,
  RefreshCw,
  RotateCcw,
  Save,
  Scale,
  SlidersHorizontal,
  Sparkles,
  Target,
  Trash2,
  UploadCloud,
} from "lucide-react";
import apiClient from "../../api/client";
import { DryRunResultPanel } from "../../components/grading/DryRunResultPanel";
import { extractApiErrorMessage } from "../../context/AuthContext";
import type {
  DryRunGradingResponse,
  HtmlDryRunRequest,
} from "../../types/api";
import type {
  CourseRead,
  CourseSlug,
  PracticalTeacherRead,
  PracticalUpdate,
} from "../../types/course";
import {
  GRADING_RULE_TYPES,
  type GradingRule,
  type GradingRulesUpdateRequest,
  type GradingRuleType,
  type PracticalFormat,
} from "../../types/grading";

interface RuleTypeSpec {
  type: GradingRuleType;
  format: PracticalFormat;
  label: string;
  targetHint: string;
  defaultTarget: string;
  expectedHint: string;
  defaultExpected: string;
  defaultPoints: number;
  defaultDescription: string;
}

const RULE_TYPE_SPECS: Record<GradingRuleType, RuleTypeSpec> = {
  docx_page_margins: {
    type: "docx_page_margins",
    format: "docx",
    label: "Поля сторінки документа (Word)",
    targetHint: "Секція документа, напр. section_0 або document",
    defaultTarget: "section_0",
    expectedHint: "Поля в мм: left=30,right=15,top=20,bottom=20",
    defaultExpected: "left=30,right=15,top=20,bottom=20",
    defaultPoints: 2.0,
    defaultDescription:
      "Поля сторінки відповідають стандарту (30/15/20/20 мм)",
  },
  docx_font: {
    type: "docx_font",
    format: "docx",
    label: "Гарнітура та кегль шрифту (Word)",
    targetHint: "Цільовий блок: body, heading_1 або paragraph_0",
    defaultTarget: "body",
    expectedHint: "Формат Гарнітура:Кегль, напр. Times New Roman:14",
    defaultExpected: "Times New Roman:14",
    defaultPoints: 2.5,
    defaultDescription:
      "Основний текст набрано шрифтом Times New Roman, 14 пт",
  },
  docx_line_spacing: {
    type: "docx_line_spacing",
    format: "docx",
    label: "Міжрядковий інтервал (Word)",
    targetHint: "Цільовий блок: body або paragraph_0",
    defaultTarget: "body",
    expectedHint: "Множник інтервалу, напр. 1.5 або 1.15",
    defaultExpected: "1.5",
    defaultPoints: 1.5,
    defaultDescription: "Встановлено полуторний міжрядковий інтервал (1.5)",
  },
  docx_alignment: {
    type: "docx_alignment",
    format: "docx",
    label: "Вирівнювання абзаців (Word)",
    targetHint: "Цільовий блок: body, title або paragraph_0",
    defaultTarget: "body",
    expectedHint: "JUSTIFY, CENTER, LEFT або RIGHT",
    defaultExpected: "JUSTIFY",
    defaultPoints: 1.5,
    defaultDescription: "Абзаци основного тексту вирівняно за шириною",
  },
  docx_table_exists: {
    type: "docx_table_exists",
    format: "docx",
    label: "Наявність таблиці у документі (Word)",
    targetHint: "document або table_0",
    defaultTarget: "document",
    expectedHint: "true, 3x4 або rows>=4",
    defaultExpected: ">=1",
    defaultPoints: 1.5,
    defaultDescription: "Документ містить щонайменше одну зведену таблицю",
  },
  docx_list_exists: {
    type: "docx_list_exists",
    format: "docx",
    label: "Наявність списку (Word)",
    targetHint: "document",
    defaultTarget: "document",
    expectedHint: "true або >=1",
    defaultExpected: "true",
    defaultPoints: 1.0,
    defaultDescription:
      "Документ містить маркований або нумерований список",
  },
  xlsx_formula: {
    type: "xlsx_formula",
    format: "xlsx",
    label: "Формула у комірці (Excel data_only=False)",
    targetHint: "Адреса комірки: D12 або Sheet1!D12",
    defaultTarget: "D12",
    expectedHint: "Вираз формули без '=' або з '=', напр. SUM(D2:D11)",
    defaultExpected: "SUM(D2:D11)",
    defaultPoints: 3.5,
    defaultDescription:
      "Використано функцію SUM для підрахунку підсумку в комірці D12",
  },
  xlsx_value: {
    type: "xlsx_value",
    format: "xlsx",
    label: "Обчислене значення комірки (Excel data_only=True)",
    targetHint: "Адреса комірки: D12 або Sheet1!D13",
    defaultTarget: "D12",
    expectedHint: "Очікуване число, not_null або >0",
    defaultExpected: "not_null",
    defaultPoints: 2.0,
    defaultDescription:
      "У комірці D12 збережено обчислене числове значення",
  },
  xlsx_chart_exists: {
    type: "xlsx_chart_exists",
    format: "xlsx",
    label: "Наявність діаграми на аркуші (Excel _charts)",
    targetHint: "Назва аркуша: Sheet1 або workbook",
    defaultTarget: "Sheet1",
    expectedHint: "true або >=1",
    defaultExpected: "true",
    defaultPoints: 2.0,
    defaultDescription: "На аркуші Sheet1 побудовано діаграму",
  },
  accdb_table_exists: {
    type: "accdb_table_exists",
    format: "accdb",
    label: "Наявність таблиці у схемі БД (Access)",
    targetHint: "Назва таблиці, напр. Students або Grades",
    defaultTarget: "Students",
    expectedHint: "true",
    defaultExpected: "true",
    defaultPoints: 3.0,
    defaultDescription: "У базі даних присутня таблиця Students",
  },
  accdb_column_exists: {
    type: "accdb_column_exists",
    format: "accdb",
    label: "Наявність стовпця в таблиці (Access)",
    targetHint: "Формат Таблиця.Поле, напр. Students.FullName",
    defaultTarget: "Students.FullName",
    expectedHint: "true",
    defaultExpected: "true",
    defaultPoints: 2.0,
    defaultDescription: "Таблиця Students містить поле FullName",
  },
  accdb_column_type: {
    type: "accdb_column_type",
    format: "accdb",
    label: "Тип даних стовпця таблиці (Access)",
    targetHint: "Формат Таблиця.Поле, напр. Grades.Score",
    defaultTarget: "Grades.Score",
    expectedHint: "Канонічний тип: TEXT, LONG, DOUBLE, CURRENCY, DATETIME",
    defaultExpected: "DOUBLE",
    defaultPoints: 2.0,
    defaultDescription: "Поле Grades.Score має числовий тип даних",
  },
  accdb_query_exists: {
    type: "accdb_query_exists",
    format: "accdb",
    label: "Наявність запиту у БД (Access MSysObjects)",
    targetHint: "Назва запиту або * / any для перевірки кількості запитів",
    defaultTarget: "*",
    expectedHint: "true або умова кількості, напр. >=1 чи min>=1",
    defaultExpected: "true",
    defaultPoints: 2.0,
    defaultDescription:
      "У базі даних створено щонайменше один користувацький запит",
  },
  accdb_form_exists: {
    type: "accdb_form_exists",
    format: "accdb",
    label: "Наявність форми у БД (Access MSysObjects)",
    targetHint: "Назва форми або * / any для перевірки кількості форм",
    defaultTarget: "*",
    expectedHint: "true або умова кількості, напр. >=1 чи min>=1",
    defaultExpected: "true",
    defaultPoints: 2.0,
    defaultDescription: "У базі даних створено користувацьку форму",
  },
  accdb_report_exists: {
    type: "accdb_report_exists",
    format: "accdb",
    label: "Наявність звіту у БД (Access MSysObjects)",
    targetHint: "Назва звіту або * / any для перевірки кількості звітів",
    defaultTarget: "*",
    expectedHint: "true або умова кількості, напр. >=1 чи min>=1",
    defaultExpected: "true",
    defaultPoints: 2.0,
    defaultDescription: "У базі даних створено користувацький звіт",
  },
  accdb_relationship_exists: {
    type: "accdb_relationship_exists",
    format: "accdb",
    label: "Наявність зв'язку між таблицями (Access MSysRelationships)",
    targetHint:
      "Таблиця1->Таблиця2, Таблиця1,Таблиця2 або * для кількості зв'язків",
    defaultTarget: "Students->Grades",
    expectedHint: "true або умова кількості, напр. >=1",
    defaultExpected: "true",
    defaultPoints: 2.0,
    defaultDescription:
      "Між таблицями Students та Grades налаштовано зв'язок",
  },
  html_tag_exists: {
    type: "html_tag_exists",
    format: "html",
    label: "Наявність HTML-елемента за CSS-селектором",
    targetHint: "CSS-селектор або doctype: main > table, header > h1",
    defaultTarget: "main > table",
    expectedHint: "true",
    defaultExpected: "true",
    defaultPoints: 2.5,
    defaultDescription:
      "Основний блок <main> містить семантичну таблицю <table>",
  },
  html_tag_count: {
    type: "html_tag_count",
    format: "html",
    label: "Кількість HTML-елементів у DOM",
    targetHint: "CSS-селектор: table tr або ul > li",
    defaultTarget: "table tr",
    expectedHint: "Умова кількості: >=4, ==5 або >2",
    defaultExpected: ">=4",
    defaultPoints: 2.5,
    defaultDescription: "Таблиця містить щонайменше 4 рядки <tr>",
  },
  html_attribute_exists: {
    type: "html_attribute_exists",
    format: "html",
    label: "Перевірка атрибута HTML-елемента",
    targetHint: "Селектор і атрибут: html[lang] або img@alt",
    defaultTarget: "html[lang]",
    expectedHint: "Очікуване значення атрибута або true, напр. uk",
    defaultExpected: "uk",
    defaultPoints: 2.0,
    defaultDescription:
      'Кореневий тег <html> містить атрибут lang="uk"',
  },
};

const FORMAT_BADGE_CONFIG: Record<
  PracticalFormat,
  { label: string; badgeClass: string }
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

interface PracticalCatalogEntry {
  practicalId: string;
  practicalFormat: PracticalFormat;
  needsRulesReview: boolean;
  moduleId: string;
  moduleOrderIndex: number;
  moduleTitle: string;
  courseId: string;
  courseTitle: string;
  courseSlug: CourseSlug;
}

async function fetchCourses(): Promise<CourseRead[]> {
  const response = await apiClient.get<CourseRead[]>("/courses");
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

function renderFormatIcon(format: PracticalFormat): ReactElement {
  switch (format) {
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

function formatPointsCompact(value: number): string {
  const rounded = Math.round(value * 100) / 100;
  return Number.isInteger(rounded)
    ? String(rounded)
    : rounded.toFixed(2).replace(/0$/, "");
}

function formatFileSizeCompact(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} Б`;
  }
  const kb = bytes / 1024;
  if (kb < 1024) {
    return `${kb.toFixed(1)} КБ`;
  }
  return `${(kb / 1024).toFixed(2)} МБ`;
}

type BinaryFormat = Exclude<PracticalFormat, "html">;

const DRY_RUN_FILE_ACCEPT: Record<BinaryFormat, string> = {
  docx: ".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  xlsx: ".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  accdb: ".accdb,application/msaccess,application/x-msaccess",
};

const DEFAULT_DRY_RUN_HTML = `<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8">
  <title>Тестова перевірка HTML</title>
</head>
<body>
  <h1>Заголовок сторінки</h1>
  <p>Тестовий абзац для перевірки правил автооцінювання.</p>
</body>
</html>`;

export function RuleBuilderPage(): ReactElement {
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const queryPracticalId = searchParams.get("practicalId");
  const dryRunFileInputRef = useRef<HTMLInputElement | null>(null);

  const [selectedPracticalId, setSelectedPracticalId] = useState<string | null>(
    queryPracticalId
  );
  const [rulesDraft, setRulesDraft] = useState<GradingRule[]>([]);
  const [syncMaxScore, setSyncMaxScore] = useState<boolean>(false);
  const [showJsonInspector, setShowJsonInspector] = useState<boolean>(false);
  const [rawJsonInput, setRawJsonInput] = useState<string>("");
  const [feedbackBanner, setFeedbackBanner] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const [dryRunVariantNumber, setDryRunVariantNumber] = useState<number>(1);
  const [dryRunFile, setDryRunFile] = useState<File | null>(null);
  const [dryRunIsDragActive, setDryRunIsDragActive] = useState<boolean>(false);
  const [dryRunHtmlCode, setDryRunHtmlCode] =
    useState<string>(DEFAULT_DRY_RUN_HTML);
  const [dryRunResult, setDryRunResult] =
    useState<DryRunGradingResponse | null>(null);
  const [dryRunError, setDryRunError] = useState<string | null>(null);

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

  // Каталог усіх практичних робіт по всіх курсах
  const practicalCatalog = useMemo<PracticalCatalogEntry[]>(() => {
    const entries: PracticalCatalogEntry[] = [];
    for (const course of courses ?? []) {
      for (const mod of course.modules) {
        if (mod.practical_id !== null && mod.practical_format !== null) {
          entries.push({
            practicalId: mod.practical_id,
            practicalFormat: mod.practical_format,
            needsRulesReview: mod.practical_needs_rules_review,
            moduleId: mod.id,
            moduleOrderIndex: mod.order_index,
            moduleTitle: mod.title,
            courseId: course.id,
            courseTitle: course.title,
            courseSlug: course.slug,
          });
        }
      }
    }
    return entries;
  }, [courses]);

  // Синхронізація обраної практичної роботи з URL або першою доступною
  useEffect(() => {
    if (practicalCatalog.length === 0) {
      setSelectedPracticalId(null);
      return;
    }
    if (
      queryPracticalId !== null &&
      practicalCatalog.some((item) => item.practicalId === queryPracticalId)
    ) {
      if (selectedPracticalId !== queryPracticalId) {
        setSelectedPracticalId(queryPracticalId);
      }
      return;
    }
    const exists = practicalCatalog.some(
      (item) => item.practicalId === selectedPracticalId
    );
    if (!exists) {
      const firstId = practicalCatalog[0]?.practicalId ?? null;
      setSelectedPracticalId(firstId);
    }
  }, [practicalCatalog, queryPracticalId, selectedPracticalId]);

  const handleSelectPractical = (practicalId: string): void => {
    setSelectedPracticalId(practicalId);
    setSearchParams({ practicalId });
    setSyncMaxScore(false);
    setFeedbackBanner(null);
    setDryRunVariantNumber(1);
    setDryRunFile(null);
    setDryRunIsDragActive(false);
    setDryRunResult(null);
    setDryRunError(null);
    if (dryRunFileInputRef.current !== null) {
      dryRunFileInputRef.current.value = "";
    }
  };

  const {
    data: practicalDetail,
    isLoading: isLoadingPractical,
    isError: isPracticalError,
    error: practicalError,
  } = useQuery<PracticalTeacherRead>({
    queryKey: ["practical-teacher", selectedPracticalId],
    queryFn: () => fetchPracticalTeacher(selectedPracticalId ?? ""),
    enabled: selectedPracticalId !== null,
  });

  useEffect(() => {
    if (practicalDetail === undefined) {
      return;
    }
    setRulesDraft(practicalDetail.grading_rules);
    setRawJsonInput(JSON.stringify(practicalDetail.grading_rules, null, 2));
    const loadedRulesSum = Number(
      practicalDetail.grading_rules
        .reduce((acc, item) => acc + (Number(item.points) || 0), 0)
        .toFixed(2)
    );
    const hasManualReserve = practicalDetail.max_score - loadedRulesSum > 0.005;
    setSyncMaxScore(!hasManualReserve);
  }, [practicalDetail]);

  useEffect(() => {
    setRawJsonInput(JSON.stringify(rulesDraft, null, 2));
  }, [rulesDraft]);

  const activeCatalogEntry = useMemo<PracticalCatalogEntry | null>(() => {
    return (
      practicalCatalog.find(
        (item) => item.practicalId === selectedPracticalId
      ) ?? null
    );
  }, [practicalCatalog, selectedPracticalId]);

  const activeFormat: PracticalFormat =
    practicalDetail?.format_type ??
    activeCatalogEntry?.practicalFormat ??
    "docx";

  // Шаблони правил для поточного формату практичної роботи
  const recommendedRuleSpecs = useMemo<RuleTypeSpec[]>(() => {
    return GRADING_RULE_TYPES.map((t) => RULE_TYPE_SPECS[t]).filter(
      (spec) => spec.format === activeFormat
    );
  }, [activeFormat]);

  const totalDraftPoints = useMemo<number>(() => {
    return Number(
      rulesDraft
        .reduce((acc, item) => acc + (Number(item.points) || 0), 0)
        .toFixed(2)
    );
  }, [rulesDraft]);

  const maxScore = practicalDetail?.max_score ?? 12;
  const isPointsBalanced = Math.abs(totalDraftPoints - maxScore) < 0.01;
  const isOverMaxScore = totalDraftPoints > maxScore + 0.005;
  const manualBonusReserve = Math.max(
    0,
    Number((maxScore - totalDraftPoints).toFixed(2))
  );

  // Мутація збереження правил перевірки PUT /practicals/{id}/rules
  const saveRulesMutation = useMutation<
    PracticalTeacherRead,
    unknown,
    GradingRulesUpdateRequest
  >({
    mutationFn: async (payload: GradingRulesUpdateRequest) => {
      if (selectedPracticalId === null) {
        throw new Error("Практичну роботу не обрано");
      }
      const response = await apiClient.put<PracticalTeacherRead>(
        `/practicals/${selectedPracticalId}/rules`,
        payload
      );
      return response.data;
    },
    onSuccess: (updated) => {
      void queryClient.invalidateQueries({
        queryKey: ["practical-teacher", updated.id],
      });
      void queryClient.invalidateQueries({ queryKey: ["courses"] });
      void queryClient.invalidateQueries({ queryKey: ["group-journal"] });
      setRulesDraft(updated.grading_rules);
      setFeedbackBanner({
        type: "success",
        text: `Збережено ${updated.grading_rules.length} правил(о) автоперевірки для «${updated.title}» (макс. бал: ${updated.max_score.toFixed(1)} б.).`,
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(
          err,
          "Не вдалося зберегти правила автоперевірки."
        ),
      });
    },
  });

  // Мутація синхронізації max_score практичної з сумою балів правил
  const syncMaxScoreMutation = useMutation<
    PracticalTeacherRead,
    unknown,
    PracticalUpdate
  >({
    mutationFn: async (payload: PracticalUpdate) => {
      if (selectedPracticalId === null) {
        throw new Error("Практичну роботу не обрано");
      }
      const response = await apiClient.patch<PracticalTeacherRead>(
        `/practicals/${selectedPracticalId}`,
        payload
      );
      return response.data;
    },
    onSuccess: (updated) => {
      void queryClient.invalidateQueries({
        queryKey: ["practical-teacher", updated.id],
      });
      void queryClient.invalidateQueries({ queryKey: ["courses"] });
      setFeedbackBanner({
        type: "success",
        text: `Максимальний бал практичної роботи оновлено до ${updated.max_score.toFixed(1)} б.`,
      });
    },
    onError: (err) => {
      setFeedbackBanner({
        type: "error",
        text: extractApiErrorMessage(
          err,
          "Не вдалося оновити максимальний бал."
        ),
      });
    },
  });

  // Мутація тестової (Dry-Run) перевірки чернеткових правил без запису в БД
  const dryRunMutation = useMutation<
    DryRunGradingResponse,
    unknown,
    {
      practicalId: string;
      format: PracticalFormat;
      variantNumber: number;
      rulesOverride: GradingRule[];
      file: File | null;
      rawCode: string;
    }
  >({
    mutationFn: async ({
      practicalId,
      format,
      variantNumber,
      rulesOverride,
      file,
      rawCode,
    }) => {
      if (format === "html") {
        const payload: HtmlDryRunRequest = {
          raw_code: rawCode,
          variant_number: variantNumber,
          rules_override: rulesOverride,
        };
        const response = await apiClient.post<DryRunGradingResponse>(
          `/practicals/${practicalId}/dry-run`,
          payload
        );
        return response.data;
      }

      if (file === null) {
        throw new Error("Оберіть тестовий файл для запуску перевірки.");
      }

      const formData = new FormData();
      formData.append("file", file);
      formData.append("variant_number", String(variantNumber));
      formData.append("rules_json", JSON.stringify(rulesOverride));

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
    },
    onSuccess: (data) => {
      setDryRunResult(data);
      setDryRunError(null);
    },
    onError: (err) => {
      setDryRunResult(null);
      setDryRunError(
        extractApiErrorMessage(
          err,
          "Не вдалося виконати тестову перевірку правил (Dry-Run)."
        )
      );
    },
  });

  const handleSelectDryRunFile = (candidate: File): void => {
    if (activeFormat === "html") {
      return;
    }
    const expectedExt = `.${activeFormat}`;
    if (!candidate.name.toLowerCase().endsWith(expectedExt)) {
      setDryRunFile(null);
      setDryRunError(
        `Невірний формат файлу «${candidate.name}». Очікується файл із розширенням ${expectedExt}.`
      );
      return;
    }
    if (candidate.size === 0) {
      setDryRunFile(null);
      setDryRunError(`Обраний файл «${candidate.name}» порожній (0 байтів).`);
      return;
    }
    setDryRunFile(candidate);
    setDryRunError(null);
  };

  const handleDryRunFileInputChange = (
    event: ChangeEvent<HTMLInputElement>
  ): void => {
    const picked = event.target.files?.[0];
    if (picked !== undefined) {
      handleSelectDryRunFile(picked);
    }
  };

  const handleDryRunDragOver = (event: DragEvent<HTMLDivElement>): void => {
    event.preventDefault();
    event.stopPropagation();
    if (!dryRunIsDragActive) {
      setDryRunIsDragActive(true);
    }
  };

  const handleDryRunDragLeave = (event: DragEvent<HTMLDivElement>): void => {
    event.preventDefault();
    event.stopPropagation();
    setDryRunIsDragActive(false);
  };

  const handleDryRunDrop = (event: DragEvent<HTMLDivElement>): void => {
    event.preventDefault();
    event.stopPropagation();
    setDryRunIsDragActive(false);
    const dropped = event.dataTransfer.files?.[0];
    if (dropped !== undefined) {
      handleSelectDryRunFile(dropped);
    }
  };

  const handleClearDryRunFile = (): void => {
    setDryRunFile(null);
    setDryRunError(null);
    if (dryRunFileInputRef.current !== null) {
      dryRunFileInputRef.current.value = "";
    }
  };

  const handleRunDryRun = (): void => {
    if (selectedPracticalId === null) {
      return;
    }
    if (rulesDraft.length === 0) {
      setDryRunError(
        "Додайте щонайменше одне правило автоперевірки перед запуском тестування."
      );
      return;
    }
    if (activeFormat === "html" && dryRunHtmlCode.trim().length === 0) {
      setDryRunError("Введіть HTML-код для тестової перевірки.");
      return;
    }
    if (activeFormat !== "html" && dryRunFile === null) {
      setDryRunError(
        `Оберіть або перетягніть тестовий файл формату .${activeFormat}.`
      );
      return;
    }

    const normalizedRules: GradingRule[] = rulesDraft.map((rule) => ({
      id: rule.id.trim(),
      type: rule.type,
      target: rule.target.trim(),
      expected: rule.expected.trim(),
      points: Number(rule.points),
      description: rule.description.trim(),
    }));

    setDryRunError(null);
    dryRunMutation.mutate({
      practicalId: selectedPracticalId,
      format: activeFormat,
      variantNumber: dryRunVariantNumber,
      rulesOverride: normalizedRules,
      file: dryRunFile,
      rawCode: dryRunHtmlCode,
    });
  };

  const generateNextRuleId = (prefixFormat: PracticalFormat): string => {
    const existingIds = new Set(rulesDraft.map((r) => r.id));
    let counter = rulesDraft.length + 1;
    let candidate = `${prefixFormat}_rule_${counter}`;
    while (existingIds.has(candidate)) {
      counter += 1;
      candidate = `${prefixFormat}_rule_${counter}`;
    }
    return candidate;
  };

  const handleAddRuleFromSpec = (spec: RuleTypeSpec): void => {
    const newRule: GradingRule = {
      id: generateNextRuleId(spec.format),
      type: spec.type,
      target: spec.defaultTarget,
      expected: spec.defaultExpected,
      points: spec.defaultPoints,
      description: spec.defaultDescription,
    };
    setRulesDraft((prev) => [...prev, newRule]);
  };

  const handleAddDefaultRule = (): void => {
    const defaultSpec =
      recommendedRuleSpecs[0] ?? RULE_TYPE_SPECS.docx_page_margins;
    handleAddRuleFromSpec(defaultSpec);
  };

  const handleUpdateRule = (
    index: number,
    patch: Partial<GradingRule>
  ): void => {
    setRulesDraft((prev) =>
      prev.map((rule, idx) => {
        if (idx !== index) {
          return rule;
        }
        return { ...rule, ...patch };
      })
    );
  };

  const handleChangeRuleType = (
    index: number,
    nextType: GradingRuleType
  ): void => {
    const spec = RULE_TYPE_SPECS[nextType];
    setRulesDraft((prev) =>
      prev.map((rule, idx) => {
        if (idx !== index) {
          return rule;
        }
        return {
          ...rule,
          type: nextType,
          target: spec.defaultTarget,
          expected: spec.defaultExpected,
          description: spec.defaultDescription,
        };
      })
    );
  };

  const handleDuplicateRule = (index: number): void => {
    const source = rulesDraft[index];
    if (source === undefined) {
      return;
    }
    const copy: GradingRule = {
      ...source,
      id: generateNextRuleId(activeFormat),
      description: `${source.description} (копія)`,
    };
    setRulesDraft((prev) => [
      ...prev.slice(0, index + 1),
      copy,
      ...prev.slice(index + 1),
    ]);
  };

  const handleMoveRule = (index: number, direction: -1 | 1): void => {
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= rulesDraft.length) {
      return;
    }
    setRulesDraft((prev) => {
      const next = [...prev];
      const currentItem = next[index];
      const swapItem = next[targetIndex];
      if (currentItem === undefined || swapItem === undefined) {
        return prev;
      }
      next[index] = swapItem;
      next[targetIndex] = currentItem;
      return next;
    });
  };

  const handleDeleteRule = (index: number): void => {
    setRulesDraft((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleApplyRawJson = (): void => {
    try {
      const parsed: unknown = JSON.parse(rawJsonInput);
      if (!Array.isArray(parsed)) {
        setFeedbackBanner({
          type: "error",
          text: "JSONB-правила повинні бути масивом об'єктів [].",
        });
        return;
      }
      const validated: GradingRule[] = [];
      for (let i = 0; i < parsed.length; i += 1) {
        const item: unknown = parsed[i];
        if (typeof item !== "object" || item === null) {
          setFeedbackBanner({
            type: "error",
            text: `Елемент №${i + 1} не є коректним об'єктом правила.`,
          });
          return;
        }
        const rec = item as Record<string, unknown>;
        const id = typeof rec.id === "string" ? rec.id.trim() : "";
        const type = rec.type as GradingRuleType;
        const target = typeof rec.target === "string" ? rec.target.trim() : "";
        const expected =
          typeof rec.expected === "string" ? rec.expected.trim() : "";
        const points = Number(rec.points);
        const description =
          typeof rec.description === "string" ? rec.description.trim() : "";

        if (
          id.length === 0 ||
          !GRADING_RULE_TYPES.includes(type) ||
          target.length === 0 ||
          expected.length === 0 ||
          Number.isNaN(points) ||
          points <= 0 ||
          description.length === 0
        ) {
          setFeedbackBanner({
            type: "error",
            text: `Правило №${i + 1} містить некоректні або порожні обов'язкові поля (id, type, target, expected, points, description).`,
          });
          return;
        }

        validated.push({
          id,
          type,
          target,
          expected,
          points,
          description,
        });
      }

      setRulesDraft(validated);
      setFeedbackBanner({
        type: "success",
        text: `Імпортовано та перевірено ${validated.length} правил(о) із JSON.`,
      });
    } catch {
      setFeedbackBanner({
        type: "error",
        text: "Помилка синтаксису JSON. Перевірте коми та лапки.",
      });
    }
  };

  const handleSaveRules = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    const seenIds = new Set<string>();
    for (let idx = 0; idx < rulesDraft.length; idx += 1) {
      const rule = rulesDraft[idx];
      if (rule === undefined) {
        continue;
      }
      if (
        rule.id.trim().length === 0 ||
        rule.target.trim().length === 0 ||
        rule.expected.trim().length === 0 ||
        rule.description.trim().length === 0
      ) {
        setFeedbackBanner({
          type: "error",
          text: `Заповніть усі обов'язкові поля у правилі №${idx + 1}.`,
        });
        return;
      }
      if (rule.points <= 0) {
        setFeedbackBanner({
          type: "error",
          text: `Вага правила «${rule.id}» у балах має бути більшою за 0.`,
        });
        return;
      }
      const normalizedId = rule.id.trim();
      if (seenIds.has(normalizedId)) {
        setFeedbackBanner({
          type: "error",
          text: `Виявлено дублікат ідентифікатора правила «${normalizedId}». Кожне правило повинно мати унікальний ID.`,
        });
        return;
      }
      seenIds.add(normalizedId);
    }

    saveRulesMutation.mutate({
      grading_rules: rulesDraft.map((rule) => ({
        id: rule.id.trim(),
        type: rule.type,
        target: rule.target.trim(),
        expected: rule.expected.trim(),
        points: Number(rule.points),
        description: rule.description.trim(),
      })),
      sync_max_score: syncMaxScore,
    });
  };

  if (isLoadingCourses) {
    return (
      <div className="flex min-h-[55vh] flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8">
        <Loader2 className="h-9 w-9 animate-spin text-blue-600" />
        <p className="mt-3 text-sm font-medium text-slate-700">
          Завантаження візуального редактора правил автоперевірки...
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
          Не вдалося завантажити перелік практичних робіт
        </h2>
        <p className="mt-1.5 text-sm text-slate-600">
          {extractApiErrorMessage(
            coursesError,
            "Сталася помилка під час завантаження курсів."
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

  const formatBadge = FORMAT_BADGE_CONFIG[activeFormat];

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Шапка візуального конструктора правил */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <div className="space-y-1.5">
            <div className="inline-flex items-center gap-1.5 rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">
              <SlidersHorizontal className="h-3.5 w-3.5" />
              Ядро детермінованої автоперевірки • JSONB Конструктор правил
            </div>
            <h1 className="text-xl font-bold text-slate-900 sm:text-2xl">
              Візуальний редактор критеріїв оцінювання практичних робіт
            </h1>
            <p className="max-w-3xl text-sm text-slate-600">
              Налаштовуйте декларативні правила перевірки документів{" "}
              <span className="font-semibold text-slate-800">
                Word (<code>.docx</code>), Excel (<code>.xlsx</code>), Access (
                <code>.accdb</code>) та HTML5 DOM
              </span>{" "}
              із зазначенням цільового селектора/комірки, очікуваного еталона та
              ваги в балах.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            {activeCatalogEntry !== null && (
              <Link
                to={`/teacher/courses/${activeCatalogEntry.courseId}/modules/${activeCatalogEntry.moduleId}/preview`}
                className="inline-flex items-center gap-1.5 rounded-xl border border-emerald-200 bg-emerald-50 px-3.5 py-2 text-xs font-semibold text-emerald-800 hover:bg-emerald-100"
              >
                <Eye className="h-4 w-4 text-emerald-600" />
                <span>Очима студента</span>
              </Link>
            )}

            <Link
              to="/teacher/courses"
              className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
            >
              <BookOpenCheck className="h-4 w-4 text-blue-600" />
              <span>До конструктора курсів</span>
            </Link>

            <button
              type="button"
              onClick={() => setShowJsonInspector((prev) => !prev)}
              className={`inline-flex items-center gap-1.5 rounded-xl border px-3.5 py-2 text-xs font-semibold transition-colors ${
                showJsonInspector
                  ? "border-slate-900 bg-slate-900 text-white"
                  : "border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100"
              }`}
            >
              <FileCode2 className="h-4 w-4" />
              <span>{showJsonInspector ? "Сховати JSONB" : "Інспектор JSONB"}</span>
            </button>
          </div>
        </div>

        {/* Повідомлення про збереження або помилку */}
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

        {/* Вибір практичної роботи */}
        <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {practicalCatalog.map((entry) => {
            const isSelected = entry.practicalId === selectedPracticalId;
            const fmtMeta = FORMAT_BADGE_CONFIG[entry.practicalFormat];

            return (
              <button
                key={entry.practicalId}
                type="button"
                onClick={() => handleSelectPractical(entry.practicalId)}
                className={`flex flex-col justify-between rounded-2xl border p-4 text-left transition-all ${
                  isSelected
                    ? "border-blue-600 bg-blue-50/50 shadow-xs ring-1 ring-blue-600"
                    : "border-slate-200 bg-slate-50/60 hover:border-blue-300 hover:bg-white"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold ${fmtMeta.badgeClass}`}
                    >
                      {renderFormatIcon(entry.practicalFormat)}
                      <span>.{entry.practicalFormat}</span>
                    </span>
                    <span className="text-[11px] font-semibold text-slate-500">
                      Тема №{entry.moduleOrderIndex}
                    </span>
                  </div>
                  <h2 className="mt-2 line-clamp-2 text-sm font-bold text-slate-900">
                    {entry.moduleTitle}
                  </h2>
                  {entry.needsRulesReview && (
                    <span
                      title="Стартові правила потребують перевірки викладачем або додаткової ручної оцінки"
                      className="mt-1.5 inline-flex items-center gap-1 rounded-full border border-amber-300 bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-800"
                    >
                      <AlertTriangle className="h-3 w-3 shrink-0 text-amber-600" />
                      <span>Потребує перевірки</span>
                    </span>
                  )}
                </div>
                <p className="mt-2 truncate text-[11px] text-slate-500">
                  {entry.courseTitle}
                </p>
              </button>
            );
          })}
        </div>
      </section>

      {selectedPracticalId === null ? (
        <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-xs">
          <Info className="mx-auto h-10 w-10 text-slate-400" />
          <h2 className="mt-3 text-base font-bold text-slate-900">
            Практичні роботи відсутні
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            Створіть практичну роботу в конструкторі курсів, щоб налаштувати для
            неї критерії автоперевірки.
          </p>
        </div>
      ) : isLoadingPractical ? (
        <div className="flex min-h-[40vh] flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p className="mt-2.5 text-xs font-medium text-slate-600">
            Завантаження правил практичної роботи...
          </p>
        </div>
      ) : isPracticalError || practicalDetail === undefined ? (
        <div className="rounded-2xl border border-rose-200 bg-white p-6 text-center shadow-xs">
          <p className="text-sm font-semibold text-rose-700">
            {extractApiErrorMessage(
              practicalError,
              "Не вдалося завантажити дані практичної роботи."
            )}
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          <form onSubmit={handleSaveRules} className="space-y-6">
          {/* Інформаційний банер про необхідність перевірки стартових правил */}
          {practicalDetail.needs_rules_review && (
            <div
              role="status"
              className="flex items-start gap-3 rounded-2xl border border-amber-300 bg-amber-50 px-5 py-4 text-xs text-amber-950 shadow-xs"
            >
              <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
              <div className="space-y-1">
                <p className="text-sm font-bold text-amber-950">
                  Стартові правила потребують перевірки викладачем або додаткової
                  ручної оцінки
                </p>
                <p className="leading-relaxed text-amber-900">
                  Ця практична робота містить візуальні, творчі або розширені
                  елементи, які не повністю оцінюються парсером. Перевірте
                  критерії нижче та збережіть правила, щоб підтвердити їх
                  (вимкніть автосинхронізацію <code>max_score</code>, якщо
                  частину балів ви плануєте виставляти вручну).
                </p>
              </div>
            </div>
          )}

          {/* Панель балансу балів та швидких шаблонів правил */}
          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs sm:p-6">
            <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${formatBadge.badgeClass}`}
                  >
                    {renderFormatIcon(activeFormat)}
                    <span>{formatBadge.label}</span>
                  </span>
                  <span className="text-xs font-semibold text-slate-500">
                    Варіантів: {practicalDetail.variants.length}
                  </span>
                </div>
                <h2 className="text-lg font-bold text-slate-900">
                  {practicalDetail.title}
                </h2>
                <p className="text-xs text-slate-600">
                  {practicalDetail.instructions}
                </p>
              </div>

              {/* Індикатор суми балів за правилами vs max_score */}
              <div className="flex flex-wrap items-center gap-3">
                <div
                  className={`flex items-center gap-3 rounded-2xl border px-4 py-3 ${
                    isOverMaxScore
                      ? "border-amber-300 bg-amber-50/80 text-amber-950"
                      : isPointsBalanced
                        ? "border-emerald-200 bg-emerald-50/70 text-emerald-950"
                        : "border-indigo-200 bg-indigo-50/70 text-indigo-950"
                  }`}
                >
                  <Scale
                    className={`h-5 w-5 shrink-0 ${
                      isOverMaxScore
                        ? "text-amber-600"
                        : isPointsBalanced
                          ? "text-emerald-600"
                          : "text-indigo-600"
                    }`}
                  />
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-wider">
                      Сума балів правил / Макс. бал
                    </p>
                    <p className="font-mono text-base font-extrabold">
                      {totalDraftPoints.toFixed(1)} / {maxScore.toFixed(1)} б.
                    </p>
                    {manualBonusReserve > 0 && !isOverMaxScore && (
                      <p className="mt-0.5 text-[11px] font-medium text-indigo-800">
                        Резерв для ручної оцінки викладача (творче завдання): +
                        {formatPointsCompact(manualBonusReserve)} б.
                      </p>
                    )}
                  </div>
                </div>

                {isOverMaxScore && totalDraftPoints > 0 && (
                  <button
                    type="button"
                    disabled={syncMaxScoreMutation.isPending}
                    onClick={() =>
                      syncMaxScoreMutation.mutate({
                        max_score: totalDraftPoints,
                      })
                    }
                    className="inline-flex items-center gap-1.5 rounded-xl border border-amber-300 bg-white px-3 py-2 text-xs font-semibold text-amber-900 hover:bg-amber-50"
                    title="Встановити max_score практичної роботи рівним сумі балів усіх правил"
                  >
                    <Scale className="h-3.5 w-3.5" />
                    <span>Вирівняти макс. бал ({totalDraftPoints.toFixed(1)})</span>
                  </button>
                )}
              </div>
            </div>

            {/* Швидкі шаблони правил для поточного парсера */}
            <div className="mt-5 border-t border-slate-100 pt-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-700">
                  <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
                  <span>
                    Швидке додавання типового критерію для{" "}
                    <code>.{activeFormat}</code>:
                  </span>
                </span>
                <span className="text-[11px] text-slate-400">
                  Натисніть на шаблон, щоб додати правило до списку
                </span>
              </div>

              <div className="mt-2.5 flex flex-wrap gap-2">
                {recommendedRuleSpecs.map((spec) => (
                  <button
                    key={spec.type}
                    type="button"
                    onClick={() => handleAddRuleFromSpec(spec)}
                    className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-800 transition-colors hover:border-blue-300 hover:bg-blue-50 hover:text-blue-800"
                  >
                    <Plus className="h-3.5 w-3.5 text-blue-600" />
                    <span>{spec.label}</span>
                    <span className="rounded bg-white px-1.5 py-0.5 font-mono text-[10px] text-slate-500">
                      +{spec.defaultPoints} б.
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </section>

          {/* Інспектор сирого JSONB (якщо увімкнено) */}
          {showJsonInspector && (
            <section className="rounded-2xl border border-slate-300 bg-slate-900 p-5 text-slate-100 shadow-xs">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div>
                  <h3 className="text-sm font-bold text-white">
                    JSONB Контракт <code>grading_rules</code>
                  </h3>
                  <p className="text-xs text-slate-400">
                    Ви можете відредагувати або вставити JSON-масив правил
                    напряму та натиснути «Застосувати JSON до форми».
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleApplyRawJson}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-blue-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-blue-500"
                >
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  <span>Застосувати JSON до форми</span>
                </button>
              </div>
              <textarea
                rows={12}
                value={rawJsonInput}
                onChange={(e) => setRawJsonInput(e.target.value)}
                className="mt-3 w-full rounded-xl border border-slate-700 bg-slate-950 p-3.5 font-mono text-xs leading-relaxed text-emerald-300 focus:border-blue-500 focus:outline-none"
              />
            </section>
          )}

          {/* Список візуальних карток правил автоперевірки */}
          <section className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2 px-1">
              <h3 className="text-sm font-bold text-slate-900">
                Активні правила автоперевірки ({rulesDraft.length})
              </h3>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() =>
                    setRulesDraft(practicalDetail.grading_rules)
                  }
                  className="inline-flex items-center gap-1 rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  <span>Скинути зміни</span>
                </button>

                <button
                  type="button"
                  onClick={handleAddDefaultRule}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-blue-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-blue-700"
                >
                  <Plus className="h-3.5 w-3.5" />
                  <span>Додати правило</span>
                </button>
              </div>
            </div>

            {rulesDraft.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center">
                <Target className="mx-auto h-10 w-10 text-slate-400" />
                <h4 className="mt-3 text-base font-bold text-slate-900">
                  Правила автоперевірки ще не додані
                </h4>
                <p className="mt-1 text-xs text-slate-500">
                  Оберіть один із готових шаблонів вище або натисніть «Додати
                  правило».
                </p>
              </div>
            ) : (
              <div className="space-y-3.5">
                {rulesDraft.map((rule, index) => {
                  const spec = RULE_TYPE_SPECS[rule.type];
                  const isFormatMismatch = spec.format !== activeFormat;

                  return (
                    <article
                      key={`${index}-${rule.id}`}
                      className={`rounded-2xl border bg-white p-5 shadow-xs transition-all ${
                        isFormatMismatch
                          ? "border-amber-300"
                          : "border-slate-200"
                      }`}
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="inline-flex h-6 w-6 items-center justify-center rounded-lg bg-slate-900 font-mono text-xs font-bold text-white">
                            {index + 1}
                          </span>
                          <span className="font-mono text-xs font-bold text-slate-800">
                            {rule.id}
                          </span>
                          <span
                            className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-bold ${
                              FORMAT_BADGE_CONFIG[spec.format].badgeClass
                            }`}
                          >
                            .{spec.format}
                          </span>
                          {isFormatMismatch && (
                            <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-[11px] font-semibold text-amber-900">
                              Увага: тип правила ({spec.format}) відрізняється
                              від формату роботи ({activeFormat})
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-1">
                          <button
                            type="button"
                            disabled={index === 0}
                            onClick={() => handleMoveRule(index, -1)}
                            className="rounded-lg border border-slate-200 p-1.5 text-slate-600 hover:bg-slate-50 disabled:opacity-40"
                            title="Перемістити вище"
                          >
                            <ArrowUp className="h-3.5 w-3.5" />
                          </button>
                          <button
                            type="button"
                            disabled={index === rulesDraft.length - 1}
                            onClick={() => handleMoveRule(index, 1)}
                            className="rounded-lg border border-slate-200 p-1.5 text-slate-600 hover:bg-slate-50 disabled:opacity-40"
                            title="Перемістити нижче"
                          >
                            <ArrowDown className="h-3.5 w-3.5" />
                          </button>
                          <button
                            type="button"
                            onClick={() => handleDuplicateRule(index)}
                            className="rounded-lg border border-slate-200 p-1.5 text-slate-600 hover:bg-slate-50"
                            title="Дублювати правило"
                          >
                            <Copy className="h-3.5 w-3.5" />
                          </button>
                          <button
                            type="button"
                            onClick={() => handleDeleteRule(index)}
                            className="rounded-lg border border-rose-200 p-1.5 text-rose-600 hover:bg-rose-50"
                            title="Видалити правило"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </div>

                      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-12">
                        {/* Ідентифікатор правила (id) */}
                        <div className="sm:col-span-3">
                          <label className="block text-xs font-semibold text-slate-700">
                            ID правила (<code>id</code>)
                          </label>
                          <input
                            type="text"
                            required
                            value={rule.id}
                            onChange={(e) =>
                              handleUpdateRule(index, { id: e.target.value })
                            }
                            className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 font-mono text-xs font-semibold text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
                          />
                        </div>

                        {/* Тип перевірки (type) */}
                        <div className="sm:col-span-6">
                          <label className="block text-xs font-semibold text-slate-700">
                            Стратегія парсера (<code>type</code>)
                          </label>
                          <select
                            value={rule.type}
                            onChange={(e) =>
                              handleChangeRuleType(
                                index,
                                e.target.value as GradingRuleType
                              )
                            }
                            className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
                          >
                            {GRADING_RULE_TYPES.map((ruleType) => {
                              const itemSpec = RULE_TYPE_SPECS[ruleType];
                              return (
                                <option key={ruleType} value={ruleType}>
                                  [{itemSpec.format.toUpperCase()}]{" "}
                                  {itemSpec.label} ({ruleType})
                                </option>
                              );
                            })}
                          </select>
                        </div>

                        {/* Вага в балах (points) */}
                        <div className="sm:col-span-3">
                          <label className="block text-xs font-semibold text-slate-700">
                            Вага критерію (<code>points</code>)
                          </label>
                          <input
                            type="number"
                            step="0.5"
                            min={0.5}
                            max={100}
                            required
                            value={rule.points}
                            onChange={(e) =>
                              handleUpdateRule(index, {
                                points: Number(e.target.value) || 0.5,
                              })
                            }
                            className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 font-mono text-xs font-bold text-blue-700 focus:border-blue-500 focus:bg-white focus:outline-none"
                          />
                        </div>

                        {/* Ціль інспекції (target) */}
                        <div className="sm:col-span-6">
                          <label className="block text-xs font-semibold text-slate-700">
                            Ціль інспекції (<code>target</code>)
                          </label>
                          <input
                            type="text"
                            required
                            value={rule.target}
                            onChange={(e) =>
                              handleUpdateRule(index, {
                                target: e.target.value,
                              })
                            }
                            placeholder={spec.defaultTarget}
                            className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 font-mono text-xs text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
                          />
                          <p className="mt-1 text-[11px] text-slate-500">
                            Підказка: {spec.targetHint}
                          </p>
                        </div>

                        {/* Очікуване значення (expected) */}
                        <div className="sm:col-span-6">
                          <label className="block text-xs font-semibold text-slate-700">
                            Очікуваний еталон (<code>expected</code>)
                          </label>
                          <input
                            type="text"
                            required
                            value={rule.expected}
                            onChange={(e) =>
                              handleUpdateRule(index, {
                                expected: e.target.value,
                              })
                            }
                            placeholder={spec.defaultExpected}
                            className="mt-1 w-full rounded-xl border border-emerald-200 bg-emerald-50/40 px-3 py-2 font-mono text-xs font-semibold text-emerald-950 focus:border-emerald-500 focus:bg-white focus:outline-none"
                          />
                          <p className="mt-1 text-[11px] text-slate-500">
                            Підказка: {spec.expectedHint}
                          </p>
                        </div>

                        {/* Людиночитаний опис критерію (description) */}
                        <div className="sm:col-span-12">
                          <label className="block text-xs font-semibold text-slate-700">
                            Опис критерію для звіту студента (
                            <code>description</code>)
                          </label>
                          <input
                            type="text"
                            required
                            value={rule.description}
                            onChange={(e) =>
                              handleUpdateRule(index, {
                                description: e.target.value,
                              })
                            }
                            className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs font-medium text-slate-900 focus:border-blue-500 focus:bg-white focus:outline-none"
                          />
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}
          </section>

          {/* Нижня панель збереження правил */}
          <div className="sticky bottom-4 z-10 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white/95 p-4 shadow-lg backdrop-blur-xs">
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600">
              <div>
                Усього правил:{" "}
                <span className="font-bold text-slate-900">
                  {rulesDraft.length}
                </span>{" "}
                • Сума балів:{" "}
                <span className="font-mono font-bold text-blue-700">
                  {totalDraftPoints.toFixed(1)} б.
                </span>
                {!syncMaxScore && (
                  <span className="ml-1.5 font-medium text-indigo-700">
                    • Резерв для ручної оцінки викладача (творче завдання): +
                    {formatPointsCompact(manualBonusReserve)} б. (макс. бал
                    залишиться {maxScore.toFixed(1)} б.)
                  </span>
                )}
                {syncMaxScore && manualBonusReserve > 0 && (
                  <span className="ml-1.5 font-medium text-amber-700">
                    (увага: max_score зменшиться з {maxScore.toFixed(1)} до{" "}
                    {totalDraftPoints.toFixed(1)} б.)
                  </span>
                )}
              </div>

              <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100">
                <input
                  type="checkbox"
                  checked={syncMaxScore}
                  onChange={(e) => setSyncMaxScore(e.target.checked)}
                  className="h-4 w-4 rounded accent-blue-600"
                />
                <span>
                  Автоматично синхронізувати <code>max_score</code> із сумою
                  балів правил
                </span>
              </label>
            </div>

            <button
              type="submit"
              disabled={saveRulesMutation.isPending}
              className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-2.5 text-xs font-semibold text-white shadow-2xs hover:bg-blue-700 disabled:opacity-60"
            >
              <Save className="h-4 w-4" />
              <span>
                {saveRulesMutation.isPending
                  ? "Збереження правил у БД..."
                  : "Зберегти правила автоперевірки"}
              </span>
            </button>
          </div>
        </form>

          {/* Панель тестування чернеткових або збережених правил (Dry-Run) */}
          <section
            className="rounded-2xl border border-indigo-200 bg-white p-5 shadow-xs sm:p-6"
            aria-label="Протестувати правила (Dry-Run)"
          >
            <div className="flex flex-col justify-between gap-3 border-b border-slate-100 pb-4 sm:flex-row sm:items-center">
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-indigo-200 bg-indigo-50 text-indigo-600">
                  <FlaskConical className="h-5 w-5" />
                </div>
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-base font-bold text-slate-900">
                      Протестувати правила (Dry-Run)
                    </h3>
                    <span className="rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-800">
                      Без запису в БД і на диск
                    </span>
                  </div>
                  <p className="mt-0.5 text-xs text-slate-600">
                    Запустіть перевірку еталонного файлу або HTML-коду за{" "}
                    <span className="font-semibold text-slate-800">
                      поточними правилами з форми вище
                    </span>{" "}
                    (навіть до натискання «Зберегти»), щоб упевнитися у
                    коректності кожного критерію.
                  </p>
                </div>
              </div>

              {activeCatalogEntry !== null && (
                <Link
                  to={`/teacher/courses/${activeCatalogEntry.courseId}/modules/${activeCatalogEntry.moduleId}/preview`}
                  className="inline-flex shrink-0 items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100"
                >
                  <Eye className="h-3.5 w-3.5 text-indigo-600" />
                  <span>Відкрити інтерактивний preview</span>
                </Link>
              )}
            </div>

            <div className="mt-4 space-y-4">
              {practicalDetail.variants.length > 1 && (
                <div className="max-w-md">
                  <label
                    htmlFor="dry-run-variant-select"
                    className="block text-xs font-semibold text-slate-700"
                  >
                    Номер індивідуального варіанта для підстановки плейсхолдерів
                  </label>
                  <select
                    id="dry-run-variant-select"
                    value={dryRunVariantNumber}
                    onChange={(event) => {
                      setDryRunVariantNumber(Number(event.target.value) || 1);
                      setDryRunResult(null);
                    }}
                    className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-900 focus:border-indigo-500 focus:bg-white focus:outline-none"
                  >
                    {practicalDetail.variants.map((variant, idx) => {
                      const num = idx + 1;
                      return (
                        <option key={num} value={num}>
                          Варіант №{num} — {variant.title}
                        </option>
                      );
                    })}
                  </select>
                </div>
              )}

              {activeFormat === "html" ? (
                <div className="space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <label
                      htmlFor="dry-run-html-textarea"
                      className="text-xs font-semibold text-slate-700"
                    >
                      Тестовий HTML5-код для перевірки (BeautifulSoup4)
                    </label>
                    <button
                      type="button"
                      onClick={() => setDryRunHtmlCode(DEFAULT_DRY_RUN_HTML)}
                      className="text-[11px] font-semibold text-indigo-600 hover:text-indigo-800"
                    >
                      Відновити базовий шаблон
                    </button>
                  </div>
                  <textarea
                    id="dry-run-html-textarea"
                    rows={8}
                    value={dryRunHtmlCode}
                    onChange={(event) => setDryRunHtmlCode(event.target.value)}
                    placeholder="<!DOCTYPE html><html lang='uk'>...</html>"
                    className="w-full rounded-xl border border-slate-200 bg-slate-900 p-3.5 font-mono text-xs leading-relaxed text-emerald-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              ) : (
                <div>
                  <input
                    ref={dryRunFileInputRef}
                    id={`dry-run-file-${practicalDetail.id}`}
                    type="file"
                    accept={DRY_RUN_FILE_ACCEPT[activeFormat]}
                    onChange={handleDryRunFileInputChange}
                    className="sr-only"
                  />

                  <div
                    onDragOver={handleDryRunDragOver}
                    onDragLeave={handleDryRunDragLeave}
                    onDrop={handleDryRunDrop}
                    className={`flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-5 text-center transition-colors ${
                      dryRunIsDragActive
                        ? "border-indigo-500 bg-indigo-50/70"
                        : dryRunFile !== null
                          ? "border-emerald-300 bg-emerald-50/40"
                          : "border-slate-300 bg-slate-50/60 hover:border-indigo-400"
                    }`}
                  >
                    {dryRunFile === null ? (
                      <>
                        <UploadCloud className="h-7 w-7 text-indigo-600" />
                        <p className="mt-2 text-xs font-bold text-slate-900">
                          Перетягніть тестовий файл{" "}
                          <span className="font-mono text-indigo-700">
                            .{activeFormat}
                          </span>{" "}
                          сюди або оберіть із комп&apos;ютера
                        </p>
                        <label
                          htmlFor={`dry-run-file-${practicalDetail.id}`}
                          className="mt-3 inline-flex cursor-pointer items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-3.5 py-1.5 text-xs font-semibold text-slate-800 hover:border-indigo-400 hover:bg-indigo-50"
                        >
                          <UploadCloud className="h-3.5 w-3.5 text-indigo-600" />
                          <span>Обрати файл .{activeFormat}</span>
                        </label>
                      </>
                    ) : (
                      <div className="flex w-full max-w-xl flex-col items-center justify-between gap-3 rounded-xl border border-emerald-200 bg-white p-3.5 text-left sm:flex-row">
                        <div className="flex min-w-0 items-center gap-2.5">
                          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-emerald-100 text-emerald-700">
                            <FileCheck2 className="h-4 w-4" />
                          </div>
                          <div className="min-w-0">
                            <p className="truncate text-xs font-bold text-slate-900">
                              {dryRunFile.name}
                            </p>
                            <p className="text-[11px] text-slate-500">
                              Розмір: {formatFileSizeCompact(dryRunFile.size)} •
                              Формат: .{activeFormat}
                            </p>
                          </div>
                        </div>
                        <div className="flex shrink-0 items-center gap-2">
                          <label
                            htmlFor={`dry-run-file-${practicalDetail.id}`}
                            className="cursor-pointer rounded-lg border border-slate-300 bg-white px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                          >
                            Замінити
                          </label>
                          <button
                            type="button"
                            onClick={handleClearDryRunFile}
                            disabled={dryRunMutation.isPending}
                            className="inline-flex items-center gap-1 rounded-lg border border-rose-200 bg-rose-50 px-2.5 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-100 disabled:opacity-50"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                            <span>Очистити</span>
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {dryRunError !== null && (
                <div
                  className="flex items-start gap-2.5 rounded-xl border border-rose-200 bg-rose-50 p-3.5 text-xs font-medium text-rose-800"
                  role="alert"
                >
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" />
                  <span>{dryRunError}</span>
                </div>
              )}

              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-[11px] text-slate-500">
                  У тестову перевірку передаються поточні{" "}
                  <span className="font-semibold text-slate-700">
                    {rulesDraft.length} правил(о)
                  </span>{" "}
                  із форми редактора (варіант №{dryRunVariantNumber}).
                </p>
                <button
                  type="button"
                  onClick={handleRunDryRun}
                  disabled={
                    dryRunMutation.isPending ||
                    rulesDraft.length === 0 ||
                    (activeFormat !== "html" && dryRunFile === null) ||
                    (activeFormat === "html" &&
                      dryRunHtmlCode.trim().length === 0)
                  }
                  className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-xs font-semibold text-white shadow-2xs transition-colors hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {dryRunMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Виконується перевірка...</span>
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4" />
                      <span>Запустити тестову перевірку</span>
                    </>
                  )}
                </button>
              </div>

              {dryRunResult !== null && (
                <DryRunResultPanel
                  result={dryRunResult}
                  isDraftRules
                  onClear={() => setDryRunResult(null)}
                />
              )}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

export default RuleBuilderPage;
