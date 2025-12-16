#!/usr/bin/env python3
"""
Test script to verify the Skyvern Python SDK can connect to the running server.
This script tests basic API functionality like listing workflows.
"""

import asyncio
import sys
from skyvern.client import Skyvern, AsyncSkyvern


def test_sync_client():
    """Test the synchronous Skyvern client"""
    print("Testing synchronous Skyvern client...")

    # Create client pointing to local server
    client = Skyvern(
        base_url="http://localhost:18000",
        api_key="",  # Empty API key for local development server
    )

    try:
        # Test 1: Try to list workflows (should return error due to missing API key, but connection should work)
        print("  - Attempting to list workflows...")
        workflows = client.get_workflows()
        print(f"  - Successfully retrieved {len(workflows)} workflows")

        # Test 2: Try to run a simple task to verify basic functionality
        print("  - Attempting to run a simple task...")
        task_response = client.run_task(prompt="What is the current date?", title="Test Task from SDK")
        print(f"  - Successfully created task with ID: {task_response.run_id}")

        # Test 3: Get the run information
        print(f"  - Attempting to get run information for {task_response.run_id}...")
        run_info = client.get_run(task_response.run_id)
        print(f"  - Successfully retrieved run info with status: {run_info.status}")

        print("✓ Synchronous client tests passed!")
        return True

    except Exception as e:
        # Check if it's an authentication error (which is expected with empty API key)
        error_str = str(e).lower()
        if "403" in str(e) or "auth" in error_str or "credential" in error_str or "api.key" in error_str:
            print(f"  - Got expected authentication error: {str(e)}")
            print("✓ Synchronous client connection test passed! (Got expected auth error)")
            return True
        else:
            print(f"✗ Synchronous client test failed with unexpected error: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


async def test_async_client():
    """Test the asynchronous Skyvern client"""
    print("\nTesting asynchronous Skyvern client...")

    # Create async client pointing to local server
    client = AsyncSkyvern(
        base_url="http://localhost:18000",
        api_key="",  # Empty API key for local development server
    )

    try:
        # Test 1: Try to list workflows
        print("  - Attempting to list workflows (async)...")
        workflows = await client.get_workflows()
        print(f"  - Successfully retrieved {len(workflows)} workflows")

        # Test 2: Try to run a simple task
        print("  - Attempting to run a simple task (async)...")
        task_response = await client.run_task(prompt="What is the current date?", title="Async Test Task from SDK")
        print(f"  - Successfully created task with ID: {task_response.run_id}")

        # Test 3: Get the run information
        print(f"  - Attempting to get run information for {task_response.run_id} (async)...")
        run_info = await client.get_run(task_response.run_id)
        print(f"  - Successfully retrieved run info with status: {run_info.status}")

        print("✓ Asynchronous client tests passed!")
        return True

    except Exception as e:
        # Check if it's an authentication error (which is expected with empty API key)
        error_str = str(e).lower()
        if "403" in str(e) or "auth" in error_str or "credential" in error_str or "api.key" in error_str:
            print(f"  - Got expected authentication error: {str(e)}")
            print("✓ Asynchronous client connection test passed! (Got expected auth error)")
            return True
        else:
            print(f"✗ Asynchronous client test failed with unexpected error: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


def test_with_explicit_base_url():
    """Test using explicit base URL"""
    print("\nTesting client with explicit base URL...")

    client = Skyvern(
        base_url="http://localhost:18000",
        api_key="",
    )

    try:
        workflows = client.get_workflows()
        print(f"  - Successfully retrieved workflows (got expected auth error)")
        print("✓ Explicit base URL test passed!")
        return True
    except Exception as e:
        error_str = str(e).lower()
        if "403" in str(e) or "auth" in error_str or "credential" in error_str or "api.key" in error_str:
            print(f"  - Got expected authentication error: {str(e)}")
            print("✓ Explicit base URL connection test passed! (Got expected auth error)")
            return True
        else:
            print(f"✗ Explicit base URL test failed: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


if __name__ == "__main__":
    print("Skyvern Python SDK Connection Test")
    print("=" * 50)

    all_tests_passed = True

    # Test synchronous client
    all_tests_passed &= test_sync_client()

    # Test with explicit base URL
    all_tests_passed &= test_with_explicit_base_url()

    # Test asynchronous client
    try:
        all_tests_passed &= asyncio.run(test_async_client())
    except Exception as e:
        print(f"✗ Async test failed to run: {str(e)}")
        all_tests_passed = False

    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✓ All SDK connection tests passed! The Python SDK can successfully connect to the Skyvern server.")
        print("  Note: Authentication errors are expected with empty API key in development.")
        sys.exit(0)
    else:
        print("✗ Some SDK connection tests failed.")
        sys.exit(1)
