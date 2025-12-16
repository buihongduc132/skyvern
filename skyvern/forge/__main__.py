import os
from pathlib import Path

import structlog
import uvicorn
from dotenv import load_dotenv

LOG = structlog.stdlib.get_logger()


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / ".env", override=True)

    from skyvern import analytics
    from skyvern.config import settings

    analytics.capture("skyvern-oss-run-server")
    port = settings.PORT
    LOG.info("Agent server starting.", host="0.0.0.0", port=port)

    reload = settings.ENV == "local"

    # Configure reload settings
    # Convert TEMP_PATH to relative path if it's absolute to avoid pathlib.glob() issues
    temp_path_for_excludes = (
        os.path.relpath(settings.TEMP_PATH) if os.path.isabs(settings.TEMP_PATH) else settings.TEMP_PATH
    )
    artifact_path_for_excludes = (
        os.path.relpath(settings.ARTIFACT_STORAGE_PATH)
        if os.path.isabs(settings.ARTIFACT_STORAGE_PATH)
        else settings.ARTIFACT_STORAGE_PATH
    )

    uvicorn.run(
        "skyvern.forge.api_app:create_api_app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=reload,
        reload_dirs=[str(repo_root / "skyvern"), str(repo_root / "alembic")],
        reload_excludes=[
            "postgres-data/**",
            f"{temp_path_for_excludes}/**/*.py",
            f"{artifact_path_for_excludes}/{settings.ENV}/**/scripts/**/**/*.py",
        ],
        factory=True,
    )
