import discord
from discord import option
from db_connection import get_db_connection, close_db_connection
from logging_config import setup_logging

logger = setup_logging()

def command_setup(bot: discord.Bot):
    """スタミナデータを削除するコマンドを登録"""

    @bot.slash_command(
        name="remove",
        description="スタミナデータを削除します。",
    )
    @option(
        name="target_account",
        description="【管理者用】対象のDiscordアカウント",
        required=False,
    )
    @option(
        name="custom_name",
        description="任意の名前で登録されたデータを削除",
        required=False,
    )
    async def remove(ctx: discord.ApplicationContext, target_account: discord.Member = None, custom_name: str = None):
        """スタミナデータを削除するコマンド"""
        user_id = ctx.author.id
        logger.info(f"Received /remove command from user ID: {user_id}, target_account: {target_account}, custom_name: {custom_name}")

        try:
            conn = await get_db_connection()
            logger.debug("Database connection established.")

            if custom_name:
                # 任意の名前で登録されたデータを削除
                target_id = -1  # 特殊なIDとして -1 を使用
                target_name = custom_name
            else:
                # 権限チェック
                if target_account and not ctx.author.guild_permissions.administrator:
                    await ctx.respond("他人のデータを操作する権限がありません。", ephemeral=True)
                    return
                target_id = target_account.id if target_account else user_id
                target_name = target_account.display_name if target_account else ctx.author.display_name

            # データ削除処理
            if target_id == -1 and target_name:
                await conn.execute(
                    """
                    DELETE FROM mememori_stamina
                    WHERE guild_id = $1 AND user_id = $2 AND user_name = $3
                    """,
                    ctx.guild.id, target_id, target_name
                )
            else:
                await conn.execute(
                    """
                    DELETE FROM mememori_stamina
                    WHERE guild_id = $1 AND user_id = $2
                    """,
                    ctx.guild.id, target_id
                )

            await ctx.respond(f"{target_name} のスタミナデータを削除しました。", ephemeral=True)
            logger.info(f"Stamina data removed for user ID: {target_id} by user ID: {user_id}.")
        except Exception as e:
            logger.error(f"Error removing stamina for user ID: {user_id}: {e}")
            await ctx.respond("スタミナデータの削除中にエラーが発生しました。", ephemeral=True)
        finally:
            if conn:
                await close_db_connection(conn)
                logger.debug("Database connection closed.")