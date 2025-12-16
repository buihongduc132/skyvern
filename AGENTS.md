# Skyvern Agent Guide
This AGENTS.md file provides comprehensive guidance for AI agents working with the Skyvern codebase. Follow these guidelines to ensure consistency and quality in all contributions.

## Project Structure for Agent Navigation

- `/skyvern`: Main Python package
  - `/cli`: Command-line interface components
  - `/client`: Client implementations and integrations
  - `/forge`: Core automation logic and workflows
  - `/library`: Shared utilities and helpers
  - `/schemas`: Data models and validation schemas
  - `/services`: Business logic and service layers
  - `/utils`: Common utility functions
  - `/webeye`: Web interaction and browser automation
- `/skyvern-frontend`: Frontend application
- `/integrations`: Third-party service integrations
- `/alembic`: Database migrations
- `/scripts`: Utility and deployment scripts

## Coding Conventions for Agents

### Python Standards

- Use Python 3.11+ features and type hints
- Follow PEP 8 with a line length of 100 characters
- Use absolute imports for all modules
- Document all public functions and classes with Google-style docstrings
- Use `snake_case` for variables and functions, `PascalCase` for classes

### Asynchronous Programming

- Prefer async/await over callbacks
- Use `asyncio` for concurrency
- Always handle exceptions in async code
- Use context managers for resource cleanup

### Error Handling

- Use specific exception classes
- Include meaningful error messages
- Log errors with appropriate severity levels
- Never expose sensitive information in error messages

## Pull Request Process

1. **Branch Naming**
   - `feature/descriptive-name` for new features
   - `fix/issue-description` for bug fixes
   - `chore/task-description` for maintenance tasks

2. **PR Guidelines**
   - Reference related issues with `Fixes #123` or `Closes #123`
   - Include a clear description of changes
   - Update relevant documentation
   - Ensure all tests pass
   - Get at least one approval before merging

3. **Commit Message Format**
   ```
   [Component] Action: Brief description
   
   More detailed explanation if needed.
   
   - Bullet points for additional context
   - Reference issues with #123
   ```

## Code Quality Checks

Before submitting code, run:
```bash
pre-commit run --all-files
```

## Performance Considerations
- Optimize database queries
- Use appropriate data structures
- Implement caching where beneficial
- Monitor memory usage

## Security Best Practices
- Never commit secrets or credentials
- Validate all inputs
- Use environment variables for configuration
- Follow the principle of least privilege
- Keep dependencies updated

## Getting Help
- Check existing issues before opening new ones
- Reference relevant documentation
- Provide reproduction steps for bugs
- Be specific about the problem and expected behavior

<lesson_learn>
---
2025-12-16T14:53:44+07:00: Playwright Chromium missing breaks remote runs
Context: Remote run failed with BrowserType.launch_persistent_context “Executable doesn't exist” under ms-playwright cache.
Solutions: Install browsers (`python -m playwright install chromium`); add startup check to auto-install if missing.
Ref: flow/lesson_learn/skyvern_playwright_browsers/2025-12-16_playwright_missing_chromium.md
</lesson_learn>

<lesson_learn>
---
2025-12-16T22:25:00+07:00: Local Skyvern auth + bhd-litellm quota interaction
Context: Self-hosted Skyvern OSS on bhd-main with backend on 18000, UI on 28742, Postgres on 15432, and bhd-litellm (glm46v) backing OPENAI_COMPATIBLE; initial 403s then 500s on workflow creation.
Solutions: Point DATABASE_STRING to dedicated Postgres; run Alembic migrations; call /v1/internal/auth/repair to generate real JWT and sync SKYVERN_API_KEY/VITE_SKYVERN_API_KEY; identify remaining 500s as upstream glm46v quota errors from litellm, not Skyvern-core bugs.
Ref: flow/findings/2025-12-16_skyvern_selfhost_auth_and_llm.md
</lesson_learn>

<lesson_learn>
---
2025-12-16T15:33:00+07:00: UI "no progress" due to missing stream frames + backend reload crash
Context: UI served, but workflow run stream never shows frames; backend sometimes not reachable after restart.
Solutions: Write streaming PNG on screenshot artifact creation; start server from `temp` with `.env` exported; load `.env` before settings import; ignore postgres-data during pytest.
Ref: flow/lesson_learn/skyvern_ui_no_progress/2025-12-16_ui_no_progress.md
</lesson_learn>

<lesson_learn>
---
2025-12-16T23:35:00+07:00: TaskV2 planner loops lacked debuggable logs
Context: TaskV2 hit “50 planning iterations” with only thought events; thought fields stayed null and no LLM artifacts existed for planner calls.
Solutions: Update thought fields when value is not None; add `LOG_LLM_ARTIFACTS_FOR_THOUGHTS` to persist prompt/request/response artifacts for Thought-only LLM calls.
Ref: flow/lesson_learn/skyvern_taskv2_planner_logging/2025-12-16_taskv2_planner_missing_debug_logs.md
</lesson_learn>
