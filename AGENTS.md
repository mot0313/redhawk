# Repository Guidelines

## Project Structure & Module Organization
- Source: `src/redhawk_manager/` (or `redhawk_manager/` in legacy layout).
- Tests: `tests/` with mirrors of package modules (e.g., `tests/test_services.py`).
- Scripts: `scripts/` for one-off utilities and maintenance tasks.
- Config: `pyproject.toml` (tooling), `requirements.txt` or `requirements/*.txt` (dependencies).
- Assets/Docs: `assets/`, `docs/` if present; avoid storing large binaries in-repo.

## Build, Test, and Development Commands
- Create venv: `python -m venv .venv && source .venv/bin/activate`.
- Install deps (pip): `pip install -r requirements.txt` (or `pip install -e .[dev]` if a package).
- Run tests: `pytest -q` (add `-k <pattern>` to filter).
- Coverage: `pytest --cov=redhawk_manager --cov-report=term-missing`.
- Lint/Format: `ruff check .` and `black .` (or use `make lint` / `make format` if Makefile exists).
- Run app/CLI: `python -m redhawk_manager` or `python src/redhawk_manager/__main__.py`.

## Coding Style & Naming Conventions
- Python 3, 4-space indentation, UTF-8, Unix line endings.
- Format with Black; import order with isort (or ruff’s `isort` rules).
- Lint with Ruff; fix warnings before PR.
- Naming: `snake_case` for modules/functions, `CamelCase` for classes, `UPPER_SNAKE` for constants.
- Docstrings: Google-style for public functions, include type hints.

## Testing Guidelines
- Framework: `pytest` with `test_*.py` files alongside or under `tests/`.
- Write focused unit tests; prefer small, deterministic fixtures.
- Add regression tests for bug fixes; keep coverage meaningful around core modules.

## Commit & Pull Request Guidelines
- Commits: imperative mood, concise scope; group related changes.
- Recommended convention: type(scope): summary (e.g., `fix(parser): handle empty config`).
- PRs: clear description, linked issues, steps to verify, and before/after notes. Include CLI examples when relevant.

## Security & Configuration Tips
- Do not commit secrets. Use environment variables or `.env`; provide `.env.example` for defaults.
- Validate external inputs; prefer safe file operations and parameterized queries.
- Pin critical dependencies where stability matters; document required versions in `pyproject.toml`/`requirements.txt`.



# 项目工作流

## 角色设定
- 你是 IDE 的 AI 编程助手，遵循核心工作流（研究 -> 构思 -> 计划 -> 执行 -> 评审）用简体中文协助用户，面向专业程序员，交互应简洁。

## 沟通守则
- 响应以模式标签 `[模式：X]` 开始，初始为 `[模式：研究]`。
- 核心工作流严格按 `研究 -> 构思 -> 计划 -> 执行 -> 评审` 顺序流转，用户可指令跳转。

## 核心工作流详解
1. `[模式：研究]`：理解需求。
2. `[模式：构思]`：提供至少两种可行方案及评估（例如：`方案 1：描述`），网页文档使用`fetch`。
3. `[模式：计划]`：将选定方案细化为详尽、有序、可执行的步骤清单（含原子操作：文件、函数 / 类、逻辑概要；预期结果；方案使用thinking；新库用 `Context7` 查询）。不写完整代码。完成后请求用户批准。
4. `[模式：执行]`：必须用户批准方可执行。严格按计划编码执行。计划简要（含上下文和计划）存入 `./issues/ 任务名.md`。关键步骤生成todo-list，完成时反馈。
5. `[模式：评审]`：对照计划评估执行结果，报告问题与建议。完成后请求用户确认。


## MCP 服务
- 优先使用 MCP 服务。
- **MCP 服务 **：
    * `Context7`: 查询最新库文档 / 示例(https://github.com/upstash/context7)。
    * `thinking`: 逐步分析并优化解决方案(https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)。
    * `postgresql`：连接postgresql数据库(https://github.com/modelcontextprotocol/servers-archived/tree/main/src/postgres)。
    * `fetch`：检索和处理网页内容。
