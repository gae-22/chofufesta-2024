import os
import logging

import pygame
from gtts import gTTS

from config import setup_logging, Member

setup_logging()
logger = logging.getLogger(__name__)


class Audio:
    @staticmethod
    def create_audio(text: str, filename: str, lang="ja") -> None:
        """
        テキストから音声ファイルを生成する
        引数:   text (str) - テキスト
                filename (str) - 保存するファイル名
                lang (str) - 言語
        返り値: なし
        """
        try:
            tts = gTTS(text, lang=lang)
            tts.save(filename)
        except Exception as e:
            logger.error(f"Failed to create audio file {filename}: {e}")

    @staticmethod
    def create_or_load_audio(user_id: str, message: str, called_by: str) -> None:
        """
        メッセージに対応する音声ファイルを生成もしくは読み込む
        引数:   user_id (str) - ユーザーID
                message (str) - メッセージ
                called_by (str) - 呼び出し元
        返り値: なし
        """
        if called_by == "":
            action_text = (
                "いらっしゃいませ" if message == "enter" else "ありがとうございました"
            )
            filename = f"./audio/{message}.mp3"
        else:
            action_text = (
                "さん，こんにちは．" if message == "enter" else "さん，お疲れ様でした．"
            )
            filename = f"./audio/{user_id}_{message}.mp3"
        if not os.path.exists(filename):
            try:
                os.makedirs("./audio", exist_ok=True)
                Audio.create_audio(f"{called_by}{action_text}", filename)
            except OSError as e:
                logger.error(f"Failed to create directory for audio: {e}")

    @staticmethod
    def play_audio_message(member: Member, message: str) -> None:
        """
        音声メッセージを再生する
        引数:   member (Member) - メンバー情報
                message (str) - メッセージ
        返り値: なし
        """
        try:
            if member["called_by"] == "":
                filename = f"./audio/{message}.mp3"
            else:
                filename = f"./audio/{member['mmaid']}_{message}.mp3"
            if not os.path.exists(filename):
                logger.error(f"Audio file does not exist: {filename}")
                return

            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            logger.error(f"Failed to play audio message: {e}")
