import discord
from discord.ext import commands

class coms_help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coms_help")
    async def help_command(self, ctx):
        """
        Comando de ajuda que mostra todos os comandos disponíveis.
        """
        embed = discord.Embed(
            title="📜 **Lista de Comandos do NOC Bot**",
            description="Aqui estão todos os comandos disponíveis no bot.",
            color=discord.Color.blue()
        )

        # Seção 1: Comandos Gerais
        embed.add_field(
            name="✨ **Comandos Gerais**",
            value=(
                "`-ping` - Mostra a latência do bot.\n"
                "`-say <mensagem>` - O bot repete a mensagem enviada.\n"
                "`-avatar <@usuário>` - Mostra o avatar do usuário.\n"
                "`-match <@usuário1> <@usuário2>` - Calcula a compatibilidade entre dois usuários."
            ),
            inline=False
        )

        # Seção 2: Comandos de Moderação
        embed.add_field(
            name="🔨 **Comandos de Moderação**",
            value=(
                "`-mute <@usuário> <tempo> <motivo>, ex(-mute 123436636363(or @user)24h quebrando regras)` - Aplica timeout em um usuário.\n"
                "`-unmute <@usuário>` - Remove o timeout de um usuário.\n"
                "`-ban <@usuário> <motivo>` - Bane um usuário do servidor.\n"
                "`-unban <ID do usuário>` - Remove o banimento de um usuário.\n"
                "`-warn <@usuário> <motivo>` - Adiciona um aviso para o usuário com confirmação.\n"
                "`-warns <@usuário>` - Mostra os avisos de um usuário.\n"
                "`-rwarn <@usuário> <número>` - Remove um aviso específico de um usuário.\n"
                "`-lock <motivo>` - Bloqueia o canal atual, impedindo o envio de mensagens.\n"
                "`-unlock <motivo>` - Desbloqueia o canal atual, permitindo o envio de mensagens.\n"
                "`-lockdown <motivo>` - Bloqueia todos os canais de conversa do servidor, impedindo o envio de mensagens.\n"
                "`-unlockdown <motivo>` - Desbloqueia todos os canais de conversa do servidor, permitindo o envio de mensagens.\n"
                "`-massban <ids dos usuários separados por vírgula, ex: 987743100401221672,234567890123456789>` - Banir vários usuários de uma vez."
            ),
            inline=False
        )

        # Seção 3: Sistema Financeiro
        embed.add_field(
            name="💰 **Sistema Financeiro**",
            value=(
                "`-work` - Trabalhe para ganhar NOC coins. (Cooldown de 2 minutos)\n"
                "`-coinflip <valor>` - Jogue cara ou coroa para apostar suas NOC coins.\n"
                "`-apostar @usuario valor`\n"
                "`-transferir @usuario valor, há 10% de imposto`\n"
                "`-jackpot valor`\n"
                "`-roleta valor`\n"
            ),
            inline=False
        )

        # Seção 4: Casamento
        embed.add_field(
            name="❤️ **Relacionamentos**",
            value=(
                "`-casar <@usuário>` - Case-se com outro usuário.\n"
                "`-divorciar` - Divorcie-se do usuário com quem você está casado."
            ),
            inline=False
        )
        embed.add_field(
            name="**misc**",
            value=(
                "`-luck`\n"
            )
        )
        # Seção 5: Evento de Halloween
        embed.add_field(
            name="🎃 **Evento de Halloween**",
            value=(
                "`-doces` - Toque a campainha e receba doces ou travessuras! (Cooldown de 1 hora)\n"
                "`-pontos` - Veja quantos pontos você possui no evento.\n"
                "`-rank_halloween` - Veja o ranking dos 10 melhores jogadores."
            ),
            inline=False
        )

        # Rodapé
        embed.set_footer(
            text="Use -<comando> para executar os comandos. Apenas administradores podem usar comandos de moderação.\n"
                 "`tá todo fudido mesmo, preguiça de fazer melhor`"
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(coms_help(bot))