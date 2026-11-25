# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 96 files · ~269,129 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1919 nodes · 5201 edges · 126 communities (57 shown, 69 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 286 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c2cf76bc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QuizService
- postgres
- compilerOptions
- conftest.py
- AccdbGrader
- SubmissionService
- _get_module_with_questions
- SqliteAsyncSessionAdapter
- MarkdownRenderer.tsx
- vite-env.d.ts
- _get_user_by_email
- metadata.py
- DomainError
- _get_course_module_and_practical
- submit_practical_work
- edu-auto-grader-backend
- change_password
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- student_import_service.py
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- GroupJournalPage.tsx
- accdb_grader.py
- HtmlSandbox.tsx
- student_import_service.py
- Submission
- submission_service.py
- HtmlGrader
- GradingReportCard.tsx
- db_session
- build_group_journal
- courses.py
- ModuleViewPage.tsx
- delete_admin_user
- SlidingWindowRateLimiter
- grading.py
- services/__init__.py
- @tanstack/react-query
- reset_admin_user_password
- schemas/__init__.py
- export_group_journal
- DocxGrader
- render_group_journal_pdf
- PlagiarismDetectedError
- Settings
- list_my_submissions
- GradingError
- main.py
- test_course_content.py
- test_auth_security.py
- .export_group_journal
- ExportService
- DocxGrader
- do_run_migrations
- conftest.py
- create_token_pair
- rewrite_openxml_core_metadata
- ExportFormat
- ChangePasswordRequest
- read_upload_file_limited
- QuizQuestionRead
- _compile_jsonb_for_sqlite
- test_lifespan_starts_and_cancels_retention_background_task
- _resolve_backend_path
- get_current_user
- _enum_values
- _SeedQuizQuestionPayload
- test_duplicate_root_auth_router_removed_returns_404
- .import_students

## God Nodes (most connected - your core abstractions)
1. `SqliteAsyncSessionAdapter` - 75 edges
2. `User` - 70 edges
3. `DomainError` - 67 edges
4. `make_auth_headers()` - 48 edges
5. `get_db()` - 45 edges
6. `DocxGrader` - 42 edges
7. `GradingError` - 42 edges
8. `InvalidFileFormatError` - 41 edges
9. `GradingRule` - 39 edges
10. `Module` - 37 edges

## Surprising Connections (you probably didn't know these)
- `QuizService` --uses--> `Module`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/models/course.py
- `QuizService` --uses--> `Practical`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/models/course.py
- `QuizService` --uses--> `QuizQuestion`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/models/course.py
- `QuizService` --uses--> `QuizAttempt`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/models/progress.py
- `QuizService` --uses--> `User`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (126 total, 69 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.09
Nodes (5): _build_module_detail_read(), get_practical_for_student(), submit_module_quiz(), get_quiz_pass_threshold_percent(), QuizService

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 4 - "AccdbGrader"
Cohesion: 0.06
Nodes (15): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _strip_identifiers(), GradingRule (+7 more)

### Community 5 - "SubmissionService"
Cohesion: 0.09
Nodes (5): role_checker(), DomainError, _save_uploaded_file(), serialize_practical_teacher(), SubmissionService

### Community 6 - "_get_module_with_questions"
Cohesion: 0.17
Nodes (8): _build_answers_for_score(), _get_module_with_questions(), _get_user_by_email(), test_excel_q42_imported_in_module_8_with_media_and_dry_run(), test_quiz_cooldown_zero_disables_wait_and_negative_config_rejected(), test_quiz_pass_threshold_setting_controls_passed_flag(), test_quiz_retry_cooldown_blocks_immediate_retry_and_unlocks_after_window(), test_quiz_submit_rejects_incomplete_duplicate_foreign_and_invalid_answers()

### Community 7 - "SqliteAsyncSessionAdapter"
Cohesion: 0.09
Nodes (20): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), _copy_course_content_dir(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found(), test_delete_module_by_teacher_and_admin_cascades_cleans_files_and_renumbers(), test_delete_practical_preserves_module_lecture_quiz_and_cleans_files(), test_media_courses_static_serving() (+12 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.13
Nodes (30): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+22 more)

### Community 11 - "_get_user_by_email"
Cohesion: 0.11
Nodes (11): _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(), test_admin_endpoints_enforce_admin_rbac() (+3 more)

### Community 13 - "metadata.py"
Cohesion: 0.07
Nodes (22): InvalidFileFormatError, check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism() (+14 more)

### Community 14 - "DomainError"
Cohesion: 0.08
Nodes (23): ensure_course_owner_or_admin(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module(), delete_practical(), delete_quiz_question() (+15 more)

### Community 16 - "_get_course_module_and_practical"
Cohesion: 0.12
Nodes (19): build_sample_docx(), make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_best_score_unified_across_student_progress_and_group_journal_export(), test_check_files_exist_batch_handles_existing_missing_and_path_traversal() (+11 more)

### Community 17 - "submit_practical_work"
Cohesion: 0.17
Nodes (3): _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 22 - "change_password"
Cohesion: 0.12
Nodes (6): change_password(), _extract_client_ip(), login(), read_current_user(), refresh_tokens(), serialize_user()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.11
Nodes (35): App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps, resolvePageTitle() (+27 more)

### Community 25 - "admin.py"
Cohesion: 0.13
Nodes (11): create_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _ensure_group_list_number_unique(), _get_group_or_404(), _get_user_with_group_or_404(), _normalize_email(), _normalize_non_empty() (+3 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (44): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+36 more)

### Community 27 - "course.ts"
Cohesion: 0.07
Nodes (50): PracticalModuleContext, CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab (+42 more)

### Community 28 - "student_import_service.py"
Cohesion: 0.12
Nodes (9): format_size_limit_mb(), calculate_variant_index(), resolve_student_variant(), build_generated_email(), _encode_ukrainian_word(), normalize_full_name(), transliterate_ukrainian_slug(), ukrainian_sort_key() (+1 more)

### Community 29 - "AuthContext.tsx"
Cohesion: 0.11
Nodes (31): axios@^1.7.7, API_BASE_URL, apiClient, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken() (+23 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.06
Nodes (8): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader, test_excel_course_formula_rules_have_valid_supported_expressions(), test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_rejects_static_value_instead_of_formula_and_missing_chart()

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.22
Nodes (15): PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal() (+7 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.14
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.18
Nodes (15): buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps, PendingDraftState (+7 more)

### Community 35 - "student_import_service.py"
Cohesion: 0.10
Nodes (11): _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _infer_default_docx_columns(), _is_txt_header_line(), _normalize_header_token(), parse_txt_students() (+3 more)

### Community 36 - "Submission"
Cohesion: 0.10
Nodes (11): Submission, build_content_disposition(), _build_submission_download_names(), _check_files_exist_batch(), _is_submission_file_available(), _resolve_existing_submission_file(), _sanitize_ascii_token(), _sanitize_utf8_token() (+3 more)

### Community 38 - "submission_service.py"
Cohesion: 0.17
Nodes (8): require_role(), PlagiarismDetectedError, QuizAttempt, _enum_values(), User, UserRole, SubmissionRead, _ensure_utc()

### Community 39 - "HtmlGrader"
Cohesion: 0.05
Nodes (18): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), has_meaningful_html_body(), HtmlGrader, _is_doctype_target(), _node_has_visible_content(), _normalize_selector() (+10 more)

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.11
Nodes (25): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+17 more)

### Community 41 - "db_session"
Cohesion: 0.13
Nodes (5): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password()

### Community 42 - "build_group_journal"
Cohesion: 0.12
Nodes (8): CriterionErrorStat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, build_group_journal(), calculate_criterion_error_stats(), _normalize_utc_timestamp(), _RuleStatAccumulator

### Community 43 - "courses.py"
Cohesion: 0.07
Nodes (19): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+11 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.11
Nodes (33): renderInlineMarkdown(), AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, extractRetryAfterSeconds(), fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META (+25 more)

### Community 45 - "delete_admin_user"
Cohesion: 0.15
Nodes (5): create_admin_group(), delete_admin_group(), delete_admin_user(), list_admin_groups(), list_admin_users()

### Community 46 - "SlidingWindowRateLimiter"
Cohesion: 0.10
Nodes (3): build_login_rate_limit_key(), SlidingWindowRateLimiter, test_sliding_window_rate_limiter_expires_old_attempts()

### Community 47 - "grading.py"
Cohesion: 0.18
Nodes (5): GradingReport, GradingRulesUpdateRequest, PlagiarismCheckResult, HtmlSubmissionRequest, ManualGradeUpdateRequest

### Community 48 - "services/__init__.py"
Cohesion: 0.10
Nodes (15): ExportedDocument, GroupJournalBundle, format_cooldown_remaining(), cleanup_expired_submissions(), _delete_submission_file_paths_with_stats(), delete_submission_file_safely(), delete_submission_file_safely_async(), delete_submission_files_for_paths() (+7 more)

### Community 49 - "@tanstack/react-query"
Cohesion: 0.15
Nodes (12): dependencies, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient (+4 more)

### Community 50 - "reset_admin_user_password"
Cohesion: 0.22
Nodes (3): reset_admin_user_password(), hash_password_async(), generate_temp_password()

### Community 51 - "schemas/__init__.py"
Cohesion: 0.09
Nodes (19): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, AdminResetPasswordRequest, AdminResetPasswordResponse, ChangePasswordResponse, ErrorResponse (+11 more)

### Community 52 - "export_group_journal"
Cohesion: 0.23
Nodes (3): export_group_journal(), get_group_journal(), list_academic_groups()

### Community 57 - "DocxGrader"
Cohesion: 0.06
Nodes (3): DocxGrader, _format_number(), test_all_course_variants_resolve_rule_placeholders_without_leftovers()

### Community 59 - "render_group_journal_pdf"
Cohesion: 0.18
Nodes (5): _auto_adjust_worksheet_columns(), _configure_pdf_font(), PracticalColumnInfo, render_group_journal_pdf(), render_group_journal_xlsx()

### Community 61 - "Settings"
Cohesion: 0.22
Nodes (3): get_settings(), Settings, test_settings_production_rejects_default_or_short_jwt_secret()

### Community 62 - "list_my_submissions"
Cohesion: 0.16
Nodes (6): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade(), get_db()

### Community 66 - "GradingError"
Cohesion: 0.07
Nodes (7): GradingError, BaseGrader, GraderFactory, PracticalFormat, CriterionResult, GradingRuleType, test_grader_factory_resolves_all_four_formats()

### Community 68 - "main.py"
Cohesion: 0.17
Nodes (3): create_application(), lifespan(), run_periodic_retention_cleanup()

### Community 70 - "test_course_content.py"
Cohesion: 0.09
Nodes (21): Base, Course, CourseSlug, Module, Practical, QuizQuestion, AcademicGroup, build_seed_bundle() (+13 more)

### Community 72 - "test_auth_security.py"
Cohesion: 0.11
Nodes (13): hash_password(), _sha256_password_bytes(), verify_password(), verify_password_async(), _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_hash_and_verify_password_async_offload_to_worker_thread(), _recording_hash() (+5 more)

### Community 73 - ".export_group_journal"
Cohesion: 0.22
Nodes (3): _prepare_pdf_text(), _sanitize_filename_token(), _transliterate_to_ascii()

### Community 77 - "DocxGrader"
Cohesion: 0.11
Nodes (3): test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_docx_grader_resolves_placeholders_in_target_and_expected()

### Community 80 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 82 - "conftest.py"
Cohesion: 0.12
Nodes (6): downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade()

### Community 84 - "create_token_pair"
Cohesion: 0.26
Nodes (4): create_access_token(), create_refresh_token(), create_token_pair(), _encode_jwt_token()

### Community 88 - "rewrite_openxml_core_metadata"
Cohesion: 0.38
Nodes (3): build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 92 - "read_upload_file_limited"
Cohesion: 0.14
Nodes (7): _extract_submission_payload(), ExtractedSubmissionPayload, _build_too_large_exception(), read_upload_file_limited(), test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 867 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **69 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `submission_service.py` to `QuizService`, `get_current_user`, `conftest.py`, `SubmissionService`, `test_course_content.py`, `SqliteAsyncSessionAdapter`, `test_auth_security.py`, `_get_module_with_questions`, `build_group_journal`, `_get_user_by_email`, `ExportService`, `delete_admin_user`, `DomainError`, `_get_course_module_and_practical`, `.import_students`, `change_password`, `admin.py`, `student_import_service.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `User` (e.g. with `ensure_course_owner_or_admin()` and `get_current_user()`) actually correct?**
  _`User` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.08912655971479501 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `SubmissionService` to `QuizService`, `get_current_user`, `GradingError`, `main.py`, `submission_service.py`, `ExportService`, `delete_admin_user`, `DomainError`, `PlagiarismDetectedError`, `student_import_service.py`, `.import_students`, `change_password`, `admin.py`, `ExportFormat`, `read_upload_file_limited`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `DocxGrader` connect `DocxGrader` to `GradingError`, `AccdbGrader`, `test_course_content.py`, `metadata.py`, `DocxGrader`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._