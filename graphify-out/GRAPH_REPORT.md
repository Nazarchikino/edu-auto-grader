# Graph Report - edu-auto-grader  (2026-11-18)

## Corpus Check
- 40 files · ~11,291 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 430 nodes · 714 edges · 33 communities (19 shown, 14 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ec5d2726`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- postgres
- compilerOptions
- main.py
- main.tsx
- DomainError
- schemas/course.py
- client.ts
- scripts
- vite-env.d.ts
- env.py
- course.py
- auth.py
- edu-auto-grader-backend
- submission.py
- devDependencies
- eslint.config.js
- api.ts
- vite
- course.ts
- grading.ts
- GradingRule
- CourseSlug
- GradingRuleType
- ExportFormat

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 19 edges
2. `Base` - 15 edges
3. `User` - 12 edges
4. `build_seed_bundle()` - 12 edges
5. `Module` - 10 edges
6. `Practical` - 10 edges
7. `Course` - 9 edges
8. `QuizQuestion` - 9 edges
9. `DomainError` - 9 edges
10. `PracticalFormat` - 8 edges

## Surprising Connections (you probably didn't know these)
- `PracticalSummaryRead` --references--> `PracticalFormat`  [EXTRACTED]
  frontend/src/types/course.ts → frontend/src/types/grading.ts
- `PracticalStudentRead` --references--> `PracticalFormat`  [EXTRACTED]
  frontend/src/types/course.ts → frontend/src/types/grading.ts
- `ModuleSummaryRead` --references--> `PracticalFormat`  [EXTRACTED]
  frontend/src/types/course.ts → frontend/src/types/grading.ts
- `create_application()` --uses--> `DomainError`  [INFERRED]
  backend/app/main.py → backend/app/core/exceptions.py
- `PracticalCreate` --uses--> `GradingRule`  [INFERRED]
  backend/app/schemas/course.py → backend/app/schemas/grading.py

## Import Cycles
- None detected.

## Communities (33 total, 14 thin omitted)

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

### Community 5 - "DomainError"
Cohesion: 0.12
Nodes (6): DomainError, GradingError, InvalidFileFormatError, PlagiarismDetectedError, QuizNotPassedError, create_application()

### Community 6 - "schemas/course.py"
Cohesion: 0.08
Nodes (16): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalStudentRead (+8 more)

### Community 7 - "client.ts"
Cohesion: 0.22
Nodes (3): axios@^1.7.7, apiClient, axios

### Community 8 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, typecheck

### Community 14 - "env.py"
Cohesion: 0.09
Nodes (6): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), get_settings(), Settings

### Community 15 - "course.py"
Cohesion: 0.06
Nodes (27): downgrade(), upgrade(), Base, get_db(), Course, _enum_values(), Module, Practical (+19 more)

### Community 16 - "auth.py"
Cohesion: 0.14
Nodes (12): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, ErrorResponse, LoginRequest, RefreshTokenRequest, TokenPayload, TokenResponse (+4 more)

### Community 22 - "submission.py"
Cohesion: 0.10
Nodes (12): CriterionResult, ExtractedMetadata, GradingReport, GradingRulesUpdateRequest, PlagiarismCheckResult, CriterionErrorStat, GroupJournalRead, GroupJournalRow (+4 more)

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

### Community 29 - "GradingRule"
Cohesion: 0.25
Nodes (4): PracticalCreate, PracticalTeacherRead, PracticalUpdate, GradingRule

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 212 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CourseSlug` connect `CourseSlug` to `submission.py`, `schemas/course.py`, `course.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `Base` connect `course.py` to `env.py`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `DomainError` be split into smaller, more focused modules?**
  _Cohesion score 0.11666666666666667 - nodes in this community are weakly interconnected._
- **Should `schemas/course.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08235294117647059 - nodes in this community are weakly interconnected._