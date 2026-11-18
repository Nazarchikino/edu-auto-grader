# Graph Report - edu-auto-grader  (2026-11-18)

## Corpus Check
- 33 files · ~8,535 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 270 nodes · 415 edges · 23 communities (10 shown, 13 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ab09d6c7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- postgres
- compilerOptions
- main.py
- main.tsx
- DomainError
- config.py
- client.ts
- scripts
- vite-env.d.ts
- env.py
- course.py
- edu-auto-grader-backend
- run_seed

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 19 edges
2. `Base` - 15 edges
3. `build_seed_bundle()` - 12 edges
4. `User` - 12 edges
5. `Module` - 10 edges
6. `Practical` - 10 edges
7. `Course` - 9 edges
8. `QuizQuestion` - 9 edges
9. `DomainError` - 9 edges
10. `_build_word_course()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `create_application()` --uses--> `DomainError`  [INFERRED]
  backend/app/main.py → backend/app/core/exceptions.py
- `_build_word_course()` --calls--> `Course`  [EXTRACTED]
  backend/app/seed.py → backend/app/models/course.py
- `_build_word_course()` --calls--> `Module`  [EXTRACTED]
  backend/app/seed.py → backend/app/models/course.py
- `_build_word_course()` --calls--> `Practical`  [EXTRACTED]
  backend/app/seed.py → backend/app/models/course.py
- `_build_word_course()` --calls--> `QuizQuestion`  [EXTRACTED]
  backend/app/seed.py → backend/app/models/course.py

## Import Cycles
- None detected.

## Communities (23 total, 13 thin omitted)

### Community 0 - "package.json"
Cohesion: 0.06
Nodes (46): dependencies, axios@^1.7.7, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, devDependencies (+38 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "main.py"
Cohesion: 0.11
Nodes (4): downgrade(), upgrade(), async_client(), test_health_check()

### Community 4 - "main.tsx"
Cohesion: 0.32
Nodes (5): react@^18.3.1, App(), queryClient, rootElement, react

### Community 5 - "DomainError"
Cohesion: 0.12
Nodes (6): DomainError, GradingError, InvalidFileFormatError, PlagiarismDetectedError, QuizNotPassedError, create_application()

### Community 8 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, typecheck

### Community 14 - "env.py"
Cohesion: 0.16
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 15 - "course.py"
Cohesion: 0.09
Nodes (20): Base, Course, CourseSlug, _enum_values(), Module, Practical, PracticalFormat, QuizQuestion (+12 more)

### Community 22 - "run_seed"
Cohesion: 0.15
Nodes (7): get_db(), main(), run_seed(), seed_database(), SeedBundle, SeedSummary, summarize_bundle()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 129 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Base` connect `course.py` to `env.py`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.06207482993197279 - nodes in this community are weakly interconnected._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._
- **Should `DomainError` be split into smaller, more focused modules?**
  _Cohesion score 0.11666666666666667 - nodes in this community are weakly interconnected._