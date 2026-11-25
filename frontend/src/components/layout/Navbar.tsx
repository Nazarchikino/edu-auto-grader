import type { ReactElement } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { KeyRound, LogOut, Menu, UserCheck } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import type { UserRole } from "../../types/api";

const ROLE_BADGE_CONFIG: Record<
  UserRole,
  { label: string; className: string }
> = {
  student: {
    label: "Студент",
    className: "bg-blue-50 text-blue-700 border-blue-200",
  },
  teacher: {
    label: "Викладач",
    className: "bg-emerald-50 text-emerald-700 border-emerald-200",
  },
  admin: {
    label: "Адміністратор",
    className: "bg-purple-50 text-purple-700 border-purple-200",
  },
};

function resolvePageTitle(pathname: string): string {
  if (pathname.startsWith("/student/courses")) {
    return "Навчальні курси та практикум";
  }
  if (pathname.startsWith("/student/modules")) {
    return "Навчальний модуль та практична робота";
  }
  if (pathname.startsWith("/student/gradebook")) {
    return "Електронна залікова книжка";
  }
  if (pathname.startsWith("/teacher/courses")) {
    return "Конструктор навчальних курсів і лекцій";
  }
  if (pathname.startsWith("/teacher/rules")) {
    return "Налаштування критеріїв автоперевірки";
  }
  if (pathname.startsWith("/teacher/journal")) {
    return "Електронний журнал групи та антиплагіат";
  }
  if (pathname.startsWith("/admin/users")) {
    return "Адміністрування користувачів та академічних груп";
  }
  return "Вебсистема електронних посібників та автоперевірки";
}

export interface NavbarProps {
  onOpenSidebar: () => void;
  onOpenChangePassword: () => void;
}

export function Navbar({
  onOpenSidebar,
  onOpenChangePassword,
}: NavbarProps): ReactElement | null {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  if (user === null) {
    return null;
  }

  const roleBadge = ROLE_BADGE_CONFIG[user.role];
  const pageTitle = resolvePageTitle(location.pathname);

  const handleLogout = (): void => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="sticky top-0 z-20 flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur-xs sm:px-6">
      <div className="flex items-center gap-3 min-w-0">
        <button
          type="button"
          onClick={onOpenSidebar}
          className="inline-flex items-center justify-center rounded-lg border border-slate-200 p-2 text-slate-600 hover:bg-slate-100 hover:text-slate-900 lg:hidden"
          aria-label="Відкрити меню навігації"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="min-w-0">
          <h1 className="truncate text-base font-bold text-slate-900 sm:text-lg">
            {pageTitle}
          </h1>
        </div>
      </div>

      <div className="flex items-center gap-3 sm:gap-4">
        {user.role === "student" && (
          <div className="hidden md:flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700">
            <span>Група: {user.group_code ?? "—"}</span>
            <span className="text-slate-300">•</span>
            <span>
              Варіант за списком: №{user.list_number ?? 1}
            </span>
          </div>
        )}

        <div className="flex items-center gap-2.5">
          <div className="hidden sm:flex flex-col items-end">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-slate-900">
                {user.full_name}
              </span>
              <span
                className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${roleBadge.className}`}
              >
                <UserCheck className="h-3 w-3" />
                {roleBadge.label}
              </span>
            </div>
            <span className="text-xs text-slate-500">{user.email}</span>
          </div>

          <span
            className={`inline-flex sm:hidden items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${roleBadge.className}`}
          >
            {roleBadge.label}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onOpenChangePassword}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-2xs transition-colors hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
            title="Змінити пароль"
            aria-label="Змінити пароль"
          >
            <KeyRound className="h-4 w-4" />
            <span className="hidden md:inline">Змінити пароль</span>
          </button>

          <button
            type="button"
            onClick={handleLogout}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-2xs transition-colors hover:border-rose-200 hover:bg-rose-50 hover:text-rose-700"
            title="Вийти з облікового запису"
          >
            <LogOut className="h-4 w-4" />
            <span className="hidden sm:inline">Вийти</span>
          </button>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
