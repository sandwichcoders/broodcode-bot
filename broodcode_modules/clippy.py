import os
import shlex


class Clippy:
    def __init__(self) -> None:
        self.__clipboard = ""

    def c_print(self, text):
        self.__clipboard += f"{text}\n"
        print(text)

    def copy_to_clipboard(self):
        # Use shlex.quote to properly escape the string for shell commands
        sanitized_text = shlex.quote(self.__clipboard)
        command = f'echo {sanitized_text} | pbcopy'
        os.system(command)
