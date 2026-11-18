# Graph Report - edu-auto-grader  (2026-11-19)

## Corpus Check
- 66 files · ~45,411 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1165 nodes · 3141 edges · 49 communities (33 shown, 16 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 327 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dabd236f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas/__init__.py
- postgres
- compilerOptions
- InvalidFileFormatError
- main.tsx
- db_session
- submission_service.py
- AuthContext.tsx
- QuizService
- vite-env.d.ts
- export_service.py
- InvalidFileFormatError
- env.py
- seed.py
- BaseGrader
- get_db
- edu-auto-grader-backend
- HtmlGrader
- package.json
- App.tsx
- api.ts
- SqliteAsyncSessionAdapter
- course.ts
- html_grader.py
- UserRole
- XlsxGrader
- DocxGrader
- AccdbGrader
- build_sample_docx
- submission.py
- .execute
- build_accdb_bytes
- SubmissionService
- Sidebar.tsx
- 0001_initial_schema.py
- CoursesPage.tsx
- DomainError
- test_submit_all_four_practical_formats_via_api
- create_application
- conftest.py
- ExportService
- get_current_user
- _enum_values
- Settings

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 64 edges
2. `DomainError` - 46 edges
3. `User` - 46 edges
4. `InvalidFileFormatError` - 45 edges
5. `DocxGrader` - 45 edges
6. `PracticalFormat` - 43 edges
7. `GradingError` - 40 edges
8. `SubmissionService` - 39 edges
9. `CriterionResult` - 36 edges
10. `XlsxGrader` - 36 edges

## Surprising Connections (you probably didn't know these)
- `list_academic_groups()` --uses--> `AcademicGroupRead`  [INFERRED]
  backend/app/api/v1/analytics.py → backend/app/schemas/auth.py
- `ExportService` --uses--> `AcademicGroupRead`  [INFERRED]
  backend/app/services/export_service.py → backend/app/schemas/auth.py
- `GroupJournalBundle` --uses--> `AcademicGroupRead`  [INFERRED]
  backend/app/services/export_service.py → backend/app/schemas/auth.py
- `export_group_journal()` --uses--> `ExportFormat`  [INFERRED]
  backend/app/api/v1/analytics.py → backend/app/schemas/submission.py
- `ExportedDocument` --uses--> `ExportFormat`  [INFERRED]
  backend/app/services/export_service.py → backend/app/schemas/submission.py

## Import Cycles
- None detected.

## Communities (49 total, 16 thin omitted)

### Community 0 - "schemas/__init__.py"
Cohesion: 0.14
Nodes (12): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, ErrorResponse, LoginRequest, RefreshTokenRequest, TokenPayload, TokenResponse (+4 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "InvalidFileFormatError"
Cohesion: 0.10
Nodes (11): InvalidFileFormatError, GraderFactory, PracticalFormat, GradingRuleType, test_accdb_grader_detects_missing_schema_elements_and_invalid_header(), test_accdb_grader_evaluates_tables_columns_and_types(), test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document() (+3 more)

### Community 4 - "main.tsx"
Cohesion: 0.22
Nodes (9): dependencies, react@^18.3.1, react-dom@^18.3.1, @tanstack/react-query@^5.60.0, queryClient, rootElement, react, react-dom (+1 more)

### Community 5 - "db_session"
Cohesion: 0.20
Nodes (3): async_client(), db_session(), _fast_seed_hash_password()

### Community 6 - "submission_service.py"
Cohesion: 0.08
Nodes (21): _serialize_practical_teacher(), Practical, CourseCreate, CourseUpdate, ModuleCreate, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+13 more)

### Community 7 - "AuthContext.tsx"
Cohesion: 0.16
Nodes (19): axios@^1.7.7, apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext (+11 more)

### Community 11 - "export_service.py"
Cohesion: 0.07
Nodes (17): Base, Module, QuizAttempt, Submission, GroupJournalStudentCell, _auto_adjust_worksheet_columns(), build_content_disposition(), build_group_journal() (+9 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (17): check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism(), extract_core_xml_metadata() (+9 more)

### Community 14 - "env.py"
Cohesion: 0.18
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 15 - "seed.py"
Cohesion: 0.12
Nodes (17): Course, CourseSlug, QuizQuestion, AcademicGroup, User, _build_access_course(), _build_excel_course(), _build_html_course() (+9 more)

### Community 16 - "BaseGrader"
Cohesion: 0.07
Nodes (3): BaseGrader, _format_number(), GradingReport

### Community 17 - "get_db"
Cohesion: 0.09
Nodes (25): _build_module_detail_read(), create_course(), create_module(), create_quiz_question(), delete_quiz_question(), _fetch_user_progress_maps(), get_course(), get_module() (+17 more)

### Community 22 - "HtmlGrader"
Cohesion: 0.11
Nodes (6): HtmlGrader, _normalize_selector(), CriterionResult, GradingRule, test_html_grader_detects_missing_tags_and_rejects_empty_code(), test_html_grader_evaluates_semantic_dom_structure_and_attributes()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (41): @monaco-editor/react@4.6.0, devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0 (+33 more)

### Community 24 - "App.tsx"
Cohesion: 0.16
Nodes (25): react-router-dom@^6.28.0, App(), ProtectedAppLayout(), RoleHomeRedirect(), WorkspaceSectionPlaceholder(), WorkspaceSectionProps, Navbar(), NavbarProps (+17 more)

### Community 25 - "api.ts"
Cohesion: 0.08
Nodes (28): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, CriterionErrorStat, EXPORT_FORMATS, ExportFormat, GroupJournalRead, GroupJournalRow (+20 more)

### Community 27 - "course.ts"
Cohesion: 0.11
Nodes (28): fetchModuleDetail(), fetchStudentPractical(), FORMAT_BADGE_LABELS, LectureMarkdownRenderer(), ModuleSectionTab, ModuleViewPage(), renderInlineMarkdown(), submitQuizAnswers() (+20 more)

### Community 28 - "html_grader.py"
Cohesion: 0.13
Nodes (8): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), _is_doctype_target(), _normalize_text(), _parse_text_match_expected(), _strip_quotes(), _tag_has_attribute()

### Community 29 - "UserRole"
Cohesion: 0.14
Nodes (9): create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token(), hash_password(), verify_password(), _enum_values() (+1 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.07
Nodes (5): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader

### Community 32 - "AccdbGrader"
Cohesion: 0.06
Nodes (9): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _parse_ddl_column_type(), _resolve_canonical_type() (+1 more)

### Community 33 - "build_sample_docx"
Cohesion: 0.27
Nodes (4): build_sample_docx(), build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 34 - "submission.py"
Cohesion: 0.22
Nodes (4): CriterionErrorStat, ExportFormat, GroupJournalRow, HtmlSubmissionRequest

### Community 36 - "build_accdb_bytes"
Cohesion: 0.24
Nodes (5): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), build_sample_accdb()

### Community 37 - "SubmissionService"
Cohesion: 0.06
Nodes (12): _extract_submission_payload(), submit_practical_work(), update_practical_grading_rules(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade(), PlagiarismDetectedError (+4 more)

### Community 38 - "Sidebar.tsx"
Cohesion: 0.22
Nodes (8): lucide-react@^0.460.0, DISCIPLINE_CHIPS, DisciplineChip, NavigationItem, ROLE_NAVIGATION_MAP, ROLE_SECTION_TITLES, SidebarProps, lucide-react

### Community 40 - "CoursesPage.tsx"
Cohesion: 0.20
Nodes (8): COURSE_VISUAL_META, CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS, COURSE_SLUGS, CourseRead

### Community 41 - "DomainError"
Cohesion: 0.14
Nodes (6): require_role(), role_checker(), _parse_export_format(), ExtractedSubmissionPayload, DomainError, QuizNotPassedError

### Community 42 - "test_submit_all_four_practical_formats_via_api"
Cohesion: 0.18
Nodes (9): make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_health_check_and_jwt_login_flow(), test_submission_blocked_without_passed_quiz_and_unlocked_after_70_percent(), test_submit_all_four_practical_formats_via_api() (+1 more)

### Community 50 - "ExportService"
Cohesion: 0.08
Nodes (7): export_group_journal(), get_group_journal(), list_academic_groups(), GroupJournalRead, ExportService, GroupJournalBundle, _sanitize_filename_token()

### Community 52 - "get_current_user"
Cohesion: 0.12
Nodes (5): get_current_user(), login(), read_current_user(), refresh_tokens(), serialize_user()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 537 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `HtmlGrader` to `AccdbGrader`, `schemas/__init__.py`, `InvalidFileFormatError`, `SubmissionService`, `submission_service.py`, `InvalidFileFormatError`, `BaseGrader`, `get_db`, `html_grader.py`, `XlsxGrader`, `DocxGrader`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `schemas/__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1396011396011396 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `DomainError` to `SubmissionService`, `submission_service.py`, `QuizService`, `create_application`, `export_service.py`, `get_db`, `ExportService`, `get_current_user`, `UserRole`, `DocxGrader`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `DomainError` (e.g. with `login()` and `refresh_tokens()`) actually correct?**
  _`DomainError` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._