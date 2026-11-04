#!/usr/bin/env python3
"""Validate or start one hardened measurement configuration.

``--check`` validates ``ManagerParams`` and ``BrowserParams`` and exits 0.
It does not launch Firefox. ``--run`` launches ``TaskManager`` only when
the Firefox binary is present.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from openwpm.config import (
    BrowserParams,
    ManagerParams,
    validate_crawl_configs,
)  # noqa: E402


def _domains() -> list[str]:
    raw = os.environ.get("OPENWPM_ALLOWED_DOMAINS", "localhost,127.0.0.1")
    return [part.strip() for part in raw.split(",") if part.strip()]


def build_params() -> tuple[ManagerParams, list[BrowserParams]]:
    data = Path(os.environ.get("CRAWL_DIRECTORY", "crawl-data"))
    manager = ManagerParams(
        num_browsers=1,
        data_directory=data,
        log_path=data / "openwpm.log",
        allowed_domains=_domains(),
        redact_identifiers=os.environ.get("REDACT_IDENTIFIERS", "1") != "0",
    )
    browser = BrowserParams(
        display_mode="headless",
        http_instrument=True,
        save_content=False,
    )
    validate_crawl_configs(manager, [browser])
    return manager, [browser]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args(argv)
    if args.run and args.check:
        print("Pass only one of --check or --run.", file=sys.stderr)
        return 2
    manager, browsers = build_params()
    if not args.run:
        domains = ",".join(manager.allowed_domains or [])
        print("hardened configuration accepted")
        print("allowed_domains={0}".format(domains))
        print("save_content={0}".format(browsers[0].save_content))
        print("redact_identifiers={0}".format(manager.redact_identifiers))
        return 0
    binary = Path(os.environ.get("FIREFOX_BINARY", "firefox-bin/firefox-bin"))
    if not binary.is_file():
        print(
            "Firefox is not installed at {0}. Run scripts/install-firefox.sh.".format(
                binary
            ),
            file=sys.stderr,
        )
        return 2
    from openwpm.command_sequence import CommandSequence
    from openwpm.storage.sql_provider import SQLiteStorageProvider
    from openwpm.task_manager import TaskManager

    url = os.environ.get("CRAWL_URL", "http://127.0.0.1/")
    structured = SQLiteStorageProvider(
        db_path=manager.data_directory / "crawl-data.sqlite"
    )
    manager_obj = TaskManager(manager, browsers, structured, None)
    sequence = CommandSequence(url)
    sequence.get(sleep=1, timeout=30)
    manager_obj.execute_command_sequence(sequence)
    manager_obj.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
