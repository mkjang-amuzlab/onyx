import importlib.util
import os
from pathlib import Path
import sysconfig
import warnings

_stdlib_platform_spec = importlib.util.spec_from_file_location(
    "_stdlib_platform", Path(sysconfig.get_paths()["stdlib"]) / "platform.py"
)
assert _stdlib_platform_spec is not None and _stdlib_platform_spec.loader is not None
_stdlib_platform = importlib.util.module_from_spec(_stdlib_platform_spec)
_stdlib_platform_spec.loader.exec_module(_stdlib_platform)

_ONYX_DOCKER_ENV_STR = "ONYX_RUNNING_IN_DOCKER"
_DANSWER_DOCKER_ENV_STR = "DANSWER_RUNNING_IN_DOCKER"


def _resolve_container_flag() -> bool:
    onyx_val = os.getenv(_ONYX_DOCKER_ENV_STR)
    if onyx_val is not None:
        return onyx_val.lower() == "true"

    danswer_val = os.getenv(_DANSWER_DOCKER_ENV_STR)
    if danswer_val is not None:
        warnings.warn(
            f"{_DANSWER_DOCKER_ENV_STR} is deprecated and will be ignored in a future release. Use {_ONYX_DOCKER_ENV_STR} instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return danswer_val.lower() == "true"

    return False


_IS_RUNNING_IN_CONTAINER: bool = _resolve_container_flag()
_IS_RUNNING_IN_KUBERNETES: bool = os.getenv("KUBERNETES_SERVICE_HOST") is not None


def is_running_in_container() -> bool:
    return _IS_RUNNING_IN_CONTAINER


def is_running_in_kubernetes() -> bool:
    return _IS_RUNNING_IN_KUBERNETES


def system() -> str:
    return _stdlib_platform.system()
