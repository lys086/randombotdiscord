import discord
from discord.ext import commands

class LockUnlock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, *, reason: str = "Sem motivo"):
        """
        Bloqueia o canal atual para que ninguém possa enviar mensagens.
        """
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False  # Nega a permissão de enviar mensagens
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"<a:check:1394360081365204993> **Canal bloqueado!** Motivo: {reason}")

    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, *, reason: str = "Sem motivo"):
        """
        Desbloqueia o canal atual permitindo que todos enviem mensagens.
        """
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None  # Remove a negação, restaurando as permissões padrão
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"<a:check:1394360081365204993> **Canal desbloqueado!** Motivo: {reason}")

    @commands.command(name="lockdown")
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx, *, reason: str = "Sem motivo"):
        if ctx.guild.id == 1369780036961308803:
            channels = ["1369780038014341122", "1375653271888334919", "1375653335411068938", "1375657903146664008", "1375654913639448629", "1375655403316187186", "1375658636789022750", "1375902292665958480"]
        elif ctx.guild.id == 1339304980737163397:
            channels = ["1345853362058297485", "1345919182918652015", "1345853362058297485", "1342843482242285700", "1347345703898452080", "1346314676379844619", "1347051527239635035", "1363687402723348551", "1365348926567354508"]
        wait_msg = await ctx.send(f"<a:loading:1393618509400899666> Esperando a API do Discord finalizar a operação...")
        for channel_id in channels:
            channel = ctx.guild.get_channel(int(channel_id))
            if channel:
                overwrite = channel.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = False
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await wait_msg.delete()
        await ctx.send(f"<a:check:1394360081365204993> Sucesso!")
    @commands.command(name="unlockdown")
    @commands.has_permissions(manage_channels=True)
    async def unlockdown(self, ctx, *, reason: str = "Sem motivo"):
        if ctx.guild.id == 1369780036961308803:
            channels = ["1369780038014341122", "1375653271888334919", "1375653335411068938", "1375657903146664008", "1375654913639448629", "1375655403316187186", "1375658636789022750", "1375902292665958480"]
        elif ctx.guild.id == 1339304980737163397:
            channels = ["1345853362058297485", "1345919182918652015", "1345853362058297485", "1342843482242285700", "1347345703898452080", "1346314676379844619", "1347051527239635035", "1363687402723348551", "1365348926567354508"]
        wait_msg = await ctx.send(f"<a:loading:1393618509400899666> Esperando a API do Discord finalizar a operação...")
        for channel_id in channels:
            channel = ctx.guild.get_channel(int(channel_id))
            if channel:
                overwrite = channel.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = None
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"<a:check:1394360081365204993> Sucesso!")
        await wait_msg.delete()


async def setup(bot):
    await bot.add_cog(LockUnlock(bot))
