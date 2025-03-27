from asyncio import Lock
from hashlib import sha1
from json import dumps, loads
from pathlib import Path
from typing import Any, Container, Dict, Literal, Optional, Tuple

import aiosqlite
from a_sync import SmartProcessingQueue
from a_sync.async_property.cached import async_cached_property
from brownie._config import CONFIG, _get_data_folder
from brownie.exceptions import BrownieEnvironmentError
from brownie.network.contract import _resolve_address
from brownie.project.build import DEPLOYMENT_KEYS
from eth_utils.toolz import keymap
from functools import lru_cache
from sqlite3 import InterfaceError, OperationalError

from y.datatypes import Address


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

BuildJson = Dict[str, Any]
Sources = Dict[SourceKey, Any]


SOURCE_KEYS: Tuple[SourceKey, ...] = SourceKey.__args__

DISCARD_SOURCE_KEYS: Tuple[SourceKey, ...] = (
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


class AsyncCursor:
    def __init__(self, filename):
        self._filename = filename

    @async_cached_property
    async def connect(self):
        """Establish an async connection to the SQLite database"""
        self._db = await aiosqlite.connect(self._filename, isolation_level=None)

    async def insert(self, table, *values):
        raise NotImplementedError
        await self.connect

        # Convert any dictionaries/lists to JSON strings before inserting
        values = [
            dumps(val) if isinstance(val, (dict, list)) else val for val in values
        ]

        # Prepare the parameter placeholders
        placeholders = ",".join("?" * len(values))
        query = f"INSERT OR REPLACE INTO {table} VALUES ({placeholders})"

        # Execute the query and commit the changes
        async with self._db.execute(query, values):
            await self._db.commit()

    async def fetchone(self, cmd: str, *args) -> Optional[Tuple]:
        await self.connect
        async with self._db.execute(cmd, args) as cursor:
            if row := await cursor.fetchone():
                # Convert any JSON-serialized columns back to their original data structures
                return tuple(
                    loads(i) if str(i).startswith(("[", "{")) else i for i in row
                )


cur = AsyncCursor(_get_data_folder().joinpath("deployments.db"))
fetchone = SmartProcessingQueue(cur.fetchone, num_workers=32)


@lru_cache(maxsize=None)
def _get_select_statement() -> str:
    try:
        return f"SELECT * FROM chain{CONFIG.active_network['chainid']}"
    except KeyError:
        raise BrownieEnvironmentError(
            "Functionality not available in local environment"
        ) from None


async def _get_deployment(
    address: str = None,
    alias: str = None,
    skip_source_keys: Container[SourceKey] = DISCARD_SOURCE_KEYS,
) -> Tuple[Optional[BuildJson], Optional[Sources]]:
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
    path_map = build_json.pop("paths")

    sources = {
        source_key: await __fetch_source_for_hash(val)
        for val, source_key in path_map.values()
        if source_key not in skip_source_keys
    }

    build_json["allSourcePaths"] = {k: v[1] for k, v in path_map.items()}
    if isinstance(build_json.get("pcMap"), dict):
        build_json["pcMap"] = keymap(int, build_json["pcMap"])

    return build_json, sources


async def __fetch_source_for_hash(hashval: str) -> Any:
    return (await fetchone("SELECT source FROM sources WHERE hash=?", hashval))[0]
