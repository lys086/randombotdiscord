import discord
from discord.ext import commands
from discord.ui import View, Button

# Lista de cores separadas
CORES_NORMAIS = [
    "Vermelho", "Vermelho escuro", "Laranja", "Laranja escuro",
    "Amarelo", "Amarelo escuro", "Verde", "Verde escuro",
    "Ciano", "Ciano escuro", "Azul", "Azul escuro",
    "Violeta", "Roxo", "Roxo escuro", "Magenta", "Magenta escuro",
    "Branco", "Cinza", "Preto"
]

CORES_CLARAS = [
    "Magenta claro", "Roxo claro", "Azul claro", "Ciano claro",
    "Verde claro", "Amarelo claro", "Laranja claro", "Vermelho claro"
]

class ColorRoleButton(Button):
    def __init__(self, bot, role_name):
        super().__init__(label=role_name, style=discord.ButtonStyle.primary, custom_id=f"color_{role_name}")
        self.bot = bot
        self.role_name = role_name

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        role = discord.utils.get(guild.roles, name=self.role_name)

        if not role:
            await interaction.response.send_message("<a:erro:1393619725472370859> Erro: Cargo não encontrado.", ephemeral=True)
            return

        # Remove outras cores antes de aplicar a nova
        all_roles = [discord.utils.get(guild.roles, name=c) for c in CORES_NORMAIS + CORES_CLARAS]
        roles_to_remove = [r for r in all_roles if r in member.roles]

        await member.remove_roles(*roles_to_remove)
        await member.add_roles(role)

        await interaction.response.send_message(
            f"<a:check:1394360081365204993> Você agora tem a cor **{self.role_name}**.", ephemeral=True
        )

class ColorRoleView(View):
    def __init__(self, bot, colors):
        super().__init__(timeout=None)
        for cor in colors:
            self.add_item(ColorRoleButton(bot, cor))

class ColorRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cargoscor")
    @commands.has_permissions(administrator=True)
    async def send_color_roles(self, ctx):
        """Cores normais"""
        view = ColorRoleView(self.bot, CORES_NORMAIS)
        embed = discord.Embed(
            title="Escolha sua Cor!",
            description="Clique em um botão para selecionar ou trocar sua cor.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=view)
        self.bot.add_view(view)

    @commands.command(name="coresvip")
    @commands.has_permissions(administrator=True)
    async def send_color_roles_vip(self, ctx):
        """Cores VIP (claras)"""
        view = ColorRoleView(self.bot, CORES_CLARAS)
        embed = discord.Embed(
            title="Escolha sua Cor VIP!",
            description="Clique em um botão para selecionar ou trocar sua cor clara.",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed, view=view)
        self.bot.add_view(view)

async def setup(bot):
    await bot.add_cog(ColorRoles(bot))
    # Registra as views persistentes (opcional)
    bot.add_view(ColorRoleView(bot, CORES_NORMAIS))
    bot.add_view(ColorRoleView(bot, CORES_CLARAS))
