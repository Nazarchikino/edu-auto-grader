# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 89 files · ~257,916 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1712 nodes · 4626 edges · 107 communities (52 shown, 55 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 180 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `620b2b89`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- .build_criterion_result
- postgres
- compilerOptions
- DocxGrader
- AccdbGrader
- evaluate_plagiarism
- test_graders.py
- SqliteAsyncSessionAdapter
- MarkdownRenderer.tsx
- vite-env.d.ts
- make_auth_headers
- metadata.py
- courses.py
- _get_course_module_and_practical
- edu-auto-grader-backend
- DomainError
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
- Settings
- AsyncSession
- submission_service.py
- ._evaluate_attribute_exists
- GradingReportCard.tsx
- test_course_teacher_reassignment_forbidden_for_owner_and_allowed_for_admin
- practicals.py
- ModuleViewPage.tsx
- refresh_tokens
- _prepare_pdf_text
- test_course_content.py
- services/__init__.py
- HtmlGrader
- build_sample_docx
- create_token_pair
- _find_tag_attr_key
- UserRead
- _parse_text_match_expected
- schemas/auth.py
- test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress
- SubmissionService
- ExportService
- create_module
- normalize_full_name
- .import_students
- submission_service.py
- main.py
- .evaluate
- do_run_migrations
- 0001_initial_schema.py
- ._evaluate_html_submission
- read_upload_file_limited
- _compile_jsonb_for_sqlite
- get_db
- ensure_course_owner_or_admin

## God Nodes (most connected - your core abstractions)
1. `DomainError` - 61 edges
2. `User` - 57 edges
3. `SqliteAsyncSessionAdapter` - 56 edges
4. `get_db()` - 43 edges
5. `DocxGrader` - 42 edges
6. `GradingError` - 42 edges
7. `InvalidFileFormatError` - 41 edges
8. `GradingRule` - 39 edges
9. `make_auth_headers()` - 35 edges
10. `XlsxGrader` - 32 edges

## Surprising Connections (you probably didn't know these)
- `test_grader_factory_resolves_all_four_formats()` --uses--> `HtmlGrader`  [INFERRED]
  backend/tests/test_graders.py → backend/app/graders/html_grader.py
- `login()` --uses--> `DomainError`  [INFERRED]
  backend/app/api/v1/auth.py → backend/app/core/exceptions.py
- `refresh_tokens()` --uses--> `DomainError`  [INFERRED]
  backend/app/api/v1/auth.py → backend/app/core/exceptions.py
- `QuizService` --uses--> `DomainError`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/core/exceptions.py
- `QuizService` --uses--> `QuizNotPassedError`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/core/exceptions.py

## Import Cycles
- None detected.

## Communities (107 total, 55 thin omitted)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 4 - "AccdbGrader"
Cohesion: 0.06
Nodes (17): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_system_table_name(), _strip_identifiers(), GradingRule, build_sample_accdb() (+9 more)

### Community 5 - "evaluate_plagiarism"
Cohesion: 0.17
Nodes (4): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), SubmissionRecordProtocol

### Community 6 - "test_graders.py"
Cohesion: 0.09
Nodes (6): BaseGrader, PracticalFormat, CriterionResult, GradingReport, GradingRuleType, PlagiarismCheckResult

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "make_auth_headers"
Cohesion: 0.13
Nodes (11): make_auth_headers(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(), test_admin_endpoints_enforce_admin_rbac() (+3 more)

### Community 13 - "metadata.py"
Cohesion: 0.09
Nodes (18): GradingError, InvalidFileFormatError, GraderFactory, compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), extract_core_xml_metadata() (+10 more)

### Community 14 - "courses.py"
Cohesion: 0.07
Nodes (24): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+16 more)

### Community 16 - "_get_course_module_and_practical"
Cohesion: 0.13
Nodes (14): _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_best_score_unified_across_student_progress_and_group_journal_export(), test_download_submissions_by_course_teacher_and_admin_with_headers_and_content(), test_health_check_and_jwt_login_flow(), test_retention_cleanup_purges_expired_files_keeps_grades_and_ignores_fresh() (+6 more)

### Community 22 - "DomainError"
Cohesion: 0.13
Nodes (5): get_current_user(), role_checker(), DomainError, PlagiarismDetectedError, QuizNotPassedError

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.08
Nodes (45): dependencies, axios@^1.7.7, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, App() (+37 more)

### Community 25 - "admin.py"
Cohesion: 0.10
Nodes (16): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404(), _get_user_with_group_or_404() (+8 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (46): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+38 more)

### Community 27 - "course.ts"
Cohesion: 0.07
Nodes (50): PracticalModuleContext, CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab (+42 more)

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.07
Nodes (6): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader, test_excel_course_formula_rules_have_valid_supported_expressions()

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.26
Nodes (14): PlagiarismBadge(), extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal(), fetchSubmissionDetail() (+6 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.14
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _is_numeric_condition(), _resolve_canonical_type()

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.22
Nodes (10): @monaco-editor/react@4.6.0, buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode (+2 more)

### Community 35 - "student_import_service.py"
Cohesion: 0.09
Nodes (17): _parse_ddl_column_type(), build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _get_cell_value(), _infer_default_docx_columns() (+9 more)

### Community 36 - "Settings"
Cohesion: 0.18
Nodes (3): get_settings(), _resolve_backend_path(), Settings

### Community 37 - "AsyncSession"
Cohesion: 0.11
Nodes (11): create_course(), create_quiz_question(), _fetch_user_progress_maps(), get_course(), get_practical_for_student(), list_courses(), list_module_quiz_questions_teacher(), _load_course_or_404() (+3 more)

### Community 38 - "submission_service.py"
Cohesion: 0.10
Nodes (9): GradingRulesUpdateRequest, build_content_disposition(), _build_submission_download_names(), _is_submission_file_available(), _sanitize_ascii_token(), _sanitize_utf8_token(), serialize_practical_teacher(), _strip_apostrophes() (+1 more)

### Community 39 - "._evaluate_attribute_exists"
Cohesion: 0.13
Nodes (4): _attribute_value_matches(), _is_doctype_target(), _normalize_selector(), _normalize_text()

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.11
Nodes (25): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+17 more)

### Community 41 - "test_course_teacher_reassignment_forbidden_for_owner_and_allowed_for_admin"
Cohesion: 0.18
Nodes (4): async_client(), _get_user_by_email(), test_course_teacher_reassignment_forbidden_for_owner_and_allowed_for_admin(), test_duplicate_root_auth_router_removed_returns_404()

### Community 43 - "practicals.py"
Cohesion: 0.10
Nodes (10): require_role(), decode_token(), verify_password(), _enum_values(), UserRole, ExportFormat, GroupJournalRead, HtmlSubmissionRequest (+2 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.12
Nodes (29): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta, FORMAT_BADGE_LABELS (+21 more)

### Community 45 - "refresh_tokens"
Cohesion: 0.21
Nodes (4): login(), read_current_user(), refresh_tokens(), TokenResponse

### Community 47 - "test_course_content.py"
Cohesion: 0.07
Nodes (18): build_seed_bundle(), hash_password(), _load_course_from_json(), main(), _question_signature(), run_seed(), seed_database(), SeedBundle (+10 more)

### Community 48 - "services/__init__.py"
Cohesion: 0.06
Nodes (20): CriterionErrorStat, _auto_adjust_worksheet_columns(), build_group_journal(), calculate_criterion_error_stats(), _configure_pdf_font(), ExportedDocument, GroupJournalBundle, _normalize_utc_timestamp() (+12 more)

### Community 49 - "HtmlGrader"
Cohesion: 0.10
Nodes (9): has_meaningful_html_body(), HtmlGrader, _node_has_visible_content(), parse_html_document(), test_minimal_html_starter_template_scores_zero_across_all_html_course_modules(), test_html_grader_attribute_filter_selector_and_compound_colspan(), test_html_grader_detects_missing_tags_and_rejects_empty_code(), test_html_grader_empty_body_and_starter_template_score_zero() (+1 more)

### Community 50 - "build_sample_docx"
Cohesion: 0.12
Nodes (8): build_sample_docx(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password(), _replace_zip_member(), rewrite_openxml_core_metadata(), test_submit_all_four_practical_formats_via_api()

### Community 51 - "create_token_pair"
Cohesion: 0.31
Nodes (4): create_access_token(), create_refresh_token(), create_token_pair(), _encode_jwt_token()

### Community 52 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 57 - "UserRead"
Cohesion: 0.33
Nodes (3): UserBase, UserCreate, UserRead

### Community 60 - "schemas/auth.py"
Cohesion: 0.12
Nodes (11): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, ErrorResponse, ImportSkippedItem, LoginRequest, RefreshTokenRequest (+3 more)

### Community 61 - "test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress"
Cohesion: 0.11
Nodes (13): hash_password(), _copy_course_content_dir(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found(), test_delete_module_by_teacher_and_admin_cascades_cleans_files_and_renumbers(), test_delete_practical_preserves_module_lecture_quiz_and_cleans_files(), test_media_courses_static_serving(), test_seed_database_sync_courses_preserves_users_and_groups() (+5 more)

### Community 62 - "SubmissionService"
Cohesion: 0.06
Nodes (12): _extract_submission_payload(), ExtractedSubmissionPayload, _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules(), download_submission_file(), get_submission_detail(), list_my_submissions() (+4 more)

### Community 63 - "ExportService"
Cohesion: 0.08
Nodes (6): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), ExportService, _sanitize_filename_token()

### Community 64 - "create_module"
Cohesion: 0.20
Nodes (5): _build_module_detail_read(), create_module(), get_module(), _load_module_or_404(), update_module()

### Community 65 - "normalize_full_name"
Cohesion: 0.25
Nodes (3): _encode_ukrainian_word(), ukrainian_sort_key(), test_ukrainian_alphabetical_sorting_and_apostrophe_normalization()

### Community 66 - ".import_students"
Cohesion: 0.14
Nodes (3): ImportedStudentItem, generate_temp_password(), StudentImportService

### Community 67 - "submission_service.py"
Cohesion: 0.11
Nodes (13): Base, Course, CourseSlug, _enum_values(), Module, Practical, QuizQuestion, QuizAttempt (+5 more)

### Community 68 - "main.py"
Cohesion: 0.15
Nodes (3): create_application(), lifespan(), test_lifespan_starts_and_cancels_retention_background_task()

### Community 77 - ".evaluate"
Cohesion: 0.12
Nodes (3): build_sample_xlsx(), test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_rejects_static_value_instead_of_formula_and_missing_chart()

### Community 80 - "do_run_migrations"
Cohesion: 0.18
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 92 - "read_upload_file_limited"
Cohesion: 0.17
Nodes (6): _build_too_large_exception(), format_size_limit_mb(), read_upload_file_limited(), test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 97 - "get_db"
Cohesion: 0.20
Nodes (5): get_practical_for_teacher(), _serialize_practical_teacher(), update_practical(), upsert_module_practical(), get_db()

### Community 114 - "ensure_course_owner_or_admin"
Cohesion: 0.24
Nodes (5): ensure_course_owner_or_admin(), _collect_practical_submission_file_paths(), delete_module(), delete_practical(), delete_quiz_question()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 763 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **55 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DocxGrader` connect `DocxGrader` to `.build_criterion_result`, `submission_service.py`, `AccdbGrader`, `test_graders.py`, `.evaluate`, `metadata.py`, `._select_paragraphs`, `._resolve_paragraph_level_font`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `DomainError` (e.g. with `login()` and `refresh_tokens()`) actually correct?**
  _`DomainError` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `DomainError` to `create_module`, `get_db`, `.import_students`, `submission_service.py`, `main.py`, `AsyncSession`, `student_import_service.py`, `submission_service.py`, `practicals.py`, `refresh_tokens`, `courses.py`, `metadata.py`, `ensure_course_owner_or_admin`, `admin.py`, `._evaluate_html_submission`, `SubmissionService`, `ExportService`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `User` (e.g. with `login()` and `read_current_user()`) actually correct?**
  _`User` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._