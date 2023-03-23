import inspect
from functools import wraps
from typing import Optional, Union

from chat_toolkit import OpenAIChatBot
from colorama import Fore, Style, just_fix_windows_console

just_fix_windows_console()


_DEFAULT_PROMPTS = {
    "Refactor": "Rewrite the function with type hints, reStructuredText "
    "docstrings (without repeating the types in the type hints). "
    "Make sure the code is clean and upholds accepted standards "
    "in Python. Make any optimizations you see for performance.",
    "Tests": "Write some unit tests with docstrings using pytest for the "
    "refactored function. Unit tests should cover edge cases and be "
    "small and use pytest.mark.parametrize where needed. Don't "
    "worry about imports. Remember that Python is not strictly typed.",
}
_COLORS = ["GREEN", "YELLOW", "LIGHTMAGENTA_EX", "CYAN"]


def suggest_improvements(
    prompt: str = "You are going to help me improve the following Python "
    "code. Be concise and clean. Keep in mind that Python is "
    "not strictly typed. I am using a Python version >= 3.9.",
    refactor_prompt: Union[bool, str] = _DEFAULT_PROMPTS["Refactor"],
    test_prompt: Union[bool, str] = _DEFAULT_PROMPTS["Tests"],
    additional_prompts: Optional[dict[str, str]] = None,
    run: bool = False,
):
    """
    Suggest documentation for a function.

    :param prompt: Prompt to give to ChatGPT.
    :param refactor_prompt: Prompt to give ChatGPT for refactoring the
    function.
    :param test_prompt: Prompt to give ChatGPT for writing tests for the
    function.
    :param additional_prompts: Additional prompts to request from ChatGPT,
    key should be a title for the prompt and the value should be the prompt.
    Will execute in order after refactor_prompt and test_prompt (in order,
    assuming neither are Falsey skipped).
    :param run: Whether to run the function.
    :return: Wrapped function's return value, if run
    """
    improvement_prompts = {}
    if refactor_prompt:
        improvement_prompts["Refactor"] = refactor_prompt
    if test_prompt:
        improvement_prompts["Tests"] = test_prompt

    if additional_prompts:
        improvement_prompts.update(additional_prompts)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            source = inspect.getsource(func)
            source = "\n".join(source.split("\n")[1:])
            chat = OpenAIChatBot()
            chat.prompt_chatbot(f"{prompt}: ```python\n{source}```")
            print(f"{Fore.BLUE}Code:\n{source}{Style.RESET_ALL}\n")
            for ii, (improvement, improvement_prompt) in enumerate(
                improvement_prompts.items()
            ):
                response, _ = chat.send_message(improvement_prompt)
                color = Fore.__dict__[_COLORS[ii % len(_COLORS)]]
                print(f"{color}{improvement}:\n{response}{Style.RESET_ALL}\n")

            if run:
                return func(*args, **kwargs)

        return wrapper

    return decorator
