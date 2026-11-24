# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 88 files · ~255,198 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1667 nodes · 4522 edges · 113 communities (55 shown, 58 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 225 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `be1e96c0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Depends
- postgres
- compilerOptions
- DocxGrader
- AccdbGrader
- GraderFactory
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
- validate_zip_archive_safety
- package.json
- App.tsx
- DomainError
- AdminUsersPage.tsx
- course.ts
- _SeedCoursePayload
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- GroupJournalPage.tsx
- accdb_grader.py
- HtmlSandbox.tsx
- student_import_service.py
- Settings
- QuizService
- _build_submission_download_names
- GradingReportCard.tsx
- ModuleViewPage.tsx
- ExportFormat
- test_course_content.py
- retention_service.py
- GradingRule
- conftest.py
- courses.py
- GroupJournalRead
- UserRole
- SqliteAsyncSessionAdapter
- submissions.py
- export_group_journal
- _build_module_detail_read
- normalize_full_name
- .import_students
- submission_service.py
- main.py
- submit_practical_work
- GradebookPage.tsx
- .evaluate
- AsyncSession
- serialize_submission
- do_run_migrations
- 0001_initial_schema.py
- AcademicGroupRead
- get_db
- .update_grading_rules
- _enum_values
- _find_tag_attr_key
- calculate_criterion_error_stats
- _build_too_large_exception
- _parse_text_match_expected
- _compile_jsonb_for_sqlite
- test_lifespan_starts_and_cancels_retention_background_task
- test_read_upload_file_limited_stops_reading_chunks_early
- run_migrations_offline
- SubmissionDownloadPayload
- test_docx_grader_supports_uniform_single_number_margin

## God Nodes (most connected - your core abstractions)
1. `DomainError` - 62 edges
2. `User` - 53 edges
3. `GradingRule` - 50 edges
4. `SqliteAsyncSessionAdapter` - 48 edges
5. `DocxGrader` - 43 edges
6. `get_db()` - 43 edges
7. `InvalidFileFormatError` - 42 edges
8. `GradingError` - 41 edges
9. `XlsxGrader` - 33 edges
10. `PracticalFormat` - 33 edges

## Surprising Connections (you probably didn't know these)
- `import_admin_students()` --uses--> `StudentImportService`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/services/student_import_service.py
- `_extract_submission_payload()` --uses--> `HtmlSubmissionRequest`  [INFERRED]
  backend/app/api/v1/practicals.py → backend/app/schemas/submission.py
- `submit_practical_work()` --uses--> `SubmissionRead`  [INFERRED]
  backend/app/api/v1/practicals.py → backend/app/schemas/submission.py
- `submit_practical_work()` --uses--> `SubmissionService`  [INFERRED]
  backend/app/api/v1/practicals.py → backend/app/services/submission_service.py
- `update_practical_grading_rules()` --uses--> `SubmissionService`  [INFERRED]
  backend/app/api/v1/practicals.py → backend/app/services/submission_service.py

## Import Cycles
- None detected.

## Communities (113 total, 58 thin omitted)

### Community 0 - "Depends"
Cohesion: 0.16
Nodes (6): create_quiz_question(), get_practical_for_teacher(), list_module_quiz_questions_teacher(), _serialize_practical_teacher(), update_practical(), upsert_module_practical()

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
Cohesion: 0.07
Nodes (12): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_system_table_name(), _strip_identifiers(), build_sample_accdb(), test_accdb_grader_accepts_hyperlink_type_as_memo() (+4 more)

### Community 6 - "test_graders.py"
Cohesion: 0.08
Nodes (9): GradingError, InvalidFileFormatError, _attribute_value_matches(), _is_doctype_target(), _normalize_text(), parse_core_xml_bytes(), GradingRulesUpdateRequest, GradingRuleType (+1 more)

### Community 7 - "SqliteAsyncSessionAdapter"
Cohesion: 0.23
Nodes (3): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), test_seed_database_sync_courses_preserves_users_and_groups()

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.13
Nodes (30): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+22 more)

### Community 11 - "make_auth_headers"
Cohesion: 0.11
Nodes (12): make_auth_headers(), _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates() (+4 more)

### Community 13 - "metadata.py"
Cohesion: 0.10
Nodes (11): check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism(), _find_xml_text() (+3 more)

### Community 14 - "courses.py"
Cohesion: 0.10
Nodes (18): PracticalFormat, CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+10 more)

### Community 16 - "_get_course_module_and_practical"
Cohesion: 0.14
Nodes (13): _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_download_submission_forbidden_for_other_teacher_and_students(), test_download_submissions_by_course_teacher_and_admin_with_headers_and_content(), test_health_check_and_jwt_login_flow(), test_retention_cleanup_purges_expired_files_keeps_grades_and_ignores_fresh() (+5 more)

### Community 22 - "validate_zip_archive_safety"
Cohesion: 0.17
Nodes (7): extract_core_xml_metadata(), extract_document_metadata(), validate_zip_archive_safety(), ExtractedMetadata, DummySubmissionRecord, test_metadata_extraction_and_plagiarism_detection(), test_zip_bomb_protection_blocks_high_ratio_many_entries_and_oversized_uncompressed()

### Community 23 - "package.json"
Cohesion: 0.05
Nodes (49): dependencies, axios@^1.7.7, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0 (+41 more)

### Community 24 - "App.tsx"
Cohesion: 0.14
Nodes (27): App(), ProtectedAppLayout(), RoleHomeRedirect(), PlagiarismBadgeProps, Navbar(), NavbarProps, resolvePageTitle(), ROLE_BADGE_CONFIG (+19 more)

### Community 25 - "DomainError"
Cohesion: 0.06
Nodes (22): require_role(), role_checker(), create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique() (+14 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (46): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+38 more)

### Community 27 - "course.ts"
Cohesion: 0.07
Nodes (50): PracticalModuleContext, CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab (+42 more)

### Community 28 - "_SeedCoursePayload"
Cohesion: 0.13
Nodes (6): HtmlSubmissionRequest, ManualGradeUpdateRequest, _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.06
Nodes (8): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader, test_excel_course_formula_rules_have_valid_supported_expressions(), test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_rejects_static_value_instead_of_formula_and_missing_chart()

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.26
Nodes (14): PlagiarismBadge(), extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal(), fetchSubmissionDetail() (+6 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.12
Nodes (7): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _is_numeric_condition(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.28
Nodes (8): buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode, PracticalVariant

### Community 35 - "student_import_service.py"
Cohesion: 0.11
Nodes (14): ImportSkippedItem, _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _get_cell_value(), _infer_default_docx_columns(), _is_txt_header_line() (+6 more)

### Community 36 - "Settings"
Cohesion: 0.18
Nodes (3): get_settings(), _resolve_backend_path(), Settings

### Community 37 - "QuizService"
Cohesion: 0.12
Nodes (4): QuizNotPassedError, QuizSubmitRequest, QuizSubmitResponse, QuizService

### Community 38 - "_build_submission_download_names"
Cohesion: 0.22
Nodes (5): build_content_disposition(), _build_submission_download_names(), _sanitize_ascii_token(), _sanitize_utf8_token(), _strip_apostrophes()

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.18
Nodes (14): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+6 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.12
Nodes (30): renderInlineMarkdown(), AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta (+22 more)

### Community 46 - "ExportFormat"
Cohesion: 0.12
Nodes (7): ExportFormat, _configure_pdf_font(), ExportedDocument, _prepare_pdf_text(), render_group_journal_pdf(), _sanitize_filename_token(), _transliterate_to_ascii()

### Community 47 - "test_course_content.py"
Cohesion: 0.08
Nodes (18): Course, QuizQuestion, build_seed_bundle(), hash_password(), _load_course_from_json(), main(), _question_signature(), run_seed() (+10 more)

### Community 48 - "retention_service.py"
Cohesion: 0.19
Nodes (7): calculate_variant_index(), resolve_student_variant(), cleanup_expired_submissions(), delete_submission_file_safely(), resolve_submission_file_path(), RetentionCleanupSummary, run_retention_cleanup_once()

### Community 49 - "GradingRule"
Cohesion: 0.08
Nodes (9): BaseGrader, HtmlGrader, _normalize_selector(), CriterionResult, GradingReport, GradingRule, test_html_grader_attribute_filter_selector_and_compound_colspan(), test_html_grader_detects_missing_tags_and_rejects_empty_code() (+1 more)

### Community 50 - "conftest.py"
Cohesion: 0.10
Nodes (9): async_client(), build_sample_docx(), build_sample_xlsx(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _replace_zip_member(), rewrite_openxml_core_metadata() (+1 more)

### Community 52 - "courses.py"
Cohesion: 0.15
Nodes (8): get_current_user(), create_course(), _fetch_user_progress_maps(), get_course(), list_courses(), _load_course_or_404(), _serialize_course(), update_course()

### Community 58 - "GroupJournalRead"
Cohesion: 0.13
Nodes (8): GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, _auto_adjust_worksheet_columns(), build_group_journal(), GroupJournalBundle, PracticalColumnInfo, render_group_journal_xlsx()

### Community 60 - "UserRole"
Cohesion: 0.06
Nodes (25): login(), read_current_user(), refresh_tokens(), create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token() (+17 more)

### Community 61 - "SqliteAsyncSessionAdapter"
Cohesion: 0.17
Nodes (8): _copy_course_content_dir(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found(), test_delete_module_by_teacher_and_admin_cascades_cleans_files_and_renumbers(), test_delete_practical_preserves_module_lecture_quiz_and_cleans_files(), test_media_courses_static_serving(), test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress(), test_seed_sync_courses_upserts_in_place_and_preserves_student_progress()

### Community 62 - "submissions.py"
Cohesion: 0.19
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 63 - "export_group_journal"
Cohesion: 0.23
Nodes (3): export_group_journal(), get_group_journal(), list_academic_groups()

### Community 64 - "_build_module_detail_read"
Cohesion: 0.20
Nodes (5): _build_module_detail_read(), create_module(), get_module(), _load_module_or_404(), update_module()

### Community 65 - "normalize_full_name"
Cohesion: 0.16
Nodes (6): build_generated_email(), _encode_ukrainian_word(), normalize_full_name(), transliterate_ukrainian_slug(), ukrainian_sort_key(), test_ukrainian_alphabetical_sorting_and_apostrophe_normalization()

### Community 66 - ".import_students"
Cohesion: 0.12
Nodes (4): ImportedStudentItem, StudentImportResponse, generate_temp_password(), StudentImportService

### Community 67 - "submission_service.py"
Cohesion: 0.12
Nodes (8): Base, CourseSlug, Module, Practical, QuizAttempt, Submission, AcademicGroup, User

### Community 68 - "main.py"
Cohesion: 0.18
Nodes (3): create_application(), lifespan(), run_periodic_retention_cleanup()

### Community 70 - "submit_practical_work"
Cohesion: 0.14
Nodes (5): _extract_submission_payload(), ExtractedSubmissionPayload, _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 76 - "GradebookPage.tsx"
Cohesion: 0.10
Nodes (21): queryClient, rootElement, COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard() (+13 more)

### Community 77 - ".evaluate"
Cohesion: 0.17
Nodes (3): test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_docx_grader_resolves_placeholders_in_target_and_expected()

### Community 78 - "AsyncSession"
Cohesion: 0.24
Nodes (5): _collect_practical_submission_file_paths(), delete_module(), delete_practical(), delete_quiz_question(), _ensure_course_owner_or_admin()

### Community 80 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 84 - "get_db"
Cohesion: 0.20
Nodes (3): get_practical_for_student(), submit_module_quiz(), get_db()

### Community 89 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 91 - "calculate_criterion_error_stats"
Cohesion: 0.33
Nodes (3): CriterionErrorStat, calculate_criterion_error_stats(), _RuleStatAccumulator

### Community 96 - "test_read_upload_file_limited_stops_reading_chunks_early"
Cohesion: 0.50
Nodes (3): test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 740 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **58 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `submission_service.py` to `_build_module_detail_read`, `.import_students`, `student_import_service.py`, `QuizService`, `SqliteAsyncSessionAdapter`, `make_auth_headers`, `AsyncSession`, `test_course_content.py`, `SubmissionService`, `ExportService`, `_get_course_module_and_practical`, `courses.py`, `DomainError`, `GroupJournalRead`, `UserRole`, `SqliteAsyncSessionAdapter`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `DomainError` (e.g. with `login()` and `refresh_tokens()`) actually correct?**
  _`DomainError` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `DomainError` to `Depends`, `_build_module_detail_read`, `.import_students`, `submission_service.py`, `main.py`, `QuizService`, `submit_practical_work`, `test_graders.py`, `student_import_service.py`, `AsyncSession`, `SubmissionService`, `ExportService`, `courses.py`, `.update_grading_rules`, `._evaluate_file_submission`, `UserRole`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `get_current_user()` and `require_role()`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._