import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logging():
    """ロギングをセットアップする関数"""
    # ログディレクトリが存在しない場合は作成
    log_dir = os.getenv("LOG_DIR", "log")
    os.makedirs(log_dir, exist_ok=True)

    # 環境変数からログレベルを取得し、デフォルトはINFO
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str)

    log_filename = os.path.join(log_dir, "discord_bot_mememori_stamina_manager.log")

    # ロガーを取得
    logger = logging.getLogger()

    # 既存のハンドラをクリア
    if logger.hasHandlers():
        logger.handlers.clear()

    # ログレベルを設定
    logger.setLevel(log_level)

    # ファイルハンドラの設定
    file_handler = TimedRotatingFileHandler(
        filename=log_filename,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] [%(process)d] [%(threadName)s]: %(message)s"
        )
    )
    logger.addHandler(file_handler)

    # コンソールハンドラの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] [%(process)d] [%(threadName)s]: %(message)s"
        )
    )
    logger.addHandler(console_handler)

    return logger
