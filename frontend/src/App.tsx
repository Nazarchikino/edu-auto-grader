import { useEffect, useState, type ReactElement } from "react";
import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
  useNavigate,
} from "react-router-dom";
import { CheckCircle2, X } from "lucide-react";
import {
  AuthProvider,
  getDefaultHomePath,
  useAuth,
} from "./context/AuthContext";
import { ChangePasswordModal } from "./components/layout/ChangePasswordModal";
import { Navbar } from "./components/layout/Navbar";
import { RoleGuard } from "./components/layout/RoleGuard";
import { Sidebar } from "./components/layout/Sidebar";
import { LoginPage } from "./pages/LoginPage";
import { AdminUsersPage } from "./pages/admin/AdminUsersPage";
import { CoursesPage } from "./pages/student/CoursesPage";
import { GradebookPage } from "./pages/student/GradebookPage";
import { ModuleViewPage } from "./pages/student/ModuleViewPage";
import { CourseEditorPage } from "./pages/teacher/CourseEditorPage";
import { GroupJournalPage } from "./pages/teacher/GroupJournalPage";
import { RuleBuilderPage } from "./pages/teacher/RuleBuilderPage";

function ProtectedAppLayout(): ReactElement {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] =
    useState<boolean>(false);
  const [passwordToast, setPasswordToast] = useState<string | null>(null);

  const isForcedPasswordChange = user?.must_change_password === true;

  useEffect(() => {
    if (passwordToast === null) {
      return;
    }
    const timeoutId = window.setTimeout(() => {
      setPasswordToast(null);
    }, 4500);
    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [passwordToast]);

  const handleForcedLogout = (): void => {
    setIsPasswordModalOpen(false);
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />
      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar
          onOpenSidebar={() => setIsSidebarOpen(true)}
          onOpenChangePassword={() => setIsPasswordModalOpen(true)}
        />
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>

      {passwordToast !== null && (
        <div
          role="status"
          className="fixed bottom-4 right-4 z-40 flex max-w-sm items-start gap-2.5 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-xs font-medium text-emerald-800 shadow-lg"
        >
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
          <span className="flex-1">{passwordToast}</span>
          <button
            type="button"
            onClick={() => setPasswordToast(null)}
            className="rounded-md p-0.5 text-emerald-600 hover:bg-emerald-100"
            aria-label="Закрити сповіщення"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      )}

      <ChangePasswordModal
        isOpen={isForcedPasswordChange || isPasswordModalOpen}
        forced={isForcedPasswordChange}
        onClose={() => {
          if (!isForcedPasswordChange) {
            setIsPasswordModalOpen(false);
          }
        }}
        onLogout={handleForcedLogout}
        onSuccess={() => {
          setIsPasswordModalOpen(false);
          setPasswordToast(
            "Пароль успішно змінено. Інші активні сесії завершено."
          );
        }}
      />
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
                  element={<CourseEditorPage />}
                />
                <Route path="/teacher/rules" element={<RuleBuilderPage />} />
                <Route
                  path="/teacher/journal"
                  element={<GroupJournalPage />}
                />
              </Route>

              <Route element={<RoleGuard allowedRoles={["admin"]} />}>
                <Route path="/admin/users" element={<AdminUsersPage />} />
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
