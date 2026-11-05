import asyncio
from collections.abc import Callable

import httpx

from scout.greenhouse_adapter import GreenhouseAdapter


def retrieve_with_handler(handler: Callable, board: str = "demo"):
    async def run():
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            return await GreenhouseAdapter(client).retrieve(board)

    return asyncio.run(run())
