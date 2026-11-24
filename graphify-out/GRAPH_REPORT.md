# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 87 files · ~251,604 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1589 nodes · 4418 edges · 82 communities (49 shown, 33 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 365 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5bfe2911`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DomainError
- postgres
- compilerOptions
- DocxGrader
- AccdbGrader
- GradingRule
- PracticalFormat
- xlsx_grader.py
- MarkdownRenderer.tsx
- vite-env.d.ts
- _get_user_by_email
- InvalidFileFormatError
- courses.py
- SubmissionService
- test_submissions_api.py
- ExportService
- edu-auto-grader-backend
- verify_password
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- _SeedQuizQuestionPayload
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- GroupJournalPage.tsx
- accdb_grader.py
- HtmlSandbox.tsx
- parse_docx_students
- Settings
- re
- .build_criterion_result
- GradebookPage.tsx
- ModuleViewPage.tsx
- ExtractedMetadata
- User
- retention_service.py
- GradingError
- conftest.py
- courses.py
- export_service.py
- schemas/__init__.py
- SqliteAsyncSessionAdapter
- submissions.py
- export_group_journal
- QuizService
- RuleBuilderPage.tsx
- import_admin_students
- DomainError
- main.py
- submit_practical_work
- lucide-react
- ukrainian_sort_key
- _find_tag_attr_key

## God Nodes (most connected - your core abstractions)
1. `DomainError` - 63 edges
2. `User` - 63 edges
3. `GradingRule` - 56 edges
4. `InvalidFileFormatError` - 43 edges
5. `SqliteAsyncSessionAdapter` - 43 edges
6. `get_db()` - 43 edges
7. `DocxGrader` - 42 edges
8. `SubmissionService` - 41 edges
9. `UserRole` - 39 edges
10. `GradingError` - 37 edges

## Surprising Connections (you probably didn't know these)
- `test_grader_factory_resolves_all_four_formats()` --uses--> `DocxGrader`  [INFERRED]
  backend/tests/test_graders.py → backend/app/graders/docx_grader.py
- `require_role()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `create_admin_user()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `list_admin_users()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `update_admin_user()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (82 total, 33 thin omitted)

### Community 0 - "DomainError"
Cohesion: 0.17
Nodes (8): create_access_token(), create_refresh_token(), create_token_pair(), _encode_jwt_token(), _enum_values(), UserRole, TokenPayload, TokenResponse

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "DocxGrader"
Cohesion: 0.07
Nodes (4): DocxGrader, test_all_course_variants_resolve_rule_placeholders_without_leftovers(), test_docx_grader_evaluates_valid_document(), test_docx_grader_resolves_placeholders_in_target_and_expected()

### Community 4 - "AccdbGrader"
Cohesion: 0.07
Nodes (9): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _resolve_canonical_type(), _strip_identifiers() (+1 more)

### Community 5 - "GradingRule"
Cohesion: 0.12
Nodes (14): GradingRule, build_sample_accdb(), build_sample_xlsx(), test_accdb_grader_accepts_hyperlink_type_as_memo(), test_accdb_grader_detects_missing_schema_elements_and_invalid_header(), test_accdb_grader_evaluates_access_module_9_multiple_variants(), test_accdb_grader_evaluates_tables_columns_and_types(), test_docx_grader_detects_formatting_violations_and_corrupt_files() (+6 more)

### Community 6 - "PracticalFormat"
Cohesion: 0.14
Nodes (4): BaseGrader, GraderFactory, _enum_values(), PracticalFormat

### Community 7 - "xlsx_grader.py"
Cohesion: 0.07
Nodes (8): _attribute_value_matches(), _is_doctype_target(), _normalize_text(), _parse_text_match_expected(), _strip_quotes(), _is_wrapped_in_parens(), GradingReport, GradingRuleType

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "_get_user_by_email"
Cohesion: 0.12
Nodes (11): AcademicGroup, _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(), test_admin_endpoints_enforce_admin_rbac() (+3 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.13
Nodes (10): InvalidFileFormatError, compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), extract_core_xml_metadata(), extract_document_metadata(), _find_xml_text() (+2 more)

### Community 14 - "courses.py"
Cohesion: 0.09
Nodes (20): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+12 more)

### Community 15 - "SubmissionService"
Cohesion: 0.10
Nodes (9): PlagiarismDetectedError, Submission, GradingRulesUpdateRequest, SubmissionRead, _build_submission_download_names(), _is_submission_file_available(), serialize_submission(), SubmissionDownloadPayload (+1 more)

### Community 16 - "test_submissions_api.py"
Cohesion: 0.16
Nodes (14): CourseSlug, make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_download_submission_forbidden_for_other_teacher_and_students(), test_download_submissions_by_course_teacher_and_admin_with_headers_and_content() (+6 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (41): @monaco-editor/react@4.6.0, devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0 (+33 more)

### Community 24 - "App.tsx"
Cohesion: 0.15
Nodes (25): App(), ProtectedAppLayout(), RoleHomeRedirect(), Navbar(), NavbarProps, resolvePageTitle(), ROLE_BADGE_CONFIG, ROLE_LABELS (+17 more)

### Community 25 - "admin.py"
Cohesion: 0.10
Nodes (18): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404(), _get_user_with_group_or_404() (+10 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (46): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+38 more)

### Community 27 - "course.ts"
Cohesion: 0.08
Nodes (42): COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS, CourseEditorPage() (+34 more)

### Community 28 - "_SeedQuizQuestionPayload"
Cohesion: 0.18
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.07
Nodes (5): _canonicalize_formula(), _format_cell_value(), _try_parse_numeric(), XlsxGrader, test_excel_course_formula_rules_have_valid_supported_expressions()

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.22
Nodes (15): PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal() (+7 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.16
Nodes (5): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type()

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.28
Nodes (8): buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode, PracticalVariant

### Community 35 - "parse_docx_students"
Cohesion: 0.09
Nodes (18): ImportSkippedItem, build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, generate_temp_password(), _get_cell_value() (+10 more)

### Community 36 - "Settings"
Cohesion: 0.08
Nodes (7): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), get_settings(), _resolve_backend_path(), Settings

### Community 38 - "re"
Cohesion: 0.25
Nodes (4): _sanitize_filename_token(), _sanitize_ascii_token(), _sanitize_utf8_token(), _strip_apostrophes()

### Community 40 - "GradebookPage.tsx"
Cohesion: 0.10
Nodes (27): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+19 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.12
Nodes (29): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta, FORMAT_BADGE_LABELS (+21 more)

### Community 46 - "ExtractedMetadata"
Cohesion: 0.12
Nodes (8): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), SubmissionRecordProtocol, ExtractedMetadata, PlagiarismCheckResult, DummySubmissionRecord, test_metadata_extraction_and_plagiarism_detection()

### Community 47 - "User"
Cohesion: 0.10
Nodes (18): downgrade(), upgrade(), Base, Course, Module, Practical, QuizQuestion, QuizAttempt (+10 more)

### Community 48 - "retention_service.py"
Cohesion: 0.16
Nodes (8): cleanup_expired_submissions(), delete_submission_file_safely(), delete_submission_files_for_paths(), main(), resolve_submission_file_path(), RetentionCleanupSummary, run_periodic_retention_cleanup(), run_retention_cleanup_once()

### Community 49 - "GradingError"
Cohesion: 0.10
Nodes (5): GradingError, HtmlGrader, _normalize_selector(), test_html_grader_attribute_filter_selector_and_compound_colspan(), test_html_grader_evaluates_semantic_dom_structure_and_attributes()

### Community 50 - "conftest.py"
Cohesion: 0.08
Nodes (8): build_sample_docx(), _compile_jsonb_for_sqlite(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 52 - "courses.py"
Cohesion: 0.08
Nodes (24): _build_module_detail_read(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module(), delete_practical(), delete_quiz_question() (+16 more)

### Community 58 - "export_service.py"
Cohesion: 0.07
Nodes (20): CriterionErrorStat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest, ManualGradeUpdateRequest, _auto_adjust_worksheet_columns(), build_content_disposition() (+12 more)

### Community 60 - "schemas/__init__.py"
Cohesion: 0.08
Nodes (13): AcademicGroupBase, AcademicGroupCreate, AcademicGroupUpdate, ErrorResponse, ImportedStudentItem, LoginRequest, RefreshTokenRequest, StudentImportResponse (+5 more)

### Community 61 - "SqliteAsyncSessionAdapter"
Cohesion: 0.11
Nodes (9): async_client(), SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found(), test_delete_module_by_teacher_and_admin_cascades_cleans_files_and_renumbers(), test_delete_practical_preserves_module_lecture_quiz_and_cleans_files(), test_media_courses_static_serving() (+1 more)

### Community 62 - "submissions.py"
Cohesion: 0.21
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 63 - "export_group_journal"
Cohesion: 0.19
Nodes (3): export_group_journal(), get_group_journal(), list_academic_groups()

### Community 64 - "QuizService"
Cohesion: 0.12
Nodes (4): get_practical_for_student(), submit_module_quiz(), QuizNotPassedError, QuizService

### Community 65 - "RuleBuilderPage.tsx"
Cohesion: 0.20
Nodes (13): fetchCourses(), fetchPracticalTeacher(), FORMAT_BADGE_CONFIG, renderFormatIcon(), RULE_TYPE_SPECS, RuleBuilderPage(), RuleTypeSpec, CriterionResult (+5 more)

### Community 67 - "DomainError"
Cohesion: 0.10
Nodes (10): get_current_user(), require_role(), role_checker(), _parse_export_format(), login(), read_current_user(), refresh_tokens(), ExtractedSubmissionPayload (+2 more)

### Community 68 - "main.py"
Cohesion: 0.15
Nodes (3): create_application(), lifespan(), test_lifespan_starts_and_cancels_retention_background_task()

### Community 70 - "submit_practical_work"
Cohesion: 0.18
Nodes (3): _extract_submission_payload(), submit_practical_work(), update_practical_grading_rules()

### Community 76 - "lucide-react"
Cohesion: 0.15
Nodes (12): dependencies, axios@^1.7.7, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient (+4 more)

### Community 78 - "ukrainian_sort_key"
Cohesion: 0.25
Nodes (3): _encode_ukrainian_word(), ukrainian_sort_key(), test_ukrainian_alphabetical_sorting_and_apostrophe_normalization()

### Community 79 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 697 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `QuizService`, `DomainError`, `parse_docx_students`, `_get_user_by_email`, `SubmissionService`, `test_submissions_api.py`, `ExportService`, `courses.py`, `admin.py`, `export_service.py`, `schemas/__init__.py`, `SqliteAsyncSessionAdapter`, `submissions.py`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `DomainError` (e.g. with `delete_admin_user()` and `update_admin_user()`) actually correct?**
  _`DomainError` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `DocxGrader` connect `DocxGrader` to `GradingRule`, `PracticalFormat`, `.build_criterion_result`, `xlsx_grader.py`, `InvalidFileFormatError`, `User`, `GradingError`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `User` (e.g. with `get_current_user()` and `require_role()`) actually correct?**
  _`User` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._