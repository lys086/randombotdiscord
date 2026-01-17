import discord
from discord.ext import commands

class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.User, *, reason: str = "Nenhuma razão fornecida"):
        """
        Desbane um usuário do servidor.
        - member: o usuário que será desbanido (deve ser fornecido o ID ou tag).
        - reason: motivo do desbanimento.
        """
        try:
            # Desbane o usuário pelo ID
            await ctx.guild.unban(member, reason=reason)
            await ctx.send(f"<a:check:1394360081365204993> {member.mention} foi desbanido do servidor. Motivo: {reason}")
        except discord.Forbidden:
            await ctx.send("<a:erro:1393619725472370859> Não tenho permissões suficientes para desbanir este membro.")
        except Exception as e:
            await ctx.send(f"<a:erro:1393619725472370859> Ocorreu um erro ao tentar desbanir o membro: {e}")

async def setup(bot):
    await bot.add_cog(Unban(bot))
