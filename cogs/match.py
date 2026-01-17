import discord
from discord.ext import commands
import database  # Importando o módulo database
import random

class Match(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = database.db  # Acessando a instância do banco de dados

    async def get_casamento(self, user1_id, user2_id):
        """Verifica se um casamento existe no banco de dados."""
        result1 = await self.db.fetchone(
            "SELECT * FROM casamentos WHERE user1_id = ? AND user2_id = ?",
            (user1_id, user2_id),
        )
        result2 = await self.db.fetchone(
            "SELECT * FROM casamentos WHERE user1_id = ? AND user2_id = ?",
            (user2_id, user1_id),
        )
        return result1 or result2

    async def add_casamento(self, user1_id, user2_id):
        """Adiciona um casamento ao banco de dados."""
        await self.db.execute(
            "INSERT INTO casamentos (user1_id, user2_id) VALUES (?, ?)",
            (user1_id, user2_id),
        )

    async def remove_casamento(self, user1_id, user2_id):
        """Remove um casamento do banco de dados."""
        await self.db.execute(
            "DELETE FROM casamentos WHERE user1_id = ? AND user2_id = ?",
            (user1_id, user2_id),
        )
        await self.db.execute(
            "DELETE FROM casamentos WHERE user1_id = ? AND user2_id = ?",
            (user2_id, user1_id),
        )

    @commands.command(name="casar")
    async def casar(self, ctx, user: discord.Member):
        """Comando para casar com outro usuário."""
        if user == ctx.author:
            await ctx.send(" Você não pode se casar consigo mesmo!")
            return

        casamento = await self.get_casamento(ctx.author.id, user.id)
        if casamento:
            await ctx.send(
                f" {ctx.author.mention}, você já está casado com {user.mention}!"
            )
            return

        msg = await ctx.send(
            f" {user.mention}, {ctx.author.mention} quer se casar com você! Clique no emoji  para aceitar."
        )
        await msg.add_reaction("💍")

        def check(reaction, reactor):
            return reactor == user and str(reaction.emoji) == "💍" and reaction.message.id == msg.id

        try:
            await self.bot.wait_for("reaction_add", timeout=None, check=check)
            await self.add_casamento(ctx.author.id, user.id)
            await ctx.send(
                f" Parabéns {ctx.author.mention} e {user.mention}, vocês estão oficialmente casados!"
            )
        except Exception as e:
            await ctx.send(f"❌ O casamento foi cancelado. Erro: {e}")

    @commands.command(name="match")
    async def match(self, ctx, user: discord.Member, user_matched: discord.member):
        """Comando para verificar a compatibilidade."""
        casamento = await self.get_casamento(ctx.author.id, user.id)

        if casamento:
            await ctx.send(
                f" {ctx.user} e {user_matched} têm 100% de compatibilidade!"
            )
        else:
            compatibilidade = random.randint(0, 100)
            await ctx.send(
                f" {ctx.user} e {user_matched} não estão casados. Compatibilidade: {compatibilidade}%."
            )

    @commands.command(name="divorciar")
    async def divorciar(self, ctx, user: discord.Member):
        """Comando para se divorciar de outro usuário."""
        casamento = await self.get_casamento(ctx.author.id, user.id)

        if casamento:
            await self.remove_casamento(ctx.author.id, user.id)
            await ctx.send(
                f" {ctx.author.mention} e {user.mention} se divorciaram com sucesso."
            )
        else:
            await ctx.send(
                f"<a:warn:1393656959441567915> {ctx.author.mention}, você não está casado com {user.mention}."
            )

async def setup(bot):
    await bot.add_cog(Match(bot))