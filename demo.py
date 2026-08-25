import argparse
from pathlib import Path

from openwpm.command_sequence import CommandSequence
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager

# The list of sites that we wish to crawl
NUM_BROWSERS = 3
sites = [
    "http://www.example.com",
    "http://www.princeton.edu",
    "http://citp.princeton.edu/",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Firefox in headless mode (used by CI).",
    )
    args = parser.parse_args()
    display_mode = "headless" if args.headless else "native"

    data_dir = Path("./datadir/")
    data_dir.mkdir(parents=True, exist_ok=True)

    manager_params = ManagerParams(
        num_browsers=NUM_BROWSERS,
        data_directory=data_dir,
        log_path=data_dir / "openwpm.log",
    )
    browser_params = [
        BrowserParams(http_instrument=True, display_mode=display_mode)
        for _ in range(NUM_BROWSERS)
    ]
    # Launch only browser 0 headless when --headless is not set (legacy demo).
    if not args.headless:
        browser_params[0].display_mode = "headless"

    manager = TaskManager(
        manager_params,
        browser_params,
        SQLiteStorageProvider(data_dir / "crawl-data.sqlite"),
        None,
    )

    for site in sites:
        command_sequence = CommandSequence(site)
        command_sequence.get(sleep=0, timeout=60)
        manager.execute_command_sequence(command_sequence)

    manager.close()


if __name__ == "__main__":
    main()
