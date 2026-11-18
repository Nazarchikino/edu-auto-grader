import type { ReactElement, ReactNode } from "react";
import { Link, Navigate, Outlet, useLocation } from "react-router-dom";
import { Loader2, ShieldAlert } from "lucide-react";
import { getDefaultHomePath, useAuth } from "../../context/AuthContext";
import type { UserRole } from "../../types/api";

const ROLE_LABELS: Record<UserRole, string> = {
  student: "Студент",
  teacher: "Викладач",
  admin: "Адміністратор",
};

export interface RoleGuardProps {
  allowedRoles?: readonly UserRole[];
  children?: ReactNode;
}

export function RoleGuard({
  allowedRoles,
  children,
}: RoleGuardProps): ReactElement {
  const { user, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 p-6">
        <div className="flex flex-col items-center gap-3 rounded-xl bg-white px-8 py-6 shadow-sm border border-slate-200">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p className="text-sm font-medium text-slate-700">
            Перевірка сесії користувача...
          </p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || user === null) {
    return (
      <Navigate
        to="/login"
        state={{ from: location.pathname }}
        replace
      />
    );
  }

  if (
    allowedRoles !== undefined &&
    allowedRoles.length > 0 &&
    !allowedRoles.includes(user.role)
  ) {
    const requiredLabels = allowedRoles
      .map((role) => ROLE_LABELS[role])
      .join(", ");
    const homePath = getDefaultHomePath(user.role);

    return (
      <div className="min-h-[60vh] flex items-center justify-center p-6">
        <div className="max-w-md w-full rounded-xl bg-white p-6 shadow-sm border border-rose-200 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose-600">
            <ShieldAlert className="h-6 w-6" />
          </div>
          <h2 className="mt-4 text-lg font-bold text-slate-900">
            Доступ обмежено
          </h2>
          <p className="mt-2 text-sm text-slate-600">
            Ваша поточна роль —{" "}
            <span className="font-semibold text-slate-800">
              {ROLE_LABELS[user.role]}
            </span>
            . Цей розділ доступний лише для ролей:{" "}
            <span className="font-semibold text-slate-800">
              {requiredLabels}
            </span>
            .
          </p>
          <div className="mt-6">
            <Link
              to={homePath}
              className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 transition-colors"
            >
              Перейти до робочого кабінету
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (children !== undefined) {
    return <>{children}</>;
  }

  return <Outlet />;
}

export default RoleGuard;
