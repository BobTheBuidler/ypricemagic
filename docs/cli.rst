CLI Tools
=========

The y/cli.py module provides command-line tools for debugging and database management.

Debugging
---------

# TODO: coming soon

Database Management
-------------------

- **db info**
  Description:
      Displays database information including table row counts and, for PostgreSQL, the storage size using pg_total_relation_size. For SQLite, it shows the file size along with row counts.

  Usage:
      ypricemagic db info

- **db vacuum**
  Description:
      Reclaims unused space by running a VACUUM operation. In SQLite, the database file is rebuilt; in PostgreSQL, space is reclaimed to improve performance.

  Usage:
      ypricemagic db vacuum

- **db clear**
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

- **db nuke**
  Description:
      Drops all tables in the database, effectively clearing all stored data. A confirmation prompt is shown unless the --force flag is used to bypass it.

  Usage:
      With confirmation:
          ypricemagic db nuke
      Without confirmation:
          ypricemagic db nuke --force
