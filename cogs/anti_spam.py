import discord
from discord.ext import commands
from datetime import timedelta, datetime
import asyncio

class AntiSpamModule(commands.Cog):
    def __init__(self, bot, user_warnings: dict | None = None, n_messages: int = 4, mute_duration_seconds: int = 1800):
        self.bot = bot
        self.n_messages = n_messages
        self.mute_duration_seconds = mute_duration_seconds
        self.user_warnings: dict = user_warnings if user_warnings is not None else {}
    
    async def delete_user_from_dict(self, user_id: int):
        await asyncio.sleep(120)
        if user_id in self.user_warnings:
            self.user_warnings.pop(user_id)
        return

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.guild is None:
            return

        if "<@" in message.content and message.channel.id != 1347051527239635035:
            print(f"mention by {message.author.name} in {message.channel.name}")
            
            if message.author.id not in self.user_warnings:
                self.user_warnings[message.author.id] = {
                    "number_of_messages": 1,
                    "last_message_time": datetime.now(),
                    "number_of_warnings": 0
                }
                return

            # calcula a diferença de tempo ANTES de atualizar
            time_difference_last_message = datetime.now() - self.user_warnings[message.author.id]["last_message_time"]

            # atualiza dados
            self.user_warnings[message.author.id]["number_of_messages"] += 1
            self.user_warnings[message.author.id]["last_message_time"] = datetime.now()

            # primeira punição (aviso)
            if (
                self.user_warnings[message.author.id]["number_of_messages"] >= self.n_messages 
                and time_difference_last_message < timedelta(seconds=2) 
                and self.user_warnings[message.author.id]["number_of_warnings"] == 0
            ):
                await message.channel.send(
                    f"<a:warn:1393656959441567915> {message.author.mention} Alerta, se você continuar a enviar spam de menções você será silenciado por nosso sistema de moderação automática."
                )
                self.user_warnings[message.author.id]["number_of_warnings"] += 1
                asyncio.create_task(self.delete_user_from_dict(message.author.id))

            # segunda punição (mute)
            elif (
                self.user_warnings[message.author.id]["number_of_messages"] >= self.n_messages 
                and time_difference_last_message < timedelta(seconds=4) 
                and self.user_warnings[message.author.id]["number_of_warnings"] == 1
            ):
                if isinstance(message.author, discord.Member):
                    try:
                        await message.author.timeout(timedelta(seconds=self.mute_duration_seconds))
                    except discord.Forbidden:
                        await message.channel.send(
                            f"<a:erro:1393619725472370859> erro da API do discord, não foi possível silenciar o usuário. Contate a Lys."
                        )
                    except discord.HTTPException as e:
                        await message.channel.send(
                            f"<a:erro:1393619725472370859> erro HTTP: {e}, não foi possível silenciar o usuário. Contate a Lys."
                        )
                    except Exception as e:
                        await message.channel.send(
                            f"<a:erro:1393619725472370859> erro desconhecido: {e}, não foi possível silenciar o usuário. Contate a Lys."
                        )
                    else:
                        await message.channel.send(
                            f"<a:check:1394360081365204993> {message.author.mention} Você foi silenciado por nosso sistema de moderação automática."
                        )
                        # limpa os dados do usuário
                        del self.user_warnings[message.author.id]

                        # envia DM para o usuário
                        try:
                            await message.author.send(
                                f"**Aviso da Staff**\n\n"
                                f"Você foi silenciado na {message.guild.name} por spam.\n\n"
                                f"A decisão foi tomada com base nas regras da comunidade. Caso tenha dúvidas, entre em contato com a equipe de moderação.\n\n"
                                f"Atenciosamente,\nAdministração"
                            )
                        except discord.Forbidden:
                            pass  # não conseguiu enviar DM, ignora

                        # log de punição
                        if message.guild.id == 1339304980737163397:
                            log_channel = discord.utils.get(message.guild.text_channels, name="📜┇provas")
                        elif message.guild.id == 1369780036961308803:
                            log_channel = discord.utils.get(message.guild.text_channels, name="⤷🗑️﹕registro")
                        else:
                            log_channel = discord.utils.get(message.guild.text_channels, name="🚔┃registro-staff")

                        if log_channel:
                            embed = discord.Embed(title="⚖️ Registro de punição ⚖️", color=discord.Color.red())
                            embed.add_field(name="Usuário", value=f"{message.author} ({message.author.id})", inline=False)
                            embed.add_field(name="Motivo", value="Spam", inline=False)
                            embed.add_field(name="Punição", value="Mute", inline=False)
                            embed.add_field(name="Responsável", value=f"{message.author} ({message.author.id})", inline=False)
                            embed.add_field(name="Prova(s)", value="(Pergunte ao moderador responsável)", inline=False)
                            await log_channel.send(embed=embed)
        else:
            return

async def setup(bot):
    await bot.add_cog(AntiSpamModule(bot))
