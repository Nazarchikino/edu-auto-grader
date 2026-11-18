# Graph Report - edu-auto-grader  (2026-11-18)

## Corpus Check
- 28 files · ~4,664 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 4, .css 1)

## Summary
- 200 nodes · 235 edges · 21 communities (7 shown, 14 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8264a9da`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- postgres
- compilerOptions
- main.py
- dependencies
- DomainError
- config.py
- scripts
- vite-env.d.ts
- user.py
- edu-auto-grader-backend

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 19 edges
2. `DomainError` - 9 edges
3. `postgres` - 8 edges
4. `Base` - 6 edges
5. `create_application()` - 6 edges
6. `scripts` - 6 edges
7. `UserRole` - 5 edges
8. `GradingError` - 5 edges
9. `Settings` - 5 edges
10. `healthcheck` - 5 edges

## Surprising Connections (you probably didn't know these)
- `create_application()` --uses--> `DomainError`  [INFERRED]
  backend/app/main.py → backend/app/core/exceptions.py
- `AcademicGroup` --inherits--> `Base`  [EXTRACTED]
  backend/app/models/user.py → backend/app/core/database.py
- `User` --inherits--> `Base`  [EXTRACTED]
  backend/app/models/user.py → backend/app/core/database.py

## Import Cycles
- None detected.

## Communities (21 total, 14 thin omitted)

### Community 0 - "package.json"
Cohesion: 0.09
Nodes (33): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+25 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 4 - "dependencies"
Cohesion: 0.08
Nodes (19): dependencies, axios@^1.7.7, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0 (+11 more)

### Community 5 - "DomainError"
Cohesion: 0.12
Nodes (6): DomainError, GradingError, InvalidFileFormatError, PlagiarismDetectedError, QuizNotPassedError, create_application()

### Community 8 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, typecheck

### Community 15 - "user.py"
Cohesion: 0.11
Nodes (6): Base, get_db(), AcademicGroup, _enum_values(), User, UserRole

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 104 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `axios` connect `dependencies` to `package.json`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.08571428571428572 - nodes in this community are weakly interconnected._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.082010582010582 - nodes in this community are weakly interconnected._
- **Should `DomainError` be split into smaller, more focused modules?**
  _Cohesion score 0.11666666666666667 - nodes in this community are weakly interconnected._