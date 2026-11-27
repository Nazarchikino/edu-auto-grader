import { useMemo, useState, type ReactElement } from "react";
import { Link } from "react-router-dom";
import {
  Award,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Fingerprint,
  FlaskConical,
  SlidersHorizontal,
  Sparkles,
  X,
  XCircle,
} from "lucide-react";
import type { DryRunGradingResponse } from "../../types/api";

export interface DryRunResultPanelProps {
  result: DryRunGradingResponse;
  isDraftRules?: boolean;
  rulesEditorLink?: string;
  onClear?: () => void;
}

function formatPoints(value: number): string {
  const rounded = Math.round(value * 100) / 100;
  return Number.isInteger(rounded)
    ? String(rounded)
    : rounded.toFixed(2).replace(/0$/, "");
}

export function DryRunResultPanel({
  result,
  isDraftRules = false,
  rulesEditorLink,
  onClear,
}: DryRunResultPanelProps): ReactElement {
  const [isMetadataExpanded, setIsMetadataExpanded] = useState<boolean>(true);

  const report = result.grading_report;
  const totalRules = report.results.length;

  const metadataEntries = useMemo<Array<{ label: string; value: string }>>(() => {
    const meta = result.extracted_metadata;
    const entries: Array<{ label: string; value: string }> = [];

    if (typeof meta.creator === "string" && meta.creator.trim().length > 0) {
      entries.push({ label: "Автор (dc:creator)", value: meta.creator });
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
      entries.push({ label: "Створено (dcterms:created)", value: meta.created });
    }
    if (typeof meta.modified === "string" && meta.modified.trim().length > 0) {
      entries.push({
        label: "Змінено (dcterms:modified)",
        value: meta.modified,
      });
    }
    if (typeof meta.revision === "string" && meta.revision.trim().length > 0) {
      entries.push({ label: "Ревізія (cp:revision)", value: meta.revision });
    }
    if (
      typeof meta.content_fingerprint === "string" &&
      meta.content_fingerprint.trim().length > 0
    ) {
      entries.push({
        label: "Структурний відбиток (content_fingerprint)",
        value: meta.content_fingerprint,
      });
    }
    if (typeof meta.has_unique_content === "boolean") {
      entries.push({
        label: "Унікальний вміст для антиплагіату",
        value: meta.has_unique_content ? "Так" : "Ні (шаблон / замало вмісту)",
      });
    }

    return entries;
  }, [result.extracted_metadata]);

  return (
    <div
      className="rounded-2xl border border-indigo-200 bg-indigo-50/40 p-5 shadow-xs sm:p-6"
      role="status"
      aria-label="Результат тестової перевірки Dry-Run"
    >
      <div className="flex flex-col justify-between gap-4 border-b border-indigo-200/80 pb-4 sm:flex-row sm:items-start">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-indigo-600 px-3 py-1 text-xs font-bold text-white">
              <Award className="h-3.5 w-3.5" />
              Автооцінка: {formatPoints(result.auto_score)} /{" "}
              {formatPoints(result.auto_max_score)} б.
            </span>

            {result.manual_bonus_max > 0 && (
              <span className="inline-flex items-center gap-1 rounded-full border border-indigo-300 bg-white px-2.5 py-1 text-xs font-semibold text-indigo-800">
                <Sparkles className="h-3 w-3 text-indigo-600" />
                +{formatPoints(result.manual_bonus_max)} б. резерв до{" "}
                {formatPoints(result.max_score)} б.
              </span>
            )}

            <span className="inline-flex items-center gap-1 rounded-full border border-slate-300 bg-white px-2.5 py-1 text-xs font-semibold text-slate-700">
              Варіант №{result.variant_number}
            </span>

            <span className="inline-flex items-center gap-1 rounded-full border border-amber-300 bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-900">
              <FlaskConical className="h-3 w-3 text-amber-600" />
              Dry-Run (без запису в БД)
            </span>

            {isDraftRules && (
              <span className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-[11px] font-semibold text-blue-800">
                Поточні чернеткові правила
              </span>
            )}
          </div>

          <p className="text-xs text-slate-700">
            Виконано правил:{" "}
            <span className="font-bold text-emerald-700">
              {report.passed_count}
            </span>{" "}
            • Помилок:{" "}
            <span className="font-bold text-rose-700">
              {report.failed_count}
            </span>{" "}
            • Усього критеріїв:{" "}
            <span className="font-bold text-slate-900">{totalRules}</span>
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {rulesEditorLink !== undefined && (
            <Link
              to={rulesEditorLink}
              className="inline-flex items-center gap-1.5 rounded-xl border border-indigo-200 bg-white px-3 py-1.5 text-xs font-semibold text-indigo-700 hover:bg-indigo-50"
            >
              <SlidersHorizontal className="h-3.5 w-3.5" />
              <span>Налаштувати правила</span>
            </Link>
          )}
          {onClear !== undefined && (
            <button
              type="button"
              onClick={onClear}
              className="inline-flex items-center gap-1 rounded-xl border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50"
              title="Очистити звіт"
            >
              <X className="h-3.5 w-3.5" />
              <span>Сховати</span>
            </button>
          )}
        </div>
      </div>

      {/* Витягнуті метадані та content_fingerprint */}
      <div className="mt-4 rounded-xl border border-slate-200 bg-white">
        <button
          type="button"
          onClick={() => setIsMetadataExpanded((prev) => !prev)}
          className="flex w-full items-center justify-between px-4 py-2.5 text-left text-xs font-semibold text-slate-800 hover:bg-slate-50"
        >
          <span className="inline-flex items-center gap-2">
            <Fingerprint className="h-4 w-4 text-indigo-600" />
            <span>
              Витягнуті метадані та відбиток файлу (
              {metadataEntries.length > 0
                ? `${metadataEntries.length} полів`
                : "немає даних"}
              )
            </span>
          </span>
          {isMetadataExpanded ? (
            <ChevronUp className="h-4 w-4 text-slate-500" />
          ) : (
            <ChevronDown className="h-4 w-4 text-slate-500" />
          )}
        </button>

        {isMetadataExpanded && (
          <div className="border-t border-slate-100 p-3.5">
            {metadataEntries.length > 0 ? (
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {metadataEntries.map((entry) => (
                  <div
                    key={entry.label}
                    className={`rounded-lg border border-slate-200 bg-slate-50 p-2.5 text-xs ${
                      entry.label.includes("content_fingerprint")
                        ? "sm:col-span-2"
                        : ""
                    }`}
                  >
                    <span className="block text-[11px] font-semibold text-slate-500">
                      {entry.label}:
                    </span>
                    <span className="mt-0.5 block break-all font-mono text-xs font-medium text-slate-900">
                      {entry.value}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500">
                Метадані документа та структурний відбиток для цього файлу не
                виявлені або відсутні.
              </p>
            )}
          </div>
        )}
      </div>

      {/* Детальний список кожного правила */}
      <div className="mt-4 space-y-2.5">
        {report.results.map((criterion) => (
          <div
            key={criterion.rule_id}
            className={`flex flex-col justify-between gap-2.5 rounded-xl border p-3.5 text-xs sm:flex-row sm:items-start ${
              criterion.passed
                ? "border-emerald-200 bg-white"
                : "border-rose-200 bg-rose-50/70"
            }`}
          >
            <div className="flex min-w-0 items-start gap-2.5">
              {criterion.passed ? (
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
              ) : (
                <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" />
              )}
              <div className="min-w-0 space-y-1">
                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[11px] font-bold text-slate-700">
                    {criterion.rule_id}
                  </span>
                  <span className="font-bold text-slate-900">
                    {criterion.description}
                  </span>
                </div>
                <p
                  className={
                    criterion.passed
                      ? "text-slate-600"
                      : "font-medium text-rose-900"
                  }
                >
                  {criterion.feedback}
                </p>
                <p className="break-all font-mono text-[11px] text-slate-600">
                  Ціль: <span className="font-semibold">{criterion.target}</span>{" "}
                  • Очікувалось:{" "}
                  <span className="font-semibold text-emerald-800">
                    {criterion.expected}
                  </span>{" "}
                  • Фактично:{" "}
                  <span
                    className={`font-semibold ${
                      criterion.passed ? "text-slate-900" : "text-rose-800"
                    }`}
                  >
                    {criterion.actual !== null &&
                    criterion.actual.trim().length > 0
                      ? criterion.actual
                      : "Не виявлено (null)"}
                  </span>
                </p>
              </div>
            </div>

            <span
              className={`inline-flex shrink-0 items-center self-start rounded-lg px-2.5 py-1 font-mono text-xs font-bold ${
                criterion.passed
                  ? "bg-emerald-100 text-emerald-800"
                  : "bg-rose-100 text-rose-800"
              }`}
            >
              +{formatPoints(criterion.points_awarded)} /{" "}
              {formatPoints(criterion.max_points)} б.
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DryRunResultPanel;
