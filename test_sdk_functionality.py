#!/usr/bin/env python3
"""Skyvern SDK functionality test script.

This script demonstrates how to verify the Skyvern server status, exercise the
Python SDK (sync and async clients), and run a simple task. It is meant for
local development and uses an empty API key, so authentication failures are
considered expected behavior.
"""

from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

import httpx

from skyvern.cli.status import _check_port
from skyvern.client import AsyncSkyvern, Skyvern
from skyvern.client.environment import SkyvernEnvironment

DEFAULT_BASE_URL = os.environ.get("SKYVERN_BASE_URL", "http://localhost:18000")
DEFAULT_API_KEY = os.environ.get("SKYVERN_API_KEY", "")
DEFAULT_TIMEOUT = 10.0


@dataclass
class TestResult:
    """Simple container for test status."""

    name: str
    success: bool
    details: str = ""


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


async def check_server_health(base_url: str) -> TestResult:
    """Check server status endpoint to validate connectivity."""

    port = int(base_url.split(":")[-1]) if ":" in base_url else 8000
    port_open = _check_port(port)
    if not port_open:
        return TestResult(name="Port check", success=False, details=f"Port {port} closed")

    health_url = base_url.rstrip("/") + "/health"
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        try:
            response = await client.get(health_url)
            if response.status_code == 200:
                return TestResult("Health endpoint", True, "Healthy response received")
            return TestResult("Health endpoint", False, f"Unexpected status {response.status_code}")
        except httpx.HTTPError as exc:
            return TestResult("Health endpoint", False, f"Request failed: {exc}")


def create_sync_client(base_url: str, api_key: str) -> Skyvern:
    return Skyvern(base_url=base_url, api_key=api_key)


def create_async_client(base_url: str, api_key: str) -> AsyncSkyvern:
    return AsyncSkyvern(base_url=base_url, api_key=api_key)


def run_sync_scenarios(base_url: str, api_key: str) -> list[TestResult]:
    results: list[TestResult] = []
    client = create_sync_client(base_url, api_key)

    scenarios: list[tuple[str, Callable[[], None]]] = [
        ("List workflows", lambda: client.get_workflows()),
        (
            "Run task",
            lambda: client.run_task(prompt="Return the current UTC date as ISO", title="SDK Test Task"),
        ),
        ("Fetch run status", lambda: client.get_run("dummy_run_id")),
    ]

    for name, func in scenarios:
        try:
            func()
            results.append(TestResult(name, True, "Success"))
        except Exception as exc:  # noqa: BLE001
            details = str(exc)
            expected_auth_error = any(keyword in details.lower() for keyword in ("403", "auth", "api key"))
            if expected_auth_error:
                results.append(TestResult(name, True, "Expected auth failure"))
            else:
                results.append(TestResult(name, False, details))

    return results


async def run_async_scenarios(base_url: str, api_key: str) -> list[TestResult]:
    results: list[TestResult] = []
    client = create_async_client(base_url, api_key)

    async def safe_exec(name: str, coro_factory: Callable[[], Awaitable[object]]) -> None:
        try:
            await coro_factory()
            results.append(TestResult(name, True, "Success"))
        except Exception as exc:  # noqa: BLE001
            details = str(exc)
            expected_auth_error = any(keyword in details.lower() for keyword in ("403", "auth", "api key"))
            if expected_auth_error:
                results.append(TestResult(name, True, "Expected auth failure"))
            else:
                results.append(TestResult(name, False, details))

    await safe_exec("Async list workflows", lambda: client.get_workflows())
    await safe_exec(
        "Async run task",
        lambda: client.run_task(prompt="Return the current UTC date as ISO", title="Async SDK Test Task"),
    )
    await safe_exec("Async fetch run status", lambda: client.get_run("dummy_run_id"))

    return results


def demo_environment_options() -> None:
    print_header("Environment Options")
    print("SkyvernEnvironment members:")
    for env in SkyvernEnvironment:
        print(f"  - {env.name} -> {env.value}")


def print_results(results: list[TestResult]) -> None:
    for result in results:
        status = "PASS" if result.success else "FAIL"
        detail = f" - {result.details}" if result.details else ""
        print(f"[{status}] {result.name}{detail}")


def main() -> int:
    print_header("Skyvern SDK Functionality Test")
    print(f"Base URL: {DEFAULT_BASE_URL}")
    print("Note: Empty API keys will cause expected authentication failures.")

    demo_environment_options()

    print_header("Server Status")
    health_result = asyncio.run(check_server_health(DEFAULT_BASE_URL))
    print_results([health_result])
    if not health_result.success:
        print("Server health check failed; continuing to demonstrate SDK usage regardless.")

    print_header("Synchronous SDK Scenarios")
    sync_results = run_sync_scenarios(DEFAULT_BASE_URL, DEFAULT_API_KEY)
    print_results(sync_results)

    print_header("Asynchronous SDK Scenarios")
    try:
        async_results = asyncio.run(run_async_scenarios(DEFAULT_BASE_URL, DEFAULT_API_KEY))
        print_results(async_results)
    except RuntimeError as exc:
        print(f"Failed to run async scenarios: {exc}")
        async_results = [TestResult("Async scenarios", False, str(exc))]

    all_results = [health_result, *sync_results, *async_results]
    success = all(result.success for result in all_results)
    print_header("Summary")
    print_results(all_results)
    print("\nOutcome: {}".format("SUCCESS" if success else "FAILURE (see above)"))
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
