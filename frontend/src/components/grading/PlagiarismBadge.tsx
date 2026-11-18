import type { ReactElement } from "react";
import { Fingerprint, ShieldAlert, ShieldCheck } from "lucide-react";

export interface PlagiarismBadgeProps {
  isFlagged: boolean;
  reason?: string | null;
  variant?: "compact" | "pill" | "banner";
  fileHash?: string | null;
}

export function PlagiarismBadge({
  isFlagged,
  reason = null,
  variant = "pill",
  fileHash = null,
}: PlagiarismBadgeProps): ReactElement {
  const tooltipText = isFlagged
    ? reason ??
      "Виявлено збіг контрольної суми SHA-256 або метаданих docProps/core.xml із роботою іншого студента."
    : "Перевірка академічної доброчесності успішна: збігів SHA-256 та метаданих docProps/core.xml не виявлено.";

  if (variant === "compact") {
    return isFlagged ? (
      <span
        title={tooltipText}
        className="inline-flex items-center gap-1 rounded-md border border-rose-300 bg-rose-100 px-1.5 py-0.5 text-[10px] font-bold text-rose-900"
      >
        <ShieldAlert className="h-3 w-3 shrink-0 text-rose-600" />
        <span>Плагіат</span>
      </span>
    ) : (
      <span
        title={tooltipText}
        className="inline-flex items-center gap-0.5 rounded-md border border-emerald-200 bg-emerald-50 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-800"
      >
        <ShieldCheck className="h-3 w-3 shrink-0 text-emerald-600" />
        <span>Ок</span>
      </span>
    );
  }

  if (variant === "banner") {
    return isFlagged ? (
      <div
        className="rounded-xl border border-rose-300 bg-rose-50/90 p-4 text-xs text-rose-950"
        role="alert"
      >
        <div className="flex items-start gap-3">
          <ShieldAlert className="mt-0.5 h-5 w-5 shrink-0 text-rose-600" />
          <div className="min-w-0 flex-1 space-y-1">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="font-bold text-rose-900">
                Червоний прапорець академічної недоброчесності
              </p>
              <span className="inline-flex items-center gap-1 rounded-full border border-rose-300 bg-white px-2.5 py-0.5 text-[11px] font-bold text-rose-800">
                <Fingerprint className="h-3 w-3" />
                Збіг відбитка / метаданих
              </span>
            </div>
            <p className="leading-relaxed text-rose-800">{tooltipText}</p>
            {fileHash !== null && fileHash.trim().length > 0 && (
              <p className="pt-1 font-mono text-[11px] text-rose-700">
                SHA-256: <span className="break-all">{fileHash}</span>
              </p>
            )}
          </div>
        </div>
      </div>
    ) : (
      <div className="rounded-xl border border-emerald-200 bg-emerald-50/70 px-4 py-3 text-xs text-emerald-950">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <ShieldCheck className="h-5 w-5 shrink-0 text-emerald-600" />
            <div>
              <span className="font-bold text-emerald-900">
                Авторство підтверджено:
              </span>{" "}
              <span className="text-emerald-800">
                унікальний SHA-256 хеш та метадані <code>docProps/core.xml</code>.
              </span>
            </div>
          </div>
          {fileHash !== null && fileHash.trim().length > 0 && (
            <span className="font-mono text-[11px] text-emerald-700">
              SHA-256: {fileHash.slice(0, 12)}…
            </span>
          )}
        </div>
      </div>
    );
  }

  return isFlagged ? (
    <span
      title={tooltipText}
      className="inline-flex items-center gap-1 rounded-full border border-rose-300 bg-rose-100 px-2.5 py-0.5 text-xs font-bold text-rose-900"
    >
      <ShieldAlert className="h-3.5 w-3.5 shrink-0 text-rose-600" />
      <span>Підозра на плагіат</span>
    </span>
  ) : (
    <span
      title={tooltipText}
      className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-800"
    >
      <ShieldCheck className="h-3.5 w-3.5 shrink-0 text-emerald-600" />
      <span>Оригінал</span>
    </span>
  );
}

export default PlagiarismBadge;
