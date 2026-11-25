import {
  useEffect,
  useState,
  type FormEvent,
  type ReactElement,
} from "react";
import {
  AlertCircle,
  AlertTriangle,
  Eye,
  EyeOff,
  KeyRound,
  Loader2,
  LogOut,
  ShieldCheck,
  X,
} from "lucide-react";
import { extractApiErrorMessage, useAuth } from "../../context/AuthContext";

const MIN_NEW_PASSWORD_LENGTH = 8;
const MAX_PASSWORD_LENGTH = 128;

export interface ChangePasswordModalProps {
  isOpen: boolean;
  forced: boolean;
  onClose: () => void;
  onLogout: () => void;
  onSuccess?: () => void;
}

export function ChangePasswordModal({
  isOpen,
  forced,
  onClose,
  onLogout,
  onSuccess,
}: ChangePasswordModalProps): ReactElement | null {
  const { changePassword } = useAuth();

  const [currentPassword, setCurrentPassword] = useState<string>("");
  const [newPassword, setNewPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [showCurrentPassword, setShowCurrentPassword] = useState<boolean>(false);
  const [showNewPassword, setShowNewPassword] = useState<boolean>(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    if (!isOpen) {
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setShowCurrentPassword(false);
      setShowNewPassword(false);
      setShowConfirmPassword(false);
      setErrorMessage(null);
      setIsSubmitting(false);
    }
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen || forced) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key === "Escape" && !isSubmitting) {
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [forced, isOpen, isSubmitting, onClose]);

  if (!isOpen) {
    return null;
  }

  const handleBackdropClick = (): void => {
    if (!forced && !isSubmitting) {
      onClose();
    }
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>
  ): Promise<void> => {
    event.preventDefault();
    setErrorMessage(null);

    if (currentPassword.length === 0) {
      setErrorMessage("Введіть поточний пароль.");
      return;
    }

    if (newPassword.length < MIN_NEW_PASSWORD_LENGTH) {
      setErrorMessage(
        `Новий пароль повинен містити щонайменше ${MIN_NEW_PASSWORD_LENGTH} символів.`
      );
      return;
    }

    if (newPassword.length > MAX_PASSWORD_LENGTH) {
      setErrorMessage(
        `Новий пароль не може перевищувати ${MAX_PASSWORD_LENGTH} символів.`
      );
      return;
    }

    if (newPassword === currentPassword) {
      setErrorMessage("Новий пароль не може збігатися з поточним паролем.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setErrorMessage("Підтвердження нового пароля не збігається.");
      return;
    }

    setIsSubmitting(true);
    try {
      await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      onSuccess?.();
      onClose();
    } catch (error: unknown) {
      setErrorMessage(
        extractApiErrorMessage(
          error,
          "Не вдалося змінити пароль. Перевірте поточний пароль і спробуйте ще раз."
        )
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/55 p-4 backdrop-blur-xs"
      role="dialog"
      aria-modal="true"
      aria-labelledby="change-password-modal-title"
      onClick={handleBackdropClick}
    >
      <div
        className="w-full max-w-md rounded-2xl border border-slate-200 bg-white shadow-xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-3 border-b border-slate-200 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
              <KeyRound className="h-5 w-5" />
            </div>
            <div>
              <h2
                id="change-password-modal-title"
                className="text-base font-bold text-slate-900"
              >
                {forced ? "Обов'язкова зміна пароля" : "Зміна пароля"}
              </h2>
              <p className="text-xs text-slate-500">
                {forced
                  ? "Встановіть власний надійний пароль для продовження роботи"
                  : "Після зміни пароля всі інші активні сесії будуть завершені"}
              </p>
            </div>
          </div>

          {!forced && (
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 disabled:opacity-50"
              aria-label="Закрити вікно зміни пароля"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        <form className="space-y-4 px-6 py-5" onSubmit={handleSubmit} noValidate>
          {forced && (
            <div className="flex items-start gap-2.5 rounded-xl border border-amber-200 bg-amber-50 p-3.5 text-xs font-medium text-amber-800">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
              <span>
                Ви увійшли з тимчасовим паролем (після імпорту або скидання
                адміністратором). Щоб продовжити роботу в системі, задайте новий
                пароль довжиною від 8 символів.
              </span>
            </div>
          )}

          {errorMessage !== null && (
            <div
              role="alert"
              className="flex items-start gap-2.5 rounded-xl border border-rose-200 bg-rose-50 p-3.5 text-xs font-medium text-rose-700"
            >
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" />
              <span>{errorMessage}</span>
            </div>
          )}

          <div>
            <label
              htmlFor="current-password"
              className="block text-xs font-semibold uppercase tracking-wide text-slate-700"
            >
              Поточний пароль
            </label>
            <div className="relative mt-1.5">
              <input
                id="current-password"
                name="current-password"
                type={showCurrentPassword ? "text" : "password"}
                autoComplete="current-password"
                required
                maxLength={MAX_PASSWORD_LENGTH}
                value={currentPassword}
                onChange={(event) => setCurrentPassword(event.target.value)}
                placeholder="Введіть поточний пароль"
                className="block w-full rounded-xl border border-slate-300 bg-white py-2.5 pl-3.5 pr-10 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/20"
              />
              <button
                type="button"
                onClick={() => setShowCurrentPassword((prev) => !prev)}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-600"
                aria-label={
                  showCurrentPassword
                    ? "Приховати поточний пароль"
                    : "Показати поточний пароль"
                }
              >
                {showCurrentPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>

          <div>
            <label
              htmlFor="new-password"
              className="block text-xs font-semibold uppercase tracking-wide text-slate-700"
            >
              Новий пароль
            </label>
            <div className="relative mt-1.5">
              <input
                id="new-password"
                name="new-password"
                type={showNewPassword ? "text" : "password"}
                autoComplete="new-password"
                required
                minLength={MIN_NEW_PASSWORD_LENGTH}
                maxLength={MAX_PASSWORD_LENGTH}
                value={newPassword}
                onChange={(event) => setNewPassword(event.target.value)}
                placeholder="Мінімум 8 символів"
                className="block w-full rounded-xl border border-slate-300 bg-white py-2.5 pl-3.5 pr-10 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/20"
              />
              <button
                type="button"
                onClick={() => setShowNewPassword((prev) => !prev)}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-600"
                aria-label={
                  showNewPassword
                    ? "Приховати новий пароль"
                    : "Показати новий пароль"
                }
              >
                {showNewPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>

          <div>
            <label
              htmlFor="confirm-new-password"
              className="block text-xs font-semibold uppercase tracking-wide text-slate-700"
            >
              Підтвердження нового пароля
            </label>
            <div className="relative mt-1.5">
              <input
                id="confirm-new-password"
                name="confirm-new-password"
                type={showConfirmPassword ? "text" : "password"}
                autoComplete="new-password"
                required
                minLength={MIN_NEW_PASSWORD_LENGTH}
                maxLength={MAX_PASSWORD_LENGTH}
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                placeholder="Повторіть новий пароль"
                className="block w-full rounded-xl border border-slate-300 bg-white py-2.5 pl-3.5 pr-10 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/20"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword((prev) => !prev)}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-600"
                aria-label={
                  showConfirmPassword
                    ? "Приховати підтвердження пароля"
                    : "Показати підтвердження пароля"
                }
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2.5 border-t border-slate-100 pt-4">
            {forced ? (
              <button
                type="button"
                onClick={onLogout}
                disabled={isSubmitting}
                className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 transition-colors hover:border-rose-200 hover:bg-rose-50 hover:text-rose-700 disabled:opacity-50"
              >
                <LogOut className="h-4 w-4" />
                <span>Вийти</span>
              </button>
            ) : (
              <button
                type="button"
                onClick={onClose}
                disabled={isSubmitting}
                className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-50 disabled:opacity-50"
              >
                Скасувати
              </button>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-xs transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600/40 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Збереження...</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="h-4 w-4" />
                  <span>Зберегти пароль</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ChangePasswordModal;
