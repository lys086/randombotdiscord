import discord
from discord.ext import commands
from datetime import timedelta

class Unmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        """
        Remove o timeout de um usuário.
        - member: o membro que será desmutado.
        """
        # Verifica se o usuário está em timeout
        if member.timed_out_until is None:
            await ctx.send(f"<a:erro:1393619725472370859> {member.mention} não está em timeout.")
            return

        try:
            # Remove o timeout do membro
            await member.edit(timed_out_until=None)
            await ctx.send(f"<a:check:1394360081365204993> {member.mention} foi desmutado com sucesso!")
        except discord.Forbidden:
            await ctx.send("<a:erro:1393619725472370859> Não tenho permissões suficientes para desmutar este membro.")
        except Exception as e:
            await ctx.send(f"<a:erro:1393619725472370859> Ocorreu um erro ao tentar desmutar o membro: {e}")

async def setup(bot):
    await bot.add_cog(Unmute(bot))
