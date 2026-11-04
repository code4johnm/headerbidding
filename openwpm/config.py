import tempfile
from dataclasses import dataclass, field
from json import JSONEncoder
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
from urllib.parse import urlparse

from dataclasses_json import DataClassJsonMixin
from dataclasses_json import config as DCJConfig

from .errors import ConfigError
from .types import BrowserId

BOOL_TYPE_VALIDATION_LIST = [True, False]
DISPLAY_MODE_VALIDATION_LIST = ["native", "headless", "xvfb"]
SUPPORTED_BROWSER_LIST = [
    "firefox"
]  # Using List instead of a str type to future proof the logic as OpenWPM may add support for more browsers in future
TP_COOKIES_OPTIONALS_LIST = ["always", "never", "from_visited"]
LOG_EXTENSION_TYPE_LIST = [".log"]
CONFIG_ERROR_STRING = (
    "Found {value} as value for {parameter_name} in BrowserParams. "
    "Supported values are {value_list}. Please look at "
    "docs/Configuration.md#browser-configuration-options for more information"
)
EXTENSION_ERROR_STRING = (
    "Found {extension} extension for {parameter_name} in ManagerParams "
    "supported extensions are {value_list}. Please look at "
    "docs/Configuration.md#platform-configuration-options for more information"
)
GENERAL_ERROR_STRING = (
    "Found invalid value `{value}` for {parameter_name} in {params_type}. "
    "Please look at docs/Configuration.md for more information"
)

ALL_RESOURCE_TYPES = {
    "beacon",
    "csp_report",
    "font",
    "image",
    "imageset",
    "main_frame",
    "media",
    "object",
    "object_subrequest",
    "ping",
    "script",
    "stylesheet",
    "sub_frame",
    "web_manifest",
    "websocket",
    "xml_dtd",
    "xmlhttprequest",
    "xslt",
    "other",
}


def str_to_path(string: Optional[str]) -> Optional[Path]:
    if string is not None:
        return Path(string)
    return None


def path_to_str(path: Optional[Path]) -> Optional[str]:
    if path is not None:
        return str(path.resolve())
    return None


@dataclass
class BrowserParams(DataClassJsonMixin):
    """
    Configuration that might differ per browser

    OpenWPM allows you to run multiple browsers with different
    configurations in parallel and this class allows you
    to customize behaviour of an individual browser
    """

    cookie_instrument: bool = True
    js_instrument: bool = False
    js_instrument_settings: List[Union[str, dict]] = field(
        default_factory=lambda: ["collection_fingerprinting"]
    )
    http_instrument: bool = False
    navigation_instrument: bool = False
    save_content: Union[bool, str] = False
    save_content_justification: str = ""
    """Required when save_content names resource types. At least 20 characters."""
    save_content_max_bytes: int = 0
    """Positive cap, at most 5000000, when save_content names resource types.
    Zero leaves the storage cap unset. Content saving stays off unless a
    resource-type list, a justification, and a cap are all set."""
    callstack_instrument: bool = False
    dns_instrument: bool = False
    seed_tar: Optional[Path] = field(
        default=None, metadata=DCJConfig(encoder=path_to_str, decoder=str_to_path)
    )
    display_mode: Literal["native", "headless", "xvfb"] = "native"
    browser: str = "firefox"
    prefs: dict = field(default_factory=dict)
    tp_cookies: str = "always"
    bot_mitigation: bool = False
    profile_archive_dir: Optional[Path] = field(
        default=None, metadata=DCJConfig(encoder=path_to_str, decoder=str_to_path)
    )

    tmp_profile_dir: Path = field(
        default=Path(tempfile.gettempdir()),
        metadata=DCJConfig(encoder=path_to_str, decoder=str_to_path),
    )
    """
    The tmp_profile_dir defaults to the OS's temporary file folder (typically /tmp) and is where the generated 
    browser profiles and residual files are stored.
    """

    maximum_profile_size: Optional[int] = None
    """
    The total amount of on disk space the generated 
    browser profiles and residual files are allowed to consume in bytes.
    If this option is not set, no checks will be performed

    Rationale
    ---------
    This option can serve as a happy medium between killing a browser after each
    crawl and allowing the application to still perform quickly.

    Used as a way to save space
    in a limited environment with minimal detriment to speed.

    If the maximum_profile_size is exceeded after a CommandSequence
    is completed, the browser will be shut down and a new one will
    be created. **Even with this setting you may temporarily have
    more disk usage than the sum of all maximum_profile_sizes**
    However, this will also ensure that a CommandSequence is
    allowed to complete without undue interruptions.

    Sample values
    -------------
    * 1073741824: 1GB
    * 20971520:  20MB - for testing purposes
    * 52428800:  50MB
    * 73400320:  70MB
    * 104857600: 100MB - IDEAL for 10+ browsers

    """

    recovery_tar: Optional[Path] = None
    donottrack: bool = False
    tracking_protection: bool = False
    custom_params: Dict[Any, Any] = field(default_factory=lambda: {})


@dataclass
class ManagerParams(DataClassJsonMixin):
    """
    Configuration for the TaskManager
    The configuration will be the same for all browsers running on the same
    TaskManager.
    It can be used to control storage locations or which watchdogs should
    run
    """

    data_directory: Path = field(
        default=Path.home() / "openwpm",
        metadata=DCJConfig(encoder=path_to_str, decoder=str_to_path),
    )
    """The directory into which screenshots and page dumps will be saved"""
    log_path: Path = field(
        default=Path.home() / "openwpm" / "openwpm.log",
        metadata=DCJConfig(encoder=path_to_str, decoder=str_to_path),
    )
    """The path to the file in which OpenWPM will log. The
    directory given will be created if it does not exist."""
    testing: bool = False
    """A platform wide flag that can be used to only run certain functionality
    while testing. For example, the Javascript instrumentation"""
    allowed_domains: Optional[List[str]] = None
    """Hostnames this TaskManager may visit. Validation rejects a missing or
    empty list. A host matches exactly or as a dot-boundary suffix
    (``a.example.com`` matches ``example.com``; ``notexample.com`` does not).
    Subresources and later ``webdriver.get`` calls inside a command are not
    filtered."""
    redact_identifiers: bool = False
    """When true, redact emails, tokens, and long hex strings in selected
    text fields and UTF-8 content bodies before storage. The library default
    is false so existing content hashes stay stable. Hardened entry points
    turn this on."""
    memory_watchdog: bool = False
    """A watchdog that tries to ensure that no Firefox instance takes up too much memory.
    It is mostly useful for long running cloud crawls"""
    process_watchdog: bool = False
    """It is used to create another thread that kills off `GeckoDriver` (or `Xvfb`)
    instances that haven't been spawned by OpenWPM. (GeckoDriver is used by
    Selenium to control Firefox and Xvfb a "virtual display" so we simulate having graphics when running on a server).
    """

    num_browsers: int = 1
    _failure_limit: Optional[int] = None
    """The number of command failures the platform will tolerate before raising a
        `CommandExecutionError` exception. Otherwise the default is set to 2 x the
         number of browsers plus 10. The failure counter is reset at the end of each
         successfully completed command sequence.
       For non-blocking command sequences that cause the number of failures to
         exceed `failure_limit` the `CommandExecutionError` is raised when
         attempting to execute the next command sequence."""

    @property
    def failure_limit(self) -> int:
        if self._failure_limit is None:
            return 2 * self.num_browsers + 10
        return self._failure_limit

    @failure_limit.setter
    def failure_limit(self, value: int) -> None:
        self._failure_limit = value


@dataclass
class BrowserParamsInternal(BrowserParams):
    browser_id: Optional[BrowserId] = None
    profile_path: Optional[Path] = None
    cleaned_js_instrument_settings: Optional[List[Dict[str, Any]]] = None


@dataclass
class ManagerParamsInternal(ManagerParams):
    storage_controller_address: Optional[Tuple[str, int]] = None
    logger_address: Optional[Tuple[str, ...]] = None
    screenshot_path: Optional[Path] = field(
        default=None, metadata=DCJConfig(encoder=path_to_str, decoder=str_to_path)
    )
    source_dump_path: Optional[Path] = field(
        default=None, metadata=DCJConfig(encoder=path_to_str, decoder=str_to_path)
    )


def host_allowed(url: str, allowed_domains: Optional[List[str]]) -> bool:
    """Return True when ``url`` is http(s) and its host is on the list."""
    if not allowed_domains:
        return False
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or parsed.username or parsed.password:
        return False
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host:
        return False
    for raw in allowed_domains:
        if not isinstance(raw, str):
            continue
        domain = raw.strip().lower().rstrip(".")
        if not domain or domain.startswith("."):
            continue
        if host == domain or host.endswith("." + domain):
            return True
    return False


def _validate_allowed_domains(manager_params: ManagerParams) -> None:
    domains = manager_params.allowed_domains
    if not isinstance(domains, list) or len(domains) == 0:
        raise ConfigError(
            "ManagerParams.allowed_domains is required and must be a non-empty "
            "list of hostnames. See docs/Configuration.md."
        )
    for domain in domains:
        if (
            not isinstance(domain, str)
            or not domain.strip()
            or any(ch in domain for ch in "/\\?# ")
            or domain.strip().lower() in {"*", "all"}
        ):
            raise ConfigError(
                "allowed_domains entries must be hostnames such as example.com, "
                "not URLs or wildcards."
            )


def _validate_save_content(browser_params: BrowserParams) -> None:
    save = browser_params.save_content
    if save is False:
        return
    if save is True:
        raise ConfigError(
            "save_content=True is rejected. Pass an explicit comma-separated "
            "resource type list, save_content_justification, and "
            "save_content_max_bytes."
        )
    if not isinstance(save, str):
        raise ConfigError(
            GENERAL_ERROR_STRING.format(
                value=save,
                parameter_name="save_content",
                params_type="BrowserParams",
            )
        )
    configured_types = {part.strip() for part in save.split(",") if part.strip()}
    if not configured_types.issubset(ALL_RESOURCE_TYPES):
        diff = configured_types.difference(ALL_RESOURCE_TYPES)
        raise ConfigError(
            "Unrecognized resource types provided "
            "in browser_params.save_content (%s)" % diff
        )
    justification = browser_params.save_content_justification
    if not isinstance(justification, str) or len(justification.strip()) < 20:
        raise ConfigError(
            "save_content requires save_content_justification of at least "
            "20 characters."
        )
    cap = browser_params.save_content_max_bytes
    if isinstance(cap, bool) or not isinstance(cap, int) or cap < 1 or cap > 5000000:
        raise ConfigError(
            "save_content_max_bytes must be an integer from 1 to 5000000."
        )


def validate_browser_params(browser_params: BrowserParams) -> None:
    if BrowserParams() == browser_params:
        return
    try:
        if browser_params.display_mode.lower() not in DISPLAY_MODE_VALIDATION_LIST:
            raise ConfigError(
                CONFIG_ERROR_STRING.format(
                    value=browser_params.display_mode,
                    value_list=DISPLAY_MODE_VALIDATION_LIST,
                    parameter_name="display_mode",
                )
            )

        if browser_params.browser.lower() not in SUPPORTED_BROWSER_LIST:
            raise ConfigError(
                CONFIG_ERROR_STRING.format(
                    value=browser_params.browser,
                    value_list=SUPPORTED_BROWSER_LIST,
                    parameter_name="browser",
                )
            )

        if browser_params.tp_cookies.lower() not in TP_COOKIES_OPTIONALS_LIST:
            raise ConfigError(
                CONFIG_ERROR_STRING.format(
                    value=browser_params.tp_cookies,
                    value_list=TP_COOKIES_OPTIONALS_LIST,
                    parameter_name="tp_cookies",
                )
            )

        if browser_params.callstack_instrument:
            raise ConfigError(
                "The callstack_instrument is currently non-functional "
                "(it has been broken since Firefox changes in prior versions). "
                "See https://github.com/openwpm/OpenWPM/issues/557 for details and progress. "
                "Do not enable this flag."
            )

        _validate_save_content(browser_params)

    except ConfigError:
        raise
    except Exception:
        raise ConfigError(
            "Something went wrong while validating BrowserParams. "
            "Please check values provided for BrowserParams are of expected types"
        )


def validate_manager_params(manager_params: ManagerParams) -> None:
    _validate_allowed_domains(manager_params)
    if ManagerParams(allowed_domains=manager_params.allowed_domains) == manager_params:
        return

    try:
        log_file_extension = manager_params.log_path.suffix
        if log_file_extension.lower() not in LOG_EXTENSION_TYPE_LIST:
            raise ConfigError(
                EXTENSION_ERROR_STRING.format(
                    extension=log_file_extension or "no",
                    value_list=LOG_EXTENSION_TYPE_LIST,
                    parameter_name="log_file",
                )
            )
    except (TypeError, AttributeError):
        raise ConfigError(
            GENERAL_ERROR_STRING.format(
                value=manager_params.log_path,
                parameter_name="log_file",
                params_type="ManagerParams",
            )
        )

    # This check is necessary to not cause any internal error
    if not isinstance(manager_params.failure_limit, int):
        raise ConfigError(
            GENERAL_ERROR_STRING.format(
                value=manager_params.failure_limit,
                parameter_name="failure_limit",
                params_type="ManagerParams",
            ).replace(
                "Please look at docs/Configuration.md for more information",
                "failure_limit must be of type `int` or `None`",
            )
        )


def validate_crawl_configs(
    manager_params: ManagerParams, browser_params: List[BrowserParams]
) -> None:
    validate_manager_params(manager_params)
    for bp in browser_params:
        validate_browser_params(bp)

    if len(browser_params) != manager_params.num_browsers:
        raise ConfigError(
            "Number of BrowserParams instances is not the same "
            "as manager_params.num_browsers. Make sure you are assigning number of browsers "
            "to be used to manager_params.num_browsers in your entry file"
        )


class ConfigEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj.resolve())
        return JSONEncoder.default(self, obj)
