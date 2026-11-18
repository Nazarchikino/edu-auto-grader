import type { ReactElement } from "react";

export function App(): ReactElement {
  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 p-6">
      <div className="max-w-xl w-full rounded-xl bg-white p-8 shadow-sm border border-slate-200">
        <h1 className="text-2xl font-bold text-slate-900">
          Edu Auto Grader
        </h1>
        <p className="mt-2 text-sm text-slate-600">
          Вебсистема електронних посібників та автоматизованої перевірки практичних робіт (Word, Excel, Access, HTML).
        </p>
      </div>
    </main>
  );
}

export default App;
