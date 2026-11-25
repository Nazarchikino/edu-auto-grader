# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 96 files · ~268,898 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1917 nodes · 5212 edges · 117 communities (51 shown, 66 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 301 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ebe4b4fa`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QuizService
- postgres
- compilerOptions
- DocxDocument
- AccdbGrader
- SubmissionService
- _get_module_with_questions
- SqliteAsyncSessionAdapter
- MarkdownRenderer.tsx
- vite-env.d.ts
- User
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
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- GroupJournalPage.tsx
- accdb_grader.py
- HtmlSandbox.tsx
- student_import_service.py
- _build_submission_download_names
- submission_service.py
- HtmlGrader
- GradingReportCard.tsx
- db_session
- export_service.py
- courses.py
- ModuleViewPage.tsx
- CoursesPage.tsx
- SlidingWindowRateLimiter
- evaluate_plagiarism
- services/__init__.py
- @tanstack/react-query
- reset_admin_user_password
- schemas/__init__.py
- _find_tag_attr_key
- DocxGrader
- PlagiarismDetectedError
- test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress
- list_my_submissions
- GradingError
- main.py
- seed.py
- test_auth_security.py
- .evaluate
- ExportService
- DocxGrader
- do_run_migrations
- conftest.py
- create_token_pair
- test_read_upload_file_limited_stops_reading_chunks_early
- _compile_jsonb_for_sqlite
- _resolve_backend_path
- get_current_user
- _SeedQuizQuestionPayload
- _parse_text_match_expected
- .import_students

## God Nodes (most connected - your core abstractions)
1. `SqliteAsyncSessionAdapter` - 75 edges
2. `User` - 71 edges
3. `DomainError` - 67 edges
4. `make_auth_headers()` - 48 edges
5. `get_db()` - 45 edges
6. `DocxGrader` - 42 edges
7. `GradingError` - 42 edges
8. `InvalidFileFormatError` - 41 edges
9. `Module` - 39 edges
10. `GradingRule` - 39 edges

## Surprising Connections (you probably didn't know these)
- `_get_group_or_404()` --uses--> `AcademicGroup`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `_get_user_with_group_or_404()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `_ensure_group_code_unique()` --uses--> `AcademicGroup`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `_ensure_email_unique()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `_ensure_group_list_number_unique()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (117 total, 66 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.09
Nodes (6): _build_module_detail_read(), get_practical_for_student(), submit_module_quiz(), format_cooldown_remaining(), get_quiz_pass_threshold_percent(), QuizService

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
Cohesion: 0.08
Nodes (6): _check_files_exist_batch(), _is_submission_file_available(), _save_uploaded_file(), serialize_submission(), SubmissionService, _unlink_file_quietly()

### Community 6 - "_get_module_with_questions"
Cohesion: 0.14
Nodes (9): Settings, _build_answers_for_score(), _get_module_with_questions(), _get_user_by_email(), test_excel_q42_imported_in_module_8_with_media_and_dry_run(), test_quiz_cooldown_zero_disables_wait_and_negative_config_rejected(), test_quiz_pass_threshold_setting_controls_passed_flag(), test_quiz_retry_cooldown_blocks_immediate_retry_and_unlocks_after_window() (+1 more)

### Community 7 - "SqliteAsyncSessionAdapter"
Cohesion: 0.11
Nodes (12): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), test_seed_database_sync_courses_preserves_users_and_groups(), _get_user_by_email(), test_admin_duplicate_group_list_number_returns_409_and_allows_other_groups(), test_delete_module_renumbers_cleanly_under_unique_constraint_with_reverse_uuids(), test_quiz_questions_preserve_order_index_independently_of_uuids(), _create_other_teacher() (+4 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "User"
Cohesion: 0.06
Nodes (25): Course, Module, AcademicGroup, User, build_seed_bundle(), _load_course_from_json(), run_seed(), seed_database() (+17 more)

### Community 13 - "metadata.py"
Cohesion: 0.08
Nodes (17): compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), extract_core_xml_metadata(), extract_document_metadata(), _find_xml_text(), normalize_code_for_hashing() (+9 more)

### Community 14 - "DomainError"
Cohesion: 0.07
Nodes (26): ensure_course_owner_or_admin(), role_checker(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module(), delete_practical() (+18 more)

### Community 16 - "_get_course_module_and_practical"
Cohesion: 0.10
Nodes (21): HtmlSubmissionRequest, build_sample_docx(), make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_best_score_unified_across_student_progress_and_group_journal_export() (+13 more)

### Community 17 - "submit_practical_work"
Cohesion: 0.11
Nodes (6): _extract_client_ip(), _extract_submission_payload(), ExtractedSubmissionPayload, _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 22 - "change_password"
Cohesion: 0.14
Nodes (5): change_password(), login(), read_current_user(), refresh_tokens(), serialize_user()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.15
Nodes (28): App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps, resolvePageTitle() (+20 more)

### Community 25 - "admin.py"
Cohesion: 0.09
Nodes (17): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _ensure_group_list_number_unique(), _get_group_or_404() (+9 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.07
Nodes (41): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+33 more)

### Community 27 - "course.ts"
Cohesion: 0.07
Nodes (50): PracticalModuleContext, CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab (+42 more)

### Community 29 - "AuthContext.tsx"
Cohesion: 0.12
Nodes (28): axios@^1.7.7, API_BASE_URL, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken(), notifyAuthFailure() (+20 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.05
Nodes (11): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader, build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata() (+3 more)

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.16
Nodes (19): PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal() (+11 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.11
Nodes (7): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type(), _resolve_canonical_type(), GradingRuleType

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.18
Nodes (15): buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps, PendingDraftState (+7 more)

### Community 35 - "student_import_service.py"
Cohesion: 0.07
Nodes (19): _build_too_large_exception(), format_size_limit_mb(), build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _encode_ukrainian_word() (+11 more)

### Community 36 - "_build_submission_download_names"
Cohesion: 0.22
Nodes (5): build_content_disposition(), _build_submission_download_names(), _sanitize_ascii_token(), _sanitize_utf8_token(), _strip_apostrophes()

### Community 38 - "submission_service.py"
Cohesion: 0.12
Nodes (8): require_role(), get_settings(), decode_token(), verify_password_async(), _enum_values(), UserRole, ManualGradeUpdateRequest, SubmissionRead

### Community 39 - "HtmlGrader"
Cohesion: 0.13
Nodes (4): _attribute_value_matches(), _is_doctype_target(), _normalize_selector(), _normalize_text()

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.11
Nodes (24): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+16 more)

### Community 41 - "db_session"
Cohesion: 0.15
Nodes (4): async_client(), _create_sqlite_test_engine(), db_session(), _fast_seed_hash_password()

### Community 42 - "export_service.py"
Cohesion: 0.06
Nodes (20): _parse_export_format(), CriterionErrorStat, ExportFormat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, _auto_adjust_worksheet_columns(), build_group_journal() (+12 more)

### Community 43 - "courses.py"
Cohesion: 0.08
Nodes (24): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+16 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.10
Nodes (33): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, extractRetryAfterSeconds(), fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta (+25 more)

### Community 45 - "CoursesPage.tsx"
Cohesion: 0.24
Nodes (9): apiClient, COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS (+1 more)

### Community 47 - "evaluate_plagiarism"
Cohesion: 0.12
Nodes (6): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), SubmissionRecordProtocol, GradingRulesUpdateRequest, PlagiarismCheckResult

### Community 48 - "services/__init__.py"
Cohesion: 0.12
Nodes (14): cleanup_expired_submissions(), _delete_submission_file_paths_with_stats(), delete_submission_file_safely(), delete_submission_file_safely_async(), delete_submission_files_for_paths(), delete_submission_files_for_paths_async(), _inspect_submission_file_paths(), main() (+6 more)

### Community 49 - "@tanstack/react-query"
Cohesion: 0.15
Nodes (12): dependencies, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient (+4 more)

### Community 51 - "schemas/__init__.py"
Cohesion: 0.07
Nodes (20): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, AdminResetPasswordRequest, AdminResetPasswordResponse, ChangePasswordRequest, ChangePasswordResponse (+12 more)

### Community 52 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 61 - "test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress"
Cohesion: 0.15
Nodes (11): QuizAttempt, Submission, _copy_course_content_dir(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found(), test_delete_module_by_teacher_and_admin_cascades_cleans_files_and_renumbers(), test_delete_practical_preserves_module_lecture_quiz_and_cleans_files(), test_full_course_json_bundle_validation() (+3 more)

### Community 62 - "list_my_submissions"
Cohesion: 0.18
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 66 - "GradingError"
Cohesion: 0.08
Nodes (10): GradingError, InvalidFileFormatError, BaseGrader, GraderFactory, has_meaningful_html_body(), _node_has_visible_content(), parse_html_document(), PracticalFormat (+2 more)

### Community 70 - "seed.py"
Cohesion: 0.09
Nodes (12): Base, CourseSlug, _enum_values(), Practical, QuizQuestion, main(), _question_signature(), _SeedCoursePayload (+4 more)

### Community 72 - "test_auth_security.py"
Cohesion: 0.11
Nodes (13): hash_password(), _sha256_password_bytes(), verify_password(), _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_hash_and_verify_password_async_offload_to_worker_thread(), _recording_hash(), _recording_verify() (+5 more)

### Community 73 - ".evaluate"
Cohesion: 0.10
Nodes (7): HtmlGrader, test_minimal_html_starter_template_scores_zero_across_all_html_course_modules(), test_grader_factory_resolves_all_four_formats(), test_html_grader_attribute_filter_selector_and_compound_colspan(), test_html_grader_detects_missing_tags_and_rejects_empty_code(), test_html_grader_empty_body_and_starter_template_score_zero(), test_html_grader_evaluates_semantic_dom_structure_and_attributes()

### Community 76 - "ExportService"
Cohesion: 0.09
Nodes (4): export_group_journal(), get_group_journal(), list_academic_groups(), ExportService

### Community 77 - "DocxGrader"
Cohesion: 0.12
Nodes (3): test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_docx_grader_resolves_placeholders_in_target_and_expected()

### Community 80 - "do_run_migrations"
Cohesion: 0.18
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 82 - "conftest.py"
Cohesion: 0.06
Nodes (7): downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade(), build_login_rate_limit_key()

### Community 84 - "create_token_pair"
Cohesion: 0.29
Nodes (4): create_access_token(), create_refresh_token(), create_token_pair(), _encode_jwt_token()

### Community 92 - "test_read_upload_file_limited_stops_reading_chunks_early"
Cohesion: 0.29
Nodes (4): read_upload_file_limited(), test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 866 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **66 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `QuizService`, `get_current_user`, `student_import_service.py`, `SubmissionService`, `submission_service.py`, `seed.py`, `test_auth_security.py`, `SqliteAsyncSessionAdapter`, `export_service.py`, `courses.py`, `ExportService`, `_get_module_with_questions`, `DomainError`, `_get_course_module_and_practical`, `.import_students`, `change_password`, `admin.py`, `test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `User` (e.g. with `ensure_course_owner_or_admin()` and `get_current_user()`) actually correct?**
  _`User` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.08912655971479501 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `DomainError` to `QuizService`, `get_current_user`, `GradingError`, `student_import_service.py`, `main.py`, `SubmissionService`, `submission_service.py`, `export_service.py`, `courses.py`, `ExportService`, `submit_practical_work`, `.import_students`, `change_password`, `admin.py`, `PlagiarismDetectedError`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `XlsxGrader` connect `XlsxGrader` to `GradingError`, `test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress`, `AccdbGrader`, `metadata.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._