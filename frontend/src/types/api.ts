import type { CourseSlug } from "./course";
import type { ExtractedMetadata, GradingReport } from "./grading";

export {
  type GradingCriterionPreviewRead,
  type PracticalStudentRead,
  type PracticalSummaryRead,
  type PracticalTeacherRead,
  type PracticalUpdate,
} from "./course";
export {
  GRADING_RULE_TYPES,
  type GradingRulesUpdateRequest,
  type GradingRuleType,
} from "./grading";

export const USER_ROLES = ["student", "teacher", "admin"] as const;

export type UserRole = (typeof USER_ROLES)[number];

export type TokenType = "access" | "refresh";

export const EXPORT_FORMATS = ["xlsx", "pdf"] as const;

export type ExportFormat = (typeof EXPORT_FORMATS)[number];

export interface ErrorResponse {
  detail: string;
  code: string;
  context: Record<string, unknown>;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
}

export interface TokenPayload {
  sub: string;
  role: UserRole;
  token_type: TokenType;
  tv: number;
  exp: number;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface ChangePasswordResponse extends TokenResponse {
  user: UserRead;
}

export interface AdminResetPasswordRequest {
  new_password?: string | null;
}

export interface AdminResetPasswordResponse {
  user: UserRead;
  temp_password: string;
}

export const ACADEMIC_COURSE_YEARS = [1, 2, 3, 4] as const;

export type AcademicCourseYear = (typeof ACADEMIC_COURSE_YEARS)[number];

export interface AcademicGroupBase {
  code: string;
  specialty: string;
  course_year: AcademicCourseYear;
}

export type AcademicGroupCreate = AcademicGroupBase;

export interface AcademicGroupUpdate {
  code?: string | null;
  specialty?: string | null;
  course_year?: AcademicCourseYear | null;
}

export interface AcademicGroupRead extends AcademicGroupBase {
  id: string;
}

export interface UserBase {
  email: string;
  full_name: string;
  role: UserRole;
  group_id: string | null;
  list_number: number | null;
}

export interface UserCreate {
  email: string;
  full_name: string;
  role: UserRole;
  group_id?: string | null;
  list_number?: number | null;
  password: string;
}

export interface UserUpdate {
  email?: string | null;
  full_name?: string | null;
  role?: UserRole | null;
  group_id?: string | null;
  list_number?: number | null;
  password?: string | null;
}

export interface UserRead extends UserBase {
  id: string;
  group_code: string | null;
  must_change_password: boolean;
  created_at: string;
}

export interface ImportedStudentItem {
  user_id: string;
  list_number: number;
  variant_number: number;
  full_name: string;
  email: string;
  temp_password: string;
}

export interface ImportSkippedItem {
  row_number: number;
  full_name: string | null;
  email: string | null;
  reason: string;
}

export interface StudentImportResponse {
  group_id: string;
  group_code: string;
  total_variants: number;
  created_count: number;
  skipped_count: number;
  created: ImportedStudentItem[];
  skipped: ImportSkippedItem[];
}

export interface HtmlSubmissionRequest {
  raw_code: string;
}

export interface ManualGradeUpdateRequest {
  final_score: number;
  teacher_comment?: string | null;
}

export interface SubmissionRead {
  id: string;
  practical_id: string;
  practical_title: string | null;
  course_slug: CourseSlug | null;
  student_id: string;
  student_full_name: string | null;
  variant_index: number;
  variant_number: number;
  file_path: string | null;
  raw_code: string | null;
  file_hash: string | null;
  extracted_metadata: ExtractedMetadata;
  is_plagiarism_flagged: boolean;
  plagiarism_reason: string | null;
  auto_score: number;
  final_score: number;
  max_score: number;
  grading_report: GradingReport;
  teacher_comment: string | null;
  submitted_at: string;
  is_file_available: boolean;
  file_expires_at: string | null;
}

export interface CriterionErrorStat {
  rule_id: string;
  description: string;
  total_attempts: number;
  failure_count: number;
  failure_rate_percent: number;
}

export interface GroupJournalStudentCell {
  practical_id: string;
  submission_id: string | null;
  auto_score: number | null;
  final_score: number | null;
  is_plagiarism_flagged: boolean;
  plagiarism_reason: string | null;
  submitted_at: string | null;
}

export interface GroupJournalRow {
  student_id: string;
  student_full_name: string;
  list_number: number | null;
  cells: GroupJournalStudentCell[];
  total_score: number;
}

export interface GroupJournalPracticalRead {
  practical_id: string;
  title: string;
  course_slug: CourseSlug;
  module_order_index: number;
  max_score: number;
  needs_rules_review: boolean;
}

export interface GroupJournalRead {
  group_id: string;
  group_code: string;
  specialty: string;
  practicals: GroupJournalPracticalRead[];
  rows: GroupJournalRow[];
  error_stats: CriterionErrorStat[];
}
