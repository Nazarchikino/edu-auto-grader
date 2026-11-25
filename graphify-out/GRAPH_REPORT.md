# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 94 files · ~266,406 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1884 nodes · 5037 edges · 130 communities (63 shown, 67 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 197 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1c9cc5b1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QuizService
- postgres
- compilerOptions
- DocxDocument
- AccdbGrader
- serialize_submission
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
- change_password
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- .export_group_journal
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- GroupJournalPage.tsx
- accdb_grader.py
- HtmlSandbox.tsx
- student_import_service.py
- Settings
- upsert_module_practical
- User
- HtmlGrader
- GradingReportCard.tsx
- db_session
- submission_service.py
- courses.py
- ModuleViewPage.tsx
- UUID
- SlidingWindowRateLimiter
- evaluate_plagiarism
- services/__init__.py
- @tanstack/react-query
- schemas/__init__.py
- _find_tag_attr_key
- DocxGrader
- SubmissionService
- DomainError
- test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress
- list_my_submissions
- export_group_journal
- test_all_course_variants_resolve_rule_placeholders_without_leftovers
- .update_grading_rules
- GradingError
- test_course_content.py
- main.py
- models/course.py
- 0001_initial_schema.py
- test_auth_security.py
- .evaluate
- ExportService
- DocxGrader
- .execute
- do_run_migrations
- test_submissions_api.py
- v1/auth.py
- create_token_pair
- AsyncSession
- _get_user_by_email
- .submit_practical
- test_read_upload_file_limited_stops_reading_chunks_early
- env.py
- _compile_jsonb_for_sqlite
- 0003_add_user_auth_security_fields.py
- _resolve_backend_path
- get_current_user
- _SeedQuizQuestionPayload
- decode_token
- get_db
- _parse_text_match_expected
- ChangePasswordRequest
- GroupJournalBundle
- .import_students
- create_quiz_question

## God Nodes (most connected - your core abstractions)
1. `SqliteAsyncSessionAdapter` - 69 edges
2. `DomainError` - 62 edges
3. `User` - 59 edges
4. `get_db()` - 45 edges
5. `make_auth_headers()` - 44 edges
6. `GradingError` - 42 edges
7. `DocxGrader` - 42 edges
8. `InvalidFileFormatError` - 41 edges
9. `GradingRule` - 39 edges
10. `XlsxGrader` - 32 edges

## Surprising Connections (you probably didn't know these)
- `import_admin_students()` --uses--> `StudentImportService`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/services/student_import_service.py
- `export_group_journal()` --uses--> `ExportService`  [INFERRED]
  backend/app/api/v1/analytics.py → backend/app/services/export_service.py
- `get_group_journal()` --uses--> `ExportService`  [INFERRED]
  backend/app/api/v1/analytics.py → backend/app/services/export_service.py
- `list_academic_groups()` --uses--> `ExportService`  [INFERRED]
  backend/app/api/v1/analytics.py → backend/app/services/export_service.py
- `submit_practical_work()` --uses--> `SubmissionService`  [INFERRED]
  backend/app/api/v1/practicals.py → backend/app/services/submission_service.py

## Import Cycles
- None detected.

## Communities (130 total, 67 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.14
Nodes (4): PracticalStudentRead, format_cooldown_remaining(), get_quiz_pass_threshold_percent(), QuizService

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 4 - "AccdbGrader"
Cohesion: 0.06
Nodes (15): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _strip_identifiers(), GradingRule (+7 more)

### Community 5 - "serialize_submission"
Cohesion: 0.16
Nodes (3): _is_submission_file_available(), _save_uploaded_file(), serialize_submission()

### Community 6 - "_get_module_with_questions"
Cohesion: 0.17
Nodes (8): _build_answers_for_score(), _get_module_with_questions(), _get_user_by_email(), test_excel_q42_imported_in_module_8_with_media_and_dry_run(), test_quiz_cooldown_zero_disables_wait_and_negative_config_rejected(), test_quiz_pass_threshold_setting_controls_passed_flag(), test_quiz_retry_cooldown_blocks_immediate_retry_and_unlocks_after_window(), test_quiz_submit_rejects_incomplete_duplicate_foreign_and_invalid_answers()

### Community 7 - "SqliteAsyncSessionAdapter"
Cohesion: 0.21
Nodes (3): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), test_seed_database_sync_courses_preserves_users_and_groups()

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.13
Nodes (30): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+22 more)

### Community 11 - "make_auth_headers"
Cohesion: 0.11
Nodes (13): calculate_variant_index(), make_auth_headers(), _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb() (+5 more)

### Community 13 - "metadata.py"
Cohesion: 0.10
Nodes (16): InvalidFileFormatError, compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), extract_core_xml_metadata(), extract_document_metadata(), _find_xml_text() (+8 more)

### Community 14 - "courses.py"
Cohesion: 0.18
Nodes (7): create_course(), _fetch_user_progress_maps(), get_course(), list_courses(), _load_course_or_404(), _serialize_course(), update_course()

### Community 16 - "_get_course_module_and_practical"
Cohesion: 0.12
Nodes (15): _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_best_score_unified_across_student_progress_and_group_journal_export(), test_download_submissions_by_course_teacher_and_admin_with_headers_and_content(), test_health_check_and_jwt_login_flow(), test_retention_cleanup_purges_expired_files_keeps_grades_and_ignores_fresh() (+7 more)

### Community 17 - "submit_practical_work"
Cohesion: 0.17
Nodes (3): _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 22 - "change_password"
Cohesion: 0.16
Nodes (4): change_password(), _extract_client_ip(), login(), refresh_tokens()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.11
Nodes (35): App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps, resolvePageTitle() (+27 more)

### Community 25 - "admin.py"
Cohesion: 0.07
Nodes (17): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404(), _get_user_with_group_or_404() (+9 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (44): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+36 more)

### Community 27 - "course.ts"
Cohesion: 0.07
Nodes (50): PracticalModuleContext, CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab (+42 more)

### Community 28 - ".export_group_journal"
Cohesion: 0.11
Nodes (8): _configure_pdf_font(), ExportedDocument, PracticalColumnInfo, _prepare_pdf_text(), render_group_journal_pdf(), render_group_journal_xlsx(), _sanitize_filename_token(), _transliterate_to_ascii()

### Community 29 - "AuthContext.tsx"
Cohesion: 0.11
Nodes (31): axios@^1.7.7, API_BASE_URL, apiClient, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken() (+23 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.05
Nodes (12): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader, _auto_adjust_worksheet_columns(), build_sample_xlsx(), _replace_zip_member() (+4 more)

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
Cohesion: 0.08
Nodes (19): build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _encode_ukrainian_word(), _get_cell_value(), _infer_default_docx_columns() (+11 more)

### Community 36 - "Settings"
Cohesion: 0.22
Nodes (3): get_settings(), Settings, test_settings_production_rejects_default_or_short_jwt_secret()

### Community 37 - "upsert_module_practical"
Cohesion: 0.19
Nodes (4): get_practical_for_teacher(), _serialize_practical_teacher(), update_practical(), upsert_module_practical()

### Community 38 - "User"
Cohesion: 0.21
Nodes (5): require_role(), read_upload_file_limited(), _enum_values(), User, UserRole

### Community 39 - "HtmlGrader"
Cohesion: 0.13
Nodes (5): _attribute_value_matches(), HtmlGrader, _is_doctype_target(), _normalize_selector(), _normalize_text()

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.11
Nodes (25): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+17 more)

### Community 41 - "db_session"
Cohesion: 0.15
Nodes (4): async_client(), _create_sqlite_test_engine(), db_session(), _fast_seed_hash_password()

### Community 42 - "submission_service.py"
Cohesion: 0.06
Nodes (20): CourseSlug, _enum_values(), Submission, CriterionErrorStat, ExportFormat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell (+12 more)

### Community 43 - "courses.py"
Cohesion: 0.09
Nodes (19): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+11 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.11
Nodes (33): renderInlineMarkdown(), AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, extractRetryAfterSeconds(), fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META (+25 more)

### Community 45 - "UUID"
Cohesion: 0.24
Nodes (5): ensure_course_owner_or_admin(), _collect_practical_submission_file_paths(), delete_module(), delete_practical(), delete_quiz_question()

### Community 47 - "evaluate_plagiarism"
Cohesion: 0.17
Nodes (4): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), SubmissionRecordProtocol

### Community 48 - "services/__init__.py"
Cohesion: 0.13
Nodes (11): cleanup_expired_submissions(), _delete_submission_file_paths_with_stats(), delete_submission_file_safely(), delete_submission_file_safely_async(), delete_submission_files_for_paths(), delete_submission_files_for_paths_async(), _inspect_submission_file_paths(), resolve_submission_file_path() (+3 more)

### Community 49 - "@tanstack/react-query"
Cohesion: 0.15
Nodes (12): dependencies, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient (+4 more)

### Community 51 - "schemas/__init__.py"
Cohesion: 0.11
Nodes (16): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, AdminResetPasswordRequest, AdminResetPasswordResponse, ErrorResponse, ImportedStudentItem (+8 more)

### Community 52 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 60 - "DomainError"
Cohesion: 0.15
Nodes (6): role_checker(), _extract_submission_payload(), ExtractedSubmissionPayload, DomainError, PlagiarismDetectedError, QuizNotPassedError

### Community 61 - "test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress"
Cohesion: 0.15
Nodes (10): build_sample_docx(), _copy_course_content_dir(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found(), test_delete_module_by_teacher_and_admin_cascades_cleans_files_and_renumbers(), test_delete_practical_preserves_module_lecture_quiz_and_cleans_files(), test_media_courses_static_serving(), test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress() (+2 more)

### Community 62 - "list_my_submissions"
Cohesion: 0.18
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 63 - "export_group_journal"
Cohesion: 0.15
Nodes (4): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format()

### Community 66 - "GradingError"
Cohesion: 0.07
Nodes (10): GradingError, BaseGrader, GraderFactory, PracticalFormat, CriterionResult, GradingReport, GradingRulesUpdateRequest, GradingRuleType (+2 more)

### Community 67 - "test_course_content.py"
Cohesion: 0.10
Nodes (14): AcademicGroup, build_seed_bundle(), _load_course_from_json(), main(), run_seed(), seed_database(), SeedBundle, _SeedCoursePayload (+6 more)

### Community 68 - "main.py"
Cohesion: 0.14
Nodes (4): create_application(), lifespan(), run_periodic_retention_cleanup(), test_lifespan_starts_and_cancels_retention_background_task()

### Community 70 - "models/course.py"
Cohesion: 0.15
Nodes (10): Base, Course, Module, Practical, QuizQuestion, _question_signature(), _sync_course_in_place(), _sync_practical_in_place() (+2 more)

### Community 72 - "test_auth_security.py"
Cohesion: 0.12
Nodes (10): hash_password(), hash_password_async(), _sha256_password_bytes(), verify_password(), verify_password_async(), test_hash_and_verify_password_async_offload_to_worker_thread(), _recording_hash(), _recording_verify() (+2 more)

### Community 73 - ".evaluate"
Cohesion: 0.10
Nodes (8): has_meaningful_html_body(), _node_has_visible_content(), parse_html_document(), test_minimal_html_starter_template_scores_zero_across_all_html_course_modules(), test_html_grader_attribute_filter_selector_and_compound_colspan(), test_html_grader_detects_missing_tags_and_rejects_empty_code(), test_html_grader_empty_body_and_starter_template_score_zero(), test_html_grader_evaluates_semantic_dom_structure_and_attributes()

### Community 77 - "DocxGrader"
Cohesion: 0.18
Nodes (3): test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_docx_grader_resolves_placeholders_in_target_and_expected()

### Community 78 - ".execute"
Cohesion: 0.16
Nodes (6): _set_sqlite_pragma(), _create_other_teacher(), _get_user_by_email(), test_course_teacher_reassignment_forbidden_for_owner_and_allowed_for_admin(), test_cross_teacher_bola_blocked_across_all_course_and_submission_endpoints(), test_duplicate_root_auth_router_removed_returns_404()

### Community 80 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 82 - "test_submissions_api.py"
Cohesion: 0.12
Nodes (3): QuizAttempt, _check_files_exist_batch(), test_check_files_exist_batch_handles_existing_missing_and_path_traversal()

### Community 83 - "v1/auth.py"
Cohesion: 0.17
Nodes (6): read_current_user(), serialize_user(), build_login_rate_limit_key(), ChangePasswordResponse, TokenResponse, UserRead

### Community 84 - "create_token_pair"
Cohesion: 0.29
Nodes (4): create_access_token(), create_refresh_token(), create_token_pair(), _encode_jwt_token()

### Community 87 - "AsyncSession"
Cohesion: 0.24
Nodes (5): _build_module_detail_read(), create_module(), get_module(), _load_module_or_404(), update_module()

### Community 88 - "_get_user_by_email"
Cohesion: 0.28
Nodes (4): _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_long_cyrillic_password_create_login_and_change_without_500(), test_token_version_revokes_tokens_on_admin_reset_and_self_change()

### Community 92 - "test_read_upload_file_limited_stops_reading_chunks_early"
Cohesion: 0.50
Nodes (3): test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 101 - "get_db"
Cohesion: 0.20
Nodes (3): get_practical_for_student(), submit_module_quiz(), get_db()

### Community 114 - ".import_students"
Cohesion: 0.14
Nodes (3): _build_too_large_exception(), format_size_limit_mb(), StudentImportService

### Community 116 - "create_quiz_question"
Cohesion: 0.29
Nodes (3): create_quiz_question(), list_module_quiz_questions_teacher(), QuizQuestionTeacherRead

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 844 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **67 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `QuizService`, `serialize_submission`, `_get_module_with_questions`, `SqliteAsyncSessionAdapter`, `make_auth_headers`, `courses.py`, `_get_course_module_and_practical`, `change_password`, `admin.py`, `student_import_service.py`, `submission_service.py`, `courses.py`, `UUID`, `SubmissionService`, `test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress`, `.update_grading_rules`, `test_course_content.py`, `models/course.py`, `test_auth_security.py`, `ExportService`, `.execute`, `test_submissions_api.py`, `v1/auth.py`, `AsyncSession`, `_get_user_by_email`, `.submit_practical`, `get_current_user`, `.import_students`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `User` (e.g. with `ensure_course_owner_or_admin()` and `get_current_user()`) actually correct?**
  _`User` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.1383399209486166 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `DomainError` to `QuizService`, `serialize_submission`, `courses.py`, `change_password`, `admin.py`, `student_import_service.py`, `upsert_module_practical`, `User`, `submission_service.py`, `courses.py`, `UUID`, `SubmissionService`, `export_group_journal`, `.update_grading_rules`, `GradingError`, `main.py`, `ExportService`, `v1/auth.py`, `AsyncSession`, `.submit_practical`, `get_current_user`, `decode_token`, `.import_students`, `create_quiz_question`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `GradingError` connect `GradingError` to `test_all_course_variants_resolve_rule_placeholders_without_leftovers`, `accdb_grader.py`, `DocxDocument`, `AccdbGrader`, `HtmlGrader`, `submission_service.py`, `metadata.py`, `.submit_practical`, `DomainError`, `XlsxGrader`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._