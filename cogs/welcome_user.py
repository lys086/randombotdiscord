import discord
from discord.ext import commands

class WelcomeUser(commands.Cog):  # <- define o cog como uma classe
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='test_message')
    @commands.has_permissions(administrator=True)
    async def test_message(self, ctx):
        role_mov= discord.utils.get(ctx.guild.roles, name="╭ ┆mov.chat ╰⊹ ࣪")
        await ctx.send(f"₊ ⊹ Seja bem vindo {ctx.author.mention} ᵎᵎ  🍵 ˎˊ˗"
                f"lembre-se de ler as regras <#1339304981466976325> e de manter o respeito com outros membros, os {role_mov.mention} vão te acolher e te familiarizar com o ambiente. Lembrando que entrar em busca de um relacionamento amoroso é expressamente proibido! <a:9decoracao6:1367565106992382084>\n"
                f"https://cdn.discordapp.com/attachments/1361514276078223421/1368712204219715745/494d8c14dbae01f9f90db8665edbe5f6.gif?ex=68193812&is=6817e692&hm=000d69754dca83488a6abc53cb9b9b4a19b6b7ef9902900b3bfdaf1bdb7ef4d3&")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{member} entrou no servidor.")

        channel = member.guild.get_channel(1339304981714567230)
        print(f"Canal: {channel}")

        if channel:
            role_mov= discord.utils.get(member.guild.roles, name="╭ ┆mov.chat ╰⊹ ࣪")
            welcome_message = (
                f"₊ ⊹ Seja bem vindo {member.mention} ᵎᵎ  🍵 ˎˊ˗"
                f"lembre-se de ler as regras <#1339304981466976325> e de manter o respeito com outros membros, os {role_mov.mention} vão te acolher e te familiarizar com o ambiente. Lembrando que entrar em busca de um relacionamento amoroso é expressamente proibido! <a:9decoracao6:1367565106992382084>\n"
                f"https://cdn.discordapp.com/attachments/1361514276078223421/1368712204219715745/494d8c14dbae01f9f90db8665edbe5f6.gif?ex=68193812&is=6817e692&hm=000d69754dca83488a6abc53cb9b9b4a19b6b7ef9902900b3bfdaf1bdb7ef4d3&"
            )

            await channel.send(welcome_message)


# Setup do cog
async def setup(bot):
    await bot.add_cog(WelcomeUser(bot))  # <- usa o nome da classe correta