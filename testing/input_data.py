from pynput.keyboard import Controller, Key
import time

keyboard = Controller()


def select_all() -> None:  # type: ignore
    keyboard.press(Key.cmd)
    keyboard.press("a")
    keyboard.release("a")
    keyboard.release(Key.cmd)


def tab() -> None:
    keyboard.press(Key.tab)
    keyboard.release(Key.tab)


def type_macro() -> None:
    buffer = 6
    for i in range(buffer):
        print(buffer - i - 1)
        time.sleep(1)  # Give yourself time to switch to the target app
    for r in range(11):
        r += 0
        for c in range(7):
            c += 0
            select_all()
            keyboard.type(f"B.{c}.{r}")
            # time.sleep(0.25)
            tab()

    time.sleep(5)  # Give yourself time to switch to the target app


type_macro()
