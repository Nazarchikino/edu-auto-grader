import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactElement,
} from "react";
import Editor from "@monaco-editor/react";
import {
  AlertTriangle,
  Check,
  Code2,
  Columns,
  Eye,
  History,
  Loader2,
  Moon,
  Play,
  RotateCcw,
  Send,
  ShieldCheck,
  Sparkles,
  Sun,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import type { PracticalVariant } from "../../types/course";

export interface HtmlSandboxProps {
  practicalId: string;
  practicalTitle: string;
  variant: PracticalVariant;
  variantNumber: number;
  userId?: string | null;
  isSubmitting: boolean;
  onSubmitCode: (rawCode: string) => void;
}

type SandboxViewMode = "split" | "editor" | "preview";
type EditorColorTheme = "vs-dark" | "light";

type DraftSaveState =
  | { status: "idle" }
  | { status: "pending" }
  | { status: "saved"; savedAt: Date }
  | { status: "restored" }
  | { status: "error" };

interface PendingDraftState {
  key: string;
  code: string;
  dirty: boolean;
}

const DRAFT_AUTOSAVE_DEBOUNCE_MS = 400;

interface QuickSnippet {
  id: string;
  label: string;
  code: string;
}

const QUICK_HTML_SNIPPETS: readonly QuickSnippet[] = [
  {
    id: "header",
    label: "+ <header> з <h1>",
    code: [
      "<header>",
      "  <h1>Заголовок навчальної сторінки</h1>",
      "  <p>Підзаголовок індивідуального варіанта</p>",
      "</header>",
    ].join("\n"),
  },
  {
    id: "table4",
    label: "+ Таблиця (4 рядки)",
    code: [
      "<table>",
      "  <thead>",
      "    <tr>",
      "      <th>№</th>",
      "      <th>Назва</th>",
      "      <th>Значення</th>",
      "    </tr>",
      "  </thead>",
      "  <tbody>",
      "    <tr>",
      "      <td>1</td>",
      "      <td>Елемент 1</td>",
      "      <td>Виконано</td>",
      "    </tr>",
      "    <tr>",
      "      <td>2</td>",
      "      <td>Елемент 2</td>",
      "      <td>Виконано</td>",
      "    </tr>",
      "    <tr>",
      "      <td>3</td>",
      "      <td>Елемент 3</td>",
      "      <td>У процесі</td>",
      "    </tr>",
      "  </tbody>",
      "</table>",
    ].join("\n"),
  },
  {
    id: "form",
    label: "+ Форма <form>",
    code: [
      '<form action="#" method="post">',
      '  <label for="student-name">ПІБ студента:</label>',
      '  <input id="student-name" name="student_name" type="text" required />',
      '  <button type="submit">Надіслати</button>',
      "</form>",
    ].join("\n"),
  },
];

const MINIMAL_STARTER_HTML_TEMPLATE = `<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Практична робота</title>
</head>
<body>
  <!-- Виконайте завдання тут -->
</body>
</html>`;

function buildStarterHtmlTemplate(): string {
  return MINIMAL_STARTER_HTML_TEMPLATE;
}

function buildDraftStorageKey(
  userId: string,
  practicalId: string,
  variantNumber: number
): string {
  return `edu_html_draft:${userId}:${practicalId}:${variantNumber}`;
}

function readDraftFromSessionStorage(storageKey: string): string | null {
  try {
    const saved = window.sessionStorage.getItem(storageKey);
    if (saved !== null && saved.trim().length > 0) {
      return saved;
    }
    return null;
  } catch {
    return null;
  }
}

function writeDraftToSessionStorage(
  storageKey: string,
  code: string
): boolean {
  try {
    window.sessionStorage.setItem(storageKey, code);
    return true;
  } catch {
    return false;
  }
}

function removeDraftFromSessionStorage(storageKey: string): void {
  try {
    window.sessionStorage.removeItem(storageKey);
  } catch {
    // Ігноруємо обмеження браузера на доступ до sessionStorage
  }
}

function formatDraftSavedTime(date: Date): string {
  return date.toLocaleTimeString("uk-UA", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function HtmlSandbox({
  practicalId,
  practicalTitle,
  variant,
  variantNumber,
  userId,
  isSubmitting,
  onSubmitCode,
}: HtmlSandboxProps): ReactElement {
  const { user } = useAuth();
  const starterTemplate = useMemo(() => buildStarterHtmlTemplate(), []);

  const resolvedUserId =
    userId !== undefined && userId !== null && userId.trim().length > 0
      ? userId.trim()
      : user !== null && user.id.trim().length > 0
        ? user.id.trim()
        : "anon";

  const effectiveVariantNumber =
    variantNumber > 0 ? variantNumber : variant.variant_number;

  const draftStorageKey = useMemo(
    () =>
      buildDraftStorageKey(resolvedUserId, practicalId, effectiveVariantNumber),
    [resolvedUserId, practicalId, effectiveVariantNumber]
  );

  const initialDraftSnapshot = useMemo(() => {
    const savedDraft = readDraftFromSessionStorage(draftStorageKey);
    if (savedDraft !== null) {
      return {
        code: savedDraft,
        status: { status: "restored" } as DraftSaveState,
      };
    }
    return {
      code: starterTemplate,
      status: { status: "idle" } as DraftSaveState,
    };
  }, [draftStorageKey, starterTemplate]);

  const [code, setCode] = useState<string>(initialDraftSnapshot.code);
  const [previewDoc, setPreviewDoc] = useState<string>(
    initialDraftSnapshot.code
  );
  const [draftState, setDraftState] = useState<DraftSaveState>(
    initialDraftSnapshot.status
  );
  const [autoPreview, setAutoPreview] = useState<boolean>(true);
  const [viewMode, setViewMode] = useState<SandboxViewMode>("split");
  const [editorTheme, setEditorTheme] = useState<EditorColorTheme>("vs-dark");

  const loadedDraftKeyRef = useRef<string>(draftStorageKey);
  const pendingDraftRef = useRef<PendingDraftState>({
    key: draftStorageKey,
    code: initialDraftSnapshot.code,
    dirty: false,
  });

  useEffect(() => {
    if (loadedDraftKeyRef.current === draftStorageKey) {
      return;
    }

    const previousPending = pendingDraftRef.current;
    if (previousPending.dirty) {
      if (previousPending.code.trim().length === 0) {
        removeDraftFromSessionStorage(previousPending.key);
      } else {
        writeDraftToSessionStorage(previousPending.key, previousPending.code);
      }
      previousPending.dirty = false;
    }

    loadedDraftKeyRef.current = draftStorageKey;
    const savedDraft = readDraftFromSessionStorage(draftStorageKey);
    const nextCode = savedDraft ?? starterTemplate;
    const nextDraftState: DraftSaveState =
      savedDraft !== null ? { status: "restored" } : { status: "idle" };

    pendingDraftRef.current = {
      key: draftStorageKey,
      code: nextCode,
      dirty: false,
    };
    setCode(nextCode);
    setPreviewDoc(nextCode);
    setDraftState(nextDraftState);
  }, [draftStorageKey, starterTemplate]);

  useEffect(() => {
    if (
      !pendingDraftRef.current.dirty ||
      pendingDraftRef.current.key !== draftStorageKey
    ) {
      return;
    }

    const timerId = window.setTimeout(() => {
      if (
        !pendingDraftRef.current.dirty ||
        pendingDraftRef.current.key !== draftStorageKey
      ) {
        return;
      }

      if (code.trim().length === 0) {
        removeDraftFromSessionStorage(draftStorageKey);
        pendingDraftRef.current.dirty = false;
        setDraftState({ status: "idle" });
        return;
      }

      const saved = writeDraftToSessionStorage(draftStorageKey, code);
      pendingDraftRef.current.dirty = false;
      setDraftState(
        saved ? { status: "saved", savedAt: new Date() } : { status: "error" }
      );
    }, DRAFT_AUTOSAVE_DEBOUNCE_MS);

    return () => window.clearTimeout(timerId);
  }, [code, draftStorageKey]);

  useEffect(() => {
    return () => {
      const pending = pendingDraftRef.current;
      if (!pending.dirty) {
        return;
      }
      if (pending.code.trim().length === 0) {
        removeDraftFromSessionStorage(pending.key);
      } else {
        writeDraftToSessionStorage(pending.key, pending.code);
      }
      pending.dirty = false;
    };
  }, []);

  useEffect(() => {
    if (!autoPreview) {
      return;
    }
    const timerId = window.setTimeout(() => {
      setPreviewDoc(code);
    }, 200);
    return () => window.clearTimeout(timerId);
  }, [code, autoPreview]);

  const lineCount = useMemo(() => {
    if (code.length === 0) {
      return 0;
    }
    return code.split(/\r\n|\r|\n/).length;
  }, [code]);

  const handleCodeChange = (nextValue: string): void => {
    if (nextValue === code) {
      return;
    }
    pendingDraftRef.current = {
      key: draftStorageKey,
      code: nextValue,
      dirty: true,
    };
    setCode(nextValue);
    setDraftState({ status: "pending" });
  };

  const handleResetTemplate = (): void => {
    pendingDraftRef.current = {
      key: draftStorageKey,
      code: starterTemplate,
      dirty: false,
    };
    removeDraftFromSessionStorage(draftStorageKey);
    setCode(starterTemplate);
    setPreviewDoc(starterTemplate);
    setDraftState({ status: "idle" });
  };

  const handleInsertSnippet = (snippetCode: string): void => {
    const updated =
      code.trim().length === 0 ? snippetCode : `${code.trimEnd()}\n\n${snippetCode}\n`;
    handleCodeChange(updated);
    if (autoPreview) {
      setPreviewDoc(updated);
    }
  };

  const handleManualRefreshPreview = (): void => {
    setPreviewDoc(code);
  };

  const handleSubmit = (): void => {
    if (code.trim().length === 0 || isSubmitting) {
      return;
    }
    onSubmitCode(code);
  };

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs">
      {/* Верхня панель керування HTML-пісочницею */}
      <div className="flex flex-col justify-between gap-3 border-b border-slate-200 bg-slate-900 px-4 py-3.5 text-slate-100 sm:flex-row sm:items-center sm:px-5">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white">
            <Code2 className="h-4 w-4" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="text-sm font-bold text-white">
                Інтерактивна HTML5-пісочниця
              </h3>
              <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/40 bg-emerald-500/15 px-2 py-0.5 text-[11px] font-semibold text-emerald-300">
                <ShieldCheck className="h-3 w-3" />
                iframe sandbox
              </span>
            </div>
            <p className="text-xs text-slate-400">
              {practicalTitle} • Варіант №{variantNumber} ({lineCount} рядків,{" "}
              {code.length} симв.)
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Режим відображення: Split / Editor / Preview */}
          <div
            className="inline-flex rounded-lg border border-slate-700 bg-slate-800 p-0.5"
            role="group"
            aria-label="Режим відображення пісочниці"
          >
            <button
              type="button"
              onClick={() => setViewMode("split")}
              className={`inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-semibold transition-colors ${
                viewMode === "split"
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              <Columns className="h-3.5 w-3.5" />
              <span>Split</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode("editor")}
              className={`inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-semibold transition-colors ${
                viewMode === "editor"
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              <Code2 className="h-3.5 w-3.5" />
              <span>Код</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode("preview")}
              className={`inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-semibold transition-colors ${
                viewMode === "preview"
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              <Eye className="h-3.5 w-3.5" />
              <span>Прев&apos;ю</span>
            </button>
          </div>

          {/* Перемикач теми редактора Monaco */}
          <button
            type="button"
            onClick={() =>
              setEditorTheme((prev) =>
                prev === "vs-dark" ? "light" : "vs-dark"
              )
            }
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-2.5 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700"
            title="Перемкнути тему редактора"
          >
            {editorTheme === "vs-dark" ? (
              <>
                <Sun className="h-3.5 w-3.5 text-amber-400" />
                <span>Світла</span>
              </>
            ) : (
              <>
                <Moon className="h-3.5 w-3.5 text-blue-300" />
                <span>Темна</span>
              </>
            )}
          </button>

          {/* Кнопка скидання до початкового мінімального шаблону */}
          <button
            type="button"
            onClick={handleResetTemplate}
            disabled={isSubmitting}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-2.5 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700 disabled:opacity-50"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Скинути шаблон</span>
          </button>
        </div>
      </div>

      {/* Панель швидкої вставки семантичних блоків та керування автооновленням */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 bg-slate-50 px-4 py-2.5 sm:px-5">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="inline-flex items-center gap-1 text-xs font-semibold text-slate-600">
            <Sparkles className="h-3.5 w-3.5 text-blue-600" />
            Швидкі блоки:
          </span>
          {QUICK_HTML_SNIPPETS.map((snippet) => (
            <button
              key={snippet.id}
              type="button"
              onClick={() => handleInsertSnippet(snippet.code)}
              disabled={isSubmitting}
              className="rounded-md border border-slate-300 bg-white px-2.5 py-1 font-mono text-xs font-medium text-slate-700 hover:border-blue-400 hover:bg-blue-50 hover:text-blue-800 disabled:opacity-50"
            >
              {snippet.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <label className="inline-flex cursor-pointer items-center gap-1.5 text-xs font-medium text-slate-700">
            <input
              type="checkbox"
              checked={autoPreview}
              onChange={(event) => setAutoPreview(event.target.checked)}
              className="h-3.5 w-3.5 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
            />
            <span>Автооновлення прев&apos;ю</span>
          </label>

          {!autoPreview && (
            <button
              type="button"
              onClick={handleManualRefreshPreview}
              className="inline-flex items-center gap-1 rounded-md bg-slate-800 px-2.5 py-1 text-xs font-semibold text-white hover:bg-slate-700"
            >
              <Play className="h-3 w-3" />
              <span>Оновити прев&apos;ю</span>
            </button>
          )}
        </div>
      </div>

      {/* Робоча область: Monaco Editor + ізольований <iframe sandbox> */}
      <div
        className={`grid grid-cols-1 ${
          viewMode === "split" ? "lg:grid-cols-2" : ""
        } divide-y divide-slate-200 lg:divide-x lg:divide-y-0`}
      >
        {viewMode !== "preview" && (
          <div className="flex flex-col">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 bg-slate-100 px-4 py-2 text-xs font-semibold text-slate-700">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono">index.html (Monaco Editor)</span>
                {draftState.status === "pending" && (
                  <span
                    className="inline-flex items-center gap-1 rounded-full border border-slate-300 bg-white px-2 py-0.5 text-[11px] font-medium text-slate-600"
                    role="status"
                    aria-live="polite"
                  >
                    <Loader2 className="h-3 w-3 animate-spin text-slate-500" />
                    <span>Збереження чернетки...</span>
                  </span>
                )}
                {draftState.status === "saved" && (
                  <span
                    className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[11px] font-medium text-emerald-700"
                    role="status"
                    aria-live="polite"
                  >
                    <Check className="h-3 w-3" />
                    <span>
                      Чернетку збережено ·{" "}
                      {formatDraftSavedTime(draftState.savedAt)}
                    </span>
                  </span>
                )}
                {draftState.status === "restored" && (
                  <span
                    className="inline-flex items-center gap-1 rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-[11px] font-medium text-blue-700"
                    role="status"
                    aria-live="polite"
                  >
                    <History className="h-3 w-3" />
                    <span>Чернетку відновлено</span>
                  </span>
                )}
                {draftState.status === "error" && (
                  <span
                    className="inline-flex items-center gap-1 rounded-full border border-amber-200 bg-amber-50 px-2 py-0.5 text-[11px] font-medium text-amber-700"
                    role="status"
                    aria-live="polite"
                  >
                    <AlertTriangle className="h-3 w-3" />
                    <span>Автозбереження недоступне</span>
                  </span>
                )}
              </div>
              <span className="text-[11px] font-normal text-slate-500">
                Стандарт: HTML5 • Кодування: UTF-8
              </span>
            </div>
            <div className="h-[460px] w-full">
              <Editor
                height="460px"
                defaultLanguage="html"
                language="html"
                theme={editorTheme}
                value={code}
                onChange={(nextValue) => handleCodeChange(nextValue ?? "")}
                options={{
                  minimap: { enabled: false },
                  fontSize: 13,
                  lineNumbers: "on",
                  wordWrap: "on",
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 2,
                  formatOnPaste: true,
                }}
              />
            </div>
          </div>
        )}

        {viewMode !== "editor" && (
          <div className="flex flex-col bg-slate-100/60">
            <div className="flex items-center justify-between border-b border-slate-200 bg-slate-100 px-4 py-2 text-xs font-semibold text-slate-700">
              <span className="inline-flex items-center gap-1.5">
                <Eye className="h-3.5 w-3.5 text-blue-600" />
                Живий рендеринг браузера
              </span>
              <span className="font-mono text-[11px] font-normal text-slate-500">
                &lt;iframe sandbox=&quot;&quot;&gt; (скрипти заблоковано)
              </span>
            </div>
            <div className="h-[460px] w-full bg-white">
              <iframe
                title={`Живе прев'ю HTML5 — Варіант №${variantNumber}`}
                sandbox=""
                srcDoc={previewDoc}
                className="h-full w-full border-0 bg-white"
              />
            </div>
          </div>
        )}
      </div>

      {/* Нижня панель відправки HTML-коду на серверний валідатор BeautifulSoup4 */}
      <div className="flex flex-col items-stretch justify-between gap-3 border-t border-slate-200 bg-slate-50 px-4 py-3.5 sm:flex-row sm:items-center sm:px-5">
        <p className="text-xs text-slate-600">
          Серверне ядро перевірить DOM-дерево через{" "}
          <span className="font-mono font-semibold text-slate-800">
            BeautifulSoup4
          </span>{" "}
          за критеріями вашого варіанта №{variantNumber}.
        </p>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={isSubmitting || code.trim().length === 0}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-xs font-semibold text-white shadow-xs transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Автоперевірка HTML-коду...</span>
            </>
          ) : (
            <>
              <Send className="h-4 w-4" />
              <span>Надіслати на перевірку</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export default HtmlSandbox;
