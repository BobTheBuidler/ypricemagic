import hashlib
import json
from asyncio import Lock
from collections.abc import Callable, Container
from functools import lru_cache
from pathlib import Path
from sqlite3 import OperationalError
from typing import Any, Final, Literal, cast, final

import aiosqlite
from a_sync import SmartProcessingQueue
from aiosqlite.context import Result
from brownie._config import CONFIG, _get_data_folder
from brownie.exceptions import BrownieEnvironmentError
from brownie.network.contract import _resolve_address

SourceKey = Literal[
    "address",
    "alias",
    "paths",
    "abi",
    "ast",
    "bytecode",
    "compiler",
    "contractName",
    "deployedBytecode",
    "deployedSourceMap",
    "language",
    "natspec",
    "opcodes",
    "pcMap",
    "sourceMap",
    "type",
]

# TODO: replace these with the typed dicts in brownie >=1.22
BuildJson = dict[str, Any]
Sources = dict[SourceKey, Any]


SOURCE_KEYS: Final = (
    "address",
    "alias",
    "paths",
    "abi",
    "ast",
    "bytecode",
    "compiler",
    "contractName",
    "deployedBytecode",
    "deployedSourceMap",
    "language",
    "natspec",
    "opcodes",
    "pcMap",
    "sourceMap",
    "type",
)

DISCARD_SOURCE_KEYS: Final = (
    "ast",
    "bytecode",
    "coverageMap",
    "deployedBytecode",
    "deployedSourceMap",
    "natspec",
    "opcodes",
    "pcMap",
)
"""
To keep our Contract objects smaller, we do not load all contract source data. Many are not relevant for our data analysis type use case.

These keys will not be included in y.Contract object build data. If you need them, consider just using a dank_mids.Contract for your use case.
"""


# C constants

sha1: Final = hashlib.sha1

dumps: Final = json.dumps
loads: Final = json.loads

sqlite_lock: Final = Lock()


@final
class AsyncCursor:
    def __init__(self, filename: Path) -> None:
        self._filename: Final = filename
        self._db: aiosqlite.Connection | None = None
        self._connected: bool = False
        self._execute: Callable[..., Result[aiosqlite.Cursor]] | None = None

    async def connect(self) -> None:
        """Establish an async connection to the SQLite database"""
        db = self._db  # must assign before checking to avoid a TypeError below
        if db is not None:
            raise RuntimeError("already connected")
        async with sqlite_lock:
            if self._db is not None:
                return
            self._db = await aiosqlite.connect(self._filename, isolation_level=None)
            self._execute = self._db.execute

    async def insert(self, table: str, *values: Any) -> None:
        raise NotImplementedError
        if self._db is None:
            await self.connect()

        # Convert any dictionaries/lists to JSON strings before inserting
        values = [dumps(val) if isinstance(val, (dict, list)) else val for val in values]

        # Prepare the parameter placeholders
        placeholders = ",".join("?" * len(values))
        query = f"INSERT OR REPLACE INTO {table} VALUES ({placeholders})"

        # Execute the query and commit the changes
        async with self._execute(query, values):
            await self._db.commit()

    async def fetchone(self, cmd: str, *args: Any) -> tuple[Any, ...] | None:
        if self._db is None:
            await self.connect()
        async with sqlite_lock:
            execute = cast(Callable[..., Result[aiosqlite.Cursor]], self._execute)
            async with execute(cmd, args) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                # Convert any JSON-serialized columns back to their original data structures
                return tuple(loads(i) if str(i).startswith(("[", "{")) else i for i in row)


cur: Final = AsyncCursor(_get_data_folder().joinpath("deployments.db"))
fetchone: Final = SmartProcessingQueue(cur.fetchone, num_workers=32)


@lru_cache(maxsize=None)
def _get_select_statement() -> str:
    try:
        return f"SELECT * FROM chain{CONFIG.active_network['chainid']}"
    except KeyError:
        raise BrownieEnvironmentError("Functionality not available in local environment") from None


async def _get_deployment(
    address: str | None = None,
    alias: str | None = None,
    skip_source_keys: Container[SourceKey] = cast(Container[SourceKey], DISCARD_SOURCE_KEYS),
) -> tuple[BuildJson | None, Sources | None]:
    if address and alias:
        raise ValueError("Passed both params address and alias, should be only one!")
    if address:
        address = _resolve_address(address)
        where_clause = f" WHERE address='{address}'"
    elif alias:
        where_clause = f" WHERE alias='{alias}'"

    try:
        row = await fetchone(_get_select_statement() + where_clause)
    except OperationalError:
        row = None
    if not row:
        return None, None

    build_json = dict(zip(SOURCE_KEYS, row))
    path_map: dict = build_json.pop("paths")  # type: ignore [type-arg]

    sources = {
        source_key: await __fetch_source_for_hash(val)
        for val, source_key in path_map.values()
        if source_key not in skip_source_keys
    }

    build_json["allSourcePaths"] = {k: v[1] for k, v in path_map.items()}
    pc_map: dict | None = build_json.get("pcMap")  # type: ignore [type-arg]
    if pc_map is not None:
        build_json["pcMap"] = {int(key): pc_map[key] for key in pc_map}

    return build_json, sources


async def __fetch_source_for_hash(hashval: str) -> Any:
    row = await fetchone("SELECT source FROM sources WHERE hash=?", hashval)
    return cast(tuple[Any, ...], row)[0]
