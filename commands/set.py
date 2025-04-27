import discord
from discord import option
from db_connection import get_db_connection, close_db_connection
from logging_config import setup_logging

logger = setup_logging()

def command_setup(bot: discord.Bot):
    """スタミナを設定するコマンドを登録"""

    @bot.slash_command(
        name="set",
        description="スタミナを設定します。",
    )
    @option(
        name="stamina",
        description="設定するスタミナの値",
        required=True,
        min_value=0,
    )
    @option(
        name="target_account",
        description="【管理者用】対象のDiscordアカウント",
        required=False,
    )
    @option(
        name="custom_name",
        description="任意の名前を指定（誰でも編集可能）",
        required=False,
    )
    async def set(ctx: discord.ApplicationContext, stamina: int, target_account: discord.Member = None, custom_name: str = None):
        """スタミナを設定するコマンド"""
        user_id = ctx.author.id
        username = ctx.author.display_name
        logger.info(f"Received /set command from user ID: {user_id}, stamina: {stamina}, target_account: {target_account}, custom_name: {custom_name}")

        try:
            conn = await get_db_connection()
            logger.debug("Database connection established.")

            # ターゲットのIDと名前を決定
            if custom_name:
                target_id = -1  # 特殊なIDとして -1 を使用
                target_name = custom_name

                # 重複チェック
                existing = await conn.fetchrow(
                    """
                    SELECT user_name FROM mememori_stamina
                    WHERE guild_id = $1 AND user_name = $2
                    """,
                    ctx.guild.id, target_name
                )
                if existing:
                    await ctx.respond(f"名前 '{target_name}' は既に使用されています。別の名前を指定してください。", ephemeral=True)
                    return
            else:
                # 権限チェック
                if target_account and not ctx.author.guild_permissions.administrator:
                    await ctx.respond("他人のデータを操作する権限がありません。", ephemeral=True)
                    return
                target_id = target_account.id if target_account else user_id
                target_name = target_account.display_name if target_account else username

            # スタミナを保存
            if target_id == -1:
                # 任意名の場合はINSERTのみを実行
                await conn.execute(
                    """
                    INSERT INTO mememori_stamina (guild_id, user_id, user_name, stamina, updated_at)
                    VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP)
                    """,
                    ctx.guild.id, target_id, target_name, stamina
                )
            else:
                # 通常のユーザーの場合はON CONFLICTを使用
                await conn.execute(
                    """
                    INSERT INTO mememori_stamina (guild_id, user_id, user_name, stamina, updated_at)
                    VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP)
                    ON CONFLICT (guild_id, user_id, user_name)
                    DO UPDATE SET 
                        stamina = EXCLUDED.stamina, 
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    ctx.guild.id, target_id, target_name, stamina
                )
            await ctx.respond(f"{target_name} のスタミナを {stamina} に更新しました。", ephemeral=True)
            logger.info(f"Stamina updated for user ID: {target_id} by user ID: {user_id}.")
        except Exception as e:
            logger.error(f"Error setting stamina for user ID: {user_id}: {e}")
            await ctx.respond("スタミナの設定中にエラーが発生しました。", ephemeral=True)
        finally:
            if conn:
                await close_db_connection(conn)
                logger.debug("Database connection closed.")