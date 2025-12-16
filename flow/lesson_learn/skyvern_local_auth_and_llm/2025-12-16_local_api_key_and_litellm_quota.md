# Lesson: Local Skyvern auth + litellm quota

## Time

- 2025-12-16T22:25:00+07:00

## Context

- Self-hosted Skyvern OSS on bhd-main with:
  - Backend on localhost:18000 and ENV=local.
  - UI on localhost:28742 (Vite-based frontend).
  - Postgres in docker (skyvern-postgres-1 on localhost:15432).
  - LLM via bhd-litellm (OPENAI_COMPATIBLE glm46v).
- Symptoms:
  - Initially all APIs returned 403 Invalid credentials.
  - After auth bootstrap, /v1/workflows/create-from-prompt produced 500 errors.

## Problems

- P1: Fake local API keys
  - SKYVERN_API_KEY and VITE_SKYVERN_API_KEY were dummy strings, never issued by org_auth_token service.
  - org_auth_service.get_current_org could not find an organization for any x-api-key.
  - Result: every request failed with 403, despite server and DB being healthy.
- P2: Upstream LLM quota
  - With real auth in place, workflow-from-prompt route failed only when calling LLM provider.
  - litellm returned RateLimitError / OpenAIError for glm46v:
    - Upstream message: “余额不足或无可用资源包,请充值” (insufficient balance).
  - Skyvern wrapped this into LLMProviderError and then FailedToCreateWorkflow (HTTP 500).
  - Direct calls to litellm confirmed 429 / 403 / 400 errors for several model groups.

## Solutions

- Auth fix:
  - Point DATABASE_STRING to dedicated Postgres on localhost:15432.
  - Run Alembic migrations to create schema and auth tables.
  - Use POST /v1/internal/auth/repair from localhost:
    - Ensures Skyvern-local org exists.
    - Generates JWT API key and persists into DB.
    - Writes SKYVERN_API_KEY into .env and VITE_SKYVERN_API_KEY into skyvern-frontend/.env.
  - Restart backend and UI to pick up updated env files.
  - Outcome: 403 only occurs when x-api-key is missing or invalid; valid JWT works everywhere.
- LLM diagnosis:
  - Do not treat 500 as generic Skyvern bug when body mentions LLMProviderError.
  - Inspect /tmp/skyvern-server.log:
    - Look for litellm stacktrace and upstream provider message.
  - Confirm litellm behavior via minimal /v1/chat/completions for the configured model group.
  - Outcome: 500 here is a surfaced provider quota error; Skyvern core logic is functioning.

## Takeaways

- Local auth:
  - Never hand-edit local API keys; always use internal_auth.repair for consistent backend/frontend config.
  - Ensure DB is ready (migrations applied) before running internal auth helpers.
- LLM behavior:
  - 403 from Skyvern → auth/config issue.
  - 500 with LLMProviderError → downstream LLM problem (quota, model missing, plan limits, concurrency).
  - When changing OPENAI_COMPATIBLE_MODEL_NAME, validate with litellm directly before wiring into Skyvern.

## References

- Findings: flow/findings/2025-12-16_skyvern_selfhost_auth_and_llm.md
- Backend env: .env
- Frontend env: skyvern-frontend/.env
- LLM proxy: ../bhd-litellm/.env and Nomad job bhd-litellm
