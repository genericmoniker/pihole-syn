import collections
import contextlib
import datetime
import logging
import os
import pathlib
import sqlite3
import sys
import time

POLL_INTERVAL_SECONDS = 60  # DB gets updated every minute by default
POLL_QUERY = """
    SELECT id, timestamp, status, domain, client
    FROM queries
    WHERE id >= ?
    AND status = 7  -- status 7 means blocked by upstream server.
    ORDER BY id DESC;
"""
LATEST_ENTRY_QUERY = """
    SELECT id
    FROM queries
    ORDER BY id DESC
    LIMIT 1;
"""

# Fields here should match those selected in the POLL_QUERY.
Entry = collections.namedtuple("Entry", "id timestamp status domain client")

logger = logging.getLogger(__name__)


def setup_logging(level=logging.DEBUG):
    """Set up logging to stdout."""
    fmt = "{asctime} {levelname:8}: {message}"
    formatter = ISO8601Formatter(fmt, style="{")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
    return root_logger


class ISO8601Formatter(logging.Formatter):
    """Formatter to output ISO8601 date/time with milliseconds and timezone."""

    def formatTime(self, record, datefmt=None):
        return (
            datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc)
            .astimezone()
            .isoformat()
        )


def monitor_db(db_path):
    with contextlib.closing(sqlite3.connect(db_path)) as conn:
        while True:
            try:
                with contextlib.closing(conn.cursor()) as cursor:
                    cursor.execute(LATEST_ENTRY_QUERY)
                    id_pos = cursor.fetchone()[0]
                    time.sleep(POLL_INTERVAL_SECONDS)
                    cursor.execute(POLL_QUERY, (id_pos,))
                    block_rows = cursor.fetchall()
                if block_rows:
                    notify(Entry(*row) for row in block_rows)
            except Exception:
                logger.exception("Error in monitor loop.")


def notify(entries):
    for entry in entries:
        request_time = datetime.datetime.fromtimestamp(entry.timestamp)
        logger.info(
            "Upstream block at %s: %s, client=%s",
            request_time,
            entry.domain,
            entry.client,
        )


def main():
    setup_logging()
    logger.info("===== Pi-Hole Notifier Startup =====")

    db_file = os.getenv("FTL_DB_FILE")
    if not db_file:
        logger.error("FTL_DB_FILE environment variable not set!")
        return 1

    db_path = pathlib.Path(db_file)
    if not db_path.exists():
        logger.error(f"'{db_path}' not found.")
        return 1

    monitor_db(db_path)


if __name__ == "__main__":
    sys.exit(main())
