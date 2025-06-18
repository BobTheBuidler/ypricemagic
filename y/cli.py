"""
A Python CLI tool for managing the database and debugging price retrieval.
"""

__all__ = ["db_nuke", "db_clear", "db_info", "db_vacuum", "db_select", "main"]

import argparse
import sys
import os
import subprocess
from pprint import pprint

from cchecksum import to_checksum_address
from faster_eth_utils import is_address
from pony.orm import db_session, commit, delete, count, select

from y.prices.utils.debug import debug_price


def db_info() -> None:
    """
    Displays basic information about the database.
    Lists each entity (table) with its row count and storage size.
    """
    import y._db.utils  # do not remove
    from y._db.config import connection_settings
    from y._db.entities import db

    provider = connection_settings["provider"]

    def get_size(entity) -> str:
        """
        Returns storage size in bytes for the given entity's table.
        For PostgreSQL returns pg_total_relation_size; for SQLite returns the database file size; otherwise 'N/A'.
        """
        table_name = entity._table_.name
        # pg_total_relation_size returns bytes
        row = db.execute(f"SELECT pg_total_relation_size('{table_name}')").fetchone()
        return str(row[0]) if row and len(row) > 0 else "N/A"

    @db_session
    def print_info() -> None:
        if not db.entities:
            print("No entities registered in the database.")
            return
        print("Database Information:")
        if provider in ("postgresql", "postgres"):
            for entity in db.entities.values():
                num = count(e for e in entity)
                size = get_size(entity)
                print(f"  Table {entity.__name__}: {num} rows, {size} bytes")
        else:
            for entity in db.entities.values():
                num = count(e for e in entity)
                print(f"  Table {entity.__name__}: {num} rows")
            db_file = connection_settings.get("filename", "")
            size = os.path.getsize(db_file)
            print("-------------------------")
            print(f"  Total Size {size} bytes")

    try:
        print_info()
    except Exception as e:
        print(f"Error retrieving database info: {e}")


def db_vacuum() -> None:
    """
    Executes the vacuum operation on the database.

    For SQLite, this performs a VACUUM.
    For PostgreSQL, ensure appropriate permissions; this issues a VACUUM command.
    """
    from y._db.config import connection_settings
    from y._db.entities import db

    try:
        provider = connection_settings["provider"]
        if provider == "sqlite":
            import sqlite3

            db_file = connection_settings["filename"]
            conn = sqlite3.connect(db_file)
            conn.execute("VACUUM;")
            conn.close()
        else:
            with db_session:
                db.execute("VACUUM;")
        print("Database vacuum operation completed.")
    except Exception as e:
        print(f"Error during vacuum operation: {e}")


def db_nuke(force: bool = False) -> None:
    """
    Drops all tables in the database.

    Parameters:
        force (bool): If True, skip confirmation prompt.
    """
    if not force:
        confirm = (
            input("Are you sure you want to drop all tables in the database? [y/N]: ")
            .strip()
            .lower()
        )
        if confirm.lower() not in ("y", "yes"):
            print("Operation cancelled.")
            return

    import y._db.utils  # do not remove
    from y._db.entities import db

    try:
        with db_session:
            db.drop_all_tables(with_all_data=True)
    except Exception as e:
        print(f"Error dropping tables: {e}")
    else:
        print("All tables dropped; database cleared.")


def db_clear(token: str = None, block: str = None) -> None:
    # sourcery skip: simplify-generator
    """
    Clears the 'Price' table rows based on token or block criteria.

    Parameters:
        token (str): Token address or symbol to clear the DB for.
        block (str): Block number (as string) to clear the DB for.

    Exactly one parameter must be provided.
    """
    if (token is None and block is None) or (token is not None and block is not None):
        raise ValueError("Exactly one option required: either --token or --block.")

    import y._db.utils  # do not remove
    from y._db.entities import Price, Token
    from y.constants import CHAINID

    @db_session
    def clear_prices() -> int:
        if token is not None:
            print(f"Deleting prices for {token}")
            deleted = 0
            if is_address(token):
                token = to_checksum_address(token)
                for t in select(t for t in Token if t.chain.id == CHAINID and t.address == token):
                    for p in select(p for p in Price if p.token == t and p.block):
                        print(f"Deleting {t.symbol} block {p.block.number} price {p.price}")
                        p.delete()
                        deleted += 1
                        commit()
                    t.delete()
                    commit()
            else:
                for t in select(t for t in Token if t.chain.id == CHAINID and t.address):
                    if t.symbol and t.symbol.lower() == token.lower():
                        for p in select(p for p in Price if p.token == t and p.block):
                            print(f"Deleting {t.symbol} block {p.block.number} price {p.price}")
                            p.delete()
                            deleted += 1
                            commit()
                        t.delete()
                        commit()
            return deleted
        else:
            try:
                block_number = int(block)
            except ValueError:
                raise ValueError("Block must be an integer value.")
            deleted = delete(p for p in Price if p.block.number == block_number)
            return deleted

    total_deleted = clear_prices()
    print(f"Cleared {total_deleted} rows from Price table based on the specified criteria.")


def db_select(target: str) -> None:
    """
    Selects a token from the database matching the given token symbol or token address,
    and prints a formatted output of the token details.
    """
    import y._db.utils  # do not remove
    from y._db.entities import Token
    from y.constants import CHAINID

    with db_session:
        if is_address(target):
            target = to_checksum_address(target)
            token = Token.get(chain=CHAINID, address=target)
        else:
            token = Token.get(chain=CHAINID, symbol=target)
        if token is None:
            print("Token not found.")
        else:
            details = {}
            # Extract token details from the entity's columns
            for col in token.__class__._columns_:
                try:
                    details[col] = getattr(token, col)
                except AttributeError:
                    pass
            print("Token found:")
            pprint(details)


def main() -> None:
    """
    The main entry point for the CLI.
    """
    parser = argparse.ArgumentParser(
        description="A CLI tool for managing the database and debugging operations."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # db command parser
    db_parser = subparsers.add_parser(
        "db", help="Perform maintenance operations on ypricemagic's database"
    )
    db_subparsers = db_parser.add_subparsers(dest="db_command", required=True)

    # db info command
    db_subparsers.add_parser("info", help="Display each table's row count and total storage size")

    # db vacuum command
    db_subparsers.add_parser(
        "vacuum",
        help="Run VACUUM operation to reclaim unused space and optimize the database.",
        description="""Run a VACUUM operation to reclaim unused space and improve performance.

        For SQLite:

        VACUUM rebuilds the entire database file, eliminating fragmentation and ensuring that unused space is reclaimed.

        For PostgreSQL:

        VACUUM marks dead row versions for reuse, freeing up space and often improving query performance.
        """,
    )

    # db clear command
    clear_parser = db_subparsers.add_parser(
        "clear", help="Clear cached price data by token or block"
    )
    group = clear_parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--token",
        type=str,
        help="Specify a token address or symbol to clear cached price data for.",
    )
    group.add_argument(
        "--block", type=str, help="Specify a block number to clear cached price data for."
    )

    # db nuke command
    nuke_parser = db_subparsers.add_parser("nuke", help="Drop all tables in the database")
    nuke_parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")

    # db select command
    select_parser = db_subparsers.add_parser(
        "select", help="Select a token from the database and display its details"
    )
    select_parser.add_argument("target", type=str, help="Token symbol or token address")

    # debug command parser
    debug_parser = subparsers.add_parser("debug", help="Debug pricing functionality")
    debug_subparsers = debug_parser.add_subparsers(dest="debug_command", required=True)

    # debug price command
    price_parser = debug_subparsers.add_parser("price", help="Debug token price retrieval")
    price_parser.add_argument("--token", type=str, required=True, help="Token address to debug")
    price_parser.add_argument(
        "--block", type=str, help="Block number at which to retrieve the price"
    )

    # debug curve command
    curve_parser = debug_subparsers.add_parser("curve", help="Debug Curve pool operations")
    curve_parser.add_argument(
        "--token", type=str, required=True, help="Token address (pool address) to debug"
    )
    curve_parser.add_argument(
        "--block", type=str, help="Block number at which to evaluate the pool"
    )

    args = parser.parse_args()

    # Dispatch commands
    if args.command == "db":
        if args.db_command == "nuke":
            db_nuke(force=args.force)
        elif args.db_command == "clear":
            db_clear(token=args.token, block=args.block)
        elif args.db_command == "info":
            db_info()
        elif args.db_command == "vacuum":
            db_vacuum()
        elif args.db_command == "select":
            db_select(args.target)
        else:
            print("Unknown db command.")
            sys.exit(1)
    elif args.command == "debug":
        if args.debug_command == "price":
            token = args.token
            block = args.block
            try:
                price = debug_price(token, int(block) if block else None)
                print(f"Price for token {token} at block {block or 'current'}: {price}")
            except Exception as e:
                print(f"Error debugging price: {e}")
                sys.exit(1)
        elif args.debug_command == "curve":
            # The curve debug command still uses Brownie script for now
            env = os.environ.copy()
            env["BAD"] = args.token
            if args.block:
                env["BLOCK"] = args.block

            network = env.get("BROWNIE_NETWORK_ID")
            script = "debug-curve"
            subprocess.run(["brownie", "run", script, "--network", network], env=env)
        else:
            print("Unknown debug command.")
            sys.exit(1)

    else:
        print("Unknown command.")
        sys.exit(1)


if __name__ == "__main__":
    main()
