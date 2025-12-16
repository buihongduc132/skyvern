# Skyvern self-hosted auth + LLM wiring (local)

## Context

- Self-hosted Skyvern OSS stack on bhd-main using bhd-litellm and local Postgres.

## Stack wiring (current)

- Backend on 0.0.0.0:18000 with ENV=local and PORT=18000.
- DATABASE_STRING points to postgres+psycopg on localhost:15432 (docker skyvern-postgres-1).
- Alembic migrations applied; core tables (organizations, workflows, tasks, runs) exist.
- LLM_KEY=OPENAI_COMPATIBLE, ENABLE_OPENAI_COMPATIBLE=true, OPENAI_COMPATIBLE_MODEL_NAME=glm46v.
- OPENAI_COMPATIBLE_API_BASE=http://192.168.1.80:14001/v1 using bhd-litellm Nomad job.
- OPENAI_COMPATIBLE_API_KEY matches LITELLM_MASTER_KEY; supports vision via glm46v group.
- Frontend dev server on http://localhost:28742 with VITE_API_BASE_URL=http://localhost:18000/api/v1.
- VITE_WSS_BASE_URL=ws://localhost:18000/api/v1 and VITE_ARTIFACT_API_BASE_URL=http://localhost:9090.

## Auth + API key behavior

- Org auth enforced by get_current_org on every /v1/* endpoint via x-api-key.
- Local-only /v1/internal/auth/* endpoints enabled when ENV=local.
- POST /v1/internal/auth/repair:
  - Ensures local org Skyvern-local (domain=skyvern.local) exists.
  - Invalidates existing API tokens for that org.
  - Generates JWT API key and stores it in organizations_auth_tokens.
  - Writes SKYVERN_API_KEY into .env and VITE_SKYVERN_API_KEY into skyvern-frontend/.env.
- GET /v1/internal/auth/status validates x-api-key and reports diagnostics (ok/invalid/expired).

## 403 root cause (resolved)

- Dummy SKYVERN_API_KEY and VITE_SKYVERN_API_KEY were never issued by DB-backed token service.
- org_auth_service.get_current_org could not resolve organization for any incoming x-api-key.
- All REST calls returned 403 Invalid credentials despite server being reachable.
- Fix: point to real Postgres, run Alembic, then call /v1/internal/auth/repair to bootstrap org and keys.
- After restart, SDK tests and UI traffic authenticate successfully with new JWT; 403 appears only for bad keys.

## 500 on /v1/workflows/create-from-prompt

- UI sends CreateFromPromptRequest with task_version=v2 and TaskV2Request body.
- Route create_workflow_from_prompt passes request into WorkflowService.create_workflow_from_prompt.
- WorkflowService uses app.LLM_API_HANDLER to call configured LLM (openai/glm46v).
- litellm.acompletion for glm46v returns RateLimitError with upstream message:
  - “余额不足或无可用资源包,请充值” (insufficient balance / no available package).
- Skyvern maps this to LLMProviderError and then to FailedToCreateWorkflow (HTTP 500).
- Direct calls to litellm /v1/chat/completions confirm:
  - glm46v → 429 throttle/insufficient balance.
  - glm4flash, glm4flashx → 400 model not found.
  - gpt-4o-mini → 403 free tier not allowed.
- Conclusion: 500s are caused by upstream LLM quota / access errors, not auth or schema issues.

## Takeaways

- Always bootstrap local auth via /v1/internal/auth/repair instead of hand-writing local API keys.
- For 500s with LLMProviderError, inspect server logs; most are wrapped upstream 4xx/5xx from bhd-litellm.
- Changing OPENAI_COMPATIBLE_MODEL_NAME requires verifying that model group actually has quota and access.
