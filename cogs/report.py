import discord
from discord.ext import commands
from discord import app_commands
import database
from datetime import timedelta


# IDs dos canais — substitua pelos corretos do seu servidor


REPORT_CHANNEL_ID = {
    1369780036961308803: {
        "channel_id": 1375911256958959626,  # Canal de denúncias para Guild ID 1
    },
    1339304980737163397: {
        "channel_id": 1375154883677655121,  # Canal de denúncias para Guild ID 2
    },
    1391535576561356871: {
        "channel_id": 1392302225845391531,  # Canal de denúncias para Guild ID 3
    }
}

LOG_CHANNEL_ID = {
    1369780036961308803: {
        "channel_id": 1375917942943911987,  # Canal de denúncias para Guild ID 1
    },
    1339304980737163397: {
        "channel_id": 1372187456882999447,  # Canal de denúncias para Guild ID 2
    },
    1391535576561356871: {
        "channel_id": 1392302225845391531,  # Canal de denúncias para Guild ID 3
    }
}    # Canal de registro das punições

database_ac = database.db # Acessando a instância do banco de dados
class ReportView(discord.ui.View):



    def __init__(self, reported_user, reason, message_link, author):

        super().__init__(timeout=None)

        self.reported_user = reported_user

        self.reason = reason

        self.message_link = message_link

        self.author = author

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.success)

    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message("Apenas administradores podem usar esse botão.", ephemeral=True)

            return

        await interaction.response.edit_message(content="Escolha a ação a ser tomada:", view=ActionView(self.reported_user, self.reason, self.reported_user.id))

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.danger)

    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message("Apenas administradores podem usar esse botão.", ephemeral=True)

            return

        await interaction.message.edit(content="A denúncia foi cancelada.", embed=None, view=None)

class ActionView(discord.ui.View):

    async def add_warning(self, user_id, reason):
        """Adiciona um aviso ao banco de dados."""
        await database_ac.execute("INSERT INTO warnings (user_id, reason) VALUES (?, ?)", (user_id, reason))

    def __init__(self, user, reason, user_id):

        super().__init__(timeout=None)

        self.user = user

        self.reason = reason

        self.user_id = user_id

    @discord.ui.button(label="Warn", style=discord.ButtonStyle.primary)

    async def warn(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(f"{self.user.mention} recebeu um aviso. Motivo: `{self.reason}`", ephemeral=False)
        await self.add_warning(self.user_id, self.reason)

        try:
            await self.user.send(f"Você foi **avisado** por `{self.reason}` da Nexus Garden.")
        except:
            pass
        if interaction.guild.id not in LOG_CHANNEL_ID:
            return
        log = interaction.guild.get_channel(LOG_CHANNEL_ID[interaction.guild.id]["channel_id"])

        if log:

            await log.send(f"**[WARN]** {self.user.mention} foi avisado. Motivo: `{self.reason}` por {interaction.user.mention}")

    @discord.ui.button(label="Mute", style=discord.ButtonStyle.secondary)

    async def mute(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not interaction.guild.me.guild_permissions.moderate_members:

            await interaction.response.send_message("Não tenho permissão para silenciar membros.", ephemeral=True)

            return

        modal = MuteModal(self.user, self.reason, interaction.user)

        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Banir", style=discord.ButtonStyle.danger)
    async def ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # 🆕 Envia DM antes de banir
            try:
                await self.user.send(f"Você foi **banido** por `{self.reason}` da Nexus Garden.")
            except:
                pass

            await self.user.ban(reason=self.reason)
            await interaction.response.send_message(f"{self.user.mention} foi banido. Motivo: `{self.reason}`",
                                                    ephemeral=False)
            if interaction.guild.id not in LOG_CHANNEL_ID:
                return
            # 🆕 Envia log de banimento
            log = interaction.guild.get_channel(LOG_CHANNEL_ID[interaction.guild.id]["channel_id"])
            if log:
                await log.send(
                    f"**[BAN]** {self.user.mention} foi banido. Motivo: `{self.reason}` por {interaction.user.mention}")
        except Exception as e:
            await interaction.response.send_message(f"Não consegui banir esse usuário. Erro: {e}", ephemeral=True)

class MuteModal(discord.ui.Modal, title="Tempo de Mute"):

    duration = discord.ui.TextInput(label="Duração (em minutos)", placeholder="Ex: 10", required=True)

    def __init__(self, user, reason, moderator):

        super().__init__()

        self.user = user

        self.reason = reason

        self.moderator = moderator

    async def on_submit(self, interaction: discord.Interaction):
        try:
            minutes = int(self.duration.value)
            until = discord.utils.utcnow() + timedelta(minutes=minutes)

            # 🆕 Envia DM antes de aplicar o mute
            try:
                await self.user.send(f"Você foi **mutado por {minutes} minutos** por `{self.reason}` da {interaction.guild.name}.")
            except:
                pass

            await self.user.timeout(until, reason=self.reason)

            await interaction.response.send_message(
                f"{self.user.mention} foi mutado por {minutes} minutos. Motivo: `{self.reason}`", ephemeral=False)
            if interaction.guild.id not in LOG_CHANNEL_ID:
                return
            log = interaction.guild.get_channel(LOG_CHANNEL_ID[interaction.guild.id]["channel_id"])
            if log:
                await log.send(
                    f"**[MUTE]** {self.user.mention} foi mutado por `{minutes}` minutos. Motivo: `{self.reason}` por {self.moderator.mention}")

        except Exception as e:
            await interaction.response.send_message(f"Erro ao aplicar mute: {e}", ephemeral=True)

class Report(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    @app_commands.command(name="report", description="Reporta um usuário.")

    @app_commands.describe(

        member="Usuário que você quer reportar",

        reason="Motivo da denúncia",

        message_link="Link da mensagem (opcional)"

    )

    async def report(self, interaction: discord.Interaction, member: discord.Member, reason: str, message_link: str = "Nenhum link fornecido"):

        embed = discord.Embed(title="Novo Report", color=discord.Color.orange())

        embed.add_field(name="Usuário", value=member.mention, inline=False)

        embed.add_field(name="Mensagem", value=message_link, inline=False)

        embed.add_field(name="Motivo", value=reason, inline=False)

        embed.set_footer(text=f"Reportado por {interaction.user}", icon_url=interaction.user.display_avatar.url)

        view = ReportView(reported_user=member, reason=reason, message_link=message_link, author=interaction.user)

        if interaction.guild.id not in REPORT_CHANNEL_ID:
            return
        canal = self.bot.get_channel(REPORT_CHANNEL_ID[interaction.guild.id]["channel_id"])

        if canal:

            await canal.send(embed=embed, view=view)

            await interaction.response.send_message("Sua denúncia foi enviada para a equipe.", ephemeral=True)

        else:

            await interaction.response.send_message("Canal de denúncias não encontrado.", ephemeral=True)

async def setup(bot):

    await bot.add_cog(Report(bot))