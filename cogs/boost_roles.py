import discord
from discord.ext import commands
class BoostRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_roles = {
            1339304980737163397: {  # Guild ID 1
                1: 1345864487172837457,  # role for 1 boost
                2: 1361044696226463761   # role for 2 or more boosts
            },
            1369780036961308803: {  # Guild ID 2 (replace with actual guild ID)
                1: 1375659062783639622,  # Different role IDs for other guild
                2: 1375659062783639622   # role for 2 or more boosts
            }
            # Add more guilds as needed
        }

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.premium_since == after.premium_since:
            return

        guild = after.guild
        if guild.id not in self.guild_roles:
            return  # Skip if guild is not configured

        # Contar quantos boosts o usuário específico deu
        user_boosts = 0
        if after.premium_since:
            # Se o usuário deu boost, verificar quantos boosts ele tem
            # No Discord, um usuário pode dar até 2 boosts por servidor
            user_boosts = 1 if before.premium_since is None else 2
        
        roles = self.guild_roles[guild.id]
        role_1 = guild.get_role(roles[1])
        role_2 = guild.get_role(roles[2])
        
        # Remover os cargos antigos
        removed_roles = []
        for role in [role_1, role_2]:
            if role and role in after.roles:
                await after.remove_roles(role)
                removed_roles.append(role.name)
        
        # Definir o novo cargo baseado na quantidade de boosts do usuário
        new_role = None
        if user_boosts > 0:
            if user_boosts >= 2:
                new_role = role_2
            else:
                new_role = role_1

        # Adicionar o novo cargo
        added_roles = []
        if new_role and new_role not in after.roles:
            await after.add_roles(new_role)
            added_roles.append(new_role.name)
        
        # Enviar mensagem privada ao usuário
        try:
            msg = ""
            if removed_roles:
                msg += f"❌ Você perdeu os cargos: {', '.join(removed_roles)}.\n"
            if added_roles:
                msg += f"✅ Você recebeu o cargo: {', '.join(added_roles)}.\n"
            if msg:
                await after.send(msg)
        except discord.Forbidden:
            print(f"Não foi possível enviar mensagem para {after.name}.")

async def setup(bot):
    await bot.add_cog(BoostRoles(bot))