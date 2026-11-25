import { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor";
import EditorWorker from "monaco-editor/editor/editor.worker?worker";
import CssWorker from "monaco-editor/language/css/css.worker?worker";
import HtmlWorker from "monaco-editor/language/html/html.worker?worker";

let isLocalMonacoConfigured = false;

/**
 * Конфігурує Monaco Editor для 100% локальної роботи без зовнішнього CDN (jsdelivr),
 * використовуючи локальний пакет `monaco-editor` і Vite Web Workers.
 */
export function configureLocalMonaco(): void {
  if (isLocalMonacoConfigured) {
    return;
  }

  if (typeof self !== "undefined") {
    self.MonacoEnvironment = {
      getWorker(_workerId: string, label: string): Worker {
        if (label === "css" || label === "scss" || label === "less") {
          return new CssWorker();
        }
        if (label === "html" || label === "handlebars" || label === "razor") {
          return new HtmlWorker();
        }
        return new EditorWorker();
      },
    };
  }

  loader.config({ monaco });
  isLocalMonacoConfigured = true;
}

configureLocalMonaco();
