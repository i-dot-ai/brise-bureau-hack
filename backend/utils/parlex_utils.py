from typing import Any, AsyncIterator


async def filter_nones_from_stream(stream: AsyncIterator[Any]) -> AsyncIterator[Any]:
    async for item in stream:
        if item is not None:
            yield item
