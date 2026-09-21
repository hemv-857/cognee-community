"""Example: sync Raindrop.io bookmarks into cognee.

Usage:
    export RAINDROP_TOKEN="your-test-token-here"
    python example.py

Get a test token at: https://app.raindrop.io/#settings/apps
"""

import asyncio

import cognee
from cognee_community_connector_raindrop import raindrop_source


async def main():
    # Reset cognee state (optional — for a clean slate)
    # await cognee.prune.prune_data()

    # Add Raindrop.io bookmarks via the connector.
    # All bookmarks from all collections will be synced.
    source = raindrop_source(token="your-test-token-here")

    # Alternative: restrict to specific collections
    # source = raindrop_source(token="...", collection_ids=[123456, 789012])

    await cognee.add(source)

    # Query your synced bookmarks
    results = await cognee.search("search", query_text="machine learning")
    for result in results:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
