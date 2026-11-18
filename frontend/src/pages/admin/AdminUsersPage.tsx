import {
  useEffect,
  useMemo,
  useState,
  type FormEvent,
  type ReactElement,
} from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  AlertTriangle,
  BookMarked,
  Building2,
  CheckCircle2,
  Edit3,
  GraduationCap,
  KeyRound,
  Layers,
  Loader2,
  Mail,
  Plus,
  RefreshCw,
  Search,
  Shield,
  Trash2,
  UserCheck,
  UserCog,
  UserPlus,
  Users,
  X,
} from "lucide-react";
import apiClient from "../../api/client";
import { extractApiErrorMessage, useAuth } from "../../context/AuthContext";
import {
  USER_ROLES,
  type AcademicGroupCreate,
  type AcademicGroupRead,
  type AcademicGroupUpdate,
  type UserCreate,
  type UserRead,
  type UserRole,
  type UserUpdate,
} from "../../types/api";

type AdminTab = "users" | "groups";
type RoleFilter = "all" | UserRole;
type GroupFilter = "all" | "unassigned" | string;
type CourseYearFilter = "all" | number;

interface FeedbackBanner {
  type: "success" | "error";
  text: string;
}

interface UserModalState {
  mode: "create" | "edit";
  targetUser: UserRead | null;
}

interface GroupModalState {
  mode: "create" | "edit";
  targetGroup: AcademicGroupRead | null;
}

interface DeleteTarget {
  kind: "user" | "group";
  id: string;
  title: string;
  description: string;
  warning?: string;
}

interface SpecialtySummary {
  specialty: string;
  groupCount: number;
  studentCount: number;
}

const ROLE_META: Record<
  UserRole,
  { label: string; pluralLabel: string; badgeClass: string }
> = {
  student: {
    label: "Студент",
    pluralLabel: "Студенти",
    badgeClass: "border-blue-200 bg-blue-50 text-blue-700",
  },
  teacher: {
    label: "Викладач",
    pluralLabel: "Викладачі",
    badgeClass: "border-emerald-200 bg-emerald-50 text-emerald-700",
  },
  admin: {
    label: "Адміністратор",
    pluralLabel: "Адміністратори",
    badgeClass: "border-purple-200 bg-purple-50 text-purple-700",
  },
};

const COURSE_YEARS: readonly number[] = [1, 2, 3, 4, 5, 6];

async function fetchAdminUsers(): Promise<UserRead[]> {
  const response = await apiClient.get<UserRead[]>("/admin/users");
  return response.data;
}

async function fetchAdminGroups(): Promise<AcademicGroupRead[]> {
  const response = await apiClient.get<AcademicGroupRead[]>("/admin/groups");
  return response.data;
}

function formatRegistrationDate(isoString: string): string {
  const parsed = new Date(isoString);
  if (Number.isNaN(parsed.getTime())) {
    return isoString;
  }
  return parsed.toLocaleDateString("uk-UA", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

export function AdminUsersPage(): ReactElement {
  const queryClient = useQueryClient();
  const { user: currentAdmin, refreshUser } = useAuth();

  const [activeTab, setActiveTab] = useState<AdminTab>("users");
  const [feedback, setFeedback] = useState<FeedbackBanner | null>(null);

  // Фільтри вкладки користувачів
  const [roleFilter, setRoleFilter] = useState<RoleFilter>("all");
  const [groupFilter, setGroupFilter] = useState<GroupFilter>("all");
  const [userSearch, setUserSearch] = useState<string>("");

  // Фільтри вкладки академічних груп та спеціальностей
  const [groupSearch, setGroupSearch] = useState<string>("");
  const [courseYearFilter, setCourseYearFilter] =
    useState<CourseYearFilter>("all");
  const [specialtyFilter, setSpecialtyFilter] = useState<string>("all");

  // Модальні вікна
  const [userModal, setUserModal] = useState<UserModalState | null>(null);
  const [groupModal, setGroupModal] = useState<GroupModalState | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null);

  // Поля форми користувача
  const [userFullName, setUserFullName] = useState<string>("");
  const [userEmail, setUserEmail] = useState<string>("");
  const [userRole, setUserRole] = useState<UserRole>("student");
  const [userGroupId, setUserGroupId] = useState<string>("");
  const [userListNumber, setUserListNumber] = useState<string>("");
  const [userPassword, setUserPassword] = useState<string>("");
  const [userFormError, setUserFormError] = useState<string | null>(null);

  // Поля форми академічної групи
  const [groupCode, setGroupCode] = useState<string>("");
  const [groupSpecialty, setGroupSpecialty] = useState<string>("");
  const [groupCourseYear, setGroupCourseYear] = useState<string>("1");
  const [groupFormError, setGroupFormError] = useState<string | null>(null);

  const {
    data: users = [],
    isLoading: isLoadingUsers,
    isError: isUsersError,
    error: usersError,
    refetch: refetchUsers,
    isFetching: isFetchingUsers,
  } = useQuery<UserRead[]>({
    queryKey: ["admin-users"],
    queryFn: fetchAdminUsers,
  });

  const {
    data: groups = [],
    isLoading: isLoadingGroups,
    isError: isGroupsError,
    error: groupsError,
    refetch: refetchGroups,
    isFetching: isFetchingGroups,
  } = useQuery<AcademicGroupRead[]>({
    queryKey: ["admin-groups"],
    queryFn: fetchAdminGroups,
  });

  // Закриття модалок за клавішею Escape
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key !== "Escape") {
        return;
      }
      if (deleteTarget !== null) {
        setDeleteTarget(null);
      } else if (userModal !== null) {
        setUserModal(null);
      } else if (groupModal !== null) {
        setGroupModal(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [deleteTarget, groupModal, userModal]);

  // Допоміжні довідники та агрегації
  const groupById = useMemo<Record<string, AcademicGroupRead>>(() => {
    const map: Record<string, AcademicGroupRead> = {};
    for (const group of groups) {
      map[group.id] = group;
    }
    return map;
  }, [groups]);

  const studentsCountByGroup = useMemo<Record<string, number>>(() => {
    const counts: Record<string, number> = {};
    for (const item of users) {
      if (item.role === "student" && item.group_id !== null) {
        counts[item.group_id] = (counts[item.group_id] ?? 0) + 1;
      }
    }
    return counts;
  }, [users]);

  const roleCounts = useMemo<Record<UserRole, number>>(() => {
    const counts: Record<UserRole, number> = {
      student: 0,
      teacher: 0,
      admin: 0,
    };
    for (const item of users) {
      counts[item.role] += 1;
    }
    return counts;
  }, [users]);

  const unassignedStudentsCount = useMemo<number>(
    () =>
      users.filter(
        (item) => item.role === "student" && item.group_id === null
      ).length,
    [users]
  );

  // Виявлення дубльованих порядкових номерів студентів у межах однієї групи
  const duplicateListNumberKeys = useMemo<Set<string>>(() => {
    const counts: Record<string, number> = {};
    for (const item of users) {
      if (
        item.role === "student" &&
        item.group_id !== null &&
        item.list_number !== null
      ) {
        const key = `${item.group_id}:${item.list_number}`;
        counts[key] = (counts[key] ?? 0) + 1;
      }
    }
    const duplicates = new Set<string>();
    for (const [key, count] of Object.entries(counts)) {
      if (count > 1) {
        duplicates.add(key);
      }
    }
    return duplicates;
  }, [users]);

  // Зведений довідник спеціальностей коледжу
  const specialtySummaries = useMemo<SpecialtySummary[]>(() => {
    const map = new Map<string, SpecialtySummary>();
    for (const group of groups) {
      const existing = map.get(group.specialty);
      const groupStudents = studentsCountByGroup[group.id] ?? 0;
      if (existing === undefined) {
        map.set(group.specialty, {
          specialty: group.specialty,
          groupCount: 1,
          studentCount: groupStudents,
        });
      } else {
        existing.groupCount += 1;
        existing.studentCount += groupStudents;
      }
    }
    return Array.from(map.values()).sort((a, b) =>
      a.specialty.localeCompare(b.specialty, "uk")
    );
  }, [groups, studentsCountByGroup]);

  // Відфільтровані користувачі
  const filteredUsers = useMemo<UserRead[]>(() => {
    const query = userSearch.trim().toLowerCase();
    return users.filter((item) => {
      if (roleFilter !== "all" && item.role !== roleFilter) {
        return false;
      }
      if (groupFilter === "unassigned") {
        if (item.role !== "student" || item.group_id !== null) {
          return false;
        }
      } else if (groupFilter !== "all") {
        if (item.group_id !== groupFilter) {
          return false;
        }
      }
      if (query.length > 0) {
        const groupInfo =
          item.group_id !== null ? groupById[item.group_id] : undefined;
        const searchable = [
          item.full_name,
          item.email,
          item.group_code ?? "",
          groupInfo?.specialty ?? "",
        ]
          .join(" ")
          .toLowerCase();
        if (!searchable.includes(query)) {
          return false;
        }
      }
      return true;
    });
  }, [groupById, groupFilter, roleFilter, userSearch, users]);

  // Відфільтровані академічні групи
  const filteredGroups = useMemo<AcademicGroupRead[]>(() => {
    const query = groupSearch.trim().toLowerCase();
    return groups.filter((group) => {
      if (courseYearFilter !== "all" && group.course_year !== courseYearFilter) {
        return false;
      }
      if (specialtyFilter !== "all" && group.specialty !== specialtyFilter) {
        return false;
      }
      if (query.length > 0) {
        const searchable = `${group.code} ${group.specialty}`.toLowerCase();
        if (!searchable.includes(query)) {
          return false;
        }
      }
      return true;
    });
  }, [courseYearFilter, groupSearch, groups, specialtyFilter]);

  const invalidateAdminCaches = async (): Promise<void> => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["admin-users"] }),
      queryClient.invalidateQueries({ queryKey: ["admin-groups"] }),
      queryClient.invalidateQueries({ queryKey: ["academic-groups"] }),
    ]);
  };

  // Мутації користувачів
  const createUserMutation = useMutation({
    mutationFn: async (payload: UserCreate): Promise<UserRead> => {
      const response = await apiClient.post<UserRead>("/admin/users", payload);
      return response.data;
    },
    onSuccess: async (created) => {
      await invalidateAdminCaches();
      setUserModal(null);
      setFeedback({
        type: "success",
        text: `Обліковий запис «${created.full_name}» (${ROLE_META[created.role].label}) успішно створено.`,
      });
    },
    onError: (error: unknown) => {
      setUserFormError(
        extractApiErrorMessage(error, "Не вдалося створити користувача.")
      );
    },
  });

  const updateUserMutation = useMutation({
    mutationFn: async ({
      userId,
      payload,
    }: {
      userId: string;
      payload: UserUpdate;
    }): Promise<UserRead> => {
      const response = await apiClient.patch<UserRead>(
        `/admin/users/${userId}`,
        payload
      );
      return response.data;
    },
    onSuccess: async (updated) => {
      await invalidateAdminCaches();
      if (currentAdmin !== null && updated.id === currentAdmin.id) {
        await refreshUser();
      }
      setUserModal(null);
      setFeedback({
        type: "success",
        text: `Дані користувача «${updated.full_name}» оновлено.`,
      });
    },
    onError: (error: unknown) => {
      setUserFormError(
        extractApiErrorMessage(error, "Не вдалося оновити дані користувача.")
      );
    },
  });

  const deleteUserMutation = useMutation({
    mutationFn: async (userId: string): Promise<void> => {
      await apiClient.delete(`/admin/users/${userId}`);
    },
    onSuccess: async () => {
      const label = deleteTarget?.title ?? "Користувача";
      await invalidateAdminCaches();
      setDeleteTarget(null);
      setFeedback({
        type: "success",
        text: `Обліковий запис «${label}» видалено із системи.`,
      });
    },
    onError: (error: unknown) => {
      setDeleteTarget(null);
      setFeedback({
        type: "error",
        text: extractApiErrorMessage(error, "Не вдалося видалити користувача."),
      });
    },
  });

  // Мутації академічних груп
  const createGroupMutation = useMutation({
    mutationFn: async (
      payload: AcademicGroupCreate
    ): Promise<AcademicGroupRead> => {
      const response = await apiClient.post<AcademicGroupRead>(
        "/admin/groups",
        payload
      );
      return response.data;
    },
    onSuccess: async (created) => {
      await invalidateAdminCaches();
      setGroupModal(null);
      setFeedback({
        type: "success",
        text: `Академічну групу «${created.code}» додано до довідника.`,
      });
    },
    onError: (error: unknown) => {
      setGroupFormError(
        extractApiErrorMessage(error, "Не вдалося створити академічну групу.")
      );
    },
  });

  const updateGroupMutation = useMutation({
    mutationFn: async ({
      groupId,
      payload,
    }: {
      groupId: string;
      payload: AcademicGroupUpdate;
    }): Promise<AcademicGroupRead> => {
      const response = await apiClient.patch<AcademicGroupRead>(
        `/admin/groups/${groupId}`,
        payload
      );
      return response.data;
    },
    onSuccess: async (updated) => {
      await invalidateAdminCaches();
      setGroupModal(null);
      setFeedback({
        type: "success",
        text: `Академічну групу «${updated.code}» оновлено.`,
      });
    },
    onError: (error: unknown) => {
      setGroupFormError(
        extractApiErrorMessage(error, "Не вдалося оновити академічну групу.")
      );
    },
  });

  const deleteGroupMutation = useMutation({
    mutationFn: async (groupId: string): Promise<void> => {
      await apiClient.delete(`/admin/groups/${groupId}`);
    },
    onSuccess: async () => {
      const label = deleteTarget?.title ?? "Групу";
      if (deleteTarget !== null && groupFilter === deleteTarget.id) {
        setGroupFilter("all");
      }
      await invalidateAdminCaches();
      setDeleteTarget(null);
      setFeedback({
        type: "success",
        text: `Академічну групу «${label}» видалено.`,
      });
    },
    onError: (error: unknown) => {
      setDeleteTarget(null);
      setFeedback({
        type: "error",
        text: extractApiErrorMessage(
          error,
          "Не вдалося видалити академічну групу."
        ),
      });
    },
  });

  // Відкриття модалок
  const openCreateUserModal = (defaultRole: UserRole = "student"): void => {
    setFeedback(null);
    setUserFormError(null);
    setUserFullName("");
    setUserEmail("");
    setUserRole(defaultRole);
    const defaultGroupId =
      defaultRole === "student" &&
      groupFilter !== "all" &&
      groupFilter !== "unassigned"
        ? groupFilter
        : defaultRole === "student"
          ? (groups[0]?.id ?? "")
          : "";
    setUserGroupId(defaultGroupId);
    setUserListNumber("");
    setUserPassword("");
    setUserModal({ mode: "create", targetUser: null });
  };

  const openEditUserModal = (target: UserRead): void => {
    setFeedback(null);
    setUserFormError(null);
    setUserFullName(target.full_name);
    setUserEmail(target.email);
    setUserRole(target.role);
    setUserGroupId(target.group_id ?? "");
    setUserListNumber(
      target.list_number !== null ? String(target.list_number) : ""
    );
    setUserPassword("");
    setUserModal({ mode: "edit", targetUser: target });
  };

  const openCreateGroupModal = (): void => {
    setFeedback(null);
    setGroupFormError(null);
    setGroupCode("");
    setGroupSpecialty(specialtyFilter !== "all" ? specialtyFilter : "");
    setGroupCourseYear(
      courseYearFilter !== "all" ? String(courseYearFilter) : "1"
    );
    setGroupModal({ mode: "create", targetGroup: null });
  };

  const openEditGroupModal = (target: AcademicGroupRead): void => {
    setFeedback(null);
    setGroupFormError(null);
    setGroupCode(target.code);
    setGroupSpecialty(target.specialty);
    setGroupCourseYear(String(target.course_year));
    setGroupModal({ mode: "edit", targetGroup: target });
  };

  const suggestNextListNumber = (): void => {
    if (userGroupId === "") {
      setUserListNumber("1");
      return;
    }
    let maxNumber = 0;
    for (const item of users) {
      if (
        item.role === "student" &&
        item.group_id === userGroupId &&
        item.list_number !== null &&
        item.id !== userModal?.targetUser?.id
      ) {
        if (item.list_number > maxNumber) {
          maxNumber = item.list_number;
        }
      }
    }
    const nextNumber = Math.min(maxNumber + 1, 100);
    setUserListNumber(String(nextNumber));
  };

  // Сабміт форми користувача
  const handleSubmitUserForm = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    setUserFormError(null);

    const cleanedFullName = userFullName.trim();
    const cleanedEmail = userEmail.trim().toLowerCase();
    const cleanedPassword = userPassword.trim();

    if (cleanedFullName.length === 0) {
      setUserFormError("Вкажіть ПІБ користувача.");
      return;
    }
    if (cleanedEmail.length < 3 || !cleanedEmail.includes("@")) {
      setUserFormError("Вкажіть коректну електронну пошту.");
      return;
    }

    let parsedListNumber: number | null = null;
    if (userRole === "student" && userListNumber.trim().length > 0) {
      const numeric = Number(userListNumber.trim());
      if (!Number.isInteger(numeric) || numeric < 1 || numeric > 100) {
        setUserFormError(
          "Порядковий номер у списку має бути цілим числом від 1 до 100."
        );
        return;
      }
      parsedListNumber = numeric;
    }

    const resolvedGroupId: string | null =
      userRole === "student" && userGroupId !== "" ? userGroupId : null;

    if (userModal?.mode === "create") {
      if (cleanedPassword.length < 6) {
        setUserFormError("Пароль має містити щонайменше 6 символів.");
        return;
      }
      const payload: UserCreate = {
        full_name: cleanedFullName,
        email: cleanedEmail,
        role: userRole,
        group_id: resolvedGroupId,
        list_number: userRole === "student" ? parsedListNumber : null,
        password: cleanedPassword,
      };
      createUserMutation.mutate(payload);
      return;
    }

    if (userModal?.mode === "edit" && userModal.targetUser !== null) {
      if (cleanedPassword.length > 0 && cleanedPassword.length < 6) {
        setUserFormError("Новий пароль має містити щонайменше 6 символів.");
        return;
      }
      const payload: UserUpdate = {
        full_name: cleanedFullName,
        email: cleanedEmail,
        role: userRole,
        group_id: resolvedGroupId,
        list_number: userRole === "student" ? parsedListNumber : null,
      };
      if (cleanedPassword.length > 0) {
        payload.password = cleanedPassword;
      }
      updateUserMutation.mutate({
        userId: userModal.targetUser.id,
        payload,
      });
    }
  };

  // Сабміт форми академічної групи
  const handleSubmitGroupForm = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    setGroupFormError(null);

    const cleanedCode = groupCode.trim();
    const cleanedSpecialty = groupSpecialty.trim();
    const parsedYear = Number(groupCourseYear);

    if (cleanedCode.length === 0) {
      setGroupFormError("Вкажіть шифр академічної групи (наприклад, КН-31).");
      return;
    }
    if (cleanedSpecialty.length === 0) {
      setGroupFormError("Вкажіть спеціальність академічної групи.");
      return;
    }
    if (!Number.isInteger(parsedYear) || parsedYear < 1 || parsedYear > 6) {
      setGroupFormError("Курс навчання має бути в межах від 1 до 6.");
      return;
    }

    if (groupModal?.mode === "create") {
      createGroupMutation.mutate({
        code: cleanedCode,
        specialty: cleanedSpecialty,
        course_year: parsedYear,
      });
      return;
    }

    if (groupModal?.mode === "edit" && groupModal.targetGroup !== null) {
      updateGroupMutation.mutate({
        groupId: groupModal.targetGroup.id,
        payload: {
          code: cleanedCode,
          specialty: cleanedSpecialty,
          course_year: parsedYear,
        },
      });
    }
  };

  const handleConfirmDelete = (): void => {
    if (deleteTarget === null) {
      return;
    }
    if (deleteTarget.kind === "user") {
      deleteUserMutation.mutate(deleteTarget.id);
    } else {
      deleteGroupMutation.mutate(deleteTarget.id);
    }
  };

  const handleRefreshAll = (): void => {
    setFeedback(null);
    void refetchUsers();
    void refetchGroups();
  };

  const handleInspectGroupStudents = (groupId: string): void => {
    setRoleFilter("student");
    setGroupFilter(groupId);
    setUserSearch("");
    setActiveTab("users");
  };

  const isEditingSelf =
    userModal?.mode === "edit" &&
    userModal.targetUser !== null &&
    currentAdmin !== null &&
    userModal.targetUser.id === currentAdmin.id;

  const isSavingUser =
    createUserMutation.isPending || updateUserMutation.isPending;
  const isSavingGroup =
    createGroupMutation.isPending || updateGroupMutation.isPending;
  const isDeleting =
    deleteUserMutation.isPending || deleteGroupMutation.isPending;

  const isInitialLoading = isLoadingUsers || isLoadingGroups;
  const isRefreshing = isFetchingUsers || isFetchingGroups;

  if (isInitialLoading) {
    return (
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white px-6 py-20 text-center shadow-sm">
        <Loader2 className="h-9 w-9 animate-spin text-blue-600" />
        <p className="mt-4 text-sm font-medium text-slate-700">
          Завантаження облікових записів та довідника академічних груп...
        </p>
      </div>
    );
  }

  if (isUsersError || isGroupsError) {
    const errText = isUsersError
      ? extractApiErrorMessage(
          usersError,
          "Не вдалося завантажити список користувачів."
        )
      : extractApiErrorMessage(
          groupsError,
          "Не вдалося завантажити довідник академічних груп."
        );

    return (
      <div className="mx-auto max-w-3xl rounded-2xl border border-rose-200 bg-white p-8 text-center shadow-sm">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose-600">
          <AlertCircle className="h-6 w-6" />
        </div>
        <h2 className="mt-4 text-lg font-bold text-slate-900">
          Помилка завантаження панелі адміністратора
        </h2>
        <p className="mt-2 text-sm text-slate-600">{errText}</p>
        <button
          type="button"
          onClick={handleRefreshAll}
          className="mt-5 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-blue-700"
        >
          <RefreshCw className="h-4 w-4" />
          Повторити запит
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Заголовок та основні дії */}
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="inline-flex items-center gap-1.5 rounded-full border border-purple-200 bg-purple-50 px-3 py-1 text-xs font-semibold text-purple-700">
              <Shield className="h-3.5 w-3.5" />
              Адміністрування коледжу
            </div>
            <h2 className="mt-2.5 text-xl font-bold text-slate-900 sm:text-2xl">
              Користувачі, ролі та академічні групи
            </h2>
            <p className="mt-1 text-sm text-slate-600">
              Керуйте обліковими записами студентів, викладачів і
              адміністраторів, а також ведіть довідники спеціальностей,
              академічних груп та порядкових номерів у журналі.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <button
              type="button"
              onClick={handleRefreshAll}
              disabled={isRefreshing}
              className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-sm font-medium text-slate-700 shadow-sm transition-colors hover:bg-slate-50 disabled:opacity-60"
            >
              <RefreshCw
                className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`}
              />
              Оновити
            </button>

            <button
              type="button"
              onClick={openCreateGroupModal}
              className="inline-flex items-center gap-1.5 rounded-xl border border-blue-200 bg-blue-50 px-3.5 py-2 text-sm font-semibold text-blue-700 transition-colors hover:bg-blue-100"
            >
              <Plus className="h-4 w-4" />
              Додати групу
            </button>

            <button
              type="button"
              onClick={() => openCreateUserModal("student")}
              className="inline-flex items-center gap-1.5 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-blue-700"
            >
              <UserPlus className="h-4 w-4" />
              Додати користувача
            </button>
          </div>
        </div>

        {/* KPI-картки */}
        <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Усього акаунтів
              </span>
              <Users className="h-4 w-4 text-slate-400" />
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              {users.length}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Адміністраторів: {roleCounts.admin}
            </p>
          </div>

          <div className="rounded-xl border border-blue-200/80 bg-blue-50/50 p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-blue-700">
                Студенти
              </span>
              <GraduationCap className="h-4 w-4 text-blue-500" />
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              {roleCounts.student}
            </p>
            <p className="mt-1 text-xs text-slate-600">
              {unassignedStudentsCount > 0
                ? `Без призначеної групи: ${unassignedStudentsCount}`
                : "Усі студенти розподілені по групах"}
            </p>
          </div>

          <div className="rounded-xl border border-emerald-200/80 bg-emerald-50/50 p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-700">
                Викладачі
              </span>
              <UserCheck className="h-4 w-4 text-emerald-500" />
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              {roleCounts.teacher}
            </p>
            <p className="mt-1 text-xs text-slate-600">
              Доступ до курсів, правил та журналів
            </p>
          </div>

          <div className="rounded-xl border border-purple-200/80 bg-purple-50/50 p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-purple-700">
                Академічні групи
              </span>
              <Building2 className="h-4 w-4 text-purple-500" />
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900">
              {groups.length}
            </p>
            <p className="mt-1 text-xs text-slate-600">
              Спеціальностей у довіднику: {specialtySummaries.length}
            </p>
          </div>
        </div>
      </section>

      {/* Повідомлення про результат операції */}
      {feedback !== null && (
        <div
          role="status"
          className={`flex items-start justify-between gap-3 rounded-xl border px-4 py-3 text-sm ${
            feedback.type === "success"
              ? "border-emerald-200 bg-emerald-50 text-emerald-800"
              : "border-rose-200 bg-rose-50 text-rose-800"
          }`}
        >
          <div className="flex items-start gap-2.5">
            {feedback.type === "success" ? (
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
            ) : (
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" />
            )}
            <span className="font-medium">{feedback.text}</span>
          </div>
          <button
            type="button"
            onClick={() => setFeedback(null)}
            className="rounded-lg p-1 opacity-70 transition-opacity hover:opacity-100"
            aria-label="Закрити сповіщення"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Попередження про дублювання порядкових номерів у групах */}
      {duplicateListNumberKeys.size > 0 && activeTab === "users" && (
        <div className="flex items-start gap-2.5 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-900">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
          <p>
            Виявлено студентів із однаковим порядковим номером у межах однієї
            академічної групи. Це призведе до призначення однакових
            індивідуальних варіантів практичних робіт — за потреби скоригуйте №
            у списку.
          </p>
        </div>
      )}

      {/* Перемикач вкладок */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-1">
        <button
          type="button"
          onClick={() => setActiveTab("users")}
          className={`inline-flex items-center gap-2 rounded-t-xl border-b-2 px-4 py-2.5 text-sm font-semibold transition-colors ${
            activeTab === "users"
              ? "border-blue-600 bg-white text-blue-700"
              : "border-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900"
          }`}
        >
          <UserCog className="h-4 w-4" />
          Облікові записи
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-700">
            {users.length}
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("groups")}
          className={`inline-flex items-center gap-2 rounded-t-xl border-b-2 px-4 py-2.5 text-sm font-semibold transition-colors ${
            activeTab === "groups"
              ? "border-blue-600 bg-white text-blue-700"
              : "border-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900"
          }`}
        >
          <Layers className="h-4 w-4" />
          Академічні групи та спеціальності
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-700">
            {groups.length}
          </span>
        </button>
      </div>

      {/* ВКЛАДКА 1: Керування користувачами */}
      {activeTab === "users" && (
        <section className="space-y-4">
          {/* Панель фільтрів */}
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              {/* Фільтр за роллю */}
              <div className="flex flex-wrap items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => setRoleFilter("all")}
                  className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                    roleFilter === "all"
                      ? "bg-slate-900 text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  Усі ({users.length})
                </button>
                {USER_ROLES.map((role) => (
                  <button
                    key={role}
                    type="button"
                    onClick={() => setRoleFilter(role)}
                    className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                      roleFilter === role
                        ? "bg-blue-600 text-white"
                        : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                  >
                    {ROLE_META[role].pluralLabel} ({roleCounts[role]})
                  </button>
                ))}
              </div>

              {/* Пошук та фільтр по групі */}
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                <select
                  value={groupFilter}
                  onChange={(event) => setGroupFilter(event.target.value)}
                  aria-label="Фільтр за академічною групою"
                  className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-800 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                >
                  <option value="all">Усі академічні групи</option>
                  <option value="unassigned">
                    Студенти без групи ({unassignedStudentsCount})
                  </option>
                  {groups.map((group) => (
                    <option key={group.id} value={group.id}>
                      {group.code} — {group.course_year} курс (
                      {studentsCountByGroup[group.id] ?? 0})
                    </option>
                  ))}
                </select>

                <div className="relative min-w-[230px]">
                  <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    value={userSearch}
                    onChange={(event) => setUserSearch(event.target.value)}
                    placeholder="Пошук за ПІБ, email, групою..."
                    className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-8 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                  {userSearch.length > 0 && (
                    <button
                      type="button"
                      onClick={() => setUserSearch("")}
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700"
                      aria-label="Очистити пошук"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Таблиця користувачів */}
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            {filteredUsers.length === 0 ? (
              <div className="px-6 py-14 text-center">
                <Users className="mx-auto h-10 w-10 text-slate-300" />
                <p className="mt-3 text-sm font-semibold text-slate-700">
                  Користувачів за заданими фільтрами не знайдено
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  Змініть параметри пошуку або створіть новий обліковий запис.
                </p>
                <div className="mt-4 flex items-center justify-center gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      setRoleFilter("all");
                      setGroupFilter("all");
                      setUserSearch("");
                    }}
                    className="rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                  >
                    Скинути фільтри
                  </button>
                  <button
                    type="button"
                    onClick={() => openCreateUserModal("student")}
                    className="rounded-xl bg-blue-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-blue-700"
                  >
                    + Додати користувача
                  </button>
                </div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
                  <thead className="bg-slate-50 text-xs font-semibold uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-4 py-3.5">Користувач</th>
                      <th className="px-4 py-3.5">Роль</th>
                      <th className="px-4 py-3.5">Академічна група</th>
                      <th className="px-4 py-3.5">№ у списку</th>
                      <th className="px-4 py-3.5">Створено</th>
                      <th className="px-4 py-3.5 text-right">Дії</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 bg-white">
                    {filteredUsers.map((item) => {
                      const isSelf =
                        currentAdmin !== null && item.id === currentAdmin.id;
                      const roleInfo = ROLE_META[item.role];
                      const groupInfo =
                        item.group_id !== null
                          ? groupById[item.group_id]
                          : undefined;
                      const dupKey =
                        item.role === "student" &&
                        item.group_id !== null &&
                        item.list_number !== null
                          ? `${item.group_id}:${item.list_number}`
                          : null;
                      const hasDuplicateNumber =
                        dupKey !== null && duplicateListNumberKeys.has(dupKey);

                      return (
                        <tr
                          key={item.id}
                          className="transition-colors hover:bg-slate-50/80"
                        >
                          <td className="px-4 py-3.5">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-slate-900">
                                {item.full_name}
                              </span>
                              {isSelf && (
                                <span className="rounded-full border border-purple-200 bg-purple-50 px-2 py-0.5 text-[10px] font-bold uppercase text-purple-700">
                                  Ви
                                </span>
                              )}
                            </div>
                            <div className="mt-0.5 flex items-center gap-1.5 text-xs text-slate-500">
                              <Mail className="h-3 w-3 shrink-0" />
                              <span>{item.email}</span>
                            </div>
                          </td>

                          <td className="px-4 py-3.5">
                            <span
                              className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${roleInfo.badgeClass}`}
                            >
                              {roleInfo.label}
                            </span>
                          </td>

                          <td className="px-4 py-3.5">
                            {item.role === "student" ? (
                              item.group_code !== null ? (
                                <div>
                                  <span className="inline-flex items-center rounded-md border border-slate-200 bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-800">
                                    {item.group_code}
                                  </span>
                                  {groupInfo !== undefined && (
                                    <p className="mt-0.5 max-w-xs truncate text-xs text-slate-500">
                                      {groupInfo.specialty}
                                    </p>
                                  )}
                                </div>
                              ) : (
                                <span className="inline-flex items-center rounded-md border border-amber-200 bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-800">
                                  Не призначено
                                </span>
                              )
                            ) : (
                              <span className="text-xs text-slate-400">—</span>
                            )}
                          </td>

                          <td className="px-4 py-3.5">
                            {item.role === "student" ? (
                              item.list_number !== null ? (
                                <div className="flex items-center gap-1.5">
                                  <span
                                    className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold ${
                                      hasDuplicateNumber
                                        ? "border-amber-300 bg-amber-50 text-amber-800"
                                        : "border-blue-200 bg-blue-50 text-blue-700"
                                    }`}
                                  >
                                    №{item.list_number}
                                  </span>
                                  {hasDuplicateNumber && (
                                    <span
                                      title="Порядковий номер дублюється в межах цієї групи"
                                      className="text-amber-600"
                                    >
                                      <AlertTriangle className="h-3.5 w-3.5" />
                                    </span>
                                  )}
                                </div>
                              ) : (
                                <span className="text-xs text-slate-400">
                                  За замовч. (№1)
                                </span>
                              )
                            ) : (
                              <span className="text-xs text-slate-400">—</span>
                            )}
                          </td>

                          <td className="px-4 py-3.5 text-xs text-slate-500">
                            {formatRegistrationDate(item.created_at)}
                          </td>

                          <td className="px-4 py-3.5 text-right">
                            <div className="inline-flex items-center justify-end gap-1.5">
                              <button
                                type="button"
                                onClick={() => openEditUserModal(item)}
                                className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-700 transition-colors hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700"
                              >
                                <Edit3 className="h-3.5 w-3.5" />
                                Редагувати
                              </button>

                              <button
                                type="button"
                                disabled={isSelf}
                                title={
                                  isSelf
                                    ? "Неможливо видалити власний акаунт"
                                    : "Видалити обліковий запис"
                                }
                                onClick={() =>
                                  setDeleteTarget({
                                    kind: "user",
                                    id: item.id,
                                    title: item.full_name,
                                    description: `${ROLE_META[item.role].label} • ${item.email}`,
                                    warning:
                                      item.role === "student"
                                        ? "Разом з обліковим записом студента буде видалено всі його спроби тестів і здані практичні роботи."
                                        : item.role === "teacher"
                                          ? "Якщо за викладачем закріплені навчальні курси, система заблокує видалення."
                                          : undefined,
                                  })
                                }
                                className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:border-rose-300 hover:bg-rose-50 hover:text-rose-700 disabled:cursor-not-allowed disabled:opacity-40"
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                                <span className="hidden sm:inline">
                                  Видалити
                                </span>
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>
      )}

      {/* ВКЛАДКА 2: Академічні групи та спеціальності */}
      {activeTab === "groups" && (
        <section className="space-y-5">
          {/* Довідник спеціальностей */}
          {specialtySummaries.length > 0 && (
            <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <BookMarked className="h-4 w-4 text-blue-600" />
                  <h3 className="text-sm font-bold text-slate-900">
                    Довідник спеціальностей коледжу
                  </h3>
                </div>
                {specialtyFilter !== "all" && (
                  <button
                    type="button"
                    onClick={() => setSpecialtyFilter("all")}
                    className="text-xs font-semibold text-blue-600 hover:text-blue-700"
                  >
                    Показати всі спеціальності
                  </button>
                )}
              </div>

              <div className="mt-3 flex flex-wrap gap-2">
                {specialtySummaries.map((item) => {
                  const isActive = specialtyFilter === item.specialty;
                  return (
                    <button
                      key={item.specialty}
                      type="button"
                      onClick={() =>
                        setSpecialtyFilter(
                          isActive ? "all" : item.specialty
                        )
                      }
                      className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-left text-xs transition-colors ${
                        isActive
                          ? "border-blue-500 bg-blue-50 text-blue-800"
                          : "border-slate-200 bg-slate-50/70 text-slate-700 hover:border-slate-300 hover:bg-slate-100"
                      }`}
                    >
                      <span className="font-semibold">{item.specialty}</span>
                      <span className="rounded-md bg-white px-1.5 py-0.5 text-[11px] font-semibold text-slate-600 shadow-sm">
                        {item.groupCount} гр. • {item.studentCount} студ.
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Панель фільтрів груп */}
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-wrap items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => setCourseYearFilter("all")}
                  className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                    courseYearFilter === "all"
                      ? "bg-slate-900 text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  Усі курси
                </button>
                {COURSE_YEARS.map((year) => (
                  <button
                    key={year}
                    type="button"
                    onClick={() => setCourseYearFilter(year)}
                    className={`rounded-lg px-2.5 py-1.5 text-xs font-semibold transition-colors ${
                      courseYearFilter === year
                        ? "bg-blue-600 text-white"
                        : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                  >
                    {year} курс
                  </button>
                ))}
              </div>

              <div className="relative min-w-[230px]">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={groupSearch}
                  onChange={(event) => setGroupSearch(event.target.value)}
                  placeholder="Пошук шифру або спеціальності..."
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-8 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
                {groupSearch.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setGroupSearch("")}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700"
                    aria-label="Очистити пошук груп"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Картки академічних груп */}
          {filteredGroups.length === 0 ? (
            <div className="rounded-2xl border border-slate-200 bg-white px-6 py-14 text-center shadow-sm">
              <Building2 className="mx-auto h-10 w-10 text-slate-300" />
              <p className="mt-3 text-sm font-semibold text-slate-700">
                Академічних груп за поточними фільтрами не знайдено
              </p>
              <div className="mt-4 flex items-center justify-center gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setCourseYearFilter("all");
                    setSpecialtyFilter("all");
                    setGroupSearch("");
                  }}
                  className="rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Скинути фільтри
                </button>
                <button
                  type="button"
                  onClick={openCreateGroupModal}
                  className="rounded-xl bg-blue-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-blue-700"
                >
                  + Додати групу
                </button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
              {filteredGroups.map((group) => {
                const studentCount = studentsCountByGroup[group.id] ?? 0;

                return (
                  <article
                    key={group.id}
                    className="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
                  >
                    <div>
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center gap-2.5">
                          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-sm font-bold text-blue-700">
                            {group.code.slice(0, 4)}
                          </div>
                          <div>
                            <h4 className="text-base font-bold text-slate-900">
                              {group.code}
                            </h4>
                            <span className="inline-flex items-center rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-[11px] font-semibold text-slate-600">
                              {group.course_year} курс
                            </span>
                          </div>
                        </div>

                        <span className="inline-flex items-center gap-1 rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">
                          <GraduationCap className="h-3.5 w-3.5" />
                          {studentCount}
                        </span>
                      </div>

                      <p className="mt-3 text-sm leading-snug text-slate-600">
                        {group.specialty}
                      </p>
                    </div>

                    <div className="mt-5 flex items-center justify-between gap-2 border-t border-slate-100 pt-3.5">
                      <button
                        type="button"
                        onClick={() => handleInspectGroupStudents(group.id)}
                        className="text-xs font-semibold text-blue-600 transition-colors hover:text-blue-800"
                      >
                        Студенти групи →
                      </button>

                      <div className="flex items-center gap-1.5">
                        <button
                          type="button"
                          onClick={() => openEditGroupModal(group)}
                          className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-700 transition-colors hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700"
                        >
                          <Edit3 className="h-3.5 w-3.5" />
                          Змінити
                        </button>
                        <button
                          type="button"
                          onClick={() =>
                            setDeleteTarget({
                              kind: "group",
                              id: group.id,
                              title: group.code,
                              description: `${group.specialty} • ${group.course_year} курс`,
                              warning:
                                studentCount > 0
                                  ? `У групі зараз ${studentCount} студ. Після видалення групи їхні облікові записи залишаться, але прив'язка до групи буде скинута.`
                                  : undefined,
                            })
                          }
                          className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:border-rose-300 hover:bg-rose-50 hover:text-rose-700"
                          aria-label={`Видалити групу ${group.code}`}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>
      )}

      {/* МОДАЛКА: Створення / редагування користувача */}
      {userModal !== null && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-xs"
          role="dialog"
          aria-modal="true"
          aria-labelledby="user-modal-title"
        >
          <div className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
              <div className="flex items-center gap-2.5">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                  <UserCog className="h-5 w-5" />
                </div>
                <div>
                  <h3
                    id="user-modal-title"
                    className="text-base font-bold text-slate-900"
                  >
                    {userModal.mode === "create"
                      ? "Новий обліковий запис"
                      : "Редагування користувача"}
                  </h3>
                  <p className="text-xs text-slate-500">
                    {userModal.mode === "create"
                      ? "Створіть акаунт студента, викладача або адміністратора"
                      : userModal.targetUser?.email}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setUserModal(null)}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
                aria-label="Закрити вікно"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleSubmitUserForm} className="space-y-4 p-6">
              {userFormError !== null && (
                <div className="flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-2.5 text-xs font-medium text-rose-700">
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>{userFormError}</span>
                </div>
              )}

              <div>
                <label
                  htmlFor="admin-user-fullname"
                  className="block text-xs font-semibold text-slate-700"
                >
                  Прізвище, ім&apos;я та по батькові *
                </label>
                <input
                  id="admin-user-fullname"
                  type="text"
                  required
                  maxLength={255}
                  value={userFullName}
                  onChange={(event) => setUserFullName(event.target.value)}
                  placeholder="Наприклад, Коваленко Андрій Петрович"
                  className="mt-1.5 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label
                    htmlFor="admin-user-email"
                    className="block text-xs font-semibold text-slate-700"
                  >
                    Електронна пошта *
                  </label>
                  <input
                    id="admin-user-email"
                    type="email"
                    required
                    maxLength={255}
                    value={userEmail}
                    onChange={(event) => setUserEmail(event.target.value)}
                    placeholder="user@kpefk.lcloud.in.ua"
                    className="mt-1.5 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </div>

                <div>
                  <label
                    htmlFor="admin-user-role"
                    className="block text-xs font-semibold text-slate-700"
                  >
                    Роль у системі *
                  </label>
                  <select
                    id="admin-user-role"
                    value={userRole}
                    disabled={isEditingSelf}
                    onChange={(event) =>
                      setUserRole(event.target.value as UserRole)
                    }
                    className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-500"
                  >
                    {USER_ROLES.map((role) => (
                      <option key={role} value={role}>
                        {ROLE_META[role].label}
                      </option>
                    ))}
                  </select>
                  {isEditingSelf && (
                    <p className="mt-1 text-[11px] text-slate-500">
                      Власну роль адміністратора змінити неможливо.
                    </p>
                  )}
                </div>
              </div>

              {/* Параметри студента: академічна група та № у списку */}
              {userRole === "student" && (
                <div className="rounded-xl border border-blue-100 bg-blue-50/50 p-4 space-y-3">
                  <p className="text-xs font-semibold text-blue-900">
                    Параметри навчання студента
                  </p>
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <div>
                      <label
                        htmlFor="admin-user-group"
                        className="block text-xs font-semibold text-slate-700"
                      >
                        Академічна група
                      </label>
                      <select
                        id="admin-user-group"
                        value={userGroupId}
                        onChange={(event) =>
                          setUserGroupId(event.target.value)
                        }
                        className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                      >
                        <option value="">— Не призначено —</option>
                        {groups.map((group) => (
                          <option key={group.id} value={group.id}>
                            {group.code} ({group.course_year} курс)
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <div className="flex items-center justify-between">
                        <label
                          htmlFor="admin-user-list-number"
                          className="block text-xs font-semibold text-slate-700"
                        >
                          № у списку (1–100)
                        </label>
                        <button
                          type="button"
                          onClick={suggestNextListNumber}
                          className="text-[11px] font-semibold text-blue-600 hover:text-blue-800"
                        >
                          Вільний №
                        </button>
                      </div>
                      <input
                        id="admin-user-list-number"
                        type="number"
                        min={1}
                        max={100}
                        step={1}
                        value={userListNumber}
                        onChange={(event) =>
                          setUserListNumber(event.target.value)
                        }
                        placeholder="Наприклад, 5"
                        className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                      />
                    </div>
                  </div>
                  <p className="text-[11px] leading-relaxed text-slate-600">
                    Порядковий номер у списку автоматично визначає персональний
                    варіант практичної роботи за формулою{" "}
                    <code className="rounded bg-white px-1 py-0.5 text-[10px] text-blue-800">
                      ((list_number || 1) - 1) % total_variants + 1
                    </code>
                    .
                  </p>
                </div>
              )}

              <div>
                <label
                  htmlFor="admin-user-password"
                  className="flex items-center gap-1.5 text-xs font-semibold text-slate-700"
                >
                  <KeyRound className="h-3.5 w-3.5 text-slate-400" />
                  {userModal.mode === "create"
                    ? "Пароль для входу *"
                    : "Новий пароль (необов'язково)"}
                </label>
                <input
                  id="admin-user-password"
                  type="password"
                  required={userModal.mode === "create"}
                  minLength={userModal.mode === "create" ? 6 : undefined}
                  maxLength={128}
                  value={userPassword}
                  onChange={(event) => setUserPassword(event.target.value)}
                  placeholder={
                    userModal.mode === "create"
                      ? "Щонайменше 6 символів"
                      : "Залиште порожнім, щоб не змінювати пароль"
                  }
                  className="mt-1.5 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>

              <div className="flex items-center justify-end gap-2.5 border-t border-slate-100 pt-4">
                <button
                  type="button"
                  onClick={() => setUserModal(null)}
                  disabled={isSavingUser}
                  className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Скасувати
                </button>
                <button
                  type="submit"
                  disabled={isSavingUser}
                  className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:opacity-60"
                >
                  {isSavingUser && <Loader2 className="h-4 w-4 animate-spin" />}
                  {userModal.mode === "create"
                    ? "Створити акаунт"
                    : "Зберегти зміни"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* МОДАЛКА: Створення / редагування академічної групи */}
      {groupModal !== null && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-xs"
          role="dialog"
          aria-modal="true"
          aria-labelledby="group-modal-title"
        >
          <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
              <div className="flex items-center gap-2.5">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-purple-50 text-purple-600">
                  <Building2 className="h-5 w-5" />
                </div>
                <div>
                  <h3
                    id="group-modal-title"
                    className="text-base font-bold text-slate-900"
                  >
                    {groupModal.mode === "create"
                      ? "Нова академічна група"
                      : "Редагування групи"}
                  </h3>
                  <p className="text-xs text-slate-500">
                    Довідник навчальних груп і спеціальностей
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setGroupModal(null)}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
                aria-label="Закрити вікно"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleSubmitGroupForm} className="space-y-4 p-6">
              {groupFormError !== null && (
                <div className="flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-2.5 text-xs font-medium text-rose-700">
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>{groupFormError}</span>
                </div>
              )}

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label
                    htmlFor="admin-group-code"
                    className="block text-xs font-semibold text-slate-700"
                  >
                    Шифр групи *
                  </label>
                  <input
                    id="admin-group-code"
                    type="text"
                    required
                    maxLength={32}
                    value={groupCode}
                    onChange={(event) => setGroupCode(event.target.value)}
                    placeholder="Наприклад, КН-31"
                    className="mt-1.5 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </div>

                <div>
                  <label
                    htmlFor="admin-group-year"
                    className="block text-xs font-semibold text-slate-700"
                  >
                    Курс навчання *
                  </label>
                  <select
                    id="admin-group-year"
                    value={groupCourseYear}
                    onChange={(event) => setGroupCourseYear(event.target.value)}
                    className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  >
                    {COURSE_YEARS.map((year) => (
                      <option key={year} value={year}>
                        {year} курс
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label
                  htmlFor="admin-group-specialty"
                  className="block text-xs font-semibold text-slate-700"
                >
                  Спеціальність *
                </label>
                <input
                  id="admin-group-specialty"
                  type="text"
                  required
                  maxLength={128}
                  list="college-specialties-list"
                  value={groupSpecialty}
                  onChange={(event) => setGroupSpecialty(event.target.value)}
                  placeholder="Наприклад, 122 Комп'ютерні науки"
                  className="mt-1.5 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
                <datalist id="college-specialties-list">
                  {specialtySummaries.map((item) => (
                    <option key={item.specialty} value={item.specialty} />
                  ))}
                </datalist>
              </div>

              <div className="flex items-center justify-end gap-2.5 border-t border-slate-100 pt-4">
                <button
                  type="button"
                  onClick={() => setGroupModal(null)}
                  disabled={isSavingGroup}
                  className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Скасувати
                </button>
                <button
                  type="submit"
                  disabled={isSavingGroup}
                  className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:opacity-60"
                >
                  {isSavingGroup && (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  )}
                  {groupModal.mode === "create"
                    ? "Створити групу"
                    : "Зберегти зміни"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* МОДАЛКА: Підтвердження видалення */}
      {deleteTarget !== null && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-xs"
          role="dialog"
          aria-modal="true"
          aria-labelledby="delete-modal-title"
        >
          <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-50 text-rose-600">
                <Trash2 className="h-5 w-5" />
              </div>
              <div>
                <h3
                  id="delete-modal-title"
                  className="text-base font-bold text-slate-900"
                >
                  {deleteTarget.kind === "user"
                    ? "Видалити обліковий запис?"
                    : "Видалити академічну групу?"}
                </h3>
                <p className="mt-1 text-sm font-semibold text-slate-800">
                  {deleteTarget.title}
                </p>
                <p className="text-xs text-slate-500">
                  {deleteTarget.description}
                </p>
              </div>
            </div>

            {deleteTarget.warning !== undefined && (
              <div className="mt-4 flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
                <span>{deleteTarget.warning}</span>
              </div>
            )}

            <div className="mt-6 flex items-center justify-end gap-2.5">
              <button
                type="button"
                onClick={() => setDeleteTarget(null)}
                disabled={isDeleting}
                className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Скасувати
              </button>
              <button
                type="button"
                onClick={handleConfirmDelete}
                disabled={isDeleting}
                className="inline-flex items-center gap-2 rounded-xl bg-rose-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-rose-700 disabled:opacity-60"
              >
                {isDeleting && <Loader2 className="h-4 w-4 animate-spin" />}
                Підтвердити видалення
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminUsersPage;
