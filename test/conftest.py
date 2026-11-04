import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Callable, Generator, List, Literal, Protocol, Tuple

import pytest

from . import utilities

# Browser tests import OpenWPM inside fixtures. Importing it here required
# the full conda env (dataclasses_json and the rest) before any test could
# be collected, including the standard-library auction tests.
NUM_BROWSERS = 2

EXTENSION_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "..",
    "Extension",
)


@pytest.fixture(scope="session", autouse=True)
def enable_subprocess_coverage():
    """Enable coverage collection in child processes when running under coverage."""
    try:
        import coverage

        # Only set this if we're actually measuring coverage
        if coverage.Coverage.current() is not None:
            project_root = Path(__file__).parent.parent
            os.environ["COVERAGE_PROCESS_START"] = str(project_root / "pyproject.toml")
            # Ensure child processes write .coverage files to the project
            # root where pytest-cov can find and combine them.
            os.environ["COVERAGE_FILE"] = str(project_root / ".coverage")
    except ImportError:
        pass


def xpi():
    # Creates a new xpi using npm run build.
    print("Building new xpi")
    subprocess.check_call(["npm", "run", "build"], cwd=EXTENSION_DIR)


@pytest.fixture(name="xpi", scope="session")
def xpi_fixture():
    return xpi()


@pytest.fixture(scope="session")
def server():
    """Run an HTTP server during the tests."""
    print("Starting local_http_server")
    server, server_thread = utilities.start_server()
    yield
    print("\nClosing server thread...")
    server.shutdown()
    server_thread.join()


@pytest.fixture()
def default_params(tmp_path: Path, num_browsers: int = NUM_BROWSERS):
    """Browser and manager params for a headless test crawl."""
    from openwpm.config import BrowserParams, ManagerParams

    manager_params = ManagerParams(
        num_browsers=num_browsers,
        allowed_domains=["localhost", "127.0.0.1", "invalid"],
    )  # num_browsers is necessary to let TaskManager know how many browsers to spawn

    browser_params = [
        BrowserParams(display_mode="headless") for _ in range(num_browsers)
    ]
    manager_params.data_directory = tmp_path
    manager_params.log_path = tmp_path / "openwpm.log"
    manager_params.testing = True
    return manager_params, browser_params


@pytest.fixture()
def task_manager_creator(server: None, xpi: None):
    """We create a callable that returns a TaskManager that has
    been configured with the Manager and BrowserParams"""

    # We need to create the fixtures like this because usefixtures doesn't work on fixtures
    def _create_task_manager(params):
        from openwpm.storage.sql_provider import SQLiteStorageProvider
        from openwpm.task_manager import TaskManager

        manager_params, browser_params = params
        db_path = manager_params.data_directory / "crawl-data.sqlite"
        structured_provider = SQLiteStorageProvider(db_path)
        manager = TaskManager(
            manager_params,
            browser_params,
            structured_provider,
            None,
        )
        return manager, db_path

    return _create_task_manager


class HttpParams(Protocol):
    def __call__(self, display_mode: Literal["headless", "xvfb"] = "headless"): ...


@pytest.fixture()
def http_params(
    default_params,
) -> HttpParams:
    manager_params, browser_params = default_params
    for browser_param in browser_params:
        browser_param.http_instrument = True

    def parameterize(
        display_mode: Literal["headless", "xvfb"] = "headless",
    ):
        for browser_param in browser_params:
            browser_param.display_mode = display_mode
        return manager_params, browser_params

    return parameterize


@pytest.fixture()
def mp_logger(tmp_path: Path) -> Generator[Any, Any, None]:
    from openwpm.mp_logger import MPLogger

    log_path = tmp_path / "openwpm.log"
    logger = MPLogger(log_path, log_level_console=logging.DEBUG)
    yield logger
    logger.close()
    # The performance hit for this might be unacceptable but it might help us discover bugs
    with log_path.open("r") as f:
        for line in f:
            assert "ERROR" not in line
