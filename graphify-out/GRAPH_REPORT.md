# Graph Report - edu-auto-grader  (2026-11-21)

## Corpus Check
- 87 files · ~245,362 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1551 nodes · 4262 edges · 80 communities (48 shown, 32 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 357 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `85b74b4d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- UserRole
- postgres
- compilerOptions
- GradingError
- AccdbGrader
- accdb_grader.py
- InvalidFileFormatError
- GradebookPage.tsx
- MarkdownRenderer.tsx
- vite-env.d.ts
- submission_service.py
- InvalidFileFormatError
- courses.py
- list_my_submissions
- test_submissions_api.py
- ExportService
- edu-auto-grader-backend
- schemas/auth.py
- package.json
- App.tsx
- DomainError
- AdminUsersPage.tsx
- course.ts
- _SeedQuizQuestionPayload
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- GroupJournalPage.tsx
- PlagiarismDetectedError
- HtmlSandbox.tsx
- normalize_full_name
- Settings
- SubmissionService
- SqliteAsyncSessionAdapter
- DocxGrader
- GradebookPage.tsx
- parse_docx_students
- make_auth_headers
- _find_tag_attr_key
- ModuleViewPage.tsx
- .import_students
- seed.py
- conftest.py
- main.py
- GradingRule
- db_session
- student_import_service.py
- get_db
- quiz_service.py
- SubmissionRead
- _attribute_value_matches
- _is_doctype_target
- _normalize_text
- services/__init__.py
- build_sample_docx
- do_run_migrations
- get_current_user
- _canonicalize_formula
- AcademicGroupRead
- _normalize_header_token
- .update_grading_rules
- submit_practical_work
- ManualGradeUpdateRequest
- test_retention_cleanup_purges_expired_files_keeps_grades_and_ignores_fresh
- _compile_jsonb_for_sqlite
- test_lifespan_starts_and_cancels_retention_background_task
- _build_module_detail_read

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 68 edges
2. `DomainError` - 58 edges
3. `User` - 53 edges
4. `InvalidFileFormatError` - 49 edges
5. `DocxGrader` - 46 edges
6. `get_db()` - 41 edges
7. `GradingError` - 40 edges
8. `SqliteAsyncSessionAdapter` - 39 edges
9. `PracticalFormat` - 39 edges
10. `XlsxGrader` - 36 edges

## Surprising Connections (you probably didn't know these)
- `list_my_submissions()` --uses--> `SubmissionRead`  [INFERRED]
  backend/app/api/v1/submissions.py → backend/app/schemas/submission.py
- `list_my_submissions()` --uses--> `SubmissionService`  [INFERRED]
  backend/app/api/v1/submissions.py → backend/app/services/submission_service.py
- `list_submissions()` --uses--> `SubmissionRead`  [INFERRED]
  backend/app/api/v1/submissions.py → backend/app/schemas/submission.py
- `list_submissions()` --uses--> `SubmissionService`  [INFERRED]
  backend/app/api/v1/submissions.py → backend/app/services/submission_service.py
- `get_submission_detail()` --uses--> `SubmissionRead`  [INFERRED]
  backend/app/api/v1/submissions.py → backend/app/schemas/submission.py

## Import Cycles
- None detected.

## Communities (80 total, 32 thin omitted)

### Community 0 - "UserRole"
Cohesion: 0.21
Nodes (6): create_access_token(), create_refresh_token(), create_token_pair(), _encode_jwt_token(), _enum_values(), UserRole

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "GradingError"
Cohesion: 0.10
Nodes (6): BaseGrader, GraderFactory, _parse_text_match_expected(), _strip_quotes(), PracticalFormat, GradingReport

### Community 4 - "AccdbGrader"
Cohesion: 0.10
Nodes (5): AccdbColumnSchema, AccdbDatabaseSchema, AccdbTableSchema, _is_system_table_name(), _resolve_canonical_type()

### Community 5 - "accdb_grader.py"
Cohesion: 0.10
Nodes (7): _is_numeric_condition(), _parse_ddl_column_type(), build_content_disposition(), _build_submission_download_names(), _sanitize_ascii_token(), _sanitize_utf8_token(), _strip_apostrophes()

### Community 6 - "InvalidFileFormatError"
Cohesion: 0.06
Nodes (18): InvalidFileFormatError, AccdbGrader, HtmlGrader, GradingRuleType, build_sample_accdb(), build_sample_xlsx(), test_accdb_grader_accepts_hyperlink_type_as_memo(), test_accdb_grader_detects_missing_schema_elements_and_invalid_header() (+10 more)

### Community 7 - "GradebookPage.tsx"
Cohesion: 0.18
Nodes (14): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+6 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "submission_service.py"
Cohesion: 0.06
Nodes (21): CourseSlug, _enum_values(), Submission, CriterionErrorStat, GroupJournalRow, GroupJournalStudentCell, _auto_adjust_worksheet_columns(), build_group_journal() (+13 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.07
Nodes (21): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256() (+13 more)

### Community 14 - "courses.py"
Cohesion: 0.12
Nodes (18): _serialize_practical_teacher(), CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+10 more)

### Community 15 - "list_my_submissions"
Cohesion: 0.21
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 16 - "test_submissions_api.py"
Cohesion: 0.16
Nodes (10): _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_download_submission_forbidden_for_other_teacher_and_students(), test_download_submissions_by_course_teacher_and_admin_with_headers_and_content(), test_health_check_and_jwt_login_flow(), test_submission_blocked_without_passed_quiz_and_unlocked_after_70_percent() (+2 more)

### Community 17 - "ExportService"
Cohesion: 0.06
Nodes (13): export_group_journal(), get_group_journal(), list_academic_groups(), ExportFormat, GroupJournalRead, _configure_pdf_font(), ExportedDocument, ExportService (+5 more)

### Community 22 - "schemas/auth.py"
Cohesion: 0.07
Nodes (19): login(), read_current_user(), refresh_tokens(), decode_token(), hash_password(), verify_password(), AcademicGroupUpdate, ErrorResponse (+11 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.13
Nodes (27): App(), ProtectedAppLayout(), RoleHomeRedirect(), Navbar(), NavbarProps, resolvePageTitle(), ROLE_BADGE_CONFIG, ROLE_LABELS (+19 more)

### Community 25 - "DomainError"
Cohesion: 0.08
Nodes (17): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404(), _get_user_with_group_or_404() (+9 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (46): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+38 more)

### Community 27 - "course.ts"
Cohesion: 0.09
Nodes (40): CourseEditorPage(), DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses(), fetchModuleDetail(), fetchModuleQuizQuestions(), fetchPracticalTeacher() (+32 more)

### Community 28 - "_SeedQuizQuestionPayload"
Cohesion: 0.18
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.09
Nodes (3): _format_cell_value(), _try_parse_numeric(), XlsxGrader

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.20
Nodes (15): PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal() (+7 more)

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.12
Nodes (18): dependencies, axios@^1.7.7, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, buildStarterHtmlTemplate() (+10 more)

### Community 35 - "normalize_full_name"
Cohesion: 0.16
Nodes (6): build_generated_email(), _encode_ukrainian_word(), normalize_full_name(), transliterate_ukrainian_slug(), ukrainian_sort_key(), test_ukrainian_alphabetical_sorting_and_apostrophe_normalization()

### Community 36 - "Settings"
Cohesion: 0.18
Nodes (3): get_settings(), _resolve_backend_path(), Settings

### Community 40 - "GradebookPage.tsx"
Cohesion: 0.10
Nodes (24): @tanstack/react-query@^5.60.0, COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS (+16 more)

### Community 41 - "parse_docx_students"
Cohesion: 0.20
Nodes (6): _clean_whitespace(), parse_docx_students(), parse_txt_students(), ParsedStudentCandidate, _strip_placeholder(), validate_and_normalize_email()

### Community 42 - "make_auth_headers"
Cohesion: 0.18
Nodes (4): make_auth_headers(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(), test_admin_users_crud_filters_and_safety_guards(), test_teacher_update_rules_manual_grade_and_group_export()

### Community 43 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.10
Nodes (32): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta, FORMAT_BADGE_LABELS (+24 more)

### Community 46 - "seed.py"
Cohesion: 0.11
Nodes (17): Base, Course, Module, Practical, QuizQuestion, AcademicGroup, build_seed_bundle(), hash_password() (+9 more)

### Community 47 - "conftest.py"
Cohesion: 0.08
Nodes (8): run_migrations_offline(), downgrade(), upgrade(), require_role(), role_checker(), _parse_export_format(), ExtractedSubmissionPayload, User

### Community 48 - "main.py"
Cohesion: 0.13
Nodes (5): create_application(), lifespan(), main(), run_periodic_retention_cleanup(), test_media_courses_static_serving()

### Community 49 - "GradingRule"
Cohesion: 0.10
Nodes (5): GradingError, _strip_identifiers(), _normalize_selector(), CriterionResult, GradingRule

### Community 50 - "db_session"
Cohesion: 0.15
Nodes (4): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session()

### Community 51 - "student_import_service.py"
Cohesion: 0.15
Nodes (6): calculate_variant_index(), _detect_docx_header_columns(), _DocxColumnMap, generate_temp_password(), _get_cell_value(), _infer_default_docx_columns()

### Community 52 - "get_db"
Cohesion: 0.11
Nodes (18): create_course(), create_module(), create_quiz_question(), delete_quiz_question(), _fetch_user_progress_maps(), get_course(), get_module(), get_practical_for_teacher() (+10 more)

### Community 53 - "quiz_service.py"
Cohesion: 0.12
Nodes (7): get_practical_for_student(), submit_module_quiz(), QuizNotPassedError, QuizAttempt, QuizSubmitRequest, QuizSubmitResponse, QuizService

### Community 54 - "SubmissionRead"
Cohesion: 0.20
Nodes (3): SubmissionRead, _is_submission_file_available(), serialize_submission()

### Community 58 - "services/__init__.py"
Cohesion: 0.26
Nodes (5): delete_submission_file_safely(), delete_submission_files_for_paths(), resolve_submission_file_path(), RetentionCleanupSummary, run_retention_cleanup_once()

### Community 60 - "build_sample_docx"
Cohesion: 0.32
Nodes (3): build_sample_docx(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 61 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 64 - "AcademicGroupRead"
Cohesion: 0.33
Nodes (3): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead

### Community 65 - "_normalize_header_token"
Cohesion: 0.40
Nodes (3): _classify_header_cell(), _is_txt_header_line(), _normalize_header_token()

### Community 67 - "submit_practical_work"
Cohesion: 0.15
Nodes (4): _extract_submission_payload(), submit_practical_work(), update_practical_grading_rules(), GradingRulesUpdateRequest

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 678 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `GradingError`, `accdb_grader.py`, `InvalidFileFormatError`, `DocxGrader`, `submission_service.py`, `InvalidFileFormatError`, `courses.py`, `seed.py`, `._evaluate_file_submission`, `_SeedQuizQuestionPayload`, `XlsxGrader`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `DocxGrader` connect `DocxGrader` to `GradingRule`, `GradingError`, `InvalidFileFormatError`, `InvalidFileFormatError`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `DomainError` (e.g. with `login()` and `refresh_tokens()`) actually correct?**
  _`DomainError` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._