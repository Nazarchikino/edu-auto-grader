# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 94 files · ~265,418 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1836 nodes · 4977 edges · 138 communities (53 shown, 85 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 272 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `60d43224`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QuizService
- postgres
- compilerOptions
- AccdbGrader
- SubmissionService
- _get_module_with_questions
- SqliteAsyncSessionAdapter
- MarkdownRenderer.tsx
- vite-env.d.ts
- make_auth_headers
- metadata.py
- courses.py
- _get_course_module_and_practical
- submit_practical_work
- edu-auto-grader-backend
- _extract_submission_payload
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- render_group_journal_pdf
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- GroupJournalPage.tsx
- accdb_grader.py
- HtmlSandbox.tsx
- student_import_service.py
- Settings
- get_db
- submission_service.py
- HtmlGrader
- GradingReportCard.tsx
- db_session
- schemas/__init__.py
- ModuleViewPage.tsx
- UUID
- SlidingWindowRateLimiter
- evaluate_plagiarism
- services/__init__.py
- @tanstack/react-query
- UserRole
- html_grader.py
- _is_submission_file_available
- DomainError
- test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress
- list_my_submissions
- ExportService
- test_all_course_variants_resolve_rule_placeholders_without_leftovers
- .update_grading_rules
- rewrite_openxml_core_metadata
- User
- main.py
- 0001_initial_schema.py
- CoursesPage.tsx
- DocxGrader
- do_run_migrations
- User
- get_module
- test_read_upload_file_limited_stops_reading_chunks_early
- _compile_jsonb_for_sqlite
- ._evaluate_page_margins
- get_current_user
- BaseModel
- Depends
- QuizQuestionRead
- _find_xml_text

## God Nodes (most connected - your core abstractions)
1. `SqliteAsyncSessionAdapter` - 69 edges
2. `User` - 67 edges
3. `DomainError` - 63 edges
4. `get_db()` - 45 edges
5. `make_auth_headers()` - 44 edges
6. `InvalidFileFormatError` - 42 edges
7. `GradingError` - 42 edges
8. `DocxGrader` - 42 edges
9. `GradingRule` - 39 edges
10. `UserRole` - 38 edges

## Surprising Connections (you probably didn't know these)
- `_serialize_practical_teacher()` --uses--> `PracticalVariant`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `create_course()` --uses--> `CourseCreate`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `update_course()` --uses--> `CourseUpdate`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `create_module()` --uses--> `ModuleCreate`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `create_module()` --uses--> `ModuleDetailRead`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py

## Import Cycles
- None detected.

## Communities (138 total, 85 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.14
Nodes (4): _build_module_detail_read(), PracticalSummaryRead, QuizSubmitResponse, QuizService

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 4 - "AccdbGrader"
Cohesion: 0.06
Nodes (16): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _strip_identifiers(), CriterionResult (+8 more)

### Community 6 - "_get_module_with_questions"
Cohesion: 0.17
Nodes (8): _build_answers_for_score(), _get_module_with_questions(), _get_user_by_email(), test_excel_q42_imported_in_module_8_with_media_and_dry_run(), test_quiz_cooldown_zero_disables_wait_and_negative_config_rejected(), test_quiz_pass_threshold_setting_controls_passed_flag(), test_quiz_retry_cooldown_blocks_immediate_retry_and_unlocks_after_window(), test_quiz_submit_rejects_incomplete_duplicate_foreign_and_invalid_answers()

### Community 7 - "SqliteAsyncSessionAdapter"
Cohesion: 0.23
Nodes (3): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), test_seed_database_sync_courses_preserves_users_and_groups()

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "make_auth_headers"
Cohesion: 0.12
Nodes (12): make_auth_headers(), _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates() (+4 more)

### Community 13 - "metadata.py"
Cohesion: 0.07
Nodes (21): GradingError, InvalidFileFormatError, BaseGrader, GraderFactory, compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash() (+13 more)

### Community 14 - "courses.py"
Cohesion: 0.16
Nodes (11): create_course(), _fetch_user_progress_maps(), get_course(), list_courses(), _load_course_or_404(), _serialize_course(), update_course(), CourseRead (+3 more)

### Community 16 - "_get_course_module_and_practical"
Cohesion: 0.11
Nodes (17): build_sample_docx(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_best_score_unified_across_student_progress_and_group_journal_export(), test_download_submission_forbidden_for_other_teacher_and_students(), test_download_submissions_by_course_teacher_and_admin_with_headers_and_content() (+9 more)

### Community 17 - "submit_practical_work"
Cohesion: 0.17
Nodes (3): _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 22 - "_extract_submission_payload"
Cohesion: 0.29
Nodes (3): _extract_client_ip(), _extract_submission_payload(), ExtractedSubmissionPayload

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.15
Nodes (28): App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps, resolvePageTitle() (+20 more)

### Community 25 - "admin.py"
Cohesion: 0.08
Nodes (24): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404(), _get_user_with_group_or_404() (+16 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.07
Nodes (41): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+33 more)

### Community 27 - "course.ts"
Cohesion: 0.07
Nodes (50): PracticalModuleContext, CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab (+42 more)

### Community 28 - "render_group_journal_pdf"
Cohesion: 0.13
Nodes (7): _auto_adjust_worksheet_columns(), _configure_pdf_font(), PracticalColumnInfo, _prepare_pdf_text(), render_group_journal_pdf(), render_group_journal_xlsx(), _transliterate_to_ascii()

### Community 29 - "AuthContext.tsx"
Cohesion: 0.12
Nodes (28): axios@^1.7.7, API_BASE_URL, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken(), notifyAuthFailure() (+20 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.07
Nodes (6): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader, test_excel_course_formula_rules_have_valid_supported_expressions()

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.16
Nodes (19): PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal() (+11 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.13
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.18
Nodes (15): buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps, PendingDraftState (+7 more)

### Community 35 - "student_import_service.py"
Cohesion: 0.05
Nodes (26): _build_too_large_exception(), format_size_limit_mb(), ImportedStudentItem, ImportSkippedItem, StudentImportResponse, build_generated_email(), _classify_header_cell(), _clean_whitespace() (+18 more)

### Community 36 - "Settings"
Cohesion: 0.12
Nodes (4): get_settings(), _resolve_backend_path(), Settings, test_settings_production_rejects_default_or_short_jwt_secret()

### Community 37 - "get_db"
Cohesion: 0.14
Nodes (10): ensure_course_owner_or_admin(), create_module(), create_quiz_question(), get_practical_for_teacher(), _serialize_practical_teacher(), update_module(), update_practical(), upsert_module_practical() (+2 more)

### Community 38 - "submission_service.py"
Cohesion: 0.10
Nodes (11): require_role(), read_upload_file_limited(), GradingRulesUpdateRequest, ExportFormat, ManualGradeUpdateRequest, SubmissionRead, build_content_disposition(), _build_submission_download_names() (+3 more)

### Community 39 - "HtmlGrader"
Cohesion: 0.08
Nodes (9): has_meaningful_html_body(), HtmlGrader, _normalize_selector(), parse_html_document(), test_minimal_html_starter_template_scores_zero_across_all_html_course_modules(), test_html_grader_attribute_filter_selector_and_compound_colspan(), test_html_grader_detects_missing_tags_and_rejects_empty_code(), test_html_grader_empty_body_and_starter_template_score_zero() (+1 more)

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.11
Nodes (24): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+16 more)

### Community 41 - "db_session"
Cohesion: 0.15
Nodes (4): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session()

### Community 43 - "schemas/__init__.py"
Cohesion: 0.08
Nodes (18): CourseCreate, CourseUpdate, ModuleCreate, ModuleUpdate, PracticalCreate, PracticalStudentRead, PracticalVariant, QuizAnswerItem (+10 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.10
Nodes (33): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, extractRetryAfterSeconds(), fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta (+25 more)

### Community 45 - "UUID"
Cohesion: 0.24
Nodes (5): _collect_practical_submission_file_paths(), delete_module(), delete_practical(), delete_quiz_question(), delete_submission_files_for_paths()

### Community 47 - "evaluate_plagiarism"
Cohesion: 0.14
Nodes (5): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), SubmissionRecordProtocol, PlagiarismCheckResult

### Community 48 - "services/__init__.py"
Cohesion: 0.09
Nodes (15): ExportedDocument, GroupJournalBundle, calculate_variant_index(), _ensure_utc(), format_cooldown_remaining(), get_quiz_pass_threshold_percent(), resolve_student_variant(), cleanup_expired_submissions() (+7 more)

### Community 49 - "@tanstack/react-query"
Cohesion: 0.15
Nodes (12): dependencies, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient (+4 more)

### Community 51 - "UserRole"
Cohesion: 0.07
Nodes (24): change_password(), login(), refresh_tokens(), build_login_rate_limit_key(), create_access_token(), create_refresh_token(), create_token_pair(), decode_token() (+16 more)

### Community 52 - "html_grader.py"
Cohesion: 0.10
Nodes (10): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), _is_doctype_target(), _node_has_visible_content(), _normalize_text(), _parse_text_match_expected(), _strip_quotes() (+2 more)

### Community 60 - "DomainError"
Cohesion: 0.22
Nodes (4): role_checker(), DomainError, PlagiarismDetectedError, QuizNotPassedError

### Community 61 - "test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress"
Cohesion: 0.10
Nodes (13): _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_login_rate_limiting_blocks_after_n_failures_and_resets_on_success(), test_long_cyrillic_password_create_login_and_change_without_500(), test_token_version_revokes_tokens_on_admin_reset_and_self_change(), _copy_course_content_dir(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found() (+5 more)

### Community 62 - "list_my_submissions"
Cohesion: 0.18
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 63 - "ExportService"
Cohesion: 0.08
Nodes (6): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), ExportService, _sanitize_filename_token()

### Community 66 - "rewrite_openxml_core_metadata"
Cohesion: 0.22
Nodes (5): build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata(), test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_rejects_static_value_instead_of_formula_and_missing_chart()

### Community 67 - "User"
Cohesion: 0.08
Nodes (17): hash_password(), QuizQuestion, build_seed_bundle(), _load_course_from_json(), main(), _question_signature(), run_seed(), seed_database() (+9 more)

### Community 68 - "main.py"
Cohesion: 0.09
Nodes (5): downgrade(), upgrade(), create_application(), lifespan(), test_lifespan_starts_and_cancels_retention_background_task()

### Community 72 - "CoursesPage.tsx"
Cohesion: 0.24
Nodes (9): apiClient, COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS (+1 more)

### Community 77 - "DocxGrader"
Cohesion: 0.20
Nodes (4): DocxGrader, test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_docx_grader_resolves_placeholders_in_target_and_expected()

### Community 80 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 82 - "User"
Cohesion: 0.08
Nodes (17): run_migrations_offline(), Base, Course, CourseSlug, _enum_values(), Module, Practical, QuizAttempt (+9 more)

### Community 87 - "get_module"
Cohesion: 0.25
Nodes (4): get_module(), list_module_quiz_questions_teacher(), _load_module_or_404(), ModuleDetailRead

### Community 92 - "test_read_upload_file_limited_stops_reading_chunks_early"
Cohesion: 0.50
Nodes (3): test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 99 - "BaseModel"
Cohesion: 0.18
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 830 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **85 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `QuizService`, `SubmissionService`, `_get_module_with_questions`, `SqliteAsyncSessionAdapter`, `make_auth_headers`, `courses.py`, `_get_course_module_and_practical`, `admin.py`, `student_import_service.py`, `get_db`, `submission_service.py`, `schemas/__init__.py`, `services/__init__.py`, `UserRole`, `test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress`, `ExportService`, `.update_grading_rules`, `User`, `get_module`, `get_current_user`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `SqliteAsyncSessionAdapter` (e.g. with `_get_user_by_email()` and `test_change_password_validation_and_imported_student_flag()`) actually correct?**
  _`SqliteAsyncSessionAdapter` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.1422924901185771 - nodes in this community are weakly interconnected._
- **Why does `GradingError` connect `metadata.py` to `test_all_course_variants_resolve_rule_placeholders_without_leftovers`, `accdb_grader.py`, `DocxDocument`, `AccdbGrader`, `submission_service.py`, `HtmlGrader`, `html_grader.py`, `._evaluate_html_submission`, `DomainError`, `XlsxGrader`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `User` (e.g. with `ensure_course_owner_or_admin()` and `get_current_user()`) actually correct?**
  _`User` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._