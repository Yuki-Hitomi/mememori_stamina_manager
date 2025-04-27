import os
import discord
import importlib
import inspect
import json
from dotenv import load_dotenv

from logging_config import setup_logging

# 環境変数を読み込む
load_dotenv(override=True)

# ロギング設定
logger = setup_logging()

# Discordボットのインスタンス作成
bot = discord.Bot()

# メンテナンスモードを設定するファイル
MAINTENANCE_FILE = "maintenance.json"

# メンテナンスモードを読み込む関数
def load_maintenance_mode():
    try:
        with open(MAINTENANCE_FILE, "r") as f:
            data = json.load(f)
        return data.get("maintenance_mode", False)
    except FileNotFoundError:
        logger.warning(f"{MAINTENANCE_FILE} not found. Defaulting to maintenance mode off.")
        return False
    except json.JSONDecodeError:
        logger.error(f"Error decoding {MAINTENANCE_FILE}. Defaulting to maintenance mode off.")
        return False

@bot.event
async def on_ready():
    """ボットが起動したときの処理"""
    logger.info(f"Bot logged in as {bot.user.name} [{bot.user.id}]")


# コマンド実行前にメンテナンスモードをチェックする
@bot.before_invoke
async def before_any_command(ctx):
    maintenance_mode = load_maintenance_mode()
    logger.info(f"Maintenance mode: {maintenance_mode}")
    if maintenance_mode:
        await ctx.respond("🚧 現在メンテナンス中です。しばらくお待ちください。", ephemeral=True)
        raise discord.ext.commands.CommandError("Bot is in maintenance mode")

# コマンドディレクトリ内のモジュールを動的にインポート
commands_dir = os.path.join(os.path.dirname(__file__), "commands")

for filename in os.listdir(commands_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"commands.{filename[:-3]}"
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "command_setup") and inspect.isfunction(module.command_setup):
                module.command_setup(bot)
            else:
                logger.warning(f"Module {module_name} does not have a 'command_setup' function.")
        except ModuleNotFoundError as e:
            logger.error(f"Module {module_name} not found: {e}")
        except Exception as e:
            logger.error(f"Error loading module {module_name}: {e}")

# DISCORD_TOKENが設定されていない場合のエラーチェック
discord_token = os.getenv("DISCORD_TOKEN")
if not discord_token:
    logger.error("DISCORD_TOKEN environment variable is not set. Exiting.")
    exit(1)

# ボットの起動
try:
    bot.run(discord_token)
except Exception as e:
    logger.error(f"Error starting the bot: {e}")
