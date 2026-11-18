import type { ComponentType, ReactElement } from "react";
import { NavLink } from "react-router-dom";
import {
  BookOpen,
  BookOpenCheck,
  Code2,
  Database,
  FileSpreadsheet,
  FileText,
  GraduationCap,
  ShieldCheck,
  SlidersHorizontal,
  TableProperties,
  UserCog,
  X,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import type { UserRole } from "../../types/api";

export interface NavigationItem {
  to: string;
  label: string;
  description: string;
  icon: ComponentType<{ className?: string }>;
}

const ROLE_SECTION_TITLES: Record<UserRole, string> = {
  student: "Кабінет студента",
  teacher: "Кабінет викладача",
  admin: "Панель адміністратора",
};

const ROLE_NAVIGATION_MAP: Record<UserRole, readonly NavigationItem[]> = {
  student: [
    {
      to: "/student/courses",
      label: "Навчальні курси",
      description: "Лекції, тести-допуски та практичні",
      icon: BookOpen,
    },
    {
      to: "/student/gradebook",
      label: "Залікова книжка",
      description: "Звіти автоперевірки та оцінки",
      icon: GraduationCap,
    },
  ],
  teacher: [
    {
      to: "/teacher/courses",
      label: "Конструктор курсів",
      description: "Модулі, лекції та тести-допуски",
      icon: BookOpenCheck,
    },
    {
      to: "/teacher/rules",
      label: "Правила перевірки",
      description: "Критерії оцінювання робіт",
      icon: SlidersHorizontal,
    },
    {
      to: "/teacher/journal",
      label: "Журнал групи",
      description: "Антиплагіат та експорт відомостей",
      icon: TableProperties,
    },
  ],
  admin: [
    {
      to: "/admin/users",
      label: "Користувачі та групи",
      description: "Облікові записи, ролі та групи",
      icon: UserCog,
    },
    {
      to: "/teacher/courses",
      label: "Конструктор курсів",
      description: "Керування навчальними курсами",
      icon: BookOpenCheck,
    },
    {
      to: "/teacher/rules",
      label: "Правила перевірки",
      description: "Критерії оцінювання робіт",
      icon: SlidersHorizontal,
    },
    {
      to: "/teacher/journal",
      label: "Журнал групи",
      description: "Відомості успішності та експорт",
      icon: TableProperties,
    },
  ],
};

interface DisciplineChip {
  slug: string;
  label: string;
  format: string;
  icon: ComponentType<{ className?: string }>;
  badgeClass: string;
}

const DISCIPLINE_CHIPS: readonly DisciplineChip[] = [
  {
    slug: "word",
    label: "MS Word",
    format: ".docx",
    icon: FileText,
    badgeClass: "bg-blue-50 text-blue-700 border-blue-200",
  },
  {
    slug: "excel",
    label: "MS Excel",
    format: ".xlsx",
    icon: FileSpreadsheet,
    badgeClass: "bg-emerald-50 text-emerald-700 border-emerald-200",
  },
  {
    slug: "access",
    label: "MS Access",
    format: ".accdb",
    icon: Database,
    badgeClass: "bg-amber-50 text-amber-700 border-amber-200",
  },
  {
    slug: "html",
    label: "HTML5",
    format: "DOM",
    icon: Code2,
    badgeClass: "bg-violet-50 text-violet-700 border-violet-200",
  },
];

export interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps): ReactElement | null {
  const { user } = useAuth();

  if (user === null) {
    return null;
  }

  const navItems = ROLE_NAVIGATION_MAP[user.role];
  const sectionTitle = ROLE_SECTION_TITLES[user.role];

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-slate-900/50 backdrop-blur-xs lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col bg-slate-900 text-slate-100 transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-16 items-center justify-between border-b border-slate-800 px-5">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 text-white shadow-xs">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <span className="block text-sm font-bold tracking-tight text-white">
                Edu Auto Grader
              </span>
              <span className="block text-xs text-slate-400">
                kpefk.lcloud.in.ua
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white lg:hidden"
            aria-label="Закрити меню навігації"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-5 space-y-6">
          <div>
            <p className="px-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
              {sectionTitle}
            </p>
            <nav className="mt-2.5 space-y-1.5" aria-label={sectionTitle}>
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    onClick={onClose}
                    className={({ isActive }) =>
                      `group flex items-start gap-3 rounded-xl px-3.5 py-2.5 text-sm transition-colors ${
                        isActive
                          ? "bg-blue-600 text-white shadow-xs"
                          : "text-slate-300 hover:bg-slate-800/80 hover:text-white"
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <Icon
                          className={`mt-0.5 h-5 w-5 shrink-0 ${
                            isActive
                              ? "text-white"
                              : "text-slate-400 group-hover:text-slate-200"
                          }`}
                        />
                        <div className="min-w-0 flex-1">
                          <p className="font-medium leading-tight">
                            {item.label}
                          </p>
                          <p
                            className={`mt-0.5 text-xs leading-snug ${
                              isActive
                                ? "text-blue-100"
                                : "text-slate-400 group-hover:text-slate-300"
                            }`}
                          >
                            {item.description}
                          </p>
                        </div>
                      </>
                    )}
                  </NavLink>
                );
              })}
            </nav>
          </div>

          {user.role === "student" && (
            <div className="rounded-xl border border-slate-800 bg-slate-800/60 p-3.5">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Параметри варіанту
              </p>
              <div className="mt-2 space-y-1.5 text-xs text-slate-300">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Академічна група:</span>
                  <span className="font-semibold text-white">
                    {user.group_code ?? "Не призначено"}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Номер у журналі:</span>
                  <span className="font-semibold text-blue-400">
                    {user.list_number !== null ? `№${user.list_number}` : "№1"}
                  </span>
                </div>
              </div>
            </div>
          )}

          <div>
            <p className="px-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
              Модулі автоперевірки
            </p>
            <div className="mt-2.5 grid grid-cols-2 gap-2 px-1">
              {DISCIPLINE_CHIPS.map((chip) => {
                const ChipIcon = chip.icon;
                return (
                  <div
                    key={chip.slug}
                    className="flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-800/50 px-2.5 py-2 text-xs text-slate-300"
                  >
                    <ChipIcon className="h-3.5 w-3.5 shrink-0 text-blue-400" />
                    <div className="min-w-0">
                      <p className="truncate font-medium text-slate-200">
                        {chip.label}
                      </p>
                      <p className="text-[10px] text-slate-400">
                        {chip.format}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="border-t border-slate-800 px-4 py-3.5 text-xs text-slate-400">
          <p className="font-medium text-slate-300">
            Ядро детермінованої перевірки
          </p>
          <p className="mt-0.5 text-[11px] text-slate-500">
            Word • Excel • Access • HTML + Антиплагіат
          </p>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
