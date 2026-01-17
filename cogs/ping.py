import time
from datetime import datetime
import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        # Marca o tempo antes de enviar a mensagem
        start_time = time.time()
        message = await ctx.send("Calculando ping...")
        end_time = time.time()

        # Latência do WebSocket em ms
        websocket_latency = self.bot.latency * 1000

        # Round-trip da mensagem em ms
        round_trip_latency = (end_time - start_time) * 1000

        # Latência da API REST (simulando uma requisição simples)
        rest_start = time.time()
        await ctx.channel.typing()
        rest_end = time.time()
        rest_latency = (rest_end - rest_start) * 1000

        # Shard ID e total de shards
        shard_id = getattr(ctx.guild, "shard_id", "Único shard") if ctx.guild else "Único shard"
        total_shards = getattr(self.bot, "shard_count", 1)

        # Informações do servidor
        server_name = ctx.guild.name if ctx.guild else "DM"
        server_id = ctx.guild.id if ctx.guild else "N/A"
        member_count = ctx.guild.member_count if ctx.guild else "N/A"
        bot_count = sum(1 for m in ctx.guild.members if m.bot) if ctx.guild else "N/A"
        human_count = member_count - bot_count if ctx.guild and member_count != "N/A" else "N/A"

        # Informações do usuário
        user_name = ctx.author.name
        user_id = ctx.author.id

        # Informações do bot
        bot_name = self.bot.user.name
        bot_id = self.bot.user.id
        total_guilds = len(self.bot.guilds)
        total_channels = sum(len(guild.channels) for guild in self.bot.guilds)

        # Hora do bot
        bot_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        # Criando embed
        embed = discord.Embed(
            title="🏓 Painel de Ping do Bot",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="Latências", value=(
            f"• WebSocket: {websocket_latency:.2f}ms\n"
            f"• Round-trip mensagem: {round_trip_latency:.2f}ms\n"
            f"• Latência API REST: {rest_latency:.2f}ms"
        ), inline=False)

        embed.add_field(name="Shard", value=(
            f"• Shard ID: {shard_id}\n"
            f"• Total de shards: {total_shards}"
        ), inline=False)

        embed.add_field(name="Servidor", value=(
            f"• Nome: {server_name}\n"
            f"• ID: {server_id}\n"
            f"• Membros: {member_count} (Humano: {human_count}, Bots: {bot_count})"
        ), inline=False)

        embed.add_field(name="Usuário", value=(
            f"• Nome: {user_name}\n"
            f"• ID: {user_id}"
        ), inline=False)

        embed.add_field(name="Bot", value=(
            f"• Nome: {bot_name}\n"
            f"• ID: {bot_id}\n"
            f"• Servidores: {total_guilds}\n"
            f"• Canais totais: {total_channels}"
        ), inline=False)

        embed.set_footer(text=f"Hora do bot: {bot_time}")

        # Edita a mensagem com o embed
        await message.edit(content=None, embed=embed)

# Setup do cog
async def setup(bot):
    await bot.add_cog(Ping(bot))