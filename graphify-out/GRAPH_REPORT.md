# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 87 files · ~253,564 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1608 nodes · 4474 edges · 89 communities (48 shown, 41 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 356 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2318999c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DomainError
- postgres
- compilerOptions
- DocxGrader
- AccdbGrader
- GradingRule
- InvalidFileFormatError
- test_course_content.py
- MarkdownRenderer.tsx
- vite-env.d.ts
- _get_user_by_email
- InvalidFileFormatError
- courses.py
- SubmissionService
- test_submissions_api.py
- ExportService
- edu-auto-grader-backend
- refresh_tokens
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- _SeedCoursePayload
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- GroupJournalPage.tsx
- accdb_grader.py
- HtmlSandbox.tsx
- parse_docx_students
- Settings
- .__init__
- re
- DocxDocument
- RuleBuilderPage.tsx
- ModuleViewPage.tsx
- export_service.py
- submission_service.py
- retention_service.py
- html_grader.py
- conftest.py
- courses.py
- submission.py
- schemas/__init__.py
- SqliteAsyncSessionAdapter
- submissions.py
- export_group_journal
- seed_database
- .import_students
- User
- main.py
- submit_practical_work
- GradebookPage.tsx
- SubmissionRead
- do_run_migrations
- 0001_initial_schema.py
- AcademicGroupRead
- PracticalTeacherRead
- _enum_values

## God Nodes (most connected - your core abstractions)
1. `DomainError` - 63 edges
2. `User` - 61 edges
3. `GradingRule` - 54 edges
4. `SqliteAsyncSessionAdapter` - 45 edges
5. `InvalidFileFormatError` - 43 edges
6. `get_db()` - 43 edges
7. `DocxGrader` - 42 edges
8. `SubmissionService` - 41 edges
9. `UserRole` - 37 edges
10. `GradingError` - 37 edges

## Surprising Connections (you probably didn't know these)
- `require_role()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `create_admin_user()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `list_admin_users()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `update_admin_user()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `TokenPayload` --uses--> `UserRole`  [INFERRED]
  backend/app/schemas/auth.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (89 total, 41 thin omitted)

### Community 0 - "DomainError"
Cohesion: 0.17
Nodes (8): create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token(), _enum_values(), UserRole, TokenResponse

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 4 - "AccdbGrader"
Cohesion: 0.07
Nodes (12): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _strip_identifiers(), build_sample_accdb() (+4 more)

### Community 5 - "GradingRule"
Cohesion: 0.11
Nodes (12): HtmlGrader, GradingRule, test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_docx_grader_supports_uniform_single_number_margin(), test_grader_factory_resolves_all_four_formats(), test_html_grader_attribute_filter_selector_and_compound_colspan(), test_html_grader_detects_missing_tags_and_rejects_empty_code() (+4 more)

### Community 6 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (7): GradingError, InvalidFileFormatError, BaseGrader, GraderFactory, PracticalFormat, GradingReport, GradingRuleType

### Community 7 - "test_course_content.py"
Cohesion: 0.13
Nodes (9): _canonicalize_formula(), _is_wrapped_in_parens(), AcademicGroup, build_seed_bundle(), test_academic_group_course_year_restricted_to_1_through_4(), test_all_course_variants_resolve_rule_placeholders_without_leftovers(), test_excel_course_formula_rules_have_valid_supported_expressions(), test_full_course_json_bundle_validation() (+1 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.13
Nodes (30): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+22 more)

### Community 11 - "_get_user_by_email"
Cohesion: 0.13
Nodes (10): calculate_variant_index(), _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(), test_admin_endpoints_enforce_admin_rbac() (+2 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (17): check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism(), extract_core_xml_metadata() (+9 more)

### Community 14 - "courses.py"
Cohesion: 0.06
Nodes (18): _build_module_detail_read(), QuizNotPassedError, CourseCreate, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleUpdate, PracticalCreate (+10 more)

### Community 15 - "SubmissionService"
Cohesion: 0.15
Nodes (3): GradingRulesUpdateRequest, SubmissionDownloadPayload, SubmissionService

### Community 16 - "test_submissions_api.py"
Cohesion: 0.16
Nodes (15): CourseSlug, build_sample_docx(), make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_download_submission_forbidden_for_other_teacher_and_students() (+7 more)

### Community 22 - "refresh_tokens"
Cohesion: 0.15
Nodes (5): login(), read_current_user(), refresh_tokens(), verify_password(), hash_password()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (41): @monaco-editor/react@4.6.0, devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0 (+33 more)

### Community 24 - "App.tsx"
Cohesion: 0.10
Nodes (35): dependencies, axios@^1.7.7, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, App(), ProtectedAppLayout() (+27 more)

### Community 25 - "admin.py"
Cohesion: 0.10
Nodes (18): role_checker(), create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404() (+10 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (46): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+38 more)

### Community 27 - "course.ts"
Cohesion: 0.10
Nodes (33): CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses() (+25 more)

### Community 28 - "_SeedCoursePayload"
Cohesion: 0.18
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.12
Nodes (3): _format_cell_value(), _try_parse_numeric(), XlsxGrader

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.22
Nodes (15): PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal() (+7 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.13
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.28
Nodes (8): buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode, PracticalVariant

### Community 35 - "parse_docx_students"
Cohesion: 0.07
Nodes (20): build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _encode_ukrainian_word(), generate_temp_password(), _get_cell_value() (+12 more)

### Community 36 - "Settings"
Cohesion: 0.18
Nodes (3): get_settings(), _resolve_backend_path(), Settings

### Community 38 - "re"
Cohesion: 0.29
Nodes (4): _build_submission_download_names(), _sanitize_ascii_token(), _sanitize_utf8_token(), _strip_apostrophes()

### Community 40 - "RuleBuilderPage.tsx"
Cohesion: 0.10
Nodes (27): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+19 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.12
Nodes (30): renderInlineMarkdown(), AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta (+22 more)

### Community 46 - "export_service.py"
Cohesion: 0.13
Nodes (8): _auto_adjust_worksheet_columns(), _configure_pdf_font(), PracticalColumnInfo, _prepare_pdf_text(), render_group_journal_pdf(), render_group_journal_xlsx(), _sanitize_filename_token(), _transliterate_to_ascii()

### Community 47 - "submission_service.py"
Cohesion: 0.09
Nodes (14): run_migrations_offline(), Base, Course, Module, Practical, QuizQuestion, PracticalVariant, _load_course_from_json() (+6 more)

### Community 48 - "retention_service.py"
Cohesion: 0.18
Nodes (7): build_content_disposition(), ExportedDocument, cleanup_expired_submissions(), delete_submission_file_safely(), resolve_submission_file_path(), RetentionCleanupSummary, run_retention_cleanup_once()

### Community 49 - "html_grader.py"
Cohesion: 0.08
Nodes (10): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), _is_doctype_target(), _normalize_selector(), _normalize_text(), _parse_text_match_expected(), _strip_quotes() (+2 more)

### Community 50 - "conftest.py"
Cohesion: 0.07
Nodes (9): async_client(), build_sample_xlsx(), _compile_jsonb_for_sqlite(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password(), _replace_zip_member() (+1 more)

### Community 52 - "courses.py"
Cohesion: 0.07
Nodes (27): _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module(), delete_practical(), delete_quiz_question(), _ensure_course_owner_or_admin() (+19 more)

### Community 58 - "submission.py"
Cohesion: 0.14
Nodes (9): CriterionErrorStat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest, ManualGradeUpdateRequest, build_group_journal(), calculate_criterion_error_stats() (+1 more)

### Community 60 - "schemas/__init__.py"
Cohesion: 0.13
Nodes (13): AcademicGroupBase, AcademicGroupCreate, AcademicGroupUpdate, ErrorResponse, ImportedStudentItem, ImportSkippedItem, LoginRequest, RefreshTokenRequest (+5 more)

### Community 61 - "SqliteAsyncSessionAdapter"
Cohesion: 0.10
Nodes (14): hash_password(), QuizAttempt, Submission, SqliteAsyncSessionAdapter, test_delete_admin_user_removes_student_submissions_and_disk_files(), _copy_course_content_dir(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found() (+6 more)

### Community 62 - "submissions.py"
Cohesion: 0.19
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 63 - "export_group_journal"
Cohesion: 0.17
Nodes (5): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), ExportFormat

### Community 64 - "seed_database"
Cohesion: 0.16
Nodes (7): main(), run_seed(), seed_database(), SeedBundle, SeedSummary, summarize_bundle(), delete_submission_files_for_paths()

### Community 67 - "User"
Cohesion: 0.20
Nodes (3): get_current_user(), require_role(), User

### Community 68 - "main.py"
Cohesion: 0.14
Nodes (4): create_application(), lifespan(), run_periodic_retention_cleanup(), test_lifespan_starts_and_cancels_retention_background_task()

### Community 70 - "submit_practical_work"
Cohesion: 0.15
Nodes (4): _extract_submission_payload(), ExtractedSubmissionPayload, submit_practical_work(), update_practical_grading_rules()

### Community 76 - "GradebookPage.tsx"
Cohesion: 0.10
Nodes (24): @tanstack/react-query@^5.60.0, COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS (+16 more)

### Community 79 - "SubmissionRead"
Cohesion: 0.22
Nodes (3): SubmissionRead, _is_submission_file_available(), serialize_submission()

### Community 80 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 704 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DomainError` connect `admin.py` to `DomainError`, `.import_students`, `User`, `main.py`, `.__init__`, `submit_practical_work`, `InvalidFileFormatError`, `parse_docx_students`, `courses.py`, `export_service.py`, `submission_service.py`, `ExportService`, `SubmissionService`, `courses.py`, `refresh_tokens`, `export_group_journal`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `DomainError` (e.g. with `delete_admin_user()` and `update_admin_user()`) actually correct?**
  _`DomainError` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `User` connect `User` to `.import_students`, `parse_docx_students`, `re`, `test_course_content.py`, `_get_user_by_email`, `courses.py`, `submission_service.py`, `export_service.py`, `ExportService`, `SubmissionRead`, `SubmissionService`, `courses.py`, `test_submissions_api.py`, `refresh_tokens`, `admin.py`, `submission.py`, `SqliteAsyncSessionAdapter`, `export_group_journal`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `User` (e.g. with `get_current_user()` and `require_role()`) actually correct?**
  _`User` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._