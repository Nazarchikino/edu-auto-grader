# Graph Report - edu-auto-grader  (2026-11-19)

## Corpus Check
- 73 files · ~65,938 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1235 nodes · 3359 edges · 48 communities (35 shown, 13 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 333 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `93b6f8d4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas/__init__.py
- postgres
- compilerOptions
- GradingRule
- seed.py
- submission_service.py
- api.ts
- InvalidFileFormatError
- vite-env.d.ts
- export_service.py
- InvalidFileFormatError
- QuizService
- models/course.py
- UserRole
- get_db
- edu-auto-grader-backend
- ._evaluate_attribute_exists
- package.json
- App.tsx
- GradingReportCard.tsx
- course.ts
- build_accdb_bytes
- AuthContext.tsx
- XlsxGrader
- DocxGrader
- AccdbGrader
- build_sample_docx
- config.py
- db_session
- CoursesPage.tsx
- SubmissionService
- GradebookPage.tsx
- DomainError
- test_submit_all_four_practical_formats_via_api
- ModuleViewPage.tsx
- HtmlSandbox.tsx
- _compile_jsonb_for_sqlite
- ExportService
- User
- 0001_initial_schema.py
- env.py

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 64 edges
2. `DomainError` - 46 edges
3. `User` - 46 edges
4. `DocxGrader` - 45 edges
5. `InvalidFileFormatError` - 45 edges
6. `PracticalFormat` - 43 edges
7. `GradingError` - 40 edges
8. `SubmissionService` - 39 edges
9. `XlsxGrader` - 36 edges
10. `CriterionResult` - 36 edges

## Surprising Connections (you probably didn't know these)
- `login()` --uses--> `LoginRequest`  [INFERRED]
  backend/app/api/v1/auth.py → backend/app/schemas/auth.py
- `refresh_tokens()` --uses--> `RefreshTokenRequest`  [INFERRED]
  backend/app/api/v1/auth.py → backend/app/schemas/auth.py
- `decode_token()` --uses--> `TokenPayload`  [INFERRED]
  backend/app/core/security.py → backend/app/schemas/auth.py
- `TokenPayload` --uses--> `UserRole`  [INFERRED]
  backend/app/schemas/auth.py → backend/app/models/user.py
- `login()` --uses--> `TokenResponse`  [INFERRED]
  backend/app/api/v1/auth.py → backend/app/schemas/auth.py

## Import Cycles
- None detected.

## Communities (48 total, 13 thin omitted)

### Community 0 - "schemas/__init__.py"
Cohesion: 0.13
Nodes (10): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, ErrorResponse, LoginRequest, RefreshTokenRequest, TokenPayload, UserBase (+2 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "GradingRule"
Cohesion: 0.08
Nodes (5): GradingRule, test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_rejects_static_value_instead_of_formula_and_missing_chart()

### Community 4 - "seed.py"
Cohesion: 0.21
Nodes (5): main(), run_seed(), seed_database(), SeedSummary, summarize_bundle()

### Community 6 - "submission_service.py"
Cohesion: 0.10
Nodes (21): _build_module_detail_read(), _serialize_practical_teacher(), CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead (+13 more)

### Community 7 - "api.ts"
Cohesion: 0.10
Nodes (26): PlagiarismBadge(), COURSE_SLUG_BADGES, fetchAcademicGroups(), fetchCourses(), fetchGroupJournal(), fetchSubmissionDetail(), formatShortDate(), GroupJournalPage() (+18 more)

### Community 8 - "InvalidFileFormatError"
Cohesion: 0.07
Nodes (14): GradingError, InvalidFileFormatError, _parse_ddl_column_type(), BaseGrader, GraderFactory, HtmlGrader, compute_code_sha256(), normalize_code_for_hashing() (+6 more)

### Community 11 - "export_service.py"
Cohesion: 0.06
Nodes (18): CriterionErrorStat, GroupJournalRow, GroupJournalStudentCell, _auto_adjust_worksheet_columns(), build_content_disposition(), build_group_journal(), calculate_criterion_error_stats(), _configure_pdf_font() (+10 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (15): check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism(), extract_core_xml_metadata(), extract_document_metadata() (+7 more)

### Community 15 - "models/course.py"
Cohesion: 0.11
Nodes (16): Base, Course, Module, Practical, QuizQuestion, QuizAttempt, Submission, AcademicGroup (+8 more)

### Community 16 - "UserRole"
Cohesion: 0.14
Nodes (9): create_access_token(), create_refresh_token(), create_token_pair(), _encode_jwt_token(), hash_password(), verify_password(), _enum_values(), UserRole (+1 more)

### Community 17 - "get_db"
Cohesion: 0.10
Nodes (20): create_course(), create_module(), create_quiz_question(), delete_quiz_question(), _fetch_user_progress_maps(), get_course(), get_module(), get_practical_for_student() (+12 more)

### Community 22 - "._evaluate_attribute_exists"
Cohesion: 0.07
Nodes (9): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), _is_doctype_target(), _normalize_selector(), _normalize_text(), _parse_text_match_expected(), _strip_quotes() (+1 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.12
Nodes (29): react-router-dom@^6.28.0, App(), ProtectedAppLayout(), RoleHomeRedirect(), WorkspaceSectionPlaceholder(), WorkspaceSectionProps, Navbar(), NavbarProps (+21 more)

### Community 25 - "GradingReportCard.tsx"
Cohesion: 0.12
Nodes (21): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+13 more)

### Community 27 - "course.ts"
Cohesion: 0.12
Nodes (29): CourseEditorPage(), DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses(), fetchModuleDetail(), fetchModuleQuizQuestions(), fetchPracticalTeacher() (+21 more)

### Community 28 - "build_accdb_bytes"
Cohesion: 0.31
Nodes (4): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page()

### Community 29 - "AuthContext.tsx"
Cohesion: 0.19
Nodes (17): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+9 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.07
Nodes (5): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader

### Community 31 - "DocxGrader"
Cohesion: 0.07
Nodes (3): DocxGrader, _format_number(), CriterionResult

### Community 32 - "AccdbGrader"
Cohesion: 0.07
Nodes (11): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _resolve_canonical_type(), _strip_identifiers() (+3 more)

### Community 33 - "build_sample_docx"
Cohesion: 0.27
Nodes (4): build_sample_docx(), build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 35 - "db_session"
Cohesion: 0.15
Nodes (4): async_client(), _create_sqlite_test_engine(), db_session(), _fast_seed_hash_password()

### Community 36 - "CoursesPage.tsx"
Cohesion: 0.22
Nodes (9): COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS, COURSE_SLUGS (+1 more)

### Community 37 - "SubmissionService"
Cohesion: 0.05
Nodes (14): _extract_submission_payload(), submit_practical_work(), update_practical_grading_rules(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade(), PlagiarismDetectedError (+6 more)

### Community 40 - "GradebookPage.tsx"
Cohesion: 0.14
Nodes (20): extractApiErrorMessage(), AttemptMeta, COURSE_BADGE_META, CourseBadgeMeta, CourseFilterOption, fetchCourses(), fetchMySubmissions(), formatShortDateTime() (+12 more)

### Community 41 - "DomainError"
Cohesion: 0.14
Nodes (6): require_role(), role_checker(), _parse_export_format(), ExtractedSubmissionPayload, DomainError, create_application()

### Community 42 - "test_submit_all_four_practical_formats_via_api"
Cohesion: 0.09
Nodes (13): CourseSlug, _enum_values(), _set_sqlite_pragma(), make_auth_headers(), SqliteAsyncSessionAdapter, _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass() (+5 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.18
Nodes (16): BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta, FORMAT_BADGE_LABELS, formatFileSize(), LectureMarkdownRenderer() (+8 more)

### Community 45 - "HtmlSandbox.tsx"
Cohesion: 0.09
Nodes (23): dependencies, axios@^1.7.7, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, @tanstack/react-query@^5.60.0, PlagiarismBadgeProps (+15 more)

### Community 50 - "ExportService"
Cohesion: 0.07
Nodes (8): export_group_journal(), get_group_journal(), list_academic_groups(), ExportFormat, GroupJournalRead, ExportService, GroupJournalBundle, _sanitize_filename_token()

### Community 52 - "User"
Cohesion: 0.13
Nodes (7): get_current_user(), login(), read_current_user(), refresh_tokens(), serialize_user(), decode_token(), UserRead

### Community 63 - "env.py"
Cohesion: 0.18
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 546 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `AccdbGrader`, `SubmissionService`, `submission_service.py`, `InvalidFileFormatError`, `export_service.py`, `InvalidFileFormatError`, `models/course.py`, `._evaluate_attribute_exists`, `XlsxGrader`, `DocxGrader`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `schemas/__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12987012987012986 - nodes in this community are weakly interconnected._
- **Why does `XlsxGrader` connect `XlsxGrader` to `InvalidFileFormatError`, `GradingRule`, `DocxGrader`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `DomainError` (e.g. with `login()` and `refresh_tokens()`) actually correct?**
  _`DomainError` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._