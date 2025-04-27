import discord
from db_connection import get_db_connection, close_db_connection
from logging_config import setup_logging

logger = setup_logging()

def command_setup(bot: discord.Bot):
    """スタミナリストを表示するコマンドを登録"""

    @bot.slash_command(
        name="view",
        description="サーバー内のスタミナリストを表示します。",
    )
    async def view(ctx: discord.ApplicationContext):
        """スタミナリストを表示するコマンド"""
        user_id = ctx.author.id
        logger.info(f"Received /view command from user ID: {user_id}")

        try:
            conn = await get_db_connection()
            logger.debug("Database connection established.")

            # スタミナリストを取得
            rows = await conn.fetch(
                """
                SELECT user_id, stamina, user_name, updated_at
                FROM mememori_stamina
                WHERE guild_id = $1
                ORDER BY updated_at DESC
                """,
                ctx.guild.id
            )
            logger.debug(f"{ctx.guild.id} stamina list fetched: {len(rows)} rows")

            # スタミナリストをフォーマット
            embed = discord.Embed(title=f"{ctx.guild.name} のスタミナリスト", color=discord.Color.blue())
            user_count = 0
            total_stamina = 0

            stamina_details = ""
            for row in rows:
                user_id, stamina, user_name, updated_at = row["user_id"], row["stamina"], row["user_name"], row["updated_at"]
                stamina_details += f"{user_name}: {stamina} ({updated_at.strftime('%Y-%m-%d %H:%M:%S')})\n"
                total_stamina += stamina
                user_count += 1

            if user_count > 0:
                average_stamina = total_stamina / user_count
            else:
                average_stamina = 0

            if stamina_details:
                embed.add_field(name="ユーザーごとのスタミナ", value=stamina_details, inline=False)
            else:
                embed.add_field(name="ユーザーごとのスタミナ", value="データがありません。", inline=False)

            embed.add_field(name="合計スタミナ", value=f"{total_stamina}", inline=False)
            embed.add_field(name="平均スタミナ", value=f"{average_stamina:.2f}", inline=False)

            await ctx.respond(embed=embed)
            logger.info(f"Stamina list sent to user ID: {user_id}.")
        except Exception as e:
            logger.error(f"Error fetching stamina list for user ID: {user_id}: {e}")
            await ctx.respond("スタミナリストの取得中にエラーが発生しました。", ephemeral=True)
        finally:
            if conn:
                await close_db_connection(conn)
                logger.debug("Database connection closed.")