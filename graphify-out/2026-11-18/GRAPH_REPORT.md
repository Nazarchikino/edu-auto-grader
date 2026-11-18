# Graph Report - edu-auto-grader  (2026-11-18)

## Corpus Check
- 56 files · ~31,294 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 980 nodes · 2337 edges · 58 communities (32 shown, 26 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 68 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8f2ea0a2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- postgres
- compilerOptions
- main.py
- main.tsx
- QuizService
- courses.py
- client.ts
- scripts
- vite-env.d.ts
- schemas/__init__.py
- metadata.py
- env.py
- seed.py
- UUID
- edu-auto-grader-backend
- HtmlGrader
- devDependencies
- eslint.config.js
- api.ts
- vite
- course.ts
- grading.ts
- security.py
- XlsxGrader
- DocxGrader
- AccdbGrader
- GradingError
- BaseGrader
- courses.py
- xlsx_grader.py
- DomainError
- get_db
- User
- submit_practical_work
- evaluate_plagiarism
- Depends
- create_application
- upsert_module_practical
- submission_service.py
- create_course
- 0001_initial_schema.py
- seed_database
- _format_number
- get_current_user
- _find_xml_text

## God Nodes (most connected - your core abstractions)
1. `DomainError` - 36 edges
2. `DocxGrader` - 34 edges
3. `User` - 34 edges
4. `GradingError` - 32 edges
5. `InvalidFileFormatError` - 32 edges
6. `get_db()` - 28 edges
7. `PracticalFormat` - 26 edges
8. `XlsxGrader` - 25 edges
9. `BaseGrader` - 25 edges
10. `SubmissionService` - 21 edges

## Surprising Connections (you probably didn't know these)
- `submit_practical_work()` --uses--> `SubmissionService`  [INFERRED]
  backend/app/api/v1/practicals.py → backend/app/services/submission_service.py
- `update_practical_grading_rules()` --uses--> `SubmissionService`  [INFERRED]
  backend/app/api/v1/practicals.py → backend/app/services/submission_service.py
- `list_my_submissions()` --uses--> `SubmissionService`  [INFERRED]
  backend/app/api/v1/submissions.py → backend/app/services/submission_service.py
- `list_submissions()` --uses--> `SubmissionService`  [INFERRED]
  backend/app/api/v1/submissions.py → backend/app/services/submission_service.py
- `get_submission_detail()` --uses--> `SubmissionService`  [INFERRED]
  backend/app/api/v1/submissions.py → backend/app/services/submission_service.py

## Import Cycles
- None detected.

## Communities (58 total, 26 thin omitted)

### Community 0 - "package.json"
Cohesion: 0.17
Nodes (15): dependencies, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, name, private (+7 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 4 - "main.tsx"
Cohesion: 0.32
Nodes (5): react@^18.3.1, App(), queryClient, rootElement, react

### Community 6 - "courses.py"
Cohesion: 0.08
Nodes (18): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+10 more)

### Community 7 - "client.ts"
Cohesion: 0.22
Nodes (3): axios@^1.7.7, apiClient, axios

### Community 8 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, typecheck

### Community 11 - "schemas/__init__.py"
Cohesion: 0.05
Nodes (25): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, ErrorResponse, LoginRequest, RefreshTokenRequest, TokenPayload, TokenResponse (+17 more)

### Community 13 - "metadata.py"
Cohesion: 0.18
Nodes (9): InvalidFileFormatError, compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), extract_core_xml_metadata(), extract_document_metadata(), normalize_code_for_hashing() (+1 more)

### Community 14 - "env.py"
Cohesion: 0.08
Nodes (7): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), get_settings(), Settings, main()

### Community 15 - "seed.py"
Cohesion: 0.12
Nodes (19): Base, Course, CourseSlug, _enum_values(), Module, Practical, PracticalFormat, QuizQuestion (+11 more)

### Community 17 - "UUID"
Cohesion: 0.23
Nodes (6): _fetch_user_progress_maps(), get_course(), list_courses(), _load_course_or_404(), _serialize_course(), update_course()

### Community 22 - "HtmlGrader"
Cohesion: 0.08
Nodes (10): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), HtmlGrader, _is_doctype_target(), _normalize_selector(), _normalize_text(), _parse_text_match_expected() (+2 more)

### Community 23 - "devDependencies"
Cohesion: 0.13
Nodes (15): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, postcss@^8.4.49, tailwindcss@^3.4.15, @types/react@^18.3.12, @types/react-dom@^18.3.1, typescript@~5.6.3 (+7 more)

### Community 24 - "eslint.config.js"
Cohesion: 0.18
Nodes (10): @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, typescript-eslint@^8.15.0, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+2 more)

### Community 25 - "api.ts"
Cohesion: 0.09
Nodes (23): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, CriterionErrorStat, ErrorResponse, EXPORT_FORMATS, ExportFormat, GroupJournalRead (+15 more)

### Community 26 - "vite"
Cohesion: 0.40
Nodes (4): vite@^5.4.11, @vitejs/plugin-react@^4.3.3, vite, @vitejs/plugin-react

### Community 27 - "course.ts"
Cohesion: 0.13
Nodes (22): COURSE_SLUGS, CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+14 more)

### Community 28 - "grading.ts"
Cohesion: 0.20
Nodes (10): SubmissionRead, CourseSlug, CriterionResult, ExtractedMetadata, GRADING_RULE_TYPES, GradingReport, GradingRulesUpdateRequest, GradingRuleType (+2 more)

### Community 29 - "security.py"
Cohesion: 0.09
Nodes (11): login(), read_current_user(), refresh_tokens(), serialize_user(), create_access_token(), create_refresh_token(), create_token_pair(), decode_token() (+3 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.11
Nodes (3): _canonicalize_formula(), _try_parse_numeric(), XlsxGrader

### Community 32 - "AccdbGrader"
Cohesion: 0.06
Nodes (13): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page() (+5 more)

### Community 35 - "courses.py"
Cohesion: 0.15
Nodes (4): require_role(), role_checker(), _enum_values(), UserRole

### Community 37 - "DomainError"
Cohesion: 0.14
Nodes (4): DomainError, PlagiarismDetectedError, serialize_submission(), SubmissionService

### Community 39 - "get_db"
Cohesion: 0.16
Nodes (6): get_practical_for_student(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade(), get_db()

### Community 40 - "User"
Cohesion: 0.24
Nodes (5): _build_module_detail_read(), create_module(), get_module(), _load_module_or_404(), update_module()

### Community 42 - "submit_practical_work"
Cohesion: 0.14
Nodes (4): _extract_submission_payload(), ExtractedSubmissionPayload, submit_practical_work(), update_practical_grading_rules()

### Community 43 - "evaluate_plagiarism"
Cohesion: 0.14
Nodes (5): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), SubmissionRecordProtocol, PlagiarismCheckResult

### Community 44 - "Depends"
Cohesion: 0.19
Nodes (4): create_quiz_question(), delete_quiz_question(), list_module_quiz_questions_teacher(), QuizQuestionTeacherRead

### Community 46 - "upsert_module_practical"
Cohesion: 0.21
Nodes (4): get_practical_for_teacher(), _serialize_practical_teacher(), update_practical(), upsert_module_practical()

### Community 47 - "submission_service.py"
Cohesion: 0.20
Nodes (5): QuizNotPassedError, PracticalVariant, calculate_variant_index(), resolve_student_variant(), serialize_practical_teacher()

### Community 50 - "seed_database"
Cohesion: 0.31
Nodes (4): run_seed(), seed_database(), SeedSummary, summarize_bundle()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 478 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingError` connect `GradingError` to `AccdbGrader`, `BaseGrader`, `courses.py`, `xlsx_grader.py`, `DomainError`, `.build_criterion_result`, `.__init__`, `schemas/__init__.py`, `metadata.py`, `HtmlGrader`, `XlsxGrader`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `User` (e.g. with `_build_access_course()` and `_build_excel_course()`) actually correct?**
  _`User` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `DomainError` to `GradingError`, `courses.py`, `QuizService`, `User`, `.__init__`, `Depends`, `upsert_module_practical`, `submission_service.py`, `create_course`, `UUID`, `get_current_user`, `security.py`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `DocxGrader` connect `DocxGrader` to `GradingError`, `BaseGrader`, `.build_criterion_result`, `schemas/__init__.py`, `metadata.py`, `BaseGrader`, `_format_number`, `._select_sections`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._