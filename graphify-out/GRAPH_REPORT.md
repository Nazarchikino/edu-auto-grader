# Graph Report - edu-auto-grader  (2026-11-19)

## Corpus Check
- 69 files · ~53,405 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1202 nodes · 3232 edges · 52 communities (35 shown, 17 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 329 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cb7e065b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas/__init__.py
- postgres
- compilerOptions
- GradingRule
- seed.py
- conftest.py
- submission_service.py
- AuthContext.tsx
- InvalidFileFormatError
- vite-env.d.ts
- export_service.py
- InvalidFileFormatError
- QuizService
- models/course.py
- .evaluate
- get_db
- edu-auto-grader-backend
- ._evaluate_attribute_exists
- package.json
- App.tsx
- GradingReportCard.tsx
- course.ts
- build_accdb_bytes
- scripts
- XlsxGrader
- DocxGrader
- AccdbGrader
- build_sample_docx
- submission.py
- .execute
- analytics.py
- SubmissionService
- _is_doctype_target
- _normalize_text
- GradebookPage.tsx
- DomainError
- test_submit_all_four_practical_formats_via_api
- ModuleViewPage.tsx
- HtmlSandbox.tsx
- _compile_jsonb_for_sqlite
- ExportService
- User
- courses.py
- _enum_values
- env.py

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 64 edges
2. `User` - 46 edges
3. `DomainError` - 46 edges
4. `InvalidFileFormatError` - 45 edges
5. `DocxGrader` - 45 edges
6. `PracticalFormat` - 43 edges
7. `GradingError` - 40 edges
8. `SubmissionService` - 39 edges
9. `CriterionResult` - 36 edges
10. `XlsxGrader` - 36 edges

## Surprising Connections (you probably didn't know these)
- `_build_module_detail_read()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/models/user.py
- `create_access_token()` --uses--> `UserRole`  [INFERRED]
  backend/app/core/security.py → backend/app/models/user.py
- `create_refresh_token()` --uses--> `UserRole`  [INFERRED]
  backend/app/core/security.py → backend/app/models/user.py
- `create_token_pair()` --uses--> `UserRole`  [INFERRED]
  backend/app/core/security.py → backend/app/models/user.py
- `_encode_jwt_token()` --uses--> `UserRole`  [INFERRED]
  backend/app/core/security.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (52 total, 17 thin omitted)

### Community 0 - "schemas/__init__.py"
Cohesion: 0.11
Nodes (11): AcademicGroupBase, AcademicGroupCreate, ErrorResponse, LoginRequest, RefreshTokenRequest, TokenPayload, TokenResponse, UserBase (+3 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "GradingRule"
Cohesion: 0.11
Nodes (12): compute_file_sha256(), GradingRuleType, build_sample_accdb(), DummySubmissionRecord, test_accdb_grader_detects_missing_schema_elements_and_invalid_header(), test_accdb_grader_evaluates_tables_columns_and_types(), test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document() (+4 more)

### Community 4 - "seed.py"
Cohesion: 0.16
Nodes (9): AcademicGroup, build_seed_bundle(), hash_password(), main(), run_seed(), seed_database(), SeedBundle, SeedSummary (+1 more)

### Community 5 - "conftest.py"
Cohesion: 0.09
Nodes (4): async_client(), _create_sqlite_test_engine(), db_session(), _fast_seed_hash_password()

### Community 6 - "submission_service.py"
Cohesion: 0.10
Nodes (13): CourseCreate, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate, PracticalSummaryRead (+5 more)

### Community 7 - "AuthContext.tsx"
Cohesion: 0.08
Nodes (37): axios@^1.7.7, apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext (+29 more)

### Community 8 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (8): GradingError, InvalidFileFormatError, BaseGrader, GraderFactory, HtmlGrader, PracticalFormat, GradingReport, test_grader_factory_resolves_all_four_formats()

### Community 11 - "export_service.py"
Cohesion: 0.09
Nodes (14): CourseSlug, _auto_adjust_worksheet_columns(), build_content_disposition(), calculate_criterion_error_stats(), _configure_pdf_font(), ExportedDocument, GroupJournalBundle, PracticalColumnInfo (+6 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (14): check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_submission_hash(), evaluate_plagiarism(), extract_core_xml_metadata(), extract_document_metadata() (+6 more)

### Community 15 - "models/course.py"
Cohesion: 0.15
Nodes (11): Base, Course, Module, Practical, QuizQuestion, QuizAttempt, Submission, _build_access_course() (+3 more)

### Community 17 - "get_db"
Cohesion: 0.10
Nodes (21): create_course(), create_module(), create_quiz_question(), delete_quiz_question(), _fetch_user_progress_maps(), get_course(), get_module(), get_practical_for_student() (+13 more)

### Community 22 - "._evaluate_attribute_exists"
Cohesion: 0.12
Nodes (7): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), _normalize_selector(), _parse_text_match_expected(), _strip_quotes(), _tag_has_attribute()

### Community 23 - "package.json"
Cohesion: 0.09
Nodes (33): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+25 more)

### Community 24 - "App.tsx"
Cohesion: 0.11
Nodes (32): react-router-dom@^6.28.0, App(), ProtectedAppLayout(), RoleHomeRedirect(), WorkspaceSectionPlaceholder(), WorkspaceSectionProps, Navbar(), NavbarProps (+24 more)

### Community 25 - "GradingReportCard.tsx"
Cohesion: 0.13
Nodes (20): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+12 more)

### Community 27 - "course.ts"
Cohesion: 0.15
Nodes (19): CourseCreate, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate, PracticalStudentRead (+11 more)

### Community 28 - "build_accdb_bytes"
Cohesion: 0.31
Nodes (4): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page()

### Community 29 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, typecheck

### Community 30 - "XlsxGrader"
Cohesion: 0.07
Nodes (5): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader

### Community 31 - "DocxGrader"
Cohesion: 0.06
Nodes (4): DocxGrader, _format_number(), CriterionResult, GradingRule

### Community 32 - "AccdbGrader"
Cohesion: 0.07
Nodes (9): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _parse_ddl_column_type(), _resolve_canonical_type() (+1 more)

### Community 33 - "build_sample_docx"
Cohesion: 0.27
Nodes (4): build_sample_docx(), build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 34 - "submission.py"
Cohesion: 0.20
Nodes (6): CriterionErrorStat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest, build_group_journal()

### Community 36 - "analytics.py"
Cohesion: 0.13
Nodes (6): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), AcademicGroupRead, ExportFormat

### Community 37 - "SubmissionService"
Cohesion: 0.07
Nodes (12): _extract_submission_payload(), submit_practical_work(), update_practical_grading_rules(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade(), GradingRulesUpdateRequest (+4 more)

### Community 40 - "GradebookPage.tsx"
Cohesion: 0.11
Nodes (23): @tanstack/react-query@^5.60.0, extractApiErrorMessage(), COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard() (+15 more)

### Community 41 - "DomainError"
Cohesion: 0.10
Nodes (9): require_role(), role_checker(), ExtractedSubmissionPayload, DomainError, PlagiarismDetectedError, QuizNotPassedError, create_application(), _enum_values() (+1 more)

### Community 42 - "test_submit_all_four_practical_formats_via_api"
Cohesion: 0.12
Nodes (10): make_auth_headers(), SqliteAsyncSessionAdapter, _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_health_check_and_jwt_login_flow(), test_submission_blocked_without_passed_quiz_and_unlocked_after_70_percent() (+2 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.21
Nodes (14): BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta, FORMAT_BADGE_LABELS, formatFileSize(), LectureMarkdownRenderer() (+6 more)

### Community 45 - "HtmlSandbox.tsx"
Cohesion: 0.14
Nodes (16): dependencies, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox() (+8 more)

### Community 52 - "User"
Cohesion: 0.09
Nodes (13): get_current_user(), login(), read_current_user(), refresh_tokens(), serialize_user(), create_access_token(), create_refresh_token(), create_token_pair() (+5 more)

### Community 53 - "courses.py"
Cohesion: 0.11
Nodes (11): downgrade(), upgrade(), _serialize_practical_teacher(), PracticalStudentRead, PracticalTeacherRead, PracticalVariant, QuizSubmitRequest, QuizSubmitResponse (+3 more)

### Community 63 - "env.py"
Cohesion: 0.10
Nodes (6): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), get_settings(), Settings

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 550 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `DocxGrader` to `AccdbGrader`, `submission.py`, `GradingRule`, `SubmissionService`, `submission_service.py`, `InvalidFileFormatError`, `InvalidFileFormatError`, `.evaluate`, `courses.py`, `._evaluate_attribute_exists`, `XlsxGrader`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `schemas/__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11333333333333333 - nodes in this community are weakly interconnected._
- **Why does `DocxGrader` connect `DocxGrader` to `InvalidFileFormatError`, `GradingRule`, `._resolve_paragraph_level_font`, `._parse_expected_margins`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `User` (e.g. with `get_current_user()` and `require_role()`) actually correct?**
  _`User` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._