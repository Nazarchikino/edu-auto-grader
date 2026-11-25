import {
  Fragment,
  useEffect,
  useMemo,
  useState,
  type ReactElement,
  type ReactNode,
} from "react";
import { ExternalLink, FileText, X, ZoomIn } from "lucide-react";

type TableAlignment = "left" | "center" | "right";

interface ListItemNode {
  content: string;
  children: MarkdownBlock[];
}

type MarkdownBlock =
  | { type: "heading"; level: 1 | 2 | 3 | 4; text: string }
  | { type: "hr" }
  | { type: "code"; language: string; code: string }
  | { type: "blockquote"; blocks: MarkdownBlock[] }
  | {
      type: "table";
      headers: string[];
      alignments: TableAlignment[];
      rows: string[][];
    }
  | { type: "image"; alt: string; src: string }
  | { type: "list"; ordered: boolean; start: number; items: ListItemNode[] }
  | { type: "paragraph"; text: string };

interface LightboxImageState {
  src: string;
  alt: string;
}

interface InlineMarkdownOptions {
  disableLinks?: boolean;
  onImageClick?: (image: LightboxImageState) => void;
}

export interface MarkdownRendererProps {
  content: string;
  compact?: boolean;
  emptyFallback?: string;
  className?: string;
}

const PATH_TRAVERSAL_RE = /(^|\/)\.\.(\/|$)/;
const HORIZONTAL_RULE_RE = /^(?:---+|\*\*\*+|___+)$/;
const HEADING_RE = /^(#{1,4})\s+(.+)$/;
const STANDALONE_IMAGE_RE = /^!\[([^\]]*)\]\(([^)\s]+)\)$/;
const UNORDERED_LIST_RE = /^[-*+]\s+(.+)$/;
const ORDERED_LIST_RE = /^(\d+)\.\s+(.+)$/;
const TABLE_SEPARATOR_CELL_RE = /^:?-{3,}:?$/;
const WORD_OR_CLOSE_PAREN_RE = /[0-9A-Za-zА-Яа-яІіЇїЄєҐґ_)]/;
const WORD_OR_OPEN_PAREN_RE = /[0-9A-Za-zА-Яа-яІіЇїЄєҐґ_(]/;
const WRAPPED_TEXT_CODE_LANGUAGES = new Set(["text", "txt", "plain"]);

function hasUnsafeControlChars(value: string): boolean {
  for (let idx = 0; idx < value.length; idx += 1) {
    const code = value.charCodeAt(idx);
    if (code <= 0x1f || code === 0x7f) {
      return true;
    }
  }
  return false;
}

/**
 * Безпечна валідація URL зображень: дозволяються лише відносні шляхи `/media/...` та `https://`.
 */
function sanitizeImageUrl(rawUrl: string): string | null {
  const trimmed = rawUrl.trim();
  if (trimmed.length === 0 || hasUnsafeControlChars(trimmed)) {
    return null;
  }

  if (trimmed.startsWith("//")) {
    return null;
  }

  if (trimmed.startsWith("/media/")) {
    if (PATH_TRAVERSAL_RE.test(trimmed)) {
      return null;
    }
    return trimmed;
  }

  if (trimmed.toLowerCase().startsWith("https://")) {
    try {
      const parsed = new URL(trimmed);
      return parsed.protocol === "https:" ? trimmed : null;
    } catch {
      return null;
    }
  }

  return null;
}

/**
 * Безпечна валідація URL посилань: блокує `javascript:`, `data:`, `vbscript:` та невідомі схеми.
 */
function sanitizeLinkUrl(rawUrl: string): string | null {
  const trimmed = rawUrl.trim();
  if (trimmed.length === 0 || hasUnsafeControlChars(trimmed)) {
    return null;
  }

  if (trimmed.startsWith("//")) {
    return null;
  }

  if (trimmed.startsWith("#")) {
    return trimmed;
  }

  if (trimmed.startsWith("/")) {
    if (PATH_TRAVERSAL_RE.test(trimmed)) {
      return null;
    }
    return trimmed;
  }

  try {
    const parsed = new URL(trimmed);
    if (
      parsed.protocol === "https:" ||
      parsed.protocol === "http:" ||
      parsed.protocol === "mailto:"
    ) {
      return trimmed;
    }
    return null;
  } catch {
    return null;
  }
}

function isPdfUrl(url: string): boolean {
  const withoutHash = url.split("#")[0] ?? "";
  const withoutQuery = withoutHash.split("?")[0] ?? "";
  return withoutQuery.toLowerCase().endsWith(".pdf");
}

function findMatchingBracket(text: string, openIndex: number): number {
  let depth = 0;
  for (let idx = openIndex; idx < text.length; idx += 1) {
    const ch = text[idx];
    if (ch === "\n") {
      return -1;
    }
    if (ch === "[") {
      depth += 1;
    } else if (ch === "]") {
      depth -= 1;
      if (depth === 0) {
        return idx;
      }
    }
  }
  return -1;
}

function findClosingParen(text: string, startIndex: number): number {
  let depth = 0;
  for (let idx = startIndex; idx < text.length; idx += 1) {
    const ch = text[idx];
    if (ch === "\n") {
      return -1;
    }
    if (ch === "(") {
      depth += 1;
    } else if (ch === ")") {
      if (depth === 0) {
        return idx;
      }
      depth -= 1;
    }
  }
  return -1;
}

function findClosingDoubleStar(text: string, startIndex: number): number {
  let idx = startIndex;
  while (idx < text.length - 1) {
    const ch = text[idx];
    if (ch === "`") {
      const codeEnd = text.indexOf("`", idx + 1);
      if (codeEnd !== -1) {
        idx = codeEnd + 1;
        continue;
      }
    }
    if (ch === "*" && text[idx + 1] === "*") {
      if (idx > startIndex) {
        return idx;
      }
    }
    idx += 1;
  }
  return -1;
}

function findClosingSingleStar(text: string, startIndex: number): number {
  let idx = startIndex;
  while (idx < text.length) {
    const ch = text[idx];
    if (ch === "\n") {
      return -1;
    }
    if (ch === "`") {
      const codeEnd = text.indexOf("`", idx + 1);
      if (codeEnd !== -1) {
        idx = codeEnd + 1;
        continue;
      }
    }
    if (ch === "*") {
      const prev = text[idx - 1] ?? "";
      const next = text[idx + 1] ?? "";
      const isDoubleStar = prev === "*" || next === "*";
      if (
        !isDoubleStar &&
        idx > startIndex &&
        !/\s/.test(prev) &&
        (next === "" || !WORD_OR_OPEN_PAREN_RE.test(next))
      ) {
        return idx;
      }
    }
    idx += 1;
  }
  return -1;
}

function parseInlineNodes(
  text: string,
  options: InlineMarkdownOptions,
  keyPrefix: string
): ReactNode[] {
  const nodes: ReactNode[] = [];
  let plainBuffer = "";
  let pos = 0;
  let tokenIndex = 0;

  const flushPlain = (): void => {
    if (plainBuffer.length > 0) {
      nodes.push(
        <Fragment key={`${keyPrefix}-t-${tokenIndex}`}>{plainBuffer}</Fragment>
      );
      plainBuffer = "";
      tokenIndex += 1;
    }
  };

  while (pos < text.length) {
    const current = text[pos];

    // 1. Інлайн-код (`...`) має найвищий пріоритет, щоб символи * та HTML-теги всередині не парсились
    if (current === "`") {
      const closeCodeIdx = text.indexOf("`", pos + 1);
      if (closeCodeIdx !== -1 && closeCodeIdx > pos + 1) {
        flushPlain();
        const codeText = text.slice(pos + 1, closeCodeIdx);
        nodes.push(
          <code
            key={`${keyPrefix}-code-${tokenIndex}`}
            className="rounded-md border border-slate-200 bg-slate-100 px-1.5 py-0.5 font-mono text-[0.85em] font-medium text-blue-800"
          >
            {codeText}
          </code>
        );
        tokenIndex += 1;
        pos = closeCodeIdx + 1;
        continue;
      }
    }

    // 2. Інлайн-зображення (![alt](src))
    if (current === "!" && text[pos + 1] === "[") {
      const altEnd = findMatchingBracket(text, pos + 1);
      if (altEnd !== -1 && text[altEnd + 1] === "(") {
        const urlEnd = findClosingParen(text, altEnd + 2);
        if (urlEnd !== -1) {
          flushPlain();
          const alt = text.slice(pos + 2, altEnd).trim();
          const rawUrl = text.slice(altEnd + 2, urlEnd).trim();
          const safeUrl = sanitizeImageUrl(rawUrl);

          if (safeUrl !== null) {
            if (options.onImageClick !== undefined) {
              const handleClick = options.onImageClick;
              nodes.push(
                <button
                  key={`${keyPrefix}-img-${tokenIndex}`}
                  type="button"
                  onClick={() => handleClick({ src: safeUrl, alt })}
                  className="mx-1 inline-flex cursor-zoom-in items-center rounded-lg border border-slate-200 bg-white p-1 align-middle shadow-2xs transition hover:border-blue-400"
                  title={
                    alt.length > 0
                      ? `${alt} (натисніть для збільшення)`
                      : "Натисніть для збільшення"
                  }
                >
                  <img
                    src={safeUrl}
                    alt={alt}
                    loading="lazy"
                    referrerPolicy="no-referrer"
                    className="max-h-40 max-w-full rounded object-contain"
                  />
                </button>
              );
            } else if (options.disableLinks) {
              nodes.push(
                <span
                  key={`${keyPrefix}-img-${tokenIndex}`}
                  className="mx-1 inline-flex items-center rounded-lg border border-slate-200 bg-white p-1 align-middle shadow-2xs"
                >
                  <img
                    src={safeUrl}
                    alt={alt}
                    loading="lazy"
                    referrerPolicy="no-referrer"
                    className="max-h-40 max-w-full rounded object-contain"
                  />
                </span>
              );
            } else {
              nodes.push(
                <a
                  key={`${keyPrefix}-img-${tokenIndex}`}
                  href={safeUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mx-1 inline-flex items-center rounded-lg border border-slate-200 bg-white p-1 align-middle shadow-2xs transition hover:border-blue-400"
                >
                  <img
                    src={safeUrl}
                    alt={alt}
                    loading="lazy"
                    referrerPolicy="no-referrer"
                    className="max-h-40 max-w-full rounded object-contain"
                  />
                </a>
              );
            }
          } else {
            nodes.push(
              <span
                key={`${keyPrefix}-img-fb-${tokenIndex}`}
                className="italic text-slate-500"
              >
                {alt.length > 0 ? `[${alt}]` : "[Зображення]"}
              </span>
            );
          }

          tokenIndex += 1;
          pos = urlEnd + 1;
          continue;
        }
      }
    }

    // 3. Посилання ([текст](url)) із безпечною перевіркою URL та PDF-бейджем
    if (!options.disableLinks && current === "[") {
      const labelEnd = findMatchingBracket(text, pos);
      if (labelEnd !== -1 && text[labelEnd + 1] === "(") {
        const urlEnd = findClosingParen(text, labelEnd + 2);
        if (urlEnd !== -1) {
          flushPlain();
          const label = text.slice(pos + 1, labelEnd);
          const rawUrl = text.slice(labelEnd + 2, urlEnd).trim();
          const safeUrl = sanitizeLinkUrl(rawUrl);
          const labelNodes = parseInlineNodes(
            label,
            { ...options, disableLinks: true },
            `${keyPrefix}-lnk-${tokenIndex}`
          );

          if (safeUrl === null) {
            nodes.push(
              <span key={`${keyPrefix}-badlnk-${tokenIndex}`}>
                {labelNodes}
              </span>
            );
          } else if (isPdfUrl(safeUrl)) {
            nodes.push(
              <a
                key={`${keyPrefix}-pdf-${tokenIndex}`}
                href={safeUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex flex-wrap items-center gap-1.5 rounded-lg border border-rose-200 bg-rose-50/90 px-2.5 py-1 text-xs font-semibold text-rose-800 no-underline transition-colors hover:border-rose-300 hover:bg-rose-100"
              >
                <FileText className="h-3.5 w-3.5 shrink-0 text-rose-600" />
                <span>{labelNodes}</span>
                <span className="rounded bg-rose-600 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white">
                  PDF
                </span>
                <ExternalLink className="h-3 w-3 shrink-0 text-rose-500" />
              </a>
            );
          } else if (safeUrl.startsWith("#")) {
            nodes.push(
              <a
                key={`${keyPrefix}-hash-${tokenIndex}`}
                href={safeUrl}
                className="font-medium text-blue-700 underline decoration-blue-300 underline-offset-2 hover:text-blue-900"
              >
                {labelNodes}
              </a>
            );
          } else {
            nodes.push(
              <a
                key={`${keyPrefix}-a-${tokenIndex}`}
                href={safeUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 font-medium text-blue-700 underline decoration-blue-300 underline-offset-2 hover:text-blue-900"
              >
                <span>{labelNodes}</span>
                <ExternalLink className="h-3 w-3 shrink-0" />
              </a>
            );
          }

          tokenIndex += 1;
          pos = urlEnd + 1;
          continue;
        }
      }
    }

    // 4. Жирний текст (**...**) із підтримкою вкладеного інлайн-коду та курсиву
    if (current === "*" && text[pos + 1] === "*") {
      const closeBoldIdx = findClosingDoubleStar(text, pos + 2);
      if (closeBoldIdx !== -1) {
        flushPlain();
        const inner = text.slice(pos + 2, closeBoldIdx);
        nodes.push(
          <strong
            key={`${keyPrefix}-b-${tokenIndex}`}
            className="font-semibold text-slate-900"
          >
            {parseInlineNodes(inner, options, `${keyPrefix}-bi-${tokenIndex}`)}
          </strong>
        );
        tokenIndex += 1;
        pos = closeBoldIdx + 2;
        continue;
      }
    }

    // 5. Курсив (*...*) із захистом від хибного спрацювання на формулах множення (A1*B1, (Ціна)*(Кількість))
    if (current === "*" && text[pos + 1] !== "*") {
      const prevChar = pos > 0 ? (text[pos - 1] ?? "") : "";
      const nextChar = text[pos + 1] ?? "";
      const canOpenItalic =
        nextChar.length > 0 &&
        !/\s/.test(nextChar) &&
        (prevChar.length === 0 || !WORD_OR_CLOSE_PAREN_RE.test(prevChar));

      if (canOpenItalic) {
        const closeItalicIdx = findClosingSingleStar(text, pos + 1);
        if (closeItalicIdx !== -1) {
          flushPlain();
          const inner = text.slice(pos + 1, closeItalicIdx);
          nodes.push(
            <em
              key={`${keyPrefix}-i-${tokenIndex}`}
              className="italic text-slate-800"
            >
              {parseInlineNodes(
                inner,
                options,
                `${keyPrefix}-ii-${tokenIndex}`
              )}
            </em>
          );
          tokenIndex += 1;
          pos = closeItalicIdx + 1;
          continue;
        }
      }
    }

    plainBuffer += current;
    pos += 1;
  }

  flushPlain();
  return nodes;
}

/**
 * Безпечний інлайн-рендерер Markdown (`код`, **жирний**, *курсив*, посилання, зображення)
 * для заголовків, варіантів відповідей у тестах та компактних підписів.
 */
// eslint-disable-next-line react-refresh/only-export-components
export function renderInlineMarkdown(
  text: string,
  options: InlineMarkdownOptions = {}
): ReactNode[] {
  if (text.length === 0) {
    return [];
  }
  return parseInlineNodes(text, options, "inl");
}

function getLineIndent(line: string): number {
  let indent = 0;
  for (let idx = 0; idx < line.length; idx += 1) {
    const ch = line[idx];
    if (ch === " ") {
      indent += 1;
    } else if (ch === "\t") {
      indent += 2;
    } else {
      break;
    }
  }
  return indent;
}

function stripLeadingIndent(line: string, count: number): string {
  let removed = 0;
  let idx = 0;
  while (idx < line.length && removed < count) {
    const ch = line[idx];
    if (ch === " ") {
      removed += 1;
      idx += 1;
    } else if (ch === "\t") {
      removed += 2;
      idx += 1;
    } else {
      break;
    }
  }
  return line.slice(idx);
}

function dedentBlockLines(lines: string[]): string[] {
  let minIndent = Number.POSITIVE_INFINITY;
  for (const line of lines) {
    if (line.trim().length > 0) {
      minIndent = Math.min(minIndent, getLineIndent(line));
    }
  }
  if (!Number.isFinite(minIndent) || minIndent <= 0) {
    return lines;
  }
  return lines.map((line) =>
    line.trim().length === 0 ? "" : stripLeadingIndent(line, minIndent)
  );
}

function splitTableRow(rawLine: string): string[] {
  let line = rawLine.trim();
  if (line.startsWith("|")) {
    line = line.slice(1);
  }
  if (line.endsWith("|") && !line.endsWith("\\|")) {
    line = line.slice(0, -1);
  }

  const cells: string[] = [];
  let current = "";
  let inInlineCode = false;

  for (let idx = 0; idx < line.length; idx += 1) {
    const ch = line[idx];
    if (ch === "\\" && line[idx + 1] === "|" && !inInlineCode) {
      current += "|";
      idx += 1;
      continue;
    }
    if (ch === "`") {
      inInlineCode = !inInlineCode;
      current += ch;
      continue;
    }
    if (ch === "|" && !inInlineCode) {
      cells.push(current.trim());
      current = "";
      continue;
    }
    current += ch;
  }
  cells.push(current.trim());
  return cells;
}

function parseTableSeparator(rawLine: string): TableAlignment[] | null {
  const trimmed = rawLine.trim();
  if (!trimmed.includes("|") && !TABLE_SEPARATOR_CELL_RE.test(trimmed)) {
    return null;
  }

  const cells = splitTableRow(trimmed);
  if (cells.length === 0) {
    return null;
  }

  const alignments: TableAlignment[] = [];
  for (const cell of cells) {
    if (!TABLE_SEPARATOR_CELL_RE.test(cell)) {
      return null;
    }
    const startsColon = cell.startsWith(":");
    const endsColon = cell.endsWith(":");
    if (startsColon && endsColon) {
      alignments.push("center");
    } else if (endsColon) {
      alignments.push("right");
    } else {
      alignments.push("left");
    }
  }
  return alignments;
}

function isTableStart(headerLine: string, separatorLine: string): boolean {
  const trimmedHeader = headerLine.trim();
  if (!trimmedHeader.includes("|")) {
    return false;
  }
  const alignments = parseTableSeparator(separatorLine);
  if (alignments === null || alignments.length === 0) {
    return false;
  }
  const headerCells = splitTableRow(trimmedHeader);
  return headerCells.length > 0;
}

function isTableDataRow(rawLine: string): boolean {
  const trimmed = rawLine.trim();
  if (trimmed.length === 0 || !trimmed.includes("|")) {
    return false;
  }
  if (
    trimmed.startsWith("```") ||
    HEADING_RE.test(trimmed) ||
    trimmed.startsWith(">")
  ) {
    return false;
  }
  return true;
}

function normalizeTableRow(cells: string[], columnCount: number): string[] {
  if (cells.length === columnCount) {
    return cells;
  }
  if (cells.length > columnCount) {
    return cells.slice(0, columnCount);
  }
  return [
    ...cells,
    ...Array.from({ length: columnCount - cells.length }, () => ""),
  ];
}

interface ParsedListLine {
  indent: number;
  ordered: boolean;
  startNumber: number;
  text: string;
}

function parseListLine(rawLine: string): ParsedListLine | null {
  const indent = getLineIndent(rawLine);
  const content = rawLine.trim();

  const unorderedMatch = UNORDERED_LIST_RE.exec(content);
  if (unorderedMatch !== null) {
    return {
      indent,
      ordered: false,
      startNumber: 1,
      text: (unorderedMatch[1] ?? "").trim(),
    };
  }

  const orderedMatch = ORDERED_LIST_RE.exec(content);
  if (orderedMatch !== null) {
    const parsedNum = Number.parseInt(orderedMatch[1] ?? "1", 10);
    return {
      indent,
      ordered: true,
      startNumber: Number.isNaN(parsedNum) ? 1 : parsedNum,
      text: (orderedMatch[2] ?? "").trim(),
    };
  }

  return null;
}

function isBlockStarter(lines: string[], index: number): boolean {
  const line = lines[index] ?? "";
  const trimmed = line.trim();
  if (trimmed.length === 0) {
    return true;
  }
  if (
    trimmed.startsWith("```") ||
    HORIZONTAL_RULE_RE.test(trimmed) ||
    HEADING_RE.test(trimmed) ||
    trimmed.startsWith(">") ||
    STANDALONE_IMAGE_RE.test(trimmed) ||
    parseListLine(line) !== null
  ) {
    return true;
  }
  if (index + 1 < lines.length && isTableStart(line, lines[index + 1] ?? "")) {
    return true;
  }
  return false;
}

function parseMarkdownBlocks(rawContent: string): MarkdownBlock[] {
  const normalized = rawContent.replace(/\r\n?/g, "\n");
  const lines = normalized.split("\n");
  const blocks: MarkdownBlock[] = [];
  let i = 0;

  while (i < lines.length) {
    const rawLine = lines[i] ?? "";
    const trimmed = rawLine.trim();

    if (trimmed.length === 0) {
      i += 1;
      continue;
    }

    // 1. Блок коду (```lang ... ```)
    if (trimmed.startsWith("```")) {
      const language = trimmed.slice(3).trim().toLowerCase();
      const codeLines: string[] = [];
      i += 1;
      while (i < lines.length) {
        const candidate = lines[i] ?? "";
        if (candidate.trim().startsWith("```")) {
          i += 1;
          break;
        }
        codeLines.push(candidate);
        i += 1;
      }
      blocks.push({
        type: "code",
        language,
        code: codeLines.join("\n"),
      });
      continue;
    }

    // 2. Горизонтальна лінія (--- / *** / ___)
    if (HORIZONTAL_RULE_RE.test(trimmed)) {
      blocks.push({ type: "hr" });
      i += 1;
      continue;
    }

    // 3. Заголовки (#, ##, ###, ####)
    const headingMatch = HEADING_RE.exec(trimmed);
    if (headingMatch !== null) {
      const levelLength = (headingMatch[1] ?? "#").length;
      const level = (
        levelLength <= 1 ? 1 : levelLength >= 4 ? 4 : levelLength
      ) as 1 | 2 | 3 | 4;
      blocks.push({
        type: "heading",
        level,
        text: (headingMatch[2] ?? "").trim(),
      });
      i += 1;
      continue;
    }

    // 4. Цитата (> ...)
    if (trimmed.startsWith(">")) {
      const quoteLines: string[] = [];
      while (i < lines.length) {
        const qTrimmed = (lines[i] ?? "").trim();
        if (!qTrimmed.startsWith(">")) {
          break;
        }
        quoteLines.push(qTrimmed.replace(/^>\s?/, ""));
        i += 1;
      }
      blocks.push({
        type: "blockquote",
        blocks: parseMarkdownBlocks(quoteLines.join("\n")),
      });
      continue;
    }

    // 5. Markdown-таблиця (| Заголовок | ... | + | --- | ... |)
    if (i + 1 < lines.length && isTableStart(rawLine, lines[i + 1] ?? "")) {
      const rawHeaders = splitTableRow(rawLine);
      const rawAlignments = parseTableSeparator(lines[i + 1] ?? "") ?? [];
      const columnCount = Math.max(rawHeaders.length, rawAlignments.length);
      const headers = normalizeTableRow(rawHeaders, columnCount);
      const alignments: TableAlignment[] = Array.from(
        { length: columnCount },
        (_, colIdx) => rawAlignments[colIdx] ?? "left"
      );

      i += 2;
      const rows: string[][] = [];
      while (i < lines.length && isTableDataRow(lines[i] ?? "")) {
        rows.push(normalizeTableRow(splitTableRow(lines[i] ?? ""), columnCount));
        i += 1;
      }

      blocks.push({
        type: "table",
        headers,
        alignments,
        rows,
      });
      continue;
    }

    // 6. Окреме зображення (![alt](src))
    const imageMatch = STANDALONE_IMAGE_RE.exec(trimmed);
    if (imageMatch !== null) {
      blocks.push({
        type: "image",
        alt: (imageMatch[1] ?? "").trim(),
        src: (imageMatch[2] ?? "").trim(),
      });
      i += 1;
      continue;
    }

    // 7. Маркований або нумерований список (з підтримкою вкладених підпунктів та вкладених блоків)
    const firstListLine = parseListLine(rawLine);
    if (firstListLine !== null) {
      const baseIndent = firstListLine.indent;
      const ordered = firstListLine.ordered;
      const start = firstListLine.startNumber;
      const items: ListItemNode[] = [];

      while (i < lines.length) {
        const candidateLine = lines[i] ?? "";
        const parsedItem = parseListLine(candidateLine);
        if (
          parsedItem === null ||
          parsedItem.ordered !== ordered ||
          parsedItem.indent !== baseIndent
        ) {
          break;
        }

        const itemText = parsedItem.text;
        const childLines: string[] = [];
        i += 1;

        while (i < lines.length) {
          const nextLine = lines[i] ?? "";
          if (nextLine.trim().length === 0) {
            // Заглядаємо на наступний непорожній рядок
            let lookahead = i + 1;
            while (
              lookahead < lines.length &&
              (lines[lookahead] ?? "").trim().length === 0
            ) {
              lookahead += 1;
            }
            if (lookahead >= lines.length) {
              i = lookahead;
              break;
            }
            const afterBlank = lines[lookahead] ?? "";
            const afterIndent = getLineIndent(afterBlank);
            if (afterIndent > baseIndent) {
              childLines.push("");
              i += 1;
              continue;
            }
            const afterList = parseListLine(afterBlank);
            if (
              afterList !== null &&
              afterList.ordered === ordered &&
              afterList.indent === baseIndent
            ) {
              i = lookahead;
              break;
            }
            break;
          }

          const nextIndent = getLineIndent(nextLine);
          if (nextIndent > baseIndent) {
            childLines.push(nextLine);
            i += 1;
            continue;
          }

          break;
        }

        const dedentedChildren = dedentBlockLines(childLines);
        const childBlocks =
          dedentedChildren.some((ln) => ln.trim().length > 0)
            ? parseMarkdownBlocks(dedentedChildren.join("\n"))
            : [];

        items.push({
          content: itemText,
          children: childBlocks,
        });
      }

      blocks.push({
        type: "list",
        ordered,
        start,
        items,
      });
      continue;
    }

    // 8. Звичайний абзац
    const paragraphLines: string[] = [trimmed];
    i += 1;
    while (i < lines.length && !isBlockStarter(lines, i)) {
      paragraphLines.push((lines[i] ?? "").trim());
      i += 1;
    }
    blocks.push({
      type: "paragraph",
      text: paragraphLines.join(" "),
    });
  }

  return blocks;
}

function getAlignmentClass(alignment: TableAlignment): string {
  switch (alignment) {
    case "center":
      return "text-center";
    case "right":
      return "text-right";
    case "left":
      return "text-left";
  }
}

/**
 * Універсальний безпечний рендерер Markdown у React JSX без `dangerouslySetInnerHTML`.
 * Підтримує заголовки, таблиці, вкладені списки, блоки коду, цитати, PDF-посилання та зображення з модальним збільшенням.
 */
export function MarkdownRenderer({
  content,
  compact = false,
  emptyFallback,
  className = "",
}: MarkdownRendererProps): ReactElement {
  const [lightboxImage, setLightboxImage] =
    useState<LightboxImageState | null>(null);

  const blocks = useMemo(() => {
    if (content.trim().length === 0) {
      return [];
    }
    return parseMarkdownBlocks(content);
  }, [content]);

  useEffect(() => {
    if (lightboxImage === null) {
      return;
    }
    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key === "Escape") {
        setLightboxImage(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [lightboxImage]);

  if (blocks.length === 0) {
    if (emptyFallback !== undefined) {
      return <p className="text-sm italic text-slate-500">{emptyFallback}</p>;
    }
    return <></>;
  }

  const inlineOptions: InlineMarkdownOptions = {
    onImageClick: (image) => setLightboxImage(image),
  };

  const renderBlocks = (
    blockList: MarkdownBlock[],
    keyPrefix: string
  ): ReactElement[] =>
    blockList.map((block, index) => {
      const key = `${keyPrefix}-${index}`;

      switch (block.type) {
        case "heading": {
          const inlineHeading = parseInlineNodes(
            block.text,
            inlineOptions,
            `${key}-h`
          );
          if (block.level === 1) {
            return (
              <h2
                key={key}
                className={
                  compact
                    ? "border-b border-slate-200 pb-1.5 text-base font-bold text-slate-900 sm:text-lg"
                    : "border-b border-slate-200 pb-2.5 text-xl font-bold text-slate-900 sm:text-2xl"
                }
              >
                {inlineHeading}
              </h2>
            );
          }
          if (block.level === 2) {
            return (
              <h3
                key={key}
                className={
                  compact
                    ? "pt-1.5 text-sm font-bold text-slate-900 sm:text-base"
                    : "pt-2 text-lg font-bold text-slate-900"
                }
              >
                {inlineHeading}
              </h3>
            );
          }
          if (block.level === 3) {
            return (
              <h4
                key={key}
                className={
                  compact
                    ? "pt-1 text-sm font-bold text-slate-900"
                    : "pt-1 text-base font-semibold text-slate-900"
                }
              >
                {inlineHeading}
              </h4>
            );
          }
          return (
            <h5
              key={key}
              className="pt-0.5 text-sm font-semibold text-slate-800"
            >
              {inlineHeading}
            </h5>
          );
        }

        case "hr":
          return <hr key={key} className="my-4 border-slate-200" />;

        case "code": {
          const shouldWrap = WRAPPED_TEXT_CODE_LANGUAGES.has(block.language);
          return (
            <div
              key={key}
              className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900 shadow-2xs"
            >
              {block.language.length > 0 && (
                <div className="flex items-center justify-between border-b border-slate-800 bg-slate-950/70 px-3.5 py-1.5">
                  <span className="font-mono text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                    {block.language}
                  </span>
                </div>
              )}
              <pre
                className={`p-4 font-mono text-xs leading-relaxed text-slate-100 ${
                  shouldWrap
                    ? "whitespace-pre-wrap break-words"
                    : "overflow-x-auto"
                }`}
              >
                <code>{block.code}</code>
              </pre>
            </div>
          );
        }

        case "blockquote":
          return (
            <blockquote
              key={key}
              className="space-y-2 rounded-r-xl border-l-4 border-blue-500 bg-blue-50/60 px-4 py-3 text-sm text-slate-700"
            >
              {renderBlocks(block.blocks, `${key}-bq`)}
            </blockquote>
          );

        case "table":
          return (
            <div
              key={key}
              className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-2xs"
            >
              <table className="min-w-full divide-y divide-slate-200 text-xs sm:text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {block.headers.map((headerText, colIdx) => (
                      <th
                        key={`${key}-th-${colIdx}`}
                        scope="col"
                        className={`border-r border-slate-200 px-3.5 py-2.5 font-semibold text-slate-900 last:border-r-0 ${getAlignmentClass(
                          block.alignments[colIdx] ?? "left"
                        )}`}
                      >
                        {parseInlineNodes(
                          headerText,
                          inlineOptions,
                          `${key}-th-${colIdx}`
                        )}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {block.rows.map((row, rowIdx) => (
                    <tr
                      key={`${key}-tr-${rowIdx}`}
                      className="transition-colors odd:bg-white even:bg-slate-50/40 hover:bg-blue-50/30"
                    >
                      {row.map((cellText, colIdx) => (
                        <td
                          key={`${key}-td-${rowIdx}-${colIdx}`}
                          className={`border-r border-slate-100 px-3.5 py-2 align-top text-slate-700 last:border-r-0 ${getAlignmentClass(
                            block.alignments[colIdx] ?? "left"
                          )}`}
                        >
                          {parseInlineNodes(
                            cellText,
                            inlineOptions,
                            `${key}-td-${rowIdx}-${colIdx}`
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );

        case "image": {
          const safeUrl = sanitizeImageUrl(block.src);
          if (safeUrl === null) {
            return (
              <p
                key={key}
                className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs italic text-slate-500"
              >
                {block.alt.length > 0
                  ? `Зображення недоступне: ${block.alt}`
                  : "Зображення заблоковано політикою безпеки URL."}
              </p>
            );
          }

          return (
            <figure
              key={key}
              className="my-2 overflow-hidden rounded-xl border border-slate-200 bg-slate-50/70 p-3 shadow-2xs"
            >
              <button
                type="button"
                onClick={() =>
                  setLightboxImage({ src: safeUrl, alt: block.alt })
                }
                className="group relative block w-full cursor-zoom-in overflow-hidden rounded-lg bg-white p-1.5 text-center transition hover:ring-2 hover:ring-blue-400/70 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label={
                  block.alt.length > 0
                    ? `Збільшити зображення: ${block.alt}`
                    : "Збільшити зображення"
                }
              >
                <img
                  src={safeUrl}
                  alt={block.alt}
                  loading="lazy"
                  referrerPolicy="no-referrer"
                  className={`mx-auto w-auto max-w-full rounded object-contain ${
                    compact ? "max-h-80" : "max-h-[480px]"
                  }`}
                />
                <span className="pointer-events-none absolute right-2.5 top-2.5 inline-flex items-center gap-1 rounded-full bg-slate-900/75 px-2.5 py-1 text-[11px] font-medium text-white opacity-0 shadow-xs transition-opacity group-hover:opacity-100">
                  <ZoomIn className="h-3.5 w-3.5" />
                  Збільшити
                </span>
              </button>
              {block.alt.length > 0 && (
                <figcaption className="mt-2 text-center text-xs leading-relaxed text-slate-600">
                  {block.alt}
                </figcaption>
              )}
            </figure>
          );
        }

        case "list": {
          const listClass = block.ordered
            ? "list-decimal space-y-1.5 pl-6 text-sm leading-relaxed text-slate-700"
            : "list-disc space-y-1.5 pl-6 text-sm leading-relaxed text-slate-700";

          const listItems = block.items.map((item, itemIdx) => (
            <li key={`${key}-li-${itemIdx}`} className="space-y-2">
              <div>
                {parseInlineNodes(
                  item.content,
                  inlineOptions,
                  `${key}-li-${itemIdx}`
                )}
              </div>
              {item.children.length > 0 && (
                <div className="space-y-2 pt-0.5">
                  {renderBlocks(item.children, `${key}-sub-${itemIdx}`)}
                </div>
              )}
            </li>
          ));

          if (block.ordered) {
            return (
              <ol
                key={key}
                start={block.start !== 1 ? block.start : undefined}
                className={listClass}
              >
                {listItems}
              </ol>
            );
          }

          return (
            <ul key={key} className={listClass}>
              {listItems}
            </ul>
          );
        }

        case "paragraph":
          return (
            <p
              key={key}
              className={
                compact
                  ? "text-sm leading-relaxed text-slate-700"
                  : "text-sm leading-relaxed text-slate-700 sm:text-base"
              }
            >
              {parseInlineNodes(block.text, inlineOptions, `${key}-p`)}
            </p>
          );
      }
    });

  return (
    <>
      <div
        className={`${compact ? "space-y-3" : "space-y-4"} text-slate-700 ${className}`.trim()}
      >
        {renderBlocks(blocks, "blk")}
      </div>

      {lightboxImage !== null && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
          aria-label={
            lightboxImage.alt.length > 0
              ? lightboxImage.alt
              : "Перегляд зображення"
          }
          onClick={() => setLightboxImage(null)}
        >
          <div
            className="relative flex max-h-[92vh] max-w-5xl flex-col overflow-hidden rounded-2xl border border-slate-700 bg-white shadow-2xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-center justify-between gap-3 border-b border-slate-200 bg-slate-50 px-4 py-3">
              <p className="truncate text-xs font-semibold text-slate-800 sm:text-sm">
                {lightboxImage.alt.length > 0
                  ? lightboxImage.alt
                  : "Перегляд ілюстрації"}
              </p>
              <div className="flex shrink-0 items-center gap-2">
                <a
                  href={lightboxImage.src}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100"
                >
                  <ExternalLink className="h-3.5 w-3.5" />
                  <span className="hidden sm:inline">У новій вкладці</span>
                </a>
                <button
                  type="button"
                  onClick={() => setLightboxImage(null)}
                  className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-slate-300 bg-white text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900"
                  aria-label="Закрити перегляд"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            <div className="overflow-auto bg-slate-100 p-4 text-center">
              <img
                src={lightboxImage.src}
                alt={lightboxImage.alt}
                loading="lazy"
                referrerPolicy="no-referrer"
                className="mx-auto max-h-[75vh] w-auto max-w-full rounded-lg bg-white object-contain shadow-xs"
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default MarkdownRenderer;
