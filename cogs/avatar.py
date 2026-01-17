import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author  # Define o autor como padrão, caso nenhum membro seja mencionado
        embed = discord.Embed(
            title=f"Avatar de {member.display_name}",
            description="",
            color=discord.Color.blue()
        )
        embed.set_image(url=member.display_avatar.url)

        # Criar botão para ver o avatar no navegador
        view = View()
        button_avatar = Button(
            label="Ver avatar no navegador",
            url=member.display_avatar.url,  # Abre o link do avatar em uma nova aba
            style=discord.ButtonStyle.link
        )
        # Adiciona o botão ao View
        view.add_item(button_avatar)

        # Adiciona botão para avatar do servidor, se disponível
        if member.guild_avatar:
            button_server_avatar = Button(
                label="Ver avatar do servidor",
                url=member.guild_avatar.url,  # Abre o link do avatar do servidor
                style=discord.ButtonStyle.link
            )
            view.add_item(button_server_avatar)

        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Avatar(bot))