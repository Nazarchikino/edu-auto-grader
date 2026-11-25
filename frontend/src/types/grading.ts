export const PRACTICAL_FORMATS = ["docx", "xlsx", "accdb", "html"] as const;

export type PracticalFormat = (typeof PRACTICAL_FORMATS)[number];

export const GRADING_RULE_TYPES = [
  // Microsoft Word (.docx)
  "docx_page_margins",
  "docx_font",
  "docx_line_spacing",
  "docx_alignment",
  "docx_table_exists",
  "docx_list_exists",
  // Microsoft Excel (.xlsx)
  "xlsx_formula",
  "xlsx_value",
  "xlsx_chart_exists",
  // Microsoft Access (.accdb)
  "accdb_table_exists",
  "accdb_column_exists",
  "accdb_column_type",
  "accdb_query_exists",
  "accdb_form_exists",
  "accdb_report_exists",
  "accdb_relationship_exists",
  // HTML5 (BeautifulSoup4 DOM)
  "html_tag_exists",
  "html_tag_count",
  "html_attribute_exists",
] as const;

export type GradingRuleType = (typeof GRADING_RULE_TYPES)[number];

export interface GradingRule {
  id: string;
  type: GradingRuleType;
  target: string;
  expected: string;
  points: number;
  description: string;
}

export interface CriterionResult {
  rule_id: string;
  rule_type: GradingRuleType;
  target: string;
  expected: string;
  actual: string | null;
  passed: boolean;
  points_awarded: number;
  max_points: number;
  description: string;
  feedback: string;
}

export interface GradingReport {
  format_type: PracticalFormat;
  total_points: number;
  max_points: number;
  passed_count: number;
  failed_count: number;
  results: CriterionResult[];
}

export interface ExtractedMetadata {
  creator?: string | null;
  last_modified_by?: string | null;
  created?: string | null;
  modified?: string | null;
  revision?: string | null;
  [key: string]: unknown;
}

export interface PlagiarismCheckResult {
  is_flagged: boolean;
  reason: string | null;
  matched_submission_id: string | null;
  matched_student_id: string | null;
}

export interface GradingRulesUpdateRequest {
  grading_rules: GradingRule[];
}
