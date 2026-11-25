# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 93 files · ~262,853 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1803 nodes · 4872 edges · 122 communities (50 shown, 72 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 246 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `26eee8bc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- quiz_service.py
- postgres
- compilerOptions
- AccdbGrader
- SubmissionService
- test_graders.py
- SqliteAsyncSessionAdapter
- MarkdownRenderer.tsx
- vite-env.d.ts
- make_auth_headers
- metadata.py
- courses.py
- _get_course_module_and_practical
- submit_practical_work
- edu-auto-grader-backend
- test_auth_security.py
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- export_group_journal
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
- HtmlGrader
- GradingReportCard.tsx
- db_session
- submission_service.py
- ModuleViewPage.tsx
- conftest.py
- SlidingWindowRateLimiter
- evaluate_plagiarism
- services/__init__.py
- @tanstack/react-query
- DomainError
- _find_tag_attr_key
- _is_submission_file_available
- schemas/__init__.py
- test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress
- list_my_submissions
- ExportService
- test_all_course_variants_resolve_rule_placeholders_without_leftovers
- .update_grading_rules
- .import_students
- User
- test_submissions_api.py
- collections_abc
- test_change_password_validation_and_imported_student_flag
- DocxGrader
- do_run_migrations
- submission_service.py
- test_course_teacher_reassignment_forbidden_for_owner_and_allowed_for_admin
- test_read_upload_file_limited_stops_reading_chunks_early
- _compile_jsonb_for_sqlite
- _format_number
- BaseModel
- SubmissionDownloadPayload

## God Nodes (most connected - your core abstractions)
1. `User` - 66 edges
2. `DomainError` - 64 edges
3. `SqliteAsyncSessionAdapter` - 61 edges
4. `get_db()` - 45 edges
5. `GradingError` - 42 edges
6. `InvalidFileFormatError` - 42 edges
7. `DocxGrader` - 42 edges
8. `make_auth_headers()` - 39 edges
9. `GradingRule` - 39 edges
10. `UserRole` - 38 edges

## Surprising Connections (you probably didn't know these)
- `get_current_user()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `require_role()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `ensure_course_owner_or_admin()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `ensure_course_owner_or_admin()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `_get_group_or_404()` --uses--> `AcademicGroup`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (122 total, 72 thin omitted)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 4 - "AccdbGrader"
Cohesion: 0.06
Nodes (15): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _strip_identifiers(), GradingRule (+7 more)

### Community 6 - "test_graders.py"
Cohesion: 0.08
Nodes (9): GradingError, BaseGrader, GraderFactory, PracticalFormat, CriterionResult, GradingReport, GradingRuleType, PlagiarismCheckResult (+1 more)

### Community 7 - "SqliteAsyncSessionAdapter"
Cohesion: 0.23
Nodes (3): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), test_seed_database_sync_courses_preserves_users_and_groups()

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.13
Nodes (30): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+22 more)

### Community 11 - "make_auth_headers"
Cohesion: 0.12
Nodes (12): make_auth_headers(), _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates() (+4 more)

### Community 13 - "metadata.py"
Cohesion: 0.10
Nodes (16): InvalidFileFormatError, compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), extract_core_xml_metadata(), extract_document_metadata(), _find_xml_text() (+8 more)

### Community 14 - "courses.py"
Cohesion: 0.08
Nodes (17): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+9 more)

### Community 16 - "_get_course_module_and_practical"
Cohesion: 0.12
Nodes (15): _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_best_score_unified_across_student_progress_and_group_journal_export(), test_download_submissions_by_course_teacher_and_admin_with_headers_and_content(), test_health_check_and_jwt_login_flow(), test_retention_cleanup_purges_expired_files_keeps_grades_and_ignores_fresh() (+7 more)

### Community 17 - "submit_practical_work"
Cohesion: 0.17
Nodes (3): _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 22 - "test_auth_security.py"
Cohesion: 0.11
Nodes (8): change_password(), _extract_client_ip(), login(), build_login_rate_limit_key(), hash_password(), _sha256_password_bytes(), verify_password(), test_password_hashing_supports_long_cyrillic_and_legacy_bcrypt_hashes()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (41): @monaco-editor/react@4.6.0, devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0 (+33 more)

### Community 24 - "App.tsx"
Cohesion: 0.15
Nodes (28): App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps, resolvePageTitle() (+20 more)

### Community 25 - "admin.py"
Cohesion: 0.09
Nodes (21): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404(), _get_user_with_group_or_404() (+13 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (45): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+37 more)

### Community 27 - "course.ts"
Cohesion: 0.07
Nodes (50): PracticalModuleContext, CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab (+42 more)

### Community 28 - "export_group_journal"
Cohesion: 0.13
Nodes (5): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), ExportFormat

### Community 29 - "AuthContext.tsx"
Cohesion: 0.12
Nodes (28): axios@^1.7.7, API_BASE_URL, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken(), notifyAuthFailure() (+20 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.05
Nodes (11): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader, build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata() (+3 more)

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.13
Nodes (24): apiClient, PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses() (+16 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.13
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.18
Nodes (15): buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps, PendingDraftState (+7 more)

### Community 35 - "student_import_service.py"
Cohesion: 0.07
Nodes (20): build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _encode_ukrainian_word(), generate_temp_password(), _get_cell_value() (+12 more)

### Community 36 - "Settings"
Cohesion: 0.12
Nodes (4): get_settings(), _resolve_backend_path(), Settings, test_settings_production_rejects_default_or_short_jwt_secret()

### Community 37 - "courses.py"
Cohesion: 0.06
Nodes (30): ensure_course_owner_or_admin(), get_current_user(), _build_module_detail_read(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module() (+22 more)

### Community 38 - "_build_submission_download_names"
Cohesion: 0.29
Nodes (4): _build_submission_download_names(), _sanitize_ascii_token(), _sanitize_utf8_token(), _strip_apostrophes()

### Community 39 - "HtmlGrader"
Cohesion: 0.06
Nodes (15): _attribute_value_matches(), has_meaningful_html_body(), HtmlGrader, _is_doctype_target(), _node_has_visible_content(), _normalize_selector(), _normalize_text(), parse_html_document() (+7 more)

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.11
Nodes (24): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+16 more)

### Community 41 - "db_session"
Cohesion: 0.15
Nodes (4): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session()

### Community 43 - "submission_service.py"
Cohesion: 0.07
Nodes (17): CriterionErrorStat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest, _auto_adjust_worksheet_columns(), build_group_journal(), calculate_criterion_error_stats() (+9 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.11
Nodes (30): renderInlineMarkdown(), AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta (+22 more)

### Community 47 - "evaluate_plagiarism"
Cohesion: 0.17
Nodes (4): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), SubmissionRecordProtocol

### Community 48 - "services/__init__.py"
Cohesion: 0.13
Nodes (10): build_content_disposition(), ExportedDocument, GroupJournalBundle, cleanup_expired_submissions(), delete_submission_file_safely(), delete_submission_files_for_paths(), resolve_submission_file_path(), RetentionCleanupSummary (+2 more)

### Community 49 - "@tanstack/react-query"
Cohesion: 0.18
Nodes (10): dependencies, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient, rootElement (+2 more)

### Community 51 - "DomainError"
Cohesion: 0.11
Nodes (14): require_role(), role_checker(), refresh_tokens(), DomainError, PlagiarismDetectedError, create_access_token(), create_refresh_token(), create_token_pair() (+6 more)

### Community 52 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 60 - "schemas/__init__.py"
Cohesion: 0.10
Nodes (15): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, ChangePasswordRequest, ErrorResponse, ImportedStudentItem, ImportSkippedItem (+7 more)

### Community 61 - "test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress"
Cohesion: 0.12
Nodes (12): build_sample_docx(), _copy_course_content_dir(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found(), test_delete_module_by_teacher_and_admin_cascades_cleans_files_and_renumbers(), test_delete_practical_preserves_module_lecture_quiz_and_cleans_files(), test_media_courses_static_serving(), test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress() (+4 more)

### Community 62 - "list_my_submissions"
Cohesion: 0.18
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 67 - "User"
Cohesion: 0.08
Nodes (22): Base, Course, Module, Practical, QuizQuestion, AcademicGroup, User, build_seed_bundle() (+14 more)

### Community 68 - "test_submissions_api.py"
Cohesion: 0.08
Nodes (9): _extract_submission_payload(), ExtractedSubmissionPayload, _build_too_large_exception(), format_size_limit_mb(), read_upload_file_limited(), create_application(), lifespan(), GradingRulesUpdateRequest (+1 more)

### Community 71 - "collections_abc"
Cohesion: 0.17
Nodes (4): downgrade(), upgrade(), downgrade(), upgrade()

### Community 72 - "test_change_password_validation_and_imported_student_flag"
Cohesion: 0.20
Nodes (5): _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_login_rate_limiting_blocks_after_n_failures_and_resets_on_success(), test_long_cyrillic_password_create_login_and_change_without_500(), test_token_version_revokes_tokens_on_admin_reset_and_self_change()

### Community 77 - "DocxGrader"
Cohesion: 0.20
Nodes (4): DocxGrader, test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_docx_grader_resolves_placeholders_in_target_and_expected()

### Community 80 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 82 - "submission_service.py"
Cohesion: 0.16
Nodes (7): CourseSlug, _enum_values(), QuizAttempt, Submission, PracticalVariant, calculate_variant_index(), resolve_student_variant()

### Community 87 - "test_course_teacher_reassignment_forbidden_for_owner_and_allowed_for_admin"
Cohesion: 0.29
Nodes (3): _get_user_by_email(), test_course_teacher_reassignment_forbidden_for_owner_and_allowed_for_admin(), test_duplicate_root_auth_router_removed_returns_404()

### Community 92 - "test_read_upload_file_limited_stops_reading_chunks_early"
Cohesion: 0.50
Nodes (3): test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 99 - "BaseModel"
Cohesion: 0.18
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 811 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **72 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `AccdbGrader` to `accdb_grader.py`, `User`, `courses.py`, `test_graders.py`, `HtmlGrader`, `metadata.py`, `courses.py`, `DocxGrader`, `submission_service.py`, `._evaluate_html_submission`, `schemas/__init__.py`, `XlsxGrader`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `User` (e.g. with `ensure_course_owner_or_admin()` and `get_current_user()`) actually correct?**
  _`User` has 19 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `quiz_service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14736842105263157 - nodes in this community are weakly interconnected._
- **Why does `User` connect `User` to `quiz_service.py`, `SubmissionService`, `SqliteAsyncSessionAdapter`, `make_auth_headers`, `_get_course_module_and_practical`, `test_auth_security.py`, `admin.py`, `student_import_service.py`, `courses.py`, `submission_service.py`, `DomainError`, `test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress`, `ExportService`, `.update_grading_rules`, `.import_students`, `test_submissions_api.py`, `test_change_password_validation_and_imported_student_flag`, `submission_service.py`, `test_course_teacher_reassignment_forbidden_for_owner_and_allowed_for_admin`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `DomainError` (e.g. with `delete_admin_user()` and `update_admin_user()`) actually correct?**
  _`DomainError` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._