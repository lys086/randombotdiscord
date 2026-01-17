import discord
import discord.ext
from discord.ext import commands
from discord import ui

class MassBanView(discord.ui.View):
    def __init__ (self, ctx, members_list):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.members_list = members_list

    @discord.ui.button(label="Banir Membros", style=discord.ButtonStyle.red)
    async def confirm(self,  interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("<a:warn:1393656959441567915> Você não tem permissão para usar este botão.", ephemeral=True)
            return
        # 1) Primeira resposta: mensagem de "por favor, aguarde..."
        await interaction.response.send_message("<a:loading:1393618509400899666> Por favor, aguarde enquanto a API do Discord finaliza a operação.", ephemeral=False)
        # Recupere a mensagem recém‑criada para poder editá‑la depois
        please_wait = await interaction.original_response()
        for member_to_ban in self.members_list:
            try:
                member_to_catch = int(member_to_ban)
                member_catch = interaction.guild.get_member(member_to_catch)
                await member_catch.ban(reason=f"banimento em massa solicitado por {self.ctx.author.name}, pergunte a ele se quiser mais informações sobre esse banimento.")
                await interaction.followup.send(f"<a:check:1394360081365204993> {member_catch.mention} foi banido com sucesso!", ephemeral=False)
            except discord.NotFound:
                await interaction.followup.send(f"<a:erro:1393619725472370859> Erro, Usuário com ID {member_catch.id} não encontrado neste servidor.", ephemeral=True)
            except discord.Forbidden:
                await interaction.followup.send(f"<a:erro:1393619725472370859> Erro, Não tenho permissão para banir {member_catch.name}.", ephemeral=True)
            else:
                await interaction.original_response.edit(content=f"<a:check:1394360081365204993> Banimento em massa concluído com sucesso!")

class MassBan(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot

    @commands.command(name="massban")
    @commands.has_permissions(ban_members=True)
    async def massban(self, ctx, *, members_ids: str):
        """
        Banir vário usuários de uma vez.
        """
        if "," not in members_ids:
            await ctx.send("<a:warn:1393656959441567915> Os ids de usuarios devem estar separados por vírgula, ex: 123456789012345678,234567890123456789")
            return
        members_list = members_ids.split(",")
        await ctx.send(members_list)
        members_with_name_to_embed_list = []
        for member_id_member_list in members_list:
            try:
                member_to_catch = int(member_id_member_list)
                member_catch = ctx.guild.get_member(member_to_catch)
            except Exception as e:
                await ctx.send(f"<a:erro:1393619725472370859> erro ao armazenar o valor na lista de membros para banir: {e}")
            if member_catch is not None:
                members_with_name_to_embed_list.append(f"{member_catch.mention}")
            else:
                await ctx.send(f"<a:erro:1393619725472370859> Usuario com ID {member_to_catch} não encontrado no servidor.")
        confirm_embed = discord.Embed(title="Banimento em massa", description=f"Você está prestes a banir os seguintes usuários: {members_with_name_to_embed_list}", color=discord.Color.yellow())
        confirm_view = MassBanView(ctx, members_list)
        await ctx.send(embed=confirm_embed, view=confirm_view)

async def setup(bot):
    await bot.add_cog(MassBan(bot))