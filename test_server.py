#!/usr/bin/env python3
"""
Test script to check if Skyvern server can be initialized properly
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from skyvern.config import settings
from skyvern.forge.api_app import create_api_app


def test_server():
    print(f"Current port setting: {settings.PORT}")
    print(f"Current environment: {settings.ENV}")

    try:
        print("Attempting to create API app...")
        app = create_api_app()
        print("✓ API app created successfully!")

        # List some routes to verify the app is set up correctly
        print("\nAvailable routes (first 10):")
        for i, route in enumerate(app.routes[:10]):
            methods = getattr(route, "methods", "Unknown")
            path = getattr(route, "path", "Unknown")
            print(f"  {methods} {path}")

        print(f"\n✓ Server configuration is valid!")
        return True

    except Exception as e:
        print(f"✗ Error creating API app: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_server()
