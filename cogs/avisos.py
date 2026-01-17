import discord
from discord.ext import commands
import database # Importando o módulo database

class Warning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = database.db  # Acessando a instância do banco de dados

    async def add_warning(self, user_id, reason):
        """Adiciona um aviso ao banco de dados."""
        await self.db.execute("INSERT INTO warnings (user_id, reason) VALUES (?, ?)", (user_id, reason))

    async def get_warnings(self, user_id):
        """Recupera todos os avisos de um usuário do banco de dados."""
        results = await self.db.fetchall("SELECT reason FROM warnings WHERE user_id = ?", (user_id,))
        return [row[0] for row in results]

    async def remove_warning(self, user_id, warning_number):
        """Remove um aviso específico de um usuário do banco de dados."""
        warnings = await self.get_warnings(user_id)
        if 1 <= warning_number <= len(warnings):
            removed_warning = warnings[warning_number - 1]
            await self.db.execute(
                "DELETE FROM warnings WHERE user_id = ? AND reason = ?", (user_id, removed_warning)
            )
            return removed_warning
        return None


    async def send_dm_warning(self, member, user_id, reason):
        message = (
            f"{member.mention}({user_id})vc foi avisado, por {reason}"
        )
        try:
            await member.send(message)
        except discord.Forbidden:
            print(f"nao foi possivel enviar mensagem para{member}")

    async def log_pun(self, ctx, member, user_id, reason):
        if ctx.guild.id == 1339304980737163397:
            log_channel = discord.utils.get(ctx.guild.text_channels, name="📜┇provas")
        elif ctx.guild.id == 1369780036961308803:
            log_channel = discord.utils.get(ctx.guild.text_channels, name="⤷🗑️﹕registro")
        else:
            log_channel = discord.utils.get(ctx.guild.text_channels, name="🚔┃registro-staff")
        if log_channel:
            await log_channel.send(f"Registro de punição📒\n👤Alvo:{member.mention}\n punição: warn\n reason {reason}")

    @commands.command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        """Adiciona um aviso a um usuário com confirmação."""
        if member == ctx.author:
            await ctx.send("<a:warn:1393656959441567915> Você não pode se avisar!")
            return

        if member.bot:
            await ctx.send("<a:warn:1393656959441567915> Você não pode avisar um bot!")
            return

        user_id = member.id
        confirm_message = await ctx.send(
            f"<a:warn:1393656959441567915> {member.mention} recebeu um aviso pelo motivo: **{reason}**. Confirme clicando no <a:check:1394360081365204993> ou no <a:erro:1393619725472370859> para cancelar."
        )
        sucess_emoji = self.bot.get_emoji(1394360081365204993)
        erro_emoji = self.bot.get_emoji(1393619725472370859)
        await confirm_message.add_reaction(sucess_emoji)
        await confirm_message.add_reaction(erro_emoji)

        def check(reaction, user):
            return (
                user == ctx.author
                and reaction.message.id == confirm_message.id
                and (
                    (getattr(reaction.emoji, "id", None) == 1394360081365204993)
                    or (getattr(reaction.emoji, "id", None) == 1393619725472370859)
                )
            )

        try:
            reaction, reactor = await self.bot.wait_for(
            "reaction_add", timeout=60.0, check=check
            )
            print("Emoji recebido:", repr(reaction.emoji))
            if getattr(reaction.emoji, "id", None) == 1394360081365204993:
                await self.add_warning(user_id, reason)
                await ctx.send(f"<a:check:1394360081365204993> O aviso para {member.mention} foi confirmado.")
                if ctx.guild.id == 1339304980737163397:
                    log_channel = discord.utils.get(ctx.guild.text_channels, name="📜┇provas")
                elif ctx.guild.id == 1369780036961308803:
                    log_channel = discord.utils.get(ctx.guild.text_channels, name="⤷🗑️﹕registro")
                else:
                    log_channel = discord.utils.get(ctx.guild.text_channels, name="🚔┃registro-staff")
                if log_channel:
                    await log_channel.send(f"Registro de punição📒\n👤Alvo:{member.mention}\n punição: warn\n reason {reason}")
                await self.send_dm_warning(member, user_id, reason)
                await confirm_message.delete()
            else:
                await ctx.send(f"<a:erro:1393619725472370859> O aviso para {member.mention} foi cancelado.")
            return
        except Exception:
            await ctx.send("<a:warn:1393656959441567915> Tempo esgotado. O aviso foi cancelado.")

    @commands.command(name="warns")
    @commands.has_permissions(moderate_members=True)
    async def warnings(self, ctx, member: discord.Member):
        """Mostra todos os avisos de um membro."""
        user_id = member.id
        warnings = await self.get_warnings(user_id)

        if warnings:
            warning_list = "\n".join(
                [f"{i + 1}. {reason}" for i, reason in enumerate(warnings)]
            )
            await ctx.send(f"<a:warn:1393656959441567915> Avisos de {member.mention}:\n{warning_list}")
        else:
            await ctx.send(f"<a:check:1394360081365204993> {member.mention} não tem avisos.")

    @commands.command(name="rwarn")
    @commands.has_permissions(moderate_members=True)
    async def clear_warning(self, ctx, member: discord.Member, warning_number: int):
        """Remove um aviso específico de um membro pelo número."""
        user_id = member.id
        removed_warning = await self.remove_warning(user_id, warning_number)

        if removed_warning:
            await ctx.send(
                f"<a:check:1394360081365204993> O aviso número {warning_number} foi removido de {member.mention}: **{removed_warning}**"
            )
        else:
            warnings = await self.get_warnings(user_id)
            if warnings:
                await ctx.send(
                    f"<a:warn:1393656959441567915> Número do aviso inválido. {member.mention} tem apenas {len(warnings)} aviso(s)."
                )
            else:
                await ctx.send(f"<a:warn:1393656959441567915> {member.mention} não tem avisos para remover.")

async def setup(bot):
    await bot.add_cog(Warning(bot))