Based on the provided PRD, here's a concise **project overview** followed by a comprehensive `RULES.md` that will guide technical implementation, development standards, and team alignment.

---

## 📘 Project Overview

**Excel-to-Python Formula Converter** is a CLI and REST API-based tool that allows users to upload `.xlsx`, `.csv`, or `.tsv` files and get a clean, executable `.py` script that replicates the logic defined in spreadsheet formulas. The system uses the [`formulas`](https://formulas.readthedocs.io/en/stable/) library for extraction and supports a sandboxed Python execution flow for output validation.

Key goals include seamless Excel-to-Python migration, reproducibility, and high formula coverage (90%+). The MVP excludes UI and focuses solely on formula logic conversion and secure runtime execution.

---

# 📜 RULES.md

## 1. ✅ TECHNOLOGY STACK DEFINITION

### Core Technologies

| Component            | Tech/Tool                        | Version        |
| -------------------- | -------------------------------- | -------------- |
| Language             | Python                           | 3.10+          |
| Formula extraction   | `formulas` library               | 1.2.2 (pinned) |
| API framework        | FastAPI                          | Latest stable  |
| CLI utility          | `argparse` or `typer`            | Latest stable  |
| File processing      | `openpyxl`, `pandas`             | Latest stable  |
| Execution sandboxing | Docker with AppArmor/SECCOMP     | Ubuntu 22.04   |
| Async job handling   | `asyncio` / `concurrent.futures` | Built-in       |
| Hosting              | Azure App Service or Azure VM    | N/A            |

---

## 2. ⚙️ TECHNICAL PREFERENCES

### Naming Conventions

| Entity                | Convention                  | Example                     |
| --------------------- | --------------------------- | --------------------------- |
| Python Variables      | snake\_case                 | `net_profit_q1`             |
| Generated Functions   | snake\_case, prefix `calc_` | `calc_total_cost`           |
| Headers with spaces   | `_` separator, lowercase    | `Revenue Q2` → `revenue_q2` |
| Ambiguous headers     | Append row index            | `revenue_q2_1`              |
| Cells without headers | `cell_<col><row>`           | `cell_A1`                   |

### Code Organization

```
/excel_to_python/
  ├── cli/               # CLI handlers
  ├── api/               # FastAPI routes
  ├── core/              # Formula parser, variable naming logic
  ├── sandbox/           # Execution environment
  ├── templates/         # Code generation templates
  ├── tests/             # Unit and integration tests
  └── utils/             # Logging, helpers
```

### Architectural Patterns

* **Layered architecture** with:

  * File handling & parsing layer
  * Formula-to-Python mapping layer
  * Code generation layer
  * Execution/sandboxing layer
* **Template-driven code generation** using string templates
* **Async REST API** with `FastAPI` for concurrency

### Data Handling & Execution

* Input file is parsed, not persisted beyond execution
* Execution uses `exec()` in an isolated container with:

  * CPU: max 30s
  * RAM: 128MB
  * No network access

### Performance Optimization

* Pre-validate file type and headers to skip unnecessary parsing
* Minimize external dependencies during code execution
* Reuse Docker containers (warm pool) where safe
* Use async workers for upload handling

### Security Practices

* Use **AppArmor or SECCOMP** for sandboxing
* Validate file size (<10MB) and content
* Timeout and memory limits on subprocess/Docker execution
* Escape potentially dangerous formula outputs

---

## 3. 🧪 DEVELOPMENT STANDARDS

### Testing

* **90%+ unit test coverage** for:

  * Formula parsing
  * Naming logic
  * Script generation
* **5 benchmark Excel files** with expected output hashes
* CLI and REST integration tests
* Race condition and concurrency tests (≥10 uploads/min)

### Documentation

* Docstrings for all functions (Google-style)
* Top-level `README.md` with CLI/API usage
* `examples/` folder with test Excel files + outputs

### Error Handling & Logging

* All parsing/execution errors must log:

  * Sheet name
  * Formula location
  * Warning or fallback applied
* Warnings output:

  * REST: `warnings[]` in JSON
  * CLI: `stderr` + `log.txt`

### Accessibility (N/A for MVP UI)

* Not applicable (CLI/API only)

### Responsive Design (N/A)

* Not applicable

---

## 4. 🚀 IMPLEMENTATION PRIORITIES

### Core Features (Must-Have)

* CLI + REST support for `.xlsx`, `.csv`, `.tsv`
* Extract all formulas using `formulas`
* Generate clean `.py` script from formulas
* Fallback placeholders for unsupported logic

### Enhancement Features (Should/Could-Have)

* Cross-sheet formula resolution
* Logging of skipped formulas and unsupported features
* Script execution + result return (sandboxed)

### Phases

| Phase                | Deadline  |
| -------------------- | --------- |
| Core CLI + API logic | July 7    |
| Azure Deployment     | July 7    |
| Testing & Feedback   | July 8-10 |
| Enhancements         | July 11+  |

### Quality Thresholds

* <10s processing for <10MB file
* 95%+ API success (200 OK)
* 0 critical sandbox violations
* Match expected outputs for 5 test sheets

---

## 5. 📌 GENERAL GUIDELINES

### Adherence to Requirements

* Features not explicitly in scope must not be implemented
* Use `# TODO:` only with accompanying `issue_id`

### Code Quality

* Follow **PEP8**
* Use type hints for all public methods
* No global mutable state
* Clearly separate concerns (e.g., parsing vs. generation)

### Completeness

* No stubbed logic in output
* Each formula must map to an executable Python expression or fallback
* Include logging for each skipped or transformed formula

### Communication Guidelines

* Raise an issue if:

  * Formula logic is ambiguous
  * Headers are missing/merged across rows
* Use inline warnings in logs and `warnings[]` for every non-critical fallback

### Handling Ambiguity

* Fallback to cell references (`cell_B3`) when headers are malformed
* Document and log all assumptions
* Use config flags for any heuristic logic (e.g., flattening headers)

---

