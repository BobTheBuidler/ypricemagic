CLI Tools
=========

The y/cli.py module provides command-line tools for debugging and database management.

Debugging
---------

The CLI includes two debugging commands that leverage Brownie's run command to execute dedicated debugging scripts. They are designed to simplify the process of investigating price retrieval and Curve pool operations without manually setting environment variables.

debug price
~~~~~~~~~~~
Description:
    Debug token price retrieval. This command runs the Brownie script "debug-price" using the specified token address and, optionally, a block number. The token is passed via the --token flag and the block number via --block.

Usage:
    ypricemagic debug price --token <token_address> [--block <block_number>]

Example:
    ypricemagic debug price --token 0xABCdef... --block 1234567

debug curve
~~~~~~~~~~~
Description:
    Debug Curve pool operations by running the Brownie script "debug-curve". This command requires a pool token address provided through the --token flag. An optional --block flag sets the block number for evaluation.

Usage:
    ypricemagic debug curve --token <pool_address> [--block <block_number>]

Example:
    ypricemagic debug curve --token 0x123456...

Database Management
-------------------

db info
~~~~~~~
Description:
    Displays database information including table row counts and, for PostgreSQL, the storage size using pg_total_relation_size. For SQLite, it shows the file size along with row counts.

Usage:
    ypricemagic db info

db vacuum
~~~~~~~~~
Description:
    Reclaims unused space by running a VACUUM operation. In SQLite, the database file is rebuilt; in PostgreSQL, space is reclaimed to improve performance.

Usage:
    ypricemagic db vacuum

db clear
~~~~~~~~
Description:
    Clears cached price data from the database. You must supply exactly one of the following options:
      - --token: Token address or symbol.
      - --block: Block number.

Usage:
    To clear by token address:
        ypricemagic db clear --token 0xABCdef
    To clear by token symbol:
        ypricemagic db clear --token MOON
    To clear by block:
        ypricemagic db clear --block 1000000

db nuke
~~~~~~~
Description:
    Drops all tables in the database, effectively clearing all stored data. A confirmation prompt is shown unless the --force flag is used to bypass it.

Usage:
    With confirmation:
        ypricemagic db nuke
    Without confirmation:
        ypricemagic db nuke --force

db select
~~~~~~~~~
Description:
    Selects a token from the database matching the specified token address or token symbol, and displays detailed information about the token.

Usage:
    ypricemagic db select <target>
    (Replace <target> with the token address or symbol, for example:
        ypricemagic db select 0x123abc... or
        ypricemagic db select MOON)
