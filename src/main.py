import time
import json
import logging
import threading
from datetime import date
from queue import Queue

from config import Config, setup_logging
from clear_buffer import clear_input_buffer
from audio import Audio
from get_idm import NFCReader
from database import GetMember

queue = Queue()
setup_logging()
logger = logging.getLogger(__name__)


def is_entering(id: str) -> bool:
    """
    すでに入室済みかどうかを判定する
    引数: id (str) - IDm
    返り値: bool - 入室済みかどうか
    """
    with open("data/entrants.json", "r") as f:
        all_data = json.load(f)
    entrants = all_data["entrants"]
    all = all_data["all"]
    today = date.today().strftime("%Y-%m-%d")
    if today not in all_data:
        all_data[today] = 0
    today_count = all_data[today]
    if id in entrants:
        is_entering = False
        entrants.remove(id)
    else:
        is_entering = True
        entrants.append(id)
        all += 1
        today_count += 1
    all_data = {"entrants": entrants, "all": all, today: today_count}
    with open("data/entrants.json", "w") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    return is_entering


def read_from_pasori(queue: Queue) -> None:
    """
    NFCリーダーからIDmを読み取り、キューに格納する
    引数: queue (Queue) - IDmを格納するキュー
    返り値: なし
    """
    reader = NFCReader()
    while True:
        try:
            idm = reader.read_from_pasori()
            if idm:
                print("IDm: ", idm)
                queue.put(idm)
                print(queue.queue)
        except Exception as e:
            logger.error(f"Error reading from pasori: {e}")
        finally:
            clear_input_buffer()
            print("Input Number: ", end="", flush=True)
            time.sleep(0.5)


def read_from_stdin(queue: Queue) -> None:
    """
    標準入力からIDmを読み取り、キューに格納する
    引数: queue (Queue) - IDmを格納するキュー
    返り値: なし
    """
    while True:
        try:
            number = input().strip()
            if len(number) == 8:
                number = number[:-1]
            if len(number) == 7 or len(number) == 16:
                queue.put(number)
            else:
                print(f"Invalid number: {number}")
        except Exception as e:
            logger.error(f"Error reading from stdin: {e}")
        finally:
            clear_input_buffer()
            print("Touch Card > ", end="", flush=True)
            time.sleep(0.5)


def main(queue: Queue) -> None:
    """
    メイン関数
    引数: queue (Queue) - IDmを格納するキュー
    返り値: なし
    """
    while True:
        try:
            number = queue.get(block=True)
            member = GetMember.get_member(number)
            if member is None:
                member = {"mmaid": number, "called_by": "", "avatar_url": ""}
            message = "enter" if is_entering(number) else "exit"
            Audio.create_or_load_audio(member["mmaid"], message, member["called_by"])
            Audio.play_audio_message(member, message)
        except Exception as e:
            logger.error(f"Error in main: {e}")
        finally:
            queue.task_done()


def start_thread(target, *args) -> threading.Thread:
    """
    新しいスレッドを開始する
    引数: target (function) - 関数
          args (tuple) - 関数に渡す引数
    返り値: threading.Thread - 新しいスレッド
    """
    thread = threading.Thread(target=target, args=args)
    thread.daemon = True
    thread.start()
    return thread


if __name__ == "__main__":
    try:
        print(Config.TEST)
        if not Config.TEST:
            pasori_thread = start_thread(read_from_pasori, queue)
            print("Started pasori thread")

        stdin_thread = start_thread(read_from_stdin, queue)
        main_thread = start_thread(main, queue)
        print("Input Number: ", end="", flush=True)

        while True:
            time.sleep(1)

    except Exception as e:
        logger.error(f"Error starting threads: {e}")
        exit(1)
