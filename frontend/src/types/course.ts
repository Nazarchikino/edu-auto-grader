import type { GradingRule, PracticalFormat } from "./grading";

export type { PracticalFormat };

export const COURSE_SLUGS = ["word", "excel", "access", "html"] as const;

export type CourseSlug = (typeof COURSE_SLUGS)[number];

export interface QuizQuestionCreate {
  question_text: string;
  options: string[];
  correct_option_index: number;
}

export interface QuizQuestionUpdate {
  question_text?: string | null;
  options?: string[] | null;
  correct_option_index?: number | null;
}

export interface QuizQuestionRead {
  id: string;
  module_id: string;
  question_text: string;
  options: string[];
}

export interface QuizQuestionTeacherRead extends QuizQuestionRead {
  correct_option_index: number;
}

export interface QuizAnswerItem {
  question_id: string;
  selected_option_index: number;
}

export interface QuizSubmitRequest {
  answers: QuizAnswerItem[];
}

export interface QuizSubmitResponse {
  id: string;
  module_id: string;
  score_percent: number;
  passed: boolean;
  correct_count: number;
  total_questions: number;
  practical_unlocked: boolean;
  attempted_at: string;
  retry_after_seconds: number;
}

export interface PracticalVariant {
  variant_number: number;
  title: string;
  task_description: string;
  parameters: Record<string, unknown>;
}

export interface PracticalCreate {
  title: string;
  instructions: string;
  format_type: PracticalFormat;
  max_score?: number;
  variants?: PracticalVariant[];
  grading_rules?: GradingRule[];
}

export interface PracticalUpdate {
  title?: string | null;
  instructions?: string | null;
  format_type?: PracticalFormat | null;
  max_score?: number | null;
  variants?: PracticalVariant[] | null;
  grading_rules?: GradingRule[] | null;
  needs_rules_review?: boolean | null;
}

export interface GradingCriterionPreviewRead {
  id: string;
  description: string;
  weight_points: number;
}

export interface PracticalSummaryRead {
  id: string;
  module_id: string;
  title: string;
  instructions?: string | null;
  format_type: PracticalFormat;
  max_score: number;
  auto_max_score: number;
  manual_bonus_max: number;
  is_unlocked: boolean;
  best_score: number | null;
  needs_rules_review: boolean;
  has_template_file: boolean;
  template_file_name: string | null;
  assigned_variant_number: number;
  total_variants: number;
  variant?: PracticalVariant | null;
  grading_criteria: GradingCriterionPreviewRead[];
}

export interface PracticalStudentRead {
  id: string;
  module_id: string;
  title: string;
  instructions: string;
  format_type: PracticalFormat;
  max_score: number;
  auto_max_score: number;
  manual_bonus_max: number;
  needs_rules_review: boolean;
  has_template_file: boolean;
  template_file_name: string | null;
  variant_index: number;
  variant_number: number;
  total_variants: number;
  variant: PracticalVariant;
  grading_criteria: GradingCriterionPreviewRead[];
}

export interface PracticalTeacherRead {
  id: string;
  module_id: string;
  title: string;
  instructions: string;
  format_type: PracticalFormat;
  max_score: number;
  auto_max_score: number;
  manual_bonus_max: number;
  needs_rules_review: boolean;
  has_template_file: boolean;
  template_file_name: string | null;
  variants: PracticalVariant[];
  grading_rules: GradingRule[];
}

export interface ModuleCreate {
  order_index: number;
  title: string;
  lecture_content: string;
}

export interface ModuleUpdate {
  order_index?: number | null;
  title?: string | null;
  lecture_content?: string | null;
}

export interface ModuleReorderRequest {
  module_ids: string[];
}

export interface CourseMediaUploadRead {
  url: string;
  markdown: string;
  filename: string;
  size_bytes: number;
}

export interface ModuleSummaryRead {
  id: string;
  course_id: string;
  order_index: number;
  title: string;
  quiz_passed: boolean;
  best_quiz_score: number | null;
  practical_id: string | null;
  practical_format: PracticalFormat | null;
  practical_score: number | null;
  practical_max_score: number | null;
  practical_needs_rules_review: boolean;
}

export interface ModuleDetailRead {
  id: string;
  course_id: string;
  order_index: number;
  title: string;
  lecture_content: string;
  quiz_questions: QuizQuestionRead[];
  quiz_passed: boolean;
  best_quiz_score: number | null;
  quiz_cooldown_remaining_seconds?: number;
  practical_unlocked: boolean;
  practical: PracticalSummaryRead | null;
}

export interface CourseCreate {
  title: string;
  slug: CourseSlug;
  description: string;
}

export interface CourseUpdate {
  title?: string | null;
  description?: string | null;
  teacher_id?: string | null;
}

export interface CourseRead {
  id: string;
  title: string;
  slug: CourseSlug;
  description: string;
  teacher_id: string;
  total_modules: number;
  completed_modules: number;
  progress_percent: number;
  modules: ModuleSummaryRead[];
}
