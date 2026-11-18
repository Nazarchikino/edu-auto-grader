import { useState, type FormEvent, type ReactElement } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import {
  AlertCircle,
  KeyRound,
  Loader2,
  LogIn,
  Mail,
  ShieldCheck,
} from "lucide-react";
import {
  extractApiErrorMessage,
  getDefaultHomePath,
  useAuth,
} from "../context/AuthContext";
import type { UserRole } from "../types/api";

interface LocationState {
  from?: string;
}

interface DemoAccount {
  label: string;
  role: UserRole;
  email: string;
  password: string;
  badgeClass: string;
}

const DEMO_ACCOUNTS: readonly DemoAccount[] = [
  {
    label: "Студент (КН-31, №1)",
    role: "student",
    email: "student1@kpefk.lcloud.in.ua",
    password: "Student123!",
    badgeClass:
      "border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100",
  },
  {
    label: "Викладач",
    role: "teacher",
    email: "teacher@kpefk.lcloud.in.ua",
    password: "Teacher123!",
    badgeClass:
      "border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100",
  },
  {
    label: "Адміністратор",
    role: "admin",
    email: "admin@kpefk.lcloud.in.ua",
    password: "Admin123!",
    badgeClass:
      "border-purple-200 bg-purple-50 text-purple-700 hover:bg-purple-100",
  },
];

function isPathAllowedForRole(pathname: string, role: UserRole): boolean {
  if (pathname.startsWith("/student/")) {
    return role === "student";
  }
  if (pathname.startsWith("/teacher/")) {
    return role === "teacher" || role === "admin";
  }
  if (pathname.startsWith("/admin/")) {
    return role === "admin";
  }
  return false;
}

export function LoginPage(): ReactElement {
  const { user, isAuthenticated, isLoading, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  if (!isLoading && isAuthenticated && user !== null) {
    return <Navigate to={getDefaultHomePath(user.role)} replace />;
  }

  const handleSelectDemoAccount = (account: DemoAccount): void => {
    setEmail(account.email);
    setPassword(account.password);
    setErrorMessage(null);
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>
  ): Promise<void> => {
    event.preventDefault();
    setErrorMessage(null);

    const trimmedEmail = email.trim();
    if (trimmedEmail.length === 0 || password.length === 0) {
      setErrorMessage("Будь ласка, введіть електронну пошту та пароль.");
      return;
    }

    setIsSubmitting(true);
    try {
      const authenticatedUser = await login({
        email: trimmedEmail,
        password,
      });

      const state = location.state as LocationState | null;
      const requestedPath = state?.from;
      const targetPath =
        typeof requestedPath === "string" &&
        isPathAllowedForRole(requestedPath, authenticatedUser.role)
          ? requestedPath
          : getDefaultHomePath(authenticatedUser.role);

      navigate(targetPath, { replace: true });
    } catch (error: unknown) {
      setErrorMessage(
        extractApiErrorMessage(
          error,
          "Не вдалося виконати вхід. Перевірте облікові дані."
        )
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center bg-slate-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm">
          <ShieldCheck className="h-7 w-7" />
        </div>
        <h1 className="mt-4 text-center text-2xl font-bold tracking-tight text-slate-900">
          Edu Auto Grader
        </h1>
        <p className="mt-1.5 text-center text-sm text-slate-600">
          Електронні посібники та автоматизована перевірка практичних робіт
          (Word, Excel, Access, HTML)
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="rounded-2xl border border-slate-200 bg-white px-6 py-8 shadow-xs sm:px-8">
          <form className="space-y-5" onSubmit={handleSubmit} noValidate>
            {errorMessage !== null && (
              <div
                role="alert"
                className="flex items-start gap-2.5 rounded-xl border border-rose-200 bg-rose-50 p-3.5 text-xs font-medium text-rose-700"
              >
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-rose-600" />
                <span>{errorMessage}</span>
              </div>
            )}

            <div>
              <label
                htmlFor="email"
                className="block text-xs font-semibold uppercase tracking-wide text-slate-700"
              >
                Електронна пошта коледжу
              </label>
              <div className="relative mt-1.5">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                  <Mail className="h-4 w-4" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="student1@kpefk.lcloud.in.ua"
                  className="block w-full rounded-xl border border-slate-300 bg-white py-2.5 pl-9 pr-3.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-600 focus:outline-hidden focus:ring-2 focus:ring-blue-600/20"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-xs font-semibold uppercase tracking-wide text-slate-700"
              >
                Пароль
              </label>
              <div className="relative mt-1.5">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                  <KeyRound className="h-4 w-4" />
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="••••••••"
                  className="block w-full rounded-xl border border-slate-300 bg-white py-2.5 pl-9 pr-3.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-600 focus:outline-hidden focus:ring-2 focus:ring-blue-600/20"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-blue-700 focus:outline-hidden focus:ring-2 focus:ring-blue-600/40 disabled:cursor-not-allowed disabled:opacity-60 transition-colors"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Автентифікація...</span>
                </>
              ) : (
                <>
                  <LogIn className="h-4 w-4" />
                  <span>Увійти до системи</span>
                </>
              )}
            </button>
          </form>

          <div className="mt-7 border-t border-slate-200 pt-5">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Демо-облікові записи (швидке заповнення)
            </p>
            <div className="mt-2.5 flex flex-wrap gap-2">
              {DEMO_ACCOUNTS.map((account) => (
                <button
                  key={account.role}
                  type="button"
                  onClick={() => handleSelectDemoAccount(account)}
                  className={`inline-flex items-center rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-colors ${account.badgeClass}`}
                >
                  {account.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
