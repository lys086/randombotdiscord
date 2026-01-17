import discord
from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Lista de nomes de cargos permitidos a usar o comando
        self.allowed_roles = ["Guarda, Guardinha"]  # Substitua pelos nomes dos cargos

    @commands.command()
    async def say(self, ctx, *, mensagem: str):
        """
        Comando que faz o bot repetir uma mensagem.
        Apenas administradores ou membros com cargos permitidos podem usar este comando.
        """
        # Verificar se o autor é administrador
        if ctx.author.guild_permissions.administrator:
            has_permission = True
        else:
            # Verificar se o autor tem algum dos cargos permitidos
            has_permission = any(role.name in self.allowed_roles for role in ctx.author.roles)

        if not has_permission:
            await ctx.send(f"<a:warn:1393656959441567915> {ctx.author.mention}, você não tem permissão para usar este comando.")
            return

        # Deletar a mensagem original para "limpar" o chat
        await ctx.message.delete()

        # Enviar a mensagem fornecida pelo usuário
        try:
            await ctx.send(mensagem)
            await ctx.send(f"<a:check:1394360081365204993> Mensagem enviada com sucesso!")
        except:
            await ctx.send(f"<a:erro:1393619725472370859> Não foi possível enviar a mensagem.")

async def setup(bot):
    await bot.add_cog(Say(bot))
