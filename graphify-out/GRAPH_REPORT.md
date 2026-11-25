# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 89 files · ~258,997 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1729 nodes · 4663 edges · 109 communities (53 shown, 56 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 180 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f6e6f530`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- quiz_service.py
- postgres
- compilerOptions
- DocxGrader
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
- get_current_user
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
- AsyncSession
- _build_submission_download_names
- HtmlGrader
- GradingReportCard.tsx
- db_session
- submission_service.py
- ModuleViewPage.tsx
- get_db
- .export_group_journal
- summarize_bundle
- services/__init__.py
- @tanstack/react-query
- build_sample_docx
- security.py
- _find_tag_attr_key
- render_group_journal_pdf
- _is_submission_file_available
- student_import_service.py
- test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress
- list_my_submissions
- ExportService
- create_module
- .update_grading_rules
- .import_students
- submission_service.py
- main.py
- build_seed_bundle
- do_run_migrations
- _enum_values
- read_upload_file_limited
- _compile_jsonb_for_sqlite
- ExportFormat
- PlagiarismDetectedError
- get_db
- _SeedCoursePayload

## God Nodes (most connected - your core abstractions)
1. `DomainError` - 61 edges
2. `User` - 57 edges
3. `SqliteAsyncSessionAdapter` - 56 edges
4. `get_db()` - 43 edges
5. `GradingError` - 42 edges
6. `DocxGrader` - 42 edges
7. `InvalidFileFormatError` - 41 edges
8. `GradingRule` - 39 edges
9. `make_auth_headers()` - 35 edges
10. `XlsxGrader` - 32 edges

## Surprising Connections (you probably didn't know these)
- `AccdbGrader` --uses--> `GradingError`  [INFERRED]
  backend/app/graders/accdb_grader.py → backend/app/core/exceptions.py
- `AccdbGrader` --uses--> `InvalidFileFormatError`  [INFERRED]
  backend/app/graders/accdb_grader.py → backend/app/core/exceptions.py
- `BaseGrader` --uses--> `InvalidFileFormatError`  [INFERRED]
  backend/app/graders/base.py → backend/app/core/exceptions.py
- `GraderFactory` --uses--> `InvalidFileFormatError`  [INFERRED]
  backend/app/graders/factory.py → backend/app/core/exceptions.py
- `QuizService` --uses--> `PracticalStudentRead`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/schemas/course.py

## Import Cycles
- None detected.

## Communities (109 total, 56 thin omitted)

### Community 0 - "quiz_service.py"
Cohesion: 0.15
Nodes (4): QuizNotPassedError, calculate_variant_index(), QuizService, resolve_student_variant()

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
Cohesion: 0.06
Nodes (16): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _strip_identifiers(), GradingRule (+8 more)

### Community 6 - "test_graders.py"
Cohesion: 0.07
Nodes (8): GradingError, BaseGrader, GraderFactory, PracticalFormat, CriterionResult, GradingReport, GradingRuleType, PlagiarismCheckResult

### Community 7 - "SqliteAsyncSessionAdapter"
Cohesion: 0.16
Nodes (4): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), _get_user_by_email(), test_course_teacher_reassignment_forbidden_for_owner_and_allowed_for_admin()

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "make_auth_headers"
Cohesion: 0.11
Nodes (12): make_auth_headers(), _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates() (+4 more)

### Community 13 - "metadata.py"
Cohesion: 0.07
Nodes (22): InvalidFileFormatError, check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism() (+14 more)

### Community 14 - "courses.py"
Cohesion: 0.09
Nodes (23): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+15 more)

### Community 16 - "_get_course_module_and_practical"
Cohesion: 0.12
Nodes (15): _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_best_score_unified_across_student_progress_and_group_journal_export(), test_download_submission_forbidden_for_other_teacher_and_students(), test_download_submissions_by_course_teacher_and_admin_with_headers_and_content(), test_health_check_and_jwt_login_flow() (+7 more)

### Community 17 - "submit_practical_work"
Cohesion: 0.13
Nodes (5): _extract_submission_payload(), ExtractedSubmissionPayload, _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.11
Nodes (35): App(), ProtectedAppLayout(), RoleHomeRedirect(), PlagiarismBadgeProps, Navbar(), NavbarProps, resolvePageTitle(), ROLE_BADGE_CONFIG (+27 more)

### Community 25 - "admin.py"
Cohesion: 0.09
Nodes (16): role_checker(), create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404() (+8 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.07
Nodes (44): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+36 more)

### Community 27 - "course.ts"
Cohesion: 0.10
Nodes (33): CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses() (+25 more)

### Community 28 - "export_group_journal"
Cohesion: 0.19
Nodes (3): export_group_journal(), get_group_journal(), list_academic_groups()

### Community 29 - "AuthContext.tsx"
Cohesion: 0.13
Nodes (26): axios@^1.7.7, API_BASE_URL, apiClient, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken() (+18 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.06
Nodes (7): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader, test_excel_course_formula_rules_have_valid_supported_expressions(), test_xlsx_grader_evaluates_formulas_values_and_charts()

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.26
Nodes (14): PlagiarismBadge(), extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal(), fetchSubmissionDetail() (+6 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.14
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.18
Nodes (15): buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps, PendingDraftState (+7 more)

### Community 35 - "student_import_service.py"
Cohesion: 0.06
Nodes (17): build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _encode_ukrainian_word(), _infer_default_docx_columns(), _is_txt_header_line() (+9 more)

### Community 36 - "Settings"
Cohesion: 0.18
Nodes (3): get_settings(), _resolve_backend_path(), Settings

### Community 37 - "AsyncSession"
Cohesion: 0.14
Nodes (11): _collect_practical_submission_file_paths(), create_course(), delete_module(), delete_practical(), delete_quiz_question(), _fetch_user_progress_maps(), get_course(), list_courses() (+3 more)

### Community 38 - "_build_submission_download_names"
Cohesion: 0.29
Nodes (4): _build_submission_download_names(), _sanitize_ascii_token(), _sanitize_utf8_token(), _strip_apostrophes()

### Community 39 - "HtmlGrader"
Cohesion: 0.05
Nodes (16): _attribute_value_matches(), has_meaningful_html_body(), HtmlGrader, _is_doctype_target(), _node_has_visible_content(), _normalize_selector(), _normalize_text(), parse_html_document() (+8 more)

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.07
Nodes (41): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+33 more)

### Community 41 - "db_session"
Cohesion: 0.13
Nodes (5): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), test_duplicate_root_auth_router_removed_returns_404()

### Community 43 - "submission_service.py"
Cohesion: 0.10
Nodes (12): AcademicGroup, GradingRulesUpdateRequest, CriterionErrorStat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, ManualGradeUpdateRequest, SubmissionRead (+4 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.12
Nodes (28): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta, FORMAT_BADGE_LABELS (+20 more)

### Community 45 - "get_db"
Cohesion: 0.15
Nodes (4): list_admin_groups(), get_practical_for_student(), submit_module_quiz(), get_db()

### Community 46 - ".export_group_journal"
Cohesion: 0.15
Nodes (5): build_content_disposition(), ExportedDocument, _prepare_pdf_text(), _sanitize_filename_token(), _transliterate_to_ascii()

### Community 47 - "summarize_bundle"
Cohesion: 0.22
Nodes (5): run_seed(), SeedBundle, SeedSummary, summarize_bundle(), test_full_course_json_bundle_validation()

### Community 48 - "services/__init__.py"
Cohesion: 0.15
Nodes (9): GroupJournalBundle, cleanup_expired_submissions(), delete_submission_file_safely(), delete_submission_files_for_paths(), resolve_submission_file_path(), RetentionCleanupSummary, run_periodic_retention_cleanup(), run_retention_cleanup_once() (+1 more)

### Community 49 - "@tanstack/react-query"
Cohesion: 0.15
Nodes (12): dependencies, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient (+4 more)

### Community 50 - "build_sample_docx"
Cohesion: 0.25
Nodes (5): build_sample_docx(), build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata(), test_submit_all_four_practical_formats_via_api()

### Community 51 - "security.py"
Cohesion: 0.12
Nodes (10): create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token(), hash_password(), verify_password(), TokenPayload (+2 more)

### Community 52 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 57 - "render_group_journal_pdf"
Cohesion: 0.18
Nodes (5): _auto_adjust_worksheet_columns(), _configure_pdf_font(), PracticalColumnInfo, render_group_journal_pdf(), render_group_journal_xlsx()

### Community 60 - "student_import_service.py"
Cohesion: 0.06
Nodes (24): require_role(), login(), read_current_user(), refresh_tokens(), serialize_user(), format_size_limit_mb(), _enum_values(), User (+16 more)

### Community 61 - "test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress"
Cohesion: 0.12
Nodes (12): seed_database(), _copy_course_content_dir(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found(), test_delete_module_by_teacher_and_admin_cascades_cleans_files_and_renumbers(), test_delete_practical_preserves_module_lecture_quiz_and_cleans_files(), test_media_courses_static_serving(), test_seed_database_sync_courses_preserves_users_and_groups() (+4 more)

### Community 62 - "list_my_submissions"
Cohesion: 0.18
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 64 - "create_module"
Cohesion: 0.20
Nodes (5): _build_module_detail_read(), create_module(), get_module(), _load_module_or_404(), update_module()

### Community 67 - "submission_service.py"
Cohesion: 0.07
Nodes (17): upgrade(), Base, Course, CourseSlug, Module, Practical, QuizQuestion, QuizAttempt (+9 more)

### Community 68 - "main.py"
Cohesion: 0.18
Nodes (3): create_application(), lifespan(), test_lifespan_starts_and_cancels_retention_background_task()

### Community 77 - "build_seed_bundle"
Cohesion: 0.11
Nodes (4): build_seed_bundle(), test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_docx_grader_resolves_placeholders_in_target_and_expected()

### Community 80 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 82 - "_enum_values"
Cohesion: 0.19
Nodes (3): run_migrations_offline(), downgrade(), _enum_values()

### Community 92 - "read_upload_file_limited"
Cohesion: 0.20
Nodes (5): _build_too_large_exception(), read_upload_file_limited(), test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 97 - "get_db"
Cohesion: 0.16
Nodes (7): ensure_course_owner_or_admin(), create_quiz_question(), get_practical_for_teacher(), list_module_quiz_questions_teacher(), _serialize_practical_teacher(), update_practical(), upsert_module_practical()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 772 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **56 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DomainError` connect `admin.py` to `create_module`, `get_db`, `PlagiarismDetectedError`, `quiz_service.py`, `.import_students`, `AsyncSession`, `test_graders.py`, `SubmissionService`, `.update_grading_rules`, `submission_service.py`, `courses.py`, `submit_practical_work`, `security.py`, `get_current_user`, `._evaluate_html_submission`, `student_import_service.py`, `ExportService`, `ExportFormat`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `DomainError` (e.g. with `login()` and `refresh_tokens()`) actually correct?**
  _`DomainError` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `quiz_service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1471861471861472 - nodes in this community are weakly interconnected._
- **Why does `User` connect `student_import_service.py` to `create_module`, `get_db`, `quiz_service.py`, `submission_service.py`, `.import_students`, `AsyncSession`, `SubmissionService`, `.update_grading_rules`, `SqliteAsyncSessionAdapter`, `submission_service.py`, `make_auth_headers`, `build_seed_bundle`, `courses.py`, `_get_course_module_and_practical`, `get_current_user`, `admin.py`, `test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress`, `ExportService`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `User` (e.g. with `login()` and `read_current_user()`) actually correct?**
  _`User` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._