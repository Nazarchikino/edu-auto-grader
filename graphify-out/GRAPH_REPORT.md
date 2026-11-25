# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 89 files · ~256,652 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1686 nodes · 4593 edges · 115 communities (49 shown, 66 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 235 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9738c7e6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- postgres
- compilerOptions
- DocxGrader
- AccdbGrader
- admin.py
- test_graders.py
- SqliteAsyncSessionAdapter
- MarkdownRenderer.tsx
- vite-env.d.ts
- make_auth_headers
- metadata.py
- courses.py
- SubmissionService
- _get_course_module_and_practical
- ExportService
- edu-auto-grader-backend
- DomainError
- package.json
- App.tsx
- list_admin_users
- AdminUsersPage.tsx
- course.ts
- conftest.py
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- GroupJournalPage.tsx
- accdb_grader.py
- HtmlSandbox.tsx
- student_import_service.py
- Settings
- courses.py
- _build_submission_download_names
- GradingReportCard.tsx
- _get_user_by_email
- ExportFormat
- ModuleViewPage.tsx
- serialize_user
- ExportFormat
- test_course_content.py
- retention_service.py
- HtmlGrader
- conftest.py
- AcademicGroupBase
- GroupJournalRead
- UserRole
- test_course_content.py
- submissions.py
- export_group_journal
- normalize_full_name
- .import_students
- submission_service.py
- main.py
- submit_practical_work
- .evaluate
- serialize_submission
- do_run_migrations
- 0001_initial_schema.py
- _enum_values
- read_upload_file_limited
- _compile_jsonb_for_sqlite
- test_lifespan_starts_and_cancels_retention_background_task

## God Nodes (most connected - your core abstractions)
1. `DomainError` - 62 edges
2. `User` - 58 edges
3. `SqliteAsyncSessionAdapter` - 54 edges
4. `GradingRule` - 47 edges
5. `DocxGrader` - 43 edges
6. `get_db()` - 43 edges
7. `InvalidFileFormatError` - 42 edges
8. `GradingError` - 41 edges
9. `XlsxGrader` - 33 edges
10. `make_auth_headers()` - 33 edges

## Surprising Connections (you probably didn't know these)
- `_serialize_practical_teacher()` --uses--> `PracticalVariant`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `create_course()` --uses--> `CourseCreate`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `update_course()` --uses--> `CourseUpdate`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `create_module()` --uses--> `ModuleCreate`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `update_module()` --uses--> `ModuleUpdate`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py

## Import Cycles
- None detected.

## Communities (115 total, 66 thin omitted)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "DocxGrader"
Cohesion: 0.05
Nodes (3): DocxGrader, _format_number(), test_all_course_variants_resolve_rule_placeholders_without_leftovers()

### Community 4 - "AccdbGrader"
Cohesion: 0.05
Nodes (16): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_system_table_name(), _strip_identifiers(), CriterionResult, GradingRule (+8 more)

### Community 5 - "admin.py"
Cohesion: 0.20
Nodes (7): create_admin_user(), _ensure_email_unique(), _get_group_or_404(), _get_user_with_group_or_404(), _normalize_email(), _normalize_non_empty(), update_admin_user()

### Community 6 - "test_graders.py"
Cohesion: 0.08
Nodes (9): GradingError, InvalidFileFormatError, BaseGrader, GraderFactory, _is_doctype_target(), _normalize_text(), PracticalFormat, GradingReport (+1 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "make_auth_headers"
Cohesion: 0.12
Nodes (12): calculate_variant_index(), make_auth_headers(), _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb() (+4 more)

### Community 13 - "metadata.py"
Cohesion: 0.07
Nodes (22): check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism(), extract_core_xml_metadata() (+14 more)

### Community 14 - "courses.py"
Cohesion: 0.06
Nodes (20): CourseCreate, CourseUpdate, ModuleCreate, ModuleSummaryRead, ModuleUpdate, PracticalCreate, PracticalStudentRead, PracticalSummaryRead (+12 more)

### Community 16 - "_get_course_module_and_practical"
Cohesion: 0.14
Nodes (11): build_sample_docx(), rewrite_openxml_core_metadata(), test_delete_admin_user_removes_student_submissions_and_disk_files(), _get_course_module_and_practical(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_download_submission_forbidden_for_other_teacher_and_students(), test_download_submissions_by_course_teacher_and_admin_with_headers_and_content() (+3 more)

### Community 22 - "DomainError"
Cohesion: 0.20
Nodes (4): require_role(), role_checker(), DomainError, PlagiarismDetectedError

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.15
Nodes (26): App(), ProtectedAppLayout(), RoleHomeRedirect(), Navbar(), NavbarProps, resolvePageTitle(), ROLE_BADGE_CONFIG, ROLE_LABELS (+18 more)

### Community 25 - "list_admin_users"
Cohesion: 0.13
Nodes (7): create_admin_group(), delete_admin_group(), delete_admin_user(), _ensure_group_code_unique(), list_admin_groups(), list_admin_users(), update_admin_group()

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (46): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+38 more)

### Community 27 - "course.ts"
Cohesion: 0.06
Nodes (55): COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS, CourseEditorPage() (+47 more)

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.07
Nodes (6): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader, test_excel_course_formula_rules_have_valid_supported_expressions()

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.22
Nodes (15): PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal() (+7 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.12
Nodes (7): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _is_numeric_condition(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.09
Nodes (21): dependencies, axios@^1.7.7, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0 (+13 more)

### Community 35 - "student_import_service.py"
Cohesion: 0.09
Nodes (17): ImportSkippedItem, build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _get_cell_value(), _infer_default_docx_columns() (+9 more)

### Community 36 - "Settings"
Cohesion: 0.18
Nodes (3): get_settings(), _resolve_backend_path(), Settings

### Community 37 - "courses.py"
Cohesion: 0.06
Nodes (33): ensure_course_owner_or_admin(), get_current_user(), _build_module_detail_read(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module() (+25 more)

### Community 38 - "_build_submission_download_names"
Cohesion: 0.29
Nodes (4): _build_submission_download_names(), _sanitize_ascii_token(), _sanitize_utf8_token(), _strip_apostrophes()

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.10
Nodes (27): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+19 more)

### Community 41 - "_get_user_by_email"
Cohesion: 0.22
Nodes (5): _get_user_by_email(), test_health_check_and_jwt_login_flow(), test_submission_blocked_without_passed_quiz_and_unlocked_after_70_percent(), test_submit_html_returns_422_when_raw_code_exceeds_max_length(), test_teacher_update_rules_manual_grade_and_group_export()

### Community 43 - "ExportFormat"
Cohesion: 0.25
Nodes (3): ExportFormat, build_content_disposition(), ExportedDocument

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.12
Nodes (29): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta, FORMAT_BADGE_LABELS (+21 more)

### Community 45 - "serialize_user"
Cohesion: 0.29
Nodes (3): read_current_user(), serialize_user(), UserRead

### Community 46 - "ExportFormat"
Cohesion: 0.18
Nodes (5): _configure_pdf_font(), _prepare_pdf_text(), render_group_journal_pdf(), _sanitize_filename_token(), _transliterate_to_ascii()

### Community 47 - "test_course_content.py"
Cohesion: 0.08
Nodes (12): build_seed_bundle(), hash_password(), _load_course_from_json(), main(), _question_signature(), run_seed(), SeedBundle, SeedSummary (+4 more)

### Community 48 - "retention_service.py"
Cohesion: 0.18
Nodes (7): cleanup_expired_submissions(), delete_submission_file_safely(), delete_submission_files_for_paths(), resolve_submission_file_path(), RetentionCleanupSummary, run_retention_cleanup_once(), generate_temp_password()

### Community 49 - "HtmlGrader"
Cohesion: 0.08
Nodes (11): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), HtmlGrader, _normalize_selector(), _parse_text_match_expected(), _strip_quotes(), _tag_has_attribute() (+3 more)

### Community 50 - "conftest.py"
Cohesion: 0.17
Nodes (4): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session()

### Community 58 - "GroupJournalRead"
Cohesion: 0.12
Nodes (8): GroupJournalRead, _auto_adjust_worksheet_columns(), build_group_journal(), calculate_criterion_error_stats(), GroupJournalBundle, PracticalColumnInfo, render_group_journal_xlsx(), _RuleStatAccumulator

### Community 60 - "UserRole"
Cohesion: 0.08
Nodes (20): login(), refresh_tokens(), create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token(), verify_password() (+12 more)

### Community 61 - "test_course_content.py"
Cohesion: 0.08
Nodes (22): hash_password(), QuizQuestion, QuizAttempt, Submission, seed_database(), summarize_bundle(), _copy_course_content_dir(), _get_user_by_email() (+14 more)

### Community 62 - "submissions.py"
Cohesion: 0.18
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 63 - "export_group_journal"
Cohesion: 0.16
Nodes (5): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), AcademicGroupRead

### Community 65 - "normalize_full_name"
Cohesion: 0.25
Nodes (3): _encode_ukrainian_word(), ukrainian_sort_key(), test_ukrainian_alphabetical_sorting_and_apostrophe_normalization()

### Community 66 - ".import_students"
Cohesion: 0.12
Nodes (3): import_admin_students(), StudentImportResponse, StudentImportService

### Community 67 - "submission_service.py"
Cohesion: 0.11
Nodes (15): Base, Course, CourseSlug, Module, Practical, AcademicGroup, User, PracticalTeacherRead (+7 more)

### Community 68 - "main.py"
Cohesion: 0.16
Nodes (3): create_application(), lifespan(), run_periodic_retention_cleanup()

### Community 70 - "submit_practical_work"
Cohesion: 0.13
Nodes (5): _extract_submission_payload(), ExtractedSubmissionPayload, _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 77 - ".evaluate"
Cohesion: 0.08
Nodes (5): build_sample_xlsx(), test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_rejects_static_value_instead_of_formula_and_missing_chart()

### Community 80 - "do_run_migrations"
Cohesion: 0.18
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 92 - "read_upload_file_limited"
Cohesion: 0.17
Nodes (6): _build_too_large_exception(), format_size_limit_mb(), read_upload_file_limited(), test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 752 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **66 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DomainError` connect `DomainError` to `.import_students`, `submission_service.py`, `main.py`, `admin.py`, `courses.py`, `submit_practical_work`, `test_graders.py`, `student_import_service.py`, `serialize_submission`, `SubmissionService`, `ExportService`, `list_admin_users`, `._evaluate_file_submission`, `UserRole`, `export_group_journal`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `DomainError` (e.g. with `login()` and `refresh_tokens()`) actually correct?**
  _`DomainError` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `GradingRule` connect `AccdbGrader` to `accdb_grader.py`, `submission_service.py`, `courses.py`, `test_graders.py`, `.evaluate`, `courses.py`, `metadata.py`, `test_course_content.py`, `HtmlGrader`, `UserRole`, `test_course_content.py`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `User` (e.g. with `login()` and `read_current_user()`) actually correct?**
  _`User` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._