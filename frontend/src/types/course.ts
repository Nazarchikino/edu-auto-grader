import type { GradingRule, PracticalFormat } from "./grading";

export type { PracticalFormat };

export const COURSE_SLUGS = ["word", "excel", "access", "html"] as const;

export type CourseSlug = (typeof COURSE_SLUGS)[number];

export interface QuizQuestionCreate {
  question_text: string;
  options: string[];
  correct_option_index: number;
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
}

export interface PracticalSummaryRead {
  id: string;
  module_id: string;
  title: string;
  format_type: PracticalFormat;
  max_score: number;
  is_unlocked: boolean;
  best_score: number | null;
}

export interface PracticalStudentRead {
  id: string;
  module_id: string;
  title: string;
  instructions: string;
  format_type: PracticalFormat;
  max_score: number;
  variant_index: number;
  variant_number: number;
  variant: PracticalVariant;
}

export interface PracticalTeacherRead {
  id: string;
  module_id: string;
  title: string;
  instructions: string;
  format_type: PracticalFormat;
  max_score: number;
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
