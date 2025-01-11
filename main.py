import os
import sys

import app.controller as controller


def main() -> None:
    path_file = get_script_folder()
    app = controller.Controller(path_file)
    app.run()


def get_script_folder() -> str:
    if getattr(sys, "frozen", False):
        script_path = os.path.dirname(sys.executable)
    else:
        script_path = os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))
    return script_path


if __name__ == "__main__":
    main()
