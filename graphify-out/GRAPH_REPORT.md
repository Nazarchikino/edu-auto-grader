# Graph Report - edu-auto-grader  (2026-11-19)

## Corpus Check
- 64 files · ~41,100 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1147 nodes · 3079 edges · 48 communities (33 shown, 15 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 326 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `83c76efd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- LoginPage.tsx
- postgres
- compilerOptions
- InvalidFileFormatError
- main.tsx
- db_session
- courses.py
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
- PracticalTeacherRead
- DomainError
- XlsxGrader
- DocxGrader
- AccdbGrader
- build_sample_docx
- _compile_jsonb_for_sqlite
- .execute
- build_accdb_bytes
- SubmissionService
- Sidebar.tsx
- 0001_initial_schema.py
- UserRole
- test_submit_all_four_practical_formats_via_api
- GradingRule
- export_group_journal
- courses.py
- submission_service.py
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
- `get_group_journal()` --uses--> `GroupJournalRead`  [INFERRED]
  backend/app/api/v1/analytics.py → backend/app/schemas/submission.py
- `_extract_submission_payload()` --uses--> `HtmlSubmissionRequest`  [INFERRED]
  backend/app/api/v1/practicals.py → backend/app/schemas/submission.py
- `PracticalColumnInfo` --uses--> `CourseSlug`  [INFERRED]
  backend/app/services/export_service.py → backend/app/models/course.py
- `create_course()` --uses--> `Course`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/models/course.py
- `list_courses()` --uses--> `Course`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/models/course.py

## Import Cycles
- None detected.

## Communities (48 total, 15 thin omitted)

### Community 0 - "LoginPage.tsx"
Cohesion: 0.19
Nodes (12): lucide-react@^0.460.0, react-router-dom@^6.28.0, ROLE_LABELS, RoleGuardProps, extractApiErrorMessage(), DEMO_ACCOUNTS, DemoAccount, isPathAllowedForRole() (+4 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "InvalidFileFormatError"
Cohesion: 0.09
Nodes (8): GradingError, InvalidFileFormatError, BaseGrader, GraderFactory, _format_cell_value(), _is_wrapped_in_parens(), PracticalFormat, test_grader_factory_resolves_all_four_formats()

### Community 4 - "main.tsx"
Cohesion: 0.22
Nodes (9): dependencies, react@^18.3.1, react-dom@^18.3.1, @tanstack/react-query@^5.60.0, queryClient, rootElement, react, react-dom (+1 more)

### Community 5 - "db_session"
Cohesion: 0.20
Nodes (3): async_client(), db_session(), _fast_seed_hash_password()

### Community 6 - "courses.py"
Cohesion: 0.11
Nodes (15): _build_module_detail_read(), AcademicGroupBase, AcademicGroupCreate, CourseCreate, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleUpdate (+7 more)

### Community 7 - "AuthContext.tsx"
Cohesion: 0.18
Nodes (17): axios@^1.7.7, apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext (+9 more)

### Community 8 - "QuizService"
Cohesion: 0.13
Nodes (6): get_practical_for_student(), submit_module_quiz(), PracticalStudentRead, QuizSubmitRequest, QuizSubmitResponse, QuizService

### Community 11 - "export_service.py"
Cohesion: 0.05
Nodes (20): AcademicGroupRead, CriterionErrorStat, ExportFormat, GroupJournalRead, GroupJournalStudentCell, _auto_adjust_worksheet_columns(), build_content_disposition(), build_group_journal() (+12 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (17): check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism(), extract_core_xml_metadata() (+9 more)

### Community 14 - "env.py"
Cohesion: 0.16
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 15 - "seed.py"
Cohesion: 0.17
Nodes (9): AcademicGroup, build_seed_bundle(), hash_password(), main(), run_seed(), seed_database(), SeedBundle, SeedSummary (+1 more)

### Community 17 - "get_db"
Cohesion: 0.14
Nodes (14): create_course(), create_module(), create_quiz_question(), delete_quiz_question(), get_module(), get_practical_for_teacher(), list_module_quiz_questions_teacher(), _load_course_or_404() (+6 more)

### Community 22 - "HtmlGrader"
Cohesion: 0.08
Nodes (11): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), HtmlGrader, _is_doctype_target(), _normalize_selector(), _normalize_text(), _parse_text_match_expected() (+3 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (41): @monaco-editor/react@4.6.0, devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0 (+33 more)

### Community 24 - "App.tsx"
Cohesion: 0.28
Nodes (14): App(), ProtectedAppLayout(), RoleHomeRedirect(), WorkspaceSectionPlaceholder(), WorkspaceSectionProps, Navbar(), NavbarProps, resolvePageTitle() (+6 more)

### Community 25 - "api.ts"
Cohesion: 0.10
Nodes (24): AuthContextValue, AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, CriterionErrorStat, EXPORT_FORMATS, ExportFormat, GroupJournalRead (+16 more)

### Community 27 - "course.ts"
Cohesion: 0.09
Nodes (28): COURSE_SLUGS, CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+20 more)

### Community 28 - "PracticalTeacherRead"
Cohesion: 0.18
Nodes (6): _serialize_practical_teacher(), PracticalTeacherRead, PracticalVariant, calculate_variant_index(), resolve_student_variant(), serialize_practical_teacher()

### Community 29 - "DomainError"
Cohesion: 0.05
Nodes (22): role_checker(), login(), read_current_user(), refresh_tokens(), serialize_user(), DomainError, PlagiarismDetectedError, QuizNotPassedError (+14 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.08
Nodes (3): _canonicalize_formula(), _try_parse_numeric(), XlsxGrader

### Community 32 - "AccdbGrader"
Cohesion: 0.07
Nodes (9): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _parse_ddl_column_type(), _resolve_canonical_type() (+1 more)

### Community 33 - "build_sample_docx"
Cohesion: 0.27
Nodes (4): build_sample_docx(), build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 36 - "build_accdb_bytes"
Cohesion: 0.31
Nodes (4): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page()

### Community 37 - "SubmissionService"
Cohesion: 0.06
Nodes (12): _extract_submission_payload(), ExtractedSubmissionPayload, submit_practical_work(), update_practical_grading_rules(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade() (+4 more)

### Community 38 - "Sidebar.tsx"
Cohesion: 0.29
Nodes (6): DISCIPLINE_CHIPS, DisciplineChip, NavigationItem, ROLE_NAVIGATION_MAP, ROLE_SECTION_TITLES, SidebarProps

### Community 41 - "UserRole"
Cohesion: 0.12
Nodes (9): require_role(), _enum_values(), UserRole, UserBase, UserCreate, UserUpdate, GroupJournalRow, HtmlSubmissionRequest (+1 more)

### Community 42 - "test_submit_all_four_practical_formats_via_api"
Cohesion: 0.18
Nodes (7): make_auth_headers(), _get_user_by_email(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_health_check_and_jwt_login_flow(), test_submission_blocked_without_passed_quiz_and_unlocked_after_70_percent(), test_submit_all_four_practical_formats_via_api(), test_teacher_update_rules_manual_grade_and_group_export()

### Community 43 - "GradingRule"
Cohesion: 0.15
Nodes (11): GradingRule, GradingRuleType, build_sample_accdb(), test_accdb_grader_detects_missing_schema_elements_and_invalid_header(), test_accdb_grader_evaluates_tables_columns_and_types(), test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_html_grader_detects_missing_tags_and_rejects_empty_code() (+3 more)

### Community 50 - "export_group_journal"
Cohesion: 0.19
Nodes (4): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format()

### Community 52 - "courses.py"
Cohesion: 0.16
Nodes (7): get_current_user(), _fetch_user_progress_maps(), get_course(), list_courses(), _serialize_course(), CourseRead, ModuleSummaryRead

### Community 55 - "submission_service.py"
Cohesion: 0.14
Nodes (15): Base, Course, CourseSlug, _enum_values(), Module, Practical, QuizQuestion, QuizAttempt (+7 more)

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 537 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `AccdbGrader`, `InvalidFileFormatError`, `SubmissionService`, `courses.py`, `InvalidFileFormatError`, `BaseGrader`, `courses.py`, `HtmlGrader`, `submission_service.py`, `PracticalTeacherRead`, `XlsxGrader`, `DocxGrader`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `PracticalFormat` connect `InvalidFileFormatError` to `AccdbGrader`, `SubmissionService`, `courses.py`, `QuizService`, `GradingRule`, `seed.py`, `BaseGrader`, `courses.py`, `HtmlGrader`, `submission_service.py`, `PracticalTeacherRead`, `XlsxGrader`, `DocxGrader`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `DomainError` (e.g. with `login()` and `refresh_tokens()`) actually correct?**
  _`DomainError` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._