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
import { AdminUsersPage } from "./pages/admin/AdminUsersPage";
import { CoursesPage } from "./pages/student/CoursesPage";
import { GradebookPage } from "./pages/student/GradebookPage";
import { ModuleViewPage } from "./pages/student/ModuleViewPage";
import { CourseEditorPage } from "./pages/teacher/CourseEditorPage";
import { GroupJournalPage } from "./pages/teacher/GroupJournalPage";
import { RuleBuilderPage } from "./pages/teacher/RuleBuilderPage";

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
