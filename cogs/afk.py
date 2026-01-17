from discord.ext import commands
from discord import app_commands
import discord

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {}  # Armazena usuários AFK {user_id: afk_message}

    @app_commands.command(name="afk", description="Defina seu status como AFK")
    async def afk(self, interaction: discord.Interaction, reason: str = "Estou AFK no momento!"):
        """Define o status do usuário como AFK com um motivo opcional."""
        user_id = interaction.user.id
        self.afk_users[user_id] = reason
        await interaction.response.send_message(f"{interaction.user.mention} agora está AFK. Motivo: {reason}", ephemeral=True)

    async def check_afk_status(self, message: discord.Message):
        """Verifica se o autor da mensagem está AFK e remove o status AFK."""
        if message.author.id in self.afk_users:
            afk_reason = self.afk_users.pop(message.author.id)
            await message.channel.send(f"Bem-vindo de volta, {message.author.mention}! Você não está mais AFK.\nMotivo anterior: {afk_reason}")

        # Notifica usuários mencionados que estão AFK
        for user in message.mentions:
            if user.id in self.afk_users:
                await message.channel.send(f"{user} está AFK. Motivo: {self.afk_users[user.id]}")

async def setup(bot):
    await bot.add_cog(AFK(bot))