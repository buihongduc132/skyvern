import types
from unittest.mock import AsyncMock

import pytest

from skyvern import config
from skyvern.forge import app
from skyvern.forge.sdk.artifact.manager import ArtifactManager
from skyvern.forge.sdk.artifact.models import ArtifactType


@pytest.mark.asyncio
async def test_creating_screenshot_artifact_writes_streaming_file(tmp_path, monkeypatch):
    monkeypatch.setattr(config.settings, "TEMP_PATH", str(tmp_path))

    manager = ArtifactManager()

    dummy_db = types.SimpleNamespace(
        create_artifact=AsyncMock(
            return_value={"artifact_id": "a1", "uri": "file:///tmp/a1.png", "task_id": "t1", "workflow_run_id": "wr1"}
        )
    )
    dummy_storage = types.SimpleNamespace(
        store_artifact=AsyncMock(return_value=None),
        store_artifact_from_path=AsyncMock(return_value=None),
        save_streaming_file=AsyncMock(return_value=None),
    )

    monkeypatch.setattr(app, "DATABASE", dummy_db)
    monkeypatch.setattr(app, "STORAGE", dummy_storage)

    png_bytes = b"\x89PNG\r\n\x1a\nfake"

    await manager._create_artifact(
        aio_task_primary_key="t1",
        artifact_id="a1",
        artifact_type=ArtifactType.SCREENSHOT_ACTION,
        uri="file:///tmp/a1.png",
        organization_id="org1",
        task_id="t1",
        workflow_run_id="wr1",
        data=png_bytes,
    )
    await manager.wait_for_upload_aiotasks(["t1"])

    expected = tmp_path / "org1" / "wr1.png"
    assert expected.read_bytes() == png_bytes


@pytest.mark.asyncio
async def test_streaming_file_falls_back_to_task_id_when_no_workflow_run(tmp_path, monkeypatch):
    monkeypatch.setattr(config.settings, "TEMP_PATH", str(tmp_path))

    manager = ArtifactManager()

    dummy_db = types.SimpleNamespace(
        create_artifact=AsyncMock(
            return_value={"artifact_id": "a1", "uri": "file:///tmp/a1.png", "task_id": "t1", "workflow_run_id": None}
        )
    )
    dummy_storage = types.SimpleNamespace(
        store_artifact=AsyncMock(return_value=None),
        store_artifact_from_path=AsyncMock(return_value=None),
        save_streaming_file=AsyncMock(return_value=None),
    )

    monkeypatch.setattr(app, "DATABASE", dummy_db)
    monkeypatch.setattr(app, "STORAGE", dummy_storage)

    png_bytes = b"\x89PNG\r\n\x1a\nfake"

    await manager._create_artifact(
        aio_task_primary_key="t1",
        artifact_id="a1",
        artifact_type=ArtifactType.SCREENSHOT_FINAL,
        uri="file:///tmp/a1.png",
        organization_id="org1",
        task_id="t1",
        data=png_bytes,
    )
    await manager.wait_for_upload_aiotasks(["t1"])

    expected = tmp_path / "org1" / "t1.png"
    assert expected.read_bytes() == png_bytes

