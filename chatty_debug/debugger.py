import sys
import traceback
from functools import wraps

from chat_toolkit import OpenAIChatBot
from colorama import Fore, Style, just_fix_windows_console

just_fix_windows_console()


def _trim_traceback(tb_list: list[str], file_path: str):
    """
    Trim traceback to a certain point

    :param tb_list:
    :param file_path:
    :return:
    """
    last_runpy_index = 0
    for idx, line in enumerate(reversed(tb_list)):
        if file_path in line:
            last_runpy_index = len(tb_list) - idx + 1
            break
    return tb_list[0:1] + tb_list[last_runpy_index:]


def chatty_debug(
    prompt: str = "Help me debug the following python error.",
    runpy_mode: bool = False,
):
    """
    Execute a function. If there is an error, send information to ChatGPT to
    help debug the function.

    :param prompt: Prompt to give ChatGPT.
    :param runpy_mode: When in runpy mode, trim traceback to things after
    runpy.
    :return: Wrapped function's return value.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # noinspection PyBroadException
            try:
                return func(*args, **kwargs)
            except Exception:  # noqa: E722
                tb_list = traceback.format_exception(*sys.exc_info())
                # make sure every line is an item
                tb_list = [
                    item
                    for sublist in tb_list
                    for item in sublist.split("\n")
                    if item
                ]

                if runpy_mode:
                    tb_list = _trim_traceback(tb_list, "runpy.py")
                else:
                    tb_list = _trim_traceback(tb_list, "debugger.py")
                tb_string = "\n".join(tb_list)

                print(f"{Fore.RED}{tb_string}{Style.RESET_ALL}\n\n")
                chat = OpenAIChatBot()
                chat.prompt_chatbot(prompt)
                response, _ = chat.send_message(tb_string)
                print(f"{response}\n")
                sys.exit(1)

        return wrapper

    return decorator
