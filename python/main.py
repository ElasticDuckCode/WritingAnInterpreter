import os

from src.monkey.repl import start

TEXT = r"""
                              _
  _ __ ___     ___    _ __   | | __   ___
 | '_ ` _ \   / _ \  | '_ \  | |/ /  / _ \
 | | | | | | | (_) | | | | | |   <  |  __/
 |_| |_| |_|  \___/  |_| |_| |_|\_\  \___|
"""
ICON = r"""
                      ██████████████
                    ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓████
                  ████▓▓▓▓▓▓░░░░▓▓▓▓░░██
                ██▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░██
                ██▓▓▓▓▓▓░░░░░░██░░░░██░░██
                ██▓▓██▓▓░░░░░░██░░░░██░░██
                ██▓▓██▓▓░░██░░░░░░░░░░░░░░██
                  ██▓▓▓▓██░░░░░░░░░░░░░░░░░░██
      ██████        ██▓▓██░░░░░░░░████░░░░░░██
    ██▓▓▓▓▓▓██        ██░░████████░░░░██████
  ██▓▓▓▓▓▓▓▓▓▓██      ████░░░░░░░░░░░░░░██
  ██▓▓▓▓██▓▓▓▓██    ██▓▓▓▓██████████████
  ██▓▓▓▓▓▓██████████▓▓▓▓▓▓▓▓▓▓██▓▓▓▓██
    ██▓▓▓▓▓▓▓▓▓▓██▓▓▓▓▓▓▓▓██▓▓▓▓██▓▓▓▓██
      ████████████▓▓▓▓▓▓▓▓▓▓██▓▓▓▓██▓▓▓▓██
                ██████████▓▓██░░░░░░██░░░░██
              ██░░░░░░░░░░██░░░░░░░░██░░░░██
              ██░░░░░░░░░░██░░░░░░██░░░░██
              ██████████████████████████
"""


def main():
    user = os.getlogin().capitalize()
    print(ICON)
    print(f"Hello {user}! This is the Monkey programming language!")
    print("Feel free to type in commands.")
    start()
    return


if __name__ == "__main__":
    main()
