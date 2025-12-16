from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from skyvern.forge.sdk.db.client import AgentDB
from skyvern.forge.sdk.db.models import Base
from skyvern.webeye.persistent_sessions_manager import PersistentSessionsManager


@pytest_asyncio.fixture
async def db_engine() -> AsyncGenerator[Any, None]:
    # Use an in-memory SQLite database for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def agent_db(db_engine: Any) -> AsyncGenerator[AgentDB, None]:
    yield AgentDB(database_string="sqlite+aiosqlite:///:memory:", debug_enabled=True, db_engine=db_engine)


@pytest.mark.asyncio
async def test_create_organization(agent_db: AgentDB) -> None:
    org_name = "Test Organization"
    domain = "test.com"
    organization = await agent_db.create_organization(organization_name=org_name, domain=domain)
    assert organization is not None
    assert organization.organization_name == org_name
    assert organization.domain == domain

    retrieved_org = await agent_db.get_organization(organization.organization_id)
    assert retrieved_org is not None
    assert retrieved_org.organization_name == org_name
    assert retrieved_org.domain == domain

    retrieved_by_domain = await agent_db.get_organization_by_domain(domain=domain)
    assert retrieved_by_domain is not None
    assert retrieved_by_domain.organization_name == org_name
    assert retrieved_by_domain.domain == domain


@pytest.mark.asyncio
async def test_get_organization_not_found(agent_db: AgentDB) -> None:
    retrieved_org = await agent_db.get_organization("non_existent_id")
    assert retrieved_org is None

    retrieved_by_domain = await agent_db.get_organization_by_domain(domain="nonexistent.com")
    assert retrieved_by_domain is None


@pytest.mark.asyncio
async def test_begin_session_marks_started(agent_db: AgentDB) -> None:
    PersistentSessionsManager.instance = None
    org_id = "o_test"
    browser_session = await agent_db.create_persistent_browser_session(
        organization_id=org_id,
        timeout_minutes=20,
    )
    manager = PersistentSessionsManager(database=agent_db)
    await manager.begin_session(
        browser_session_id=browser_session.persistent_browser_session_id,
        runnable_type="workflow_run",
        runnable_id="wr_test",
        organization_id=org_id,
    )

    refreshed = await agent_db.get_persistent_browser_session(
        browser_session.persistent_browser_session_id,
        org_id,
    )
    assert refreshed is not None
    assert refreshed.runnable_id == "wr_test"
    assert refreshed.started_at is not None
    assert refreshed.status == "running"


@pytest.mark.asyncio
async def test_get_active_sessions_reconciles_started_for_occupied(agent_db: AgentDB) -> None:
    PersistentSessionsManager.instance = None
    org_id = "o_test"
    browser_session = await agent_db.create_persistent_browser_session(
        organization_id=org_id,
        timeout_minutes=20,
    )
    await agent_db.occupy_persistent_browser_session(
        session_id=browser_session.persistent_browser_session_id,
        runnable_type="workflow_run",
        runnable_id="wr_test",
        organization_id=org_id,
    )

    manager = PersistentSessionsManager(database=agent_db)
    sessions = await manager.get_active_sessions(org_id)
    target = next(
        (s for s in sessions if s.persistent_browser_session_id == browser_session.persistent_browser_session_id), None
    )
    assert target is not None
    assert target.runnable_id == "wr_test"
    assert target.started_at is not None
    assert target.status == "running"


@pytest.mark.asyncio
async def test_get_browser_sessions_history_reconciles_started_for_occupied(agent_db: AgentDB) -> None:
    org_id = "o_test"
    browser_session = await agent_db.create_persistent_browser_session(
        organization_id=org_id,
        timeout_minutes=20,
    )
    await agent_db.occupy_persistent_browser_session(
        session_id=browser_session.persistent_browser_session_id,
        runnable_type="workflow_run",
        runnable_id="wr_test",
        organization_id=org_id,
    )

    history = await agent_db.get_persistent_browser_sessions_history(org_id, page=1, page_size=10)
    target = next(
        (s for s in history if s.persistent_browser_session_id == browser_session.persistent_browser_session_id), None
    )
    assert target is not None
    assert target.runnable_id == "wr_test"
    assert target.started_at is not None
    assert target.status == "running"
