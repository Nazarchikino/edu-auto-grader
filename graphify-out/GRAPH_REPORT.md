# Graph Report - edu-auto-grader  (2026-11-22)

## Corpus Check
- 87 files · ~249,113 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1571 nodes · 4408 edges · 66 communities (45 shown, 21 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 402 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c17a9cbc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DomainError
- postgres
- compilerOptions
- BaseGrader
- AccdbGrader
- accdb_grader.py
- InvalidFileFormatError
- get_db
- MarkdownRenderer.tsx
- vite-env.d.ts
- test_admin_api.py
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
- QuizService
- HtmlSandbox.tsx
- parse_docx_students
- Settings
- SubmissionService
- SubmissionRead
- DocxGrader
- GradebookPage.tsx
- ModuleViewPage.tsx
- seed.py
- submission_service.py
- main.py
- GradingRule
- conftest.py
- UUID
- export_service.py
- do_run_migrations
- get_current_user
- 0001_initial_schema.py
- submit_practical_work
- ManualGradeUpdateRequest
- _compile_jsonb_for_sqlite

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 70 edges
2. `DomainError` - 63 edges
3. `User` - 63 edges
4. `InvalidFileFormatError` - 50 edges
5. `DocxGrader` - 46 edges
6. `SqliteAsyncSessionAdapter` - 43 edges
7. `get_db()` - 43 edges
8. `PracticalFormat` - 42 edges
9. `SubmissionService` - 41 edges
10. `UserRole` - 40 edges

## Surprising Connections (you probably didn't know these)
- `SubmissionRead` --uses--> `ExtractedMetadata`  [INFERRED]
  backend/app/schemas/submission.py → backend/app/schemas/grading.py
- `serialize_submission()` --uses--> `ExtractedMetadata`  [INFERRED]
  backend/app/services/submission_service.py → backend/app/schemas/grading.py
- `SubmissionService` --uses--> `ExtractedMetadata`  [INFERRED]
  backend/app/services/submission_service.py → backend/app/schemas/grading.py
- `QuizService` --uses--> `QuizNotPassedError`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/core/exceptions.py
- `CourseCreate` --uses--> `CourseSlug`  [INFERRED]
  backend/app/schemas/course.py → backend/app/models/course.py

## Import Cycles
- None detected.

## Communities (66 total, 21 thin omitted)

### Community 0 - "DomainError"
Cohesion: 0.09
Nodes (12): require_role(), role_checker(), _parse_export_format(), DomainError, PlagiarismDetectedError, QuizNotPassedError, create_access_token(), create_refresh_token() (+4 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "BaseGrader"
Cohesion: 0.09
Nodes (3): BaseGrader, _format_cell_value(), GradingReport

### Community 4 - "AccdbGrader"
Cohesion: 0.08
Nodes (7): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _strip_identifiers()

### Community 5 - "accdb_grader.py"
Cohesion: 0.14
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 6 - "InvalidFileFormatError"
Cohesion: 0.07
Nodes (13): GradingError, GraderFactory, _enum_values(), PracticalFormat, GradingRuleType, build_sample_accdb(), test_accdb_grader_accepts_hyperlink_type_as_memo(), test_accdb_grader_detects_missing_schema_elements_and_invalid_header() (+5 more)

### Community 7 - "get_db"
Cohesion: 0.12
Nodes (10): _collect_practical_submission_file_paths(), delete_module(), delete_practical(), delete_quiz_question(), _ensure_course_owner_or_admin(), get_practical_for_teacher(), _serialize_practical_teacher(), update_practical() (+2 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "test_admin_api.py"
Cohesion: 0.07
Nodes (22): AcademicGroup, calculate_variant_index(), _set_sqlite_pragma(), make_auth_headers(), SqliteAsyncSessionAdapter, _build_college_import_docx(), _get_user_by_email(), test_academic_group_course_year_restricted_to_1_through_4() (+14 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (18): InvalidFileFormatError, check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism() (+10 more)

### Community 14 - "courses.py"
Cohesion: 0.12
Nodes (18): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+10 more)

### Community 15 - "list_my_submissions"
Cohesion: 0.19
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 16 - "test_submissions_api.py"
Cohesion: 0.09
Nodes (20): CourseSlug, _SeedCoursePayload, cleanup_expired_submissions(), main(), RetentionCleanupSummary, run_periodic_retention_cleanup(), run_retention_cleanup_once(), build_sample_docx() (+12 more)

### Community 17 - "ExportService"
Cohesion: 0.08
Nodes (8): export_group_journal(), get_group_journal(), list_academic_groups(), ExportFormat, GroupJournalRead, ExportedDocument, ExportService, GroupJournalBundle

### Community 22 - "schemas/auth.py"
Cohesion: 0.09
Nodes (16): login(), read_current_user(), refresh_tokens(), verify_password(), AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate (+8 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.08
Nodes (45): dependencies, axios@^1.7.7, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, App() (+37 more)

### Community 25 - "DomainError"
Cohesion: 0.10
Nodes (16): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404(), _get_user_with_group_or_404() (+8 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (46): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+38 more)

### Community 27 - "course.ts"
Cohesion: 0.07
Nodes (50): PracticalModuleContext, CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab (+42 more)

### Community 28 - "_SeedQuizQuestionPayload"
Cohesion: 0.22
Nodes (3): _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.06
Nodes (6): _canonicalize_formula(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader, test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_rejects_static_value_instead_of_formula_and_missing_chart()

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.26
Nodes (14): PlagiarismBadge(), extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal(), fetchSubmissionDetail() (+6 more)

### Community 33 - "QuizService"
Cohesion: 0.13
Nodes (3): get_practical_for_student(), submit_module_quiz(), QuizService

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.22
Nodes (10): @monaco-editor/react@4.6.0, buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode (+2 more)

### Community 35 - "parse_docx_students"
Cohesion: 0.06
Nodes (24): ImportedStudentItem, ImportSkippedItem, StudentImportResponse, build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap (+16 more)

### Community 36 - "Settings"
Cohesion: 0.18
Nodes (3): get_settings(), _resolve_backend_path(), Settings

### Community 37 - "SubmissionService"
Cohesion: 0.16
Nodes (3): PracticalTeacherRead, serialize_practical_teacher(), SubmissionService

### Community 38 - "SubmissionRead"
Cohesion: 0.22
Nodes (3): SubmissionRead, _is_submission_file_available(), serialize_submission()

### Community 39 - "DocxGrader"
Cohesion: 0.06
Nodes (3): DocxGrader, _format_number(), CriterionResult

### Community 40 - "GradebookPage.tsx"
Cohesion: 0.11
Nodes (25): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+17 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.12
Nodes (29): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta, FORMAT_BADGE_LABELS (+21 more)

### Community 46 - "seed.py"
Cohesion: 0.10
Nodes (11): _enum_values(), UserRole, build_seed_bundle(), hash_password(), main(), run_seed(), seed_database(), SeedBundle (+3 more)

### Community 47 - "submission_service.py"
Cohesion: 0.11
Nodes (15): run_migrations_offline(), Base, Course, Module, Practical, QuizQuestion, QuizAttempt, Submission (+7 more)

### Community 48 - "main.py"
Cohesion: 0.15
Nodes (3): create_application(), lifespan(), test_lifespan_starts_and_cancels_retention_background_task()

### Community 49 - "GradingRule"
Cohesion: 0.07
Nodes (14): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), HtmlGrader, _is_doctype_target(), _normalize_selector(), _normalize_text(), _parse_text_match_expected() (+6 more)

### Community 50 - "conftest.py"
Cohesion: 0.08
Nodes (8): hash_password(), async_client(), build_sample_xlsx(), _create_sqlite_test_engine(), db_session(), _fast_seed_hash_password(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 52 - "UUID"
Cohesion: 0.12
Nodes (11): create_course(), create_module(), create_quiz_question(), _fetch_user_progress_maps(), get_course(), list_courses(), list_module_quiz_questions_teacher(), _load_course_or_404() (+3 more)

### Community 58 - "export_service.py"
Cohesion: 0.07
Nodes (17): GroupJournalStudentCell, _auto_adjust_worksheet_columns(), build_content_disposition(), build_group_journal(), calculate_criterion_error_stats(), _configure_pdf_font(), PracticalColumnInfo, _prepare_pdf_text() (+9 more)

### Community 61 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 62 - "get_current_user"
Cohesion: 0.16
Nodes (4): get_current_user(), _build_module_detail_read(), get_module(), update_module()

### Community 67 - "submit_practical_work"
Cohesion: 0.13
Nodes (6): _extract_submission_payload(), ExtractedSubmissionPayload, submit_practical_work(), update_practical_grading_rules(), GradingRulesUpdateRequest, HtmlSubmissionRequest

### Community 68 - "ManualGradeUpdateRequest"
Cohesion: 0.29
Nodes (3): CriterionErrorStat, GroupJournalRow, ManualGradeUpdateRequest

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 687 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `BaseGrader`, `AccdbGrader`, `accdb_grader.py`, `InvalidFileFormatError`, `DocxGrader`, `SubmissionService`, `InvalidFileFormatError`, `courses.py`, `submission_service.py`, `_SeedQuizQuestionPayload`, `XlsxGrader`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `GradingRule` (e.g. with `AccdbGrader` and `BaseGrader`) actually correct?**
  _`GradingRule` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `DomainError` be split into smaller, more focused modules?**
  _Cohesion score 0.0945945945945946 - nodes in this community are weakly interconnected._
- **Why does `InvalidFileFormatError` connect `InvalidFileFormatError` to `DomainError`, `submit_practical_work`, `AccdbGrader`, `accdb_grader.py`, `InvalidFileFormatError`, `BaseGrader`, `DocxGrader`, `parse_docx_students`, `SubmissionService`, `submission_service.py`, `GradingRule`, `XlsxGrader`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `DomainError` (e.g. with `delete_admin_user()` and `update_admin_user()`) actually correct?**
  _`DomainError` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._