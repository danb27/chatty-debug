import argparse
import runpy
from typing import Any, Optional

from .debugger import chatty_debug


def chatty_debug_script(script_path: str, prompt: Optional[str] = None):
    kwargs: dict[str, Any] = {"runpy_mode": True}
    if prompt:
        kwargs["prompt"] = prompt

    @chatty_debug(**kwargs)
    def _inner():
        runpy.run_path(script_path, run_name="__main__")

    _inner()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a Python script with chatty-debug."
    )
    parser.add_argument("script", help="Path to the Python script to run.")
    parser.add_argument(
        "--prompt", help="Custom prompt to give ChatGPT, if desired."
    )
    args = parser.parse_args()
    chatty_debug_script(args.script, args.prompt)
