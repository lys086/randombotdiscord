import discord
from discord.ext import commands
import database  # Importando o módulo database

class Rank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = database.db  # Acessando a instância do banco de dados

    @commands.command(name="rank")
    async def rank(self, ctx):
        """
        Mostra os 10 usuários com mais dinheiro (NOC coins) do banco de dados SQLite.
        """
        try:
            results = await self.db.fetchall("SELECT user_id, balance FROM user_balances ORDER BY balance DESC LIMIT 10")
        except Exception as e:
            await ctx.send(f"<a:erro:1393619725472370859> Erro ao acessar o banco de dados: {e}")
            return

        if not results:
            await ctx.send("<a:erro:1393619725472370859> Não há dados suficientes para exibir o ranking.")
            return

        embed = discord.Embed(
            title=" Ranking de NOC Coins ",
            description="Top 10 usuários com mais dinheiro.",
            color=discord.Color.gold()
        )

        for i, (user_id, balance) in enumerate(results, start=1):
            try:
                member = await self.bot.fetch_user(user_id)
                username = member.name if member else f"ID: {user_id}"
            except Exception:
                username = f"ID: {user_id}"
            embed.add_field(
                name=f"#{i} - {username}",
                value=f"Saldo: {balance} NOC Coins",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    """Configura o cog Rank para o bot."""
    await bot.add_cog(Rank(bot))