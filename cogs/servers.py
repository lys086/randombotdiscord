import discord
from discord.ext import commands
from discord import ui


class ServerListView(ui.View):
    def __init__(self, bot, owner_id):
        super().__init__(timeout=60)
        self.bot = bot
        self.owner_id = owner_id

        # Criando botões para cada servidor
        for guild in bot.guilds:
            self.add_item(LeaveServerButton(guild.id, guild.name))


class LeaveServerButton(ui.Button):
    def __init__(self, guild_id, guild_name):
        super().__init__(label=guild_name, style=discord.ButtonStyle.danger)
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.owner_id:
            await interaction.response.send_message("<a:erro:1393619725472370859> Você não tem permissão para usar esse botão!", ephemeral=True)
            return

        guild = self.view.bot.get_guild(self.guild_id)
        if guild:
            await guild.leave()
            await interaction.response.send_message(f"<a:check:1394360081365204993> O bot saiu do servidor **{guild.name}**.", ephemeral=True)
        else:
            await interaction.response.send_message("<a:erro:1393619725472370859> O bot já saiu desse servidor.", ephemeral=True)


class ServerManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = 1257376889769562147  # Substitua pelo seu ID

    @commands.command(name="servers")
    async def list_servers(self, ctx):
        """Lista os servidores onde o bot está e permite sair deles."""
        if ctx.author.id != self.owner_id:
            await ctx.send("<a:erro:1393619725472370859> Você não tem permissão para usar esse comando.")
            return

        if not self.bot.guilds:
            await ctx.send("📜 O bot não está em nenhum servidor além deste.")
            return

        await ctx.send("🔹 Lista de servidores:", view=ServerListView(self.bot, self.owner_id))


async def setup(bot):
    await bot.add_cog(ServerManager(bot))