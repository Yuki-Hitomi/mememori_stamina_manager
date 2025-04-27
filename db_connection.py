import os
import asyncpg
from dotenv import load_dotenv

from logging_config import setup_logging

# 環境変数を読み込む
load_dotenv()

# ロギング設定
logger = setup_logging()

# データベース接続設定
DB_CONFIG = {
    "user": os.getenv("DB_CONFIG_USER"),
    "password": os.getenv("DB_CONFIG_PASSWORD"),
    "database": os.getenv("DB_CONFIG_DATABASE"),
    "host": os.getenv("DB_CONFIG_HOST"),
    "port": os.getenv("DB_CONFIG_PORT"),
}

# 環境変数のチェック
for key, value in DB_CONFIG.items():
    if value is None:
        logger.error(f"Missing environment variable: {key}")
        raise ValueError(f"Environment variable {key} is missing.")

# データベース接続を行う関数
async def get_db_connection():
    """データベース接続を取得する関数"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        raise e

# データベース接続を閉じる関数
async def close_db_connection(conn):
    """データベース接続を閉じる関数"""
    await conn.close()
