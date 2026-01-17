import discord
from discord.ext import commands
from datetime import timedelta
import asyncio
import re

class BanView(discord.ui.View):
    def __init__ (self, bot, member, reason, ban_msg, ban_ctx):
        super().__init__(timeout=None)
        self.bot = bot
        self.member = member
        self.reason = reason
        self.punishment = "ban"
        self.ban_msg = ban_msg
        self.ban_ctx = ban_ctx

    @discord.ui.button(
        label="Confirmar Banimento!",
        style=discord.ButtonStyle.red,
        emoji=discord.PartialEmoji(animated=True, name="check", id=1394360081365204993)
    )
    async def ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False)
        dm_tempo_limite = 30
        if interaction.user.id != self.ban_ctx.author.id:
            await interaction.response.send_message("<a:erro:1393619725472370859> **Você não tem permissão para banir este usuário.**", ephemeral=True)
            return
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("<a:erro:1393619725472370859> **Você não tem permissão para banir membros.**", ephemeral=True)
            return
        # Função para enviar DM
        async def enviar_dm():
            await self.member.send(
                f"**Aviso da Staff**\n\n"
                f"Você foi banido da {interaction.guild.name} por {self.reason}.\n\n"
                f"A decisão foi tomada com base nas regras da comunidade. Caso tenha dúvidas, entre em contato com a equipe de moderação.\n\n"
                f"Atenciosamente,\nAdministração"
            )

        try:
            # Tenta enviar a DM com timeout
            await asyncio.wait_for(enviar_dm(), timeout=dm_tempo_limite)
            dm_status = "<a:check:1394360081365204993> DM enviada com sucesso."
        except asyncio.TimeoutError:
            dm_status = "⏰ Tempo limite excedido ao tentar enviar a DM."
            await interaction.followup.send(dm_status, ephemeral=False)
        except discord.Forbidden:
            dm_status = "<a:erro:1393619725472370859> Não foi possível enviar a DM (DM fechada)."
            await interaction.followup.send(dm_status, ephemeral=False)
        finally:
            # Bane o usuário independentemente do status da DM
            await self.member.ban(reason=self.reason)
            banned_embed = discord.Embed(
                title="<a:check:1394360081365204993> Banimento Confirmado",
                description=f"{self.member.mention} foi banido por {self.reason}.",
                color=discord.Color.green()
            )
            await self.ban_msg.edit(embed=banned_embed, view=None)

            # Envia o log
        if interaction.guild.id == 1339304980737163397:
            log_channel = discord.utils.get(interaction.guild.text_channels, name="📜┇provas")
        elif interaction.guild.id == 1369780036961308803:
            log_channel = discord.utils.get(interaction.guild.text_channels, name="⤷🗑️﹕registro")
        else:
            log_channel = discord.utils.get(interaction.guild.text_channels, name="🚔┃registro-staff")

        if log_channel:
            embed = discord.Embed(title="⚖️ Registro de punição ⚖️", color=discord.Color.red())
            embed.add_field(name="Usuário", value=f"{self.member} ({self.member.id})", inline=False)
            embed.add_field(name="Motivo", value=self.reason, inline=False)
            embed.add_field(name="Punição", value="Ban", inline=False)
            embed.add_field(name="Responsável", value=f"{interaction.user} ({interaction.user.id})", inline=False)
            embed.add_field(name="Status da DM", value=dm_status, inline=False)
            embed.add_field(name="Prova(s)", value="(Pergunte ao moderador responsável)", inline=False)
            await log_channel.send(embed=embed)
            await interaction.followup.send(f"<a:check:1394360081365204993> **{self.member.mention} foi banido do servidor.** {dm_status}")
        else:
            await interaction.followup.send(f"<a:warn:1393656959441567915> **Canal de logs não encontrado. Certifique-se de que o canal existe.**")

    @discord.ui.button(
        label="Cancelar Banimento",
        style=discord.ButtonStyle.blurple,
        emoji=discord.PartialEmoji(animated=True, name="erro", id=1393619725472370859)
    )
    async def cancel_ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ban_ctx.author.id:
            await interaction.response.send_message("<a:erro:1393619725472370859> **Você não tem permissão para banir este usuário.**", ephemeral=True)
            return
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("<a:erro:1393619725472370859> **Você não tem permissão para banir membros.**", ephemeral=True)
            return
        banned_embed = discord.Embed(
                title="<a:erro:1393619725472370859> Banimento Cancelado",
                description=f"O banimento de {self.member.mention} foi cancelado.",
                color=discord.Color.red()
            )
        await self.ban_msg.edit(embed=banned_embed, view=None)
        return

class MuteView(discord.ui.View):
    def __init__(self, bot, member, reason, mute_ctx, mute_msg, time):
        super().__init__(timeout=None)
        self.bot = bot
        self.member = member
        self.reason = reason
        self.mute_ctx = mute_ctx
        self.mute_msg = mute_msg
        self.time = time

    @discord.ui.button(
        label="Confirmar Castigo",
        style=discord.ButtonStyle.blurple,
        emoji=discord.PartialEmoji(animated=True, name="check", id=1394360081365204993)
    )
    async def mute(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False)
        dm_tempo_limite = 30
        async def enviar_dm():
            await self.member.send(
                f"**Aviso da Staff**\n\n"
                f"Você foi silenciado na {interaction.guild.name} por {self.reason}.\n\n"
                f"A decisão foi tomada com base nas regras da comunidade. Caso tenha dúvidas, entre em contato com a equipe de moderação.\n\n"
                f"Atenciosamente,\nAdministração"
            )
        if interaction.user.id != self.mute_ctx.author.id:
            await interaction.followup.send("<a:erro:1393619725472370859> **Você não tem permissão para silenciar este usuário.**", ephemeral=True)
            return
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.followup.send("<a:erro:1393619725472370859> **Você não tem permissão para silenciar membros.**", ephemeral=True)
            return

        # Envia a DM ao usuário
        try:
            await asyncio.wait_for(enviar_dm(), timeout=dm_tempo_limite)
            dm_status = "<a:check:1394360081365204993> DM enviada com sucesso."
        except discord.Forbidden:
            await interaction.followup.send("<a:erro:1393619725472370859> **Não foi possível enviar a DM (DM fechada).**", ephemeral=False)
            dm_status = "<a:erro:1393619725472370859> Não foi possível enviar a DM (DM fechada)."
            return
        except asyncio.TimeoutError:
            await interaction.followup.send("<a:erro:1393619725472370859> Tempo limite excedido ao tentar enviar a DM.", ephemeral=False)
            dm_status = "<a:erro:1393619725472370859> Tempo limite excedido ao tentar enviar a DM."
            return
        finally:
            # Silencia o usuário
            await self.member.timeout(discord.utils.utcnow() + timedelta(seconds=self.time), reason=self.reason)

            muted_embed = discord.Embed(
                title="<a:check:1394360081365204993> Silenciamento Confirmado",
                description=f"{self.member.mention} foi silenciado por {self.reason} durante {self.time // 60} minutos.",
                color=discord.Color.green()
            )

            await self.mute_msg.edit(embed=muted_embed, view=None)

        # Envia o log
        if interaction.guild.id == 1339304980737163397:
            log_channel = discord.utils.get(interaction.guild.text_channels, name="📜┇provas")
        elif interaction.guild.id == 1369780036961308803:
            log_channel = discord.utils.get(interaction.guild.text_channels, name="⤷🗑️﹕registro")
        else:
            log_channel = discord.utils.get(interaction.guild.text_channels, name="🚔┃registro-staff")
        if log_channel:
            embed = discord.Embed(title="⚖️ Registro de punição ⚖️", color=discord.Color.red())
            embed.add_field(name="Usuário", value=f"{self.member} ({self.member.id})", inline=False)
            embed.add_field(name="Motivo", value=self.reason, inline=False)
            embed.add_field(name="Punição", value="Mute", inline=False)
            embed.add_field(name="Responsável", value=f"{interaction.user} ({interaction.user.id})", inline=False)
            embed.add_field(name="Prova(s)", value="(Pergunte ao moderador responsável)", inline=False)
            await log_channel.send(embed=embed)
            await interaction.followup.send(f"<a:check:1394360081365204993> **{self.member.mention} foi silenciado.**")
        else:
            await interaction.followup.send("<a:warn:1393656959441567915> **Canal de logs não encontrado. Certifique-se de que o canal 🚔┃registro-staff existe.**")

    @discord.ui.button(
        label="Cancelar Silenciamento",
        style=discord.ButtonStyle.red,
        emoji=discord.PartialEmoji(animated=True, name="erro", id=1393619725472370859)
    )
    async def cancel_mute(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.mute_ctx.author.id:
            await interaction.response.send_message("<a:erro:1393619725472370859> **Você não tem permissão para silenciar este usuário.**", ephemeral=True)
            return
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("<a:erro:1393619725472370859> **Você não tem permissão para silenciar membros.**", ephemeral=True)
            return
        confirm_embed = discord.Embed(
            title="<a:erro:1393619725472370859> Silenciamento Cancelado",
            description=f"O silenciamento de {self.member.mention} foi cancelado.",
            color=discord.Color.red()
        )
        await self.mute_msg.edit(embed=confirm_embed, view=None)
        return

class AutoPune(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando de ban
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason=None):
        try:
            BanView.ban_ctx = ctx
            # Obtenção do membro
            if not member:
                if reason and reason.isdigit():
                    await ctx.send(
                        f"<a:erro:1393619725472370859> **Você colocou o motivo no lugar do usuário. Certifique-se de usar o comando corretamente.**\n"
                        f"Uso correto: N$ban @usuário motivo"
                    )
                    return
                ask_member_msg = await ctx.send("<a:warn:1393656959441567915> Usuário não informado. Por favor, digite o usuário:")
                def check_ban_user_message(msg):
                    return msg.author == ctx.author and msg.channel == ctx.channel
                try:
                    member_msg = await self.bot.wait_for("message", timeout=30.0, check=check_ban_user_message)
                    member_input = member_msg.content.strip()
                    if member_msg.mentions:
                        member = member_msg.mentions[0]
                    else:
                        try:
                            member_id = int(member_input)
                            member = ctx.guild.get_member(member_id)
                            if member is None:
                                member = await ctx.guild.fetch_member(member_id)
                        except Exception:
                            member = None
                    if not member:
                        await ctx.send("<a:erro:1393619725472370859> **Usuário não encontrado. Certifique-se de mencionar o usuário ou fornecer um ID válido.**")
                        return
                    await ask_member_msg.delete()
                except asyncio.TimeoutError:
                    await ctx.send("⏰ **Tempo esgotado. Ação de ban cancelada.**")
                    await ask_member_msg.delete()
                    return
                except Exception as e:
                    await ctx.send(f"<a:erro:1393619725472370859> **Erro desconhecido ao obter o usuário: {e}**")
                    return
            # Checa se o membro é banível
            if not member:
                await ctx.send("<a:erro:1393619725472370859> **Usuário não informado ou não encontrado.**")
                return
            if member == ctx.author:
                await ctx.send("<a:erro:1393619725472370859> **Você não pode se banir!**")
                return
            if member == ctx.guild.owner:
                await ctx.send("<a:erro:1393619725472370859> **Você não pode banir o dono do servidor!**")
                return
            if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                await ctx.send("<a:erro:1393619725472370859> **Você não pode banir alguém com cargo igual ou superior ao seu.**")
                return
            # Checagem de hierarquia do bot
            if ctx.guild.me.top_role <= member.top_role:
                await ctx.send("<a:erro:1393619725472370859> **Não tenho permissão para banir este usuário (cargo igual ou superior ao meu).**")
                return
            # Motivo
            if not reason:
                def check_message(msg):
                    return msg.author == ctx.author and msg.channel == ctx.channel
                ask_reason_msg = await ctx.send("<a:warn:1393656959441567915> Motivo para a punição não informado. Por favor, digite o motivo:")
                try:
                    reason_msg = await self.bot.wait_for("message", timeout=30.0, check=check_message)
                    reason = reason_msg.content
                    await ask_reason_msg.delete()
                except asyncio.TimeoutError:
                    await ctx.send("⏰ **Tempo esgotado. Ação de ban cancelada.**")
                    await ask_reason_msg.delete()
                    return
                except Exception as e:
                    await ctx.send(f"<a:erro:1393619725472370859> **Erro desconhecido ao obter o motivo: {e}**")
                    return
            BanView.member = member
            BanView.reason = reason
            BanView.punishment = "ban"
            confirm_embed = discord.Embed(
                title="<a:warn:1393656959441567915> Confirmação de punição",
                description=f"Você está prestes a banir {member.mention} por {reason}. Confirme clicando no botão abaixo.",
                color=discord.Color.red()
            )
            ban_msg_variable = await ctx.send("<a:loading:1393618509400899666> carregando...")
            view = BanView(self.bot, member, reason,  ban_msg_variable, ctx)
            await ban_msg_variable.edit(content="",embed=confirm_embed, view=view)
        except Exception as e:
            await ctx.send(f"<a:erro:1393619725472370859> **Erro inesperado: {e}**")

    # Comando de mute
    @commands.command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member = None, *, args=None):
        try:
            MuteView.mute_ctx = ctx
            
            # Processa os argumentos se fornecidos
            duration = None
            reason = None
            
            if args:
                # Divide os argumentos em partes
                args_parts = args.split()
                
                # Tenta encontrar duração e motivo nos argumentos
                if len(args_parts) >= 2:
                    # Verifica se a primeira parte é um número
                    if args_parts[0].isdigit():
                        # Se é só número, precisa da segunda parte para determinar unidade
                        if len(args_parts) >= 3:
                            # Formato: "30 minutos teste" -> duração = "30 minutos", motivo = "teste"
                            if any(word in args_parts[1].lower() for word in ["minuto", "minutos", "hora", "horas", "m", "h"]):
                                duration = f"{args_parts[0]} {args_parts[1]}"
                                reason = ' '.join(args_parts[2:]) if len(args_parts) > 2 else None
                            else:
                                # Se a segunda parte não é unidade, tudo é motivo
                                reason = args
                        else:
                            # Apenas duas partes: "30 minutos" -> duração = "30 minutos"
                            if any(word in args_parts[1].lower() for word in ["minuto", "minutos", "hora", "horas", "m", "h"]):
                                duration = f"{args_parts[0]} {args_parts[1]}"
                            else:
                                # Se não tem unidade, tudo é motivo
                                reason = args
                    else:
                        # Se não é número, tudo é motivo
                        reason = args
                elif len(args_parts) == 1:
                    # Apenas uma parte - pode ser duração ou motivo
                    if any(char.isdigit() for char in args_parts[0]):
                        duration = args_parts[0]
                    else:
                        reason = args_parts[0]
            
            # Obtenção do membro
            if not member:
                if args and args.isdigit():
                    await ctx.send(
                        f"<a:erro:1393619725472370859> **Você colocou o motivo no lugar do usuário. Certifique-se de usar o comando corretamente.**\n"
                        f"Uso correto: N$mute @usuário duração motivo"
                    )
                    return
                ask_member_msg = await ctx.send("<a:warn:1393656959441567915> Usuário não informado. Por favor, digite o usuário:")
                def check_mute_user_message(msg):
                    return msg.author == ctx.author and msg.channel == ctx.channel
                try:
                    member_msg = await self.bot.wait_for("message", timeout=30.0, check=check_mute_user_message)
                    member_input = member_msg.content.strip()
                    if member_msg.mentions:
                        member = member_msg.mentions[0]
                    else:
                        try:
                            member_id = int(member_input)
                            member = ctx.guild.get_member(member_id)
                            if member is None:
                                member = await ctx.guild.fetch_member(member_id)
                        except Exception as e:
                            await ctx.send(f"<a:erro:1393619725472370859> **Erro desconhecido ao obter o usuário: {e}**")
                            return
                        except discord.Forbidden:
                            await ctx.send("<a:erro:1393619725472370859> **Não foi possível obter o usuário. Verifique se o usuário existe e se você tem permissão para ver os membros.**")
                            return
                    await ask_member_msg.delete()
                except asyncio.TimeoutError:
                    await ctx.send("⏰ **Tempo esgotado. Ação de mute cancelada.**")
                    await ask_member_msg.delete()
                    return
            # Checa se o membro é mutável
            if not member:
                await ctx.send("<a:erro:1393619725472370859> **Usuário não informado ou não encontrado.**")
                return
            if member == ctx.author:
                await ctx.send("<a:erro:1393619725472370859> **Você não pode se mutar!**")
                return
            if member == ctx.guild.owner:
                await ctx.send("<a:erro:1393619725472370859> **Você não pode mutar o dono do servidor!**")
                return
            if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                await ctx.send("<a:erro:1393619725472370859> **Você não pode mutar alguém com cargo igual ou superior ao seu.**")
                return
            # Motivo
            if reason is None:
                msg1 = await ctx.send(f"{ctx.author.mention}, qual o motivo do mute para {member.mention}?")
                def check_message(msg):
                    return msg.author == ctx.author and msg.channel == ctx.channel
                try:
                    reason_msg = await self.bot.wait_for("message", timeout=30.0, check=check_message)
                    reason = reason_msg.content
                    await msg1.delete()
                except asyncio.TimeoutError:
                    await ctx.send("⏰ **Tempo esgotado. Ação de mute cancelada.**")
                    await msg1.delete()
                    return
                except Exception as e:
                    await ctx.send(f"<a:erro:1393619725472370859> **Erro desconhecido ao obter o motivo: {e}**")
                    return
            # Duração
            if duration is None:
                msg2 = await ctx.send(f"{ctx.author.mention}, por quanto tempo deseja silenciar {member.mention}? (Exemplo: 10m, 1h)")
                def check_message(msg):
                    return msg.author == ctx.author and msg.channel == ctx.channel
                try:
                    duration_msg = await self.bot.wait_for("message", timeout=30.0, check=check_message)
                    duration_input = duration_msg.content.strip().lower()
                    
                    # Extrai números da entrada
                    numbers = re.findall(r'\d+', duration_input)
                    
                    if not numbers:
                        await ctx.send("<a:erro:1393619725472370859> **Formato de tempo inválido!** Use h para horas ou m para minutos (ex: 10m, 1h).")
                        return
                    
                    time_value = int(numbers[0])
                    
                    # Verifica se contém palavras-chave para determinar a unidade
                    if "minuto" in duration_input or "minutos" in duration_input or "m" in duration_input:
                        duration = f"{time_value}m"
                    elif "hora" in duration_input or "horas" in duration_input or "h" in duration_input:
                        duration = f"{time_value}h"
                    else:
                        # Se não encontrou palavras-chave, verifica se é apenas um número seguido de m ou h
                        if duration_input.endswith('m') or duration_input.endswith('h'):
                            duration = duration_input
                        else:
                            await ctx.send("<a:erro:1393619725472370859> **Formato de tempo inválido!** Use h para horas ou m para minutos (ex: 10m, 1h).")
                            return
                    
                    await msg2.delete()
                except asyncio.TimeoutError:
                    await ctx.send("⏰ **Tempo esgotado. Ação de mute cancelada.**")
                    await msg2.delete()
                    return
                except Exception as e:
                    await ctx.send(f"<a:erro:1393619725472370859> **Erro desconhecido ao obter a duração: {e}**")
                    return
            # Verifica e converte a duração
            time_map = {"h": 3600, "m": 60}
            try:
                # Se a duração já foi processada (formato 10m, 1h), usa diretamente
                if duration and (duration.endswith('m') or duration.endswith('h')):
                    time_unit = duration[-1].lower()
                    time_value = int(duration[:-1])
                elif duration:
                    # Processa duração em formato texto (ex: "10 minutos", "1 hora")
                    duration_input = duration.lower()
                    
                    # Extrai números da entrada
                    numbers = re.findall(r'\d+', duration_input)
                    
                    if not numbers:
                        await ctx.send("<a:erro:1393619725472370859> **Formato de tempo inválido!** Use h para horas ou m para minutos (ex: 10m, 1h).")
                        return
                    
                    time_value = int(numbers[0])
                    
                    # Verifica se contém palavras-chave para determinar a unidade
                    if "minuto" in duration_input or "minutos" in duration_input or "m" in duration_input:
                        time_unit = "m"
                    elif "hora" in duration_input or "horas" in duration_input or "h" in duration_input:
                        time_unit = "h"
                    else:
                        # Se não encontrou palavras-chave, verifica se é apenas um número seguido de m ou h
                        if duration_input.endswith('m') or duration_input.endswith('h'):
                            time_unit = duration_input[-1].lower()
                        else:
                            await ctx.send("<a:erro:1393619725472370859> **Formato de tempo inválido!** Use h para horas ou m para minutos (ex: 10m, 1h).")
                            return
                else:
                    await ctx.send("<a:erro:1393619725472370859> **Duração não fornecida.**")
                    return
                
                time_seconds = time_value * time_map[time_unit]
                if time_seconds <= 0:
                    await ctx.send("<a:erro:1393619725472370859> **A duração deve ser maior que zero.**")
                    return
            except ValueError:
                await ctx.send("<a:erro:1393619725472370859> **Formato de tempo inválido!** Certifique-se de usar um número seguido por h ou m (ex: 10m, 1h).")
                return
            except Exception as e:
                await ctx.send(f"<a:erro:1393619725472370859> **Erro desconhecido ao processar a duração: {e}**")
                return
            question_embed = discord.Embed(
                title="<a:warn:1393656959441567915> Confirmação de silenciamento",
                description=f"Você está prestes a silenciar {member.mention} por {reason} durante {time_value} {time_unit}. Confirme clicando no botão abaixo.",
                color=discord.Color.red()
            )
            msg3 = await ctx.send("<a:loading:1393618509400899666>carregando...")
            view = MuteView(self.bot, member, reason, ctx, msg3, time_seconds)
            await msg3.edit(content="", embed=question_embed, view=view)
            MuteView.member = member
            MuteView.reason = reason
            MuteView.mute_msg = msg3
            MuteView.time = time_seconds
        except Exception as e:
            await ctx.send(f"<a:erro:1393619725472370859> **Erro inesperado: {e}**")

async def setup(bot):
    await bot.add_cog(AutoPune(bot))