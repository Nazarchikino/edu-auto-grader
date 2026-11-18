import { useState, type ReactElement } from "react";
import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
} from "react-router-dom";
import {
  AuthProvider,
  getDefaultHomePath,
  useAuth,
} from "./context/AuthContext";
import { Navbar } from "./components/layout/Navbar";
import { RoleGuard } from "./components/layout/RoleGuard";
import { Sidebar } from "./components/layout/Sidebar";
import { LoginPage } from "./pages/LoginPage";
import { CoursesPage } from "./pages/student/CoursesPage";
import { GradebookPage } from "./pages/student/GradebookPage";
import { ModuleViewPage } from "./pages/student/ModuleViewPage";

function ProtectedAppLayout(): ReactElement {
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />
      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar onOpenSidebar={() => setIsSidebarOpen(true)} />
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function RoleHomeRedirect(): ReactElement {
  const { user } = useAuth();
  if (user === null) {
    return <Navigate to="/login" replace />;
  }
  return <Navigate to={getDefaultHomePath(user.role)} replace />;
}

interface WorkspaceSectionProps {
  title: string;
  subtitle: string;
  taskBadge: string;
}

function WorkspaceSectionPlaceholder({
  title,
  subtitle,
  taskBadge,
}: WorkspaceSectionProps): ReactElement {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-4xl rounded-2xl border border-slate-200 bg-white p-6 shadow-xs sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
          {taskBadge}
        </span>
        {user !== null && (
          <span className="text-xs font-medium text-slate-500">
            Активний профіль: {user.full_name} ({user.email})
          </span>
        )}
      </div>
      <h2 className="mt-4 text-xl font-bold text-slate-900">{title}</h2>
      <p className="mt-2 text-sm leading-relaxed text-slate-600">{subtitle}</p>
    </div>
  );
}

export function App(): ReactElement {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route element={<RoleGuard />}>
            <Route element={<ProtectedAppLayout />}>
              <Route index element={<RoleHomeRedirect />} />

              <Route element={<RoleGuard allowedRoles={["student"]} />}>
                <Route path="/student/courses" element={<CoursesPage />} />
                <Route
                  path="/student/modules/:moduleId"
                  element={<ModuleViewPage />}
                />
                <Route path="/student/gradebook" element={<GradebookPage />} />
              </Route>

              <Route
                element={<RoleGuard allowedRoles={["teacher", "admin"]} />}
              >
                <Route
                  path="/teacher/courses"
                  element={
                    <WorkspaceSectionPlaceholder
                      title="Конструктор навчальних курсів і лекцій"
                      subtitle="Створення та редагування курсів, модулів, лекційних матеріалів, тестових питань для допуску та методичних вказівок."
                      taskBadge="Кабінет викладача"
                    />
                  }
                />
                <Route
                  path="/teacher/rules"
                  element={
                    <WorkspaceSectionPlaceholder
                      title="Налаштування критеріїв автоперевірки"
                      subtitle="Візуальний конструктор JSONB-правил оцінювання практичних робіт із дисциплін Word, Excel, Access та HTML."
                      taskBadge="Правила автоперевірки"
                    />
                  }
                />
                <Route
                  path="/teacher/journal"
                  element={
                    <WorkspaceSectionPlaceholder
                      title="Електронний журнал групи та антиплагіат"
                      subtitle="Зведена відомість успішності групи, індикація збігів SHA-256 / core.xml, ручне коригування оцінок та експорт у .xlsx / .pdf."
                      taskBadge="Журнал та аналітика"
                    />
                  }
                />
              </Route>

              <Route element={<RoleGuard allowedRoles={["admin"]} />}>
                <Route
                  path="/admin/users"
                  element={
                    <WorkspaceSectionPlaceholder
                      title="Керування користувачами та академічними групами"
                      subtitle="Адміністрування облікових записів студентів, викладачів, призначення ролей та ведення довідника академічних груп коледжу."
                      taskBadge="Панель адміністратора"
                    />
                  }
                />
              </Route>

              <Route path="*" element={<RoleHomeRedirect />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
