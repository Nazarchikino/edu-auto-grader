# Graph Report - edu-auto-grader  (2026-11-18)

## Corpus Check
- 51 files · ~22,905 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 795 nodes · 1777 edges · 45 communities (27 shown, 18 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 48 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1c9f1850`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- postgres
- compilerOptions
- main.py
- main.tsx
- DomainError
- courses.py
- client.ts
- scripts
- vite-env.d.ts
- schemas/__init__.py
- metadata.py
- env.py
- models/course.py
- get_db
- edu-auto-grader-backend
- DocxDocument
- devDependencies
- eslint.config.js
- api.ts
- vite
- course.ts
- grading.ts
- login
- XlsxGrader
- DocxGrader
- AsyncSession
- GradingError
- BaseGrader
- graders/__init__.py
- xlsx_grader.py
- DomainError
- upsert_module_practical
- docx_grader.py
- _build_module_detail_read
- InvalidFileFormatError
- GradingReport
- SubmissionRecordProtocol
- get_current_user

## God Nodes (most connected - your core abstractions)
1. `DocxGrader` - 34 edges
2. `DomainError` - 28 edges
3. `User` - 28 edges
4. `XlsxGrader` - 25 edges
5. `PracticalFormat` - 23 edges
6. `GradingError` - 23 edges
7. `get_db()` - 22 edges
8. `InvalidFileFormatError` - 21 edges
9. `BaseGrader` - 21 edges
10. `compilerOptions` - 19 edges

## Surprising Connections (you probably didn't know these)
- `TokenPayload` --uses--> `UserRole`  [INFERRED]
  backend/app/schemas/auth.py → backend/app/models/user.py
- `UserBase` --uses--> `UserRole`  [INFERRED]
  backend/app/schemas/auth.py → backend/app/models/user.py
- `UserUpdate` --uses--> `UserRole`  [INFERRED]
  backend/app/schemas/auth.py → backend/app/models/user.py
- `CourseCreate` --uses--> `CourseSlug`  [INFERRED]
  backend/app/schemas/course.py → backend/app/models/course.py
- `CourseRead` --uses--> `CourseSlug`  [INFERRED]
  backend/app/schemas/course.py → backend/app/models/course.py

## Import Cycles
- None detected.

## Communities (45 total, 18 thin omitted)

### Community 0 - "package.json"
Cohesion: 0.17
Nodes (15): dependencies, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, name, private (+7 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "main.py"
Cohesion: 0.10
Nodes (3): create_application(), async_client(), test_health_check()

### Community 4 - "main.tsx"
Cohesion: 0.32
Nodes (5): react@^18.3.1, App(), queryClient, rootElement, react

### Community 5 - "DomainError"
Cohesion: 0.08
Nodes (5): PlagiarismDetectedError, QuizNotPassedError, calculate_variant_index(), QuizService, resolve_student_variant()

### Community 6 - "courses.py"
Cohesion: 0.09
Nodes (20): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+12 more)

### Community 7 - "client.ts"
Cohesion: 0.22
Nodes (3): axios@^1.7.7, apiClient, axios

### Community 8 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, typecheck

### Community 11 - "schemas/__init__.py"
Cohesion: 0.07
Nodes (20): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, ErrorResponse, LoginRequest, RefreshTokenRequest, TokenPayload, TokenResponse (+12 more)

### Community 13 - "metadata.py"
Cohesion: 0.15
Nodes (8): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), extract_core_xml_metadata(), extract_document_metadata(), _find_xml_text(), parse_core_xml_bytes(), ExtractedMetadata

### Community 14 - "env.py"
Cohesion: 0.09
Nodes (6): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), get_settings(), Settings

### Community 15 - "models/course.py"
Cohesion: 0.06
Nodes (30): downgrade(), upgrade(), Base, hash_password(), verify_password(), Course, CourseSlug, _enum_values() (+22 more)

### Community 17 - "get_db"
Cohesion: 0.12
Nodes (6): delete_quiz_question(), get_module(), get_practical_for_student(), list_module_quiz_questions_teacher(), submit_module_quiz(), get_db()

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

### Community 29 - "login"
Cohesion: 0.10
Nodes (9): login(), read_current_user(), refresh_tokens(), serialize_user(), create_access_token(), create_refresh_token(), create_token_pair(), decode_token() (+1 more)

### Community 32 - "AsyncSession"
Cohesion: 0.19
Nodes (7): create_course(), _fetch_user_progress_maps(), get_course(), list_courses(), _load_course_or_404(), _serialize_course(), update_course()

### Community 35 - "graders/__init__.py"
Cohesion: 0.23
Nodes (5): compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), normalize_code_for_hashing()

### Community 37 - "DomainError"
Cohesion: 0.20
Nodes (5): require_role(), role_checker(), create_quiz_question(), _load_module_or_404(), DomainError

### Community 38 - "upsert_module_practical"
Cohesion: 0.24
Nodes (4): get_practical_for_teacher(), _serialize_practical_teacher(), update_practical(), upsert_module_practical()

### Community 40 - "_build_module_detail_read"
Cohesion: 0.24
Nodes (3): _build_module_detail_read(), create_module(), update_module()

### Community 42 - "GradingReport"
Cohesion: 0.22
Nodes (4): CriterionResult, GradingReport, GradingRulesUpdateRequest, PlagiarismCheckResult

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 390 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DocxGrader` connect `DocxGrader` to `GradingError`, `BaseGrader`, `graders/__init__.py`, `docx_grader.py`, `BaseGrader`, `DocxDocument`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `User` (e.g. with `_build_access_course()` and `_build_excel_course()`) actually correct?**
  _`User` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `GradingError` connect `GradingError` to `BaseGrader`, `xlsx_grader.py`, `DomainError`, `DomainError`, `docx_grader.py`, `InvalidFileFormatError`, `DocxDocument`, `XlsxGrader`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `PracticalFormat` (e.g. with `ModuleSummaryRead` and `PracticalCreate`) actually correct?**
  _`PracticalFormat` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._