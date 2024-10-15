import os
import logging
import binascii

import nfc
import pygame

from config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
nfcpy_logger = logging.getLogger("nfc")
nfcpy_logger.setLevel(logging.WARNING)


class NFCReader:
    """
    NFCリーダーを使ってIDmを読み取るクラス
    """

    def __init__(self):
        """
        NFCリーダーの初期化
        """
        self.idm = None
        self.logger = logging.Logger(__name__)

    def on_startup(self, targets):
        """
        NFCリーダーが起動したときに実行される関数
        """
        for target in targets:
            target.sensf_req = bytearray.fromhex("0000030000")
        return targets

    def on_connect(self, tag):
        """
        NFCリーダーがカードに接続したときに実行される関数
        引数: tag (nfc.tag.Tag) - NFCカードの情報
        返り値: bool型
        """
        try:
            print("Card Touched")
            sound_file = "./se/maou_se_8bit02.wav"
            self.play_sound(sound_file)
            self.idm = binascii.hexlify(tag._nfcid).lower().decode("utf-8")
            return True
        except Exception as e:
            self.logger.error(f"Failed to read IDm: {e}")
            return False

    def play_sound(self, sound_file: str):
        """
        指定された音声ファイルを再生する
        引数: sound_file (str) - 音声ファイルのパス
        返り値: なし
        """
        try:
            if not os.path.exists(sound_file):
                logger.error(f"Audio file does not exist: {sound_file}")
                return

            pygame.mixer.init()
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.set_volume(1)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

        except Exception as e:
            logger.error(f"Failed to play audio message: {e}")

    def read_from_pasori(self):
        """
        NFCリーダーを使ってIDmを読み取る
        引数: なし
        返り値: str型 - IDm
        """
        try:
            with nfc.ContactlessFrontend("usb:054c:06c1") as clf:
                rdwr = {
                    "targets": ["212F"],
                    "on-startup": self.on_startup,
                    "on-connect": self.on_connect,
                }
                clf.connect(rdwr=rdwr)
        except IOError as e:
            self.logger.error(f"Failed to connect to NFC reader: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        return self.idm


if __name__ == "__main__":
    reader = NFCReader()
    idm = reader.read_from_pasori()
    print(f"IDm: {idm}")
