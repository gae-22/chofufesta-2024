import sys
import tty
import select
import termios


def clear_input_buffer():
    """
    ターミナルの入力バッファをクリアする
    引数: なし
    返り値: なし
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)

        while select.select([sys.stdin], [], [], 0)[0]:
            sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
