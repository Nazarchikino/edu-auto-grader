# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 87 files · ~249,169 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1574 nodes · 4406 edges · 76 communities (48 shown, 28 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 400 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3b0456a9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DomainError
- postgres
- compilerOptions
- GradingRuleType
- AccdbGrader
- export_group_journal
- InvalidFileFormatError
- RuleBuilderPage.tsx
- MarkdownRenderer.tsx
- vite-env.d.ts
- _get_user_by_email
- InvalidFileFormatError
- courses.py
- list_my_submissions
- test_submissions_api.py
- ExportService
- edu-auto-grader-backend
- refresh_tokens
- package.json
- App.tsx
- DomainError
- AdminUsersPage.tsx
- course.ts
- _SeedQuizQuestionPayload
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- GroupJournalPage.tsx
- QuizService
- HtmlSandbox.tsx
- parse_docx_students
- Settings
- SubmissionService
- submission_service.py
- DocxGrader
- GradebookPage.tsx
- ModuleViewPage.tsx
- lucide-react
- User
- Submission
- GradingRule
- conftest.py
- courses.py
- export_service.py
- BaseModel
- env.py
- list_admin_users
- AcademicGroupRead
- ExportFormat
- GroupJournalRead
- _find_tag_attr_key
- submit_practical_work
- build_group_journal
- _parse_text_match_expected
- _enum_values

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 70 edges
2. `DomainError` - 63 edges
3. `User` - 63 edges
4. `InvalidFileFormatError` - 50 edges
5. `DocxGrader` - 46 edges
6. `SqliteAsyncSessionAdapter` - 43 edges
7. `get_db()` - 43 edges
8. `PracticalFormat` - 42 edges
9. `SubmissionService` - 41 edges
10. `GradingError` - 40 edges

## Surprising Connections (you probably didn't know these)
- `_get_user_by_email()` --uses--> `SqliteAsyncSessionAdapter`  [INFERRED]
  backend/tests/test_admin_api.py → backend/tests/conftest.py
- `test_academic_group_course_year_restricted_to_1_through_4()` --uses--> `SqliteAsyncSessionAdapter`  [INFERRED]
  backend/tests/test_admin_api.py → backend/tests/conftest.py
- `test_admin_academic_groups_crud_and_detachment()` --uses--> `SqliteAsyncSessionAdapter`  [INFERRED]
  backend/tests/test_admin_api.py → backend/tests/conftest.py
- `test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants()` --uses--> `SqliteAsyncSessionAdapter`  [INFERRED]
  backend/tests/test_admin_api.py → backend/tests/conftest.py
- `test_admin_bulk_import_rbac_and_validation_errors()` --uses--> `SqliteAsyncSessionAdapter`  [INFERRED]
  backend/tests/test_admin_api.py → backend/tests/conftest.py

## Import Cycles
- None detected.

## Communities (76 total, 28 thin omitted)

### Community 0 - "DomainError"
Cohesion: 0.12
Nodes (11): require_role(), role_checker(), create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token(), _enum_values() (+3 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "GradingRuleType"
Cohesion: 0.08
Nodes (7): GradingRuleType, build_sample_xlsx(), test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_docx_grader_supports_uniform_single_number_margin(), test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_rejects_static_value_instead_of_formula_and_missing_chart()

### Community 4 - "AccdbGrader"
Cohesion: 0.06
Nodes (12): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _parse_ddl_column_type(), _resolve_canonical_type() (+4 more)

### Community 5 - "export_group_journal"
Cohesion: 0.19
Nodes (3): export_group_journal(), get_group_journal(), list_academic_groups()

### Community 6 - "InvalidFileFormatError"
Cohesion: 0.09
Nodes (8): GradingError, InvalidFileFormatError, BaseGrader, GraderFactory, _format_cell_value(), PracticalFormat, GradingReport, test_grader_factory_resolves_all_four_formats()

### Community 7 - "RuleBuilderPage.tsx"
Cohesion: 0.20
Nodes (13): fetchCourses(), fetchPracticalTeacher(), FORMAT_BADGE_CONFIG, renderFormatIcon(), RULE_TYPE_SPECS, RuleBuilderPage(), RuleTypeSpec, CriterionResult (+5 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "_get_user_by_email"
Cohesion: 0.11
Nodes (10): _build_college_import_docx(), _get_user_by_email(), test_academic_group_course_year_restricted_to_1_through_4(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(), test_admin_endpoints_enforce_admin_rbac() (+2 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.07
Nodes (21): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256() (+13 more)

### Community 14 - "courses.py"
Cohesion: 0.13
Nodes (13): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleSummaryRead, ModuleUpdate, PracticalCreate, PracticalTeacherRead (+5 more)

### Community 15 - "list_my_submissions"
Cohesion: 0.15
Nodes (7): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade(), ManualGradeUpdateRequest, SubmissionRead

### Community 16 - "test_submissions_api.py"
Cohesion: 0.10
Nodes (21): CourseSlug, build_sample_docx(), make_auth_headers(), SqliteAsyncSessionAdapter, test_delete_admin_user_removes_student_submissions_and_disk_files(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found(), test_delete_module_by_teacher_and_admin_cascades_cleans_files_and_renumbers() (+13 more)

### Community 22 - "refresh_tokens"
Cohesion: 0.18
Nodes (4): login(), read_current_user(), refresh_tokens(), verify_password()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (41): @monaco-editor/react@4.6.0, devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0 (+33 more)

### Community 24 - "App.tsx"
Cohesion: 0.15
Nodes (25): App(), ProtectedAppLayout(), RoleHomeRedirect(), Navbar(), NavbarProps, resolvePageTitle(), ROLE_BADGE_CONFIG, ROLE_LABELS (+17 more)

### Community 25 - "DomainError"
Cohesion: 0.13
Nodes (13): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404(), _get_user_with_group_or_404() (+5 more)

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
Cohesion: 0.08
Nodes (4): _canonicalize_formula(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.22
Nodes (15): PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal() (+7 more)

### Community 33 - "QuizService"
Cohesion: 0.14
Nodes (4): QuizNotPassedError, PracticalStudentRead, QuizSubmitResponse, QuizService

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.28
Nodes (8): buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode, PracticalVariant

### Community 35 - "parse_docx_students"
Cohesion: 0.05
Nodes (27): ImportedStudentItem, ImportSkippedItem, calculate_variant_index(), delete_submission_file_safely(), delete_submission_files_for_paths(), resolve_submission_file_path(), build_generated_email(), _classify_header_cell() (+19 more)

### Community 36 - "Settings"
Cohesion: 0.16
Nodes (3): get_settings(), _resolve_backend_path(), Settings

### Community 37 - "SubmissionService"
Cohesion: 0.14
Nodes (3): DomainError, PlagiarismDetectedError, SubmissionService

### Community 38 - "submission_service.py"
Cohesion: 0.12
Nodes (11): Practical, build_content_disposition(), resolve_student_variant(), _build_submission_download_names(), _is_submission_file_available(), _sanitize_ascii_token(), _sanitize_utf8_token(), serialize_practical_teacher() (+3 more)

### Community 40 - "GradebookPage.tsx"
Cohesion: 0.10
Nodes (27): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+19 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.12
Nodes (29): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta, FORMAT_BADGE_LABELS (+21 more)

### Community 46 - "lucide-react"
Cohesion: 0.15
Nodes (12): dependencies, axios@^1.7.7, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient (+4 more)

### Community 47 - "User"
Cohesion: 0.12
Nodes (16): Base, Course, Module, QuizQuestion, QuizAttempt, AcademicGroup, User, build_seed_bundle() (+8 more)

### Community 48 - "Submission"
Cohesion: 0.07
Nodes (12): downgrade(), upgrade(), create_application(), lifespan(), Submission, main(), cleanup_expired_submissions(), main() (+4 more)

### Community 49 - "GradingRule"
Cohesion: 0.07
Nodes (11): _strip_identifiers(), _attribute_value_matches(), HtmlGrader, _is_doctype_target(), _normalize_selector(), _normalize_text(), CriterionResult, GradingRule (+3 more)

### Community 50 - "conftest.py"
Cohesion: 0.06
Nodes (9): hash_password(), async_client(), _compile_jsonb_for_sqlite(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password(), _replace_zip_member() (+1 more)

### Community 52 - "courses.py"
Cohesion: 0.06
Nodes (31): get_current_user(), _build_module_detail_read(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module(), delete_practical() (+23 more)

### Community 58 - "export_service.py"
Cohesion: 0.16
Nodes (6): _configure_pdf_font(), PracticalColumnInfo, _prepare_pdf_text(), render_group_journal_pdf(), _sanitize_filename_token(), _transliterate_to_ascii()

### Community 60 - "BaseModel"
Cohesion: 0.15
Nodes (6): AcademicGroupUpdate, ErrorResponse, LoginRequest, RefreshTokenRequest, StudentImportResponse, UserUpdate

### Community 61 - "env.py"
Cohesion: 0.12
Nodes (6): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), test_media_courses_static_serving(), test_seed_database_sync_courses_preserves_users_and_groups()

### Community 62 - "list_admin_users"
Cohesion: 0.18
Nodes (5): list_admin_users(), serialize_user(), UserBase, UserCreate, UserRead

### Community 63 - "AcademicGroupRead"
Cohesion: 0.22
Nodes (4): list_admin_groups(), AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead

### Community 64 - "ExportFormat"
Cohesion: 0.25
Nodes (3): _parse_export_format(), ExportFormat, ExportedDocument

### Community 65 - "GroupJournalRead"
Cohesion: 0.22
Nodes (4): GroupJournalRead, _auto_adjust_worksheet_columns(), GroupJournalBundle, render_group_journal_xlsx()

### Community 66 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 67 - "submit_practical_work"
Cohesion: 0.12
Nodes (6): _extract_submission_payload(), ExtractedSubmissionPayload, submit_practical_work(), update_practical_grading_rules(), GradingRulesUpdateRequest, HtmlSubmissionRequest

### Community 68 - "build_group_journal"
Cohesion: 0.18
Nodes (6): CriterionErrorStat, GroupJournalRow, GroupJournalStudentCell, build_group_journal(), calculate_criterion_error_stats(), _RuleStatAccumulator

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 692 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `GradingRuleType`, `AccdbGrader`, `SubmissionService`, `InvalidFileFormatError`, `DocxGrader`, `submission_service.py`, `courses.py`, `User`, `courses.py`, `_SeedQuizQuestionPayload`, `XlsxGrader`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `GradingRule` (e.g. with `AccdbGrader` and `BaseGrader`) actually correct?**
  _`GradingRule` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `DomainError` be split into smaller, more focused modules?**
  _Cohesion score 0.12222222222222222 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `SubmissionService` to `DomainError`, `ExportFormat`, `QuizService`, `submit_practical_work`, `parse_docx_students`, `InvalidFileFormatError`, `submission_service.py`, `Submission`, `ExportService`, `courses.py`, `refresh_tokens`, `DomainError`, `export_service.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `DomainError` (e.g. with `delete_admin_user()` and `update_admin_user()`) actually correct?**
  _`DomainError` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._