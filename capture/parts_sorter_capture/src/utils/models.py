# MIT License

# Copyright (c) 2025 Jaime Álvarez Díaz
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import asyncio
from typing import Any, Generic, TypeVar

from typing_extensions import Self

T= TypeVar('T')


class AsyncList(Generic[T]):
    def __init__(self) -> None:
        self._list: list[Any] = []
        self._lock: asyncio.Lock = asyncio.Lock()

    async def put(self, element: T) -> None:
        async with self._lock:
            self._list.append(element)

    async def get(self) -> T:
        async with self._lock:
            if not self._list:
                raise asyncio.QueueEmpty
            return self._list.pop(0)

    async def check_first(self) -> T:
        async with self._lock:
            if not self._list:
                raise asyncio.QueueEmpty
            return self._list[0]

    async def empty(self) -> bool:
        async with self._lock:
            return len(self._list) == 0

    async def count(self) -> int:
        async with self._lock:
            return len(self._list)

    async def __aenter__(self) -> Self:
        await self._lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._lock.release()


class AsyncCounter:
    def __init__(self) -> None:
        self._counter: int = 0
        self._lock: asyncio.Lock = asyncio.Lock()

    async def reset(self) -> None:
        async with self._lock:
            self._counter = 0

    async def get(self) -> int:
        async with self._lock:
            return self._counter

    async def set(self, value: int) -> None:
        async with self._lock:
            self._counter = value

    async def inc(self, value: int = 1) -> int:
        async with self._lock:
            self._counter += value
            return self._counter

    async def dec(self, value: int = 1) -> int:
        async with self._lock:
            self._counter -= value
            return self._counter

    async def __aenter__(self) -> Self:
        await self._lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._lock.release()
