import discord
import random
from discord.ext import commands
import asyncio
import database

# Classe do Cog de Comandos Financeiros
class FinanceiroCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = database.db  # Acessando a instância do banco de dados

    async def get_balance(self, user_id):
        result = await self.db.fetchone("SELECT balance FROM user_balances WHERE user_id = ?", (user_id,))
        return result[0] if result else 0

    async def update_balance(self, user_id, amount):
        current_balance =  await self.get_balance(user_id)
        new_balance = current_balance + amount
        await self.db.execute(
            "INSERT OR REPLACE INTO user_balances (user_id, balance) VALUES (?, ?)",
            (user_id, new_balance),
        )

    @commands.command(name="balance")
    async def balance(self, ctx):
        """Mostra o saldo atual do usuário."""
        balance = await self.get_balance(ctx.author.id)
        await ctx.send(f"💰 {ctx.author.mention}, você possui **{balance} NOC Coins**.")

    @commands.command(name="work")
    @commands.cooldown(1, 120, commands.BucketType.user)  # Cooldown de 2 minutos
    async def work(self, ctx):
        """Permite que o usuário trabalhe para ganhar dinheiro."""
        earnings = random.randint(50, 150)
        await self.update_balance(ctx.author.id, earnings)
        await ctx.send(f"💼 {ctx.author.mention}, você trabalhou duro e ganhou **{earnings} NOC Coins**!")

    @work.error
    async def work_error(self, ctx, error):
        """Mensagem quando o cooldown está ativo."""
        if isinstance(error, commands.CommandOnCooldown):
            remaining = int(error.retry_after)
            await ctx.send(f"⏳ {ctx.author.mention}, você precisa esperar **{remaining} segundos** antes de usar o comando `N$work` novamente.")

    @commands.command(name="coinflip")
    async def coinflip(self, ctx, amount: int):
        """Aposta um valor em cara ou coroa."""
        if amount <= 0:
            await ctx.send("<a:erro:1393619725472370859> O valor da aposta deve ser maior que zero.")
            return

        balance = await self.get_balance(ctx.author.id)
        if amount > balance:
            await ctx.send(f"<a:erro:1393619725472370859> {ctx.author.mention}, você não tem saldo suficiente para essa aposta!")
            return

        outcome = random.choice(["win", "lose"])
        if outcome == "win":
            await self.update_balance(ctx.author.id, amount)
            await ctx.send(f"🎉 {ctx.author.mention}, você ganhou! Recebeu **{amount} NOC Coins**.")
        else:
            await self.update_balance(ctx.author.id, -amount)
            await ctx.send(f"💸 {ctx.author.mention}, você perdeu! Foram descontados **{amount} NOC Coins**.")

    @commands.command(name="apostar")
    async def apostar(self, ctx, opponent: discord.Member, amount: int):
        """Comando para apostar moedas contra outro jogador."""
        if amount <= 0:
            await ctx.send("<a:erro:1393619725472370859> O valor da aposta deve ser maior que zero.")
            return

        if opponent == ctx.author:
            await ctx.send("<a:erro:1393619725472370859> Você não pode apostar contra você mesmo!")
            return

        author_balance = await self.get_balance(ctx.author.id)
        opponent_balance = await self.get_balance(opponent.id)

        if amount > author_balance or amount > opponent_balance:
            await ctx.send(f"<a:erro:1393619725472370859> {ctx.author.mention}, você ou o oponente não têm saldo suficiente para essa aposta!")
            return

        confirmation_message = await ctx.send(
            f"🎲 {opponent.mention}, {ctx.author.mention} desafiou você para uma aposta de **{amount} NOC Coins**! "
            "Reaja com <a:check:1394360081365204993> para aceitar ou <a:erro:1393619725472370859> para recusar."
        )

        await confirmation_message.add_reaction("<a:check:1394360081365204993>")
        await confirmation_message.add_reaction("<a:erro:1393619725472370859>")

        def check(reaction, user):
            return user == opponent and str(reaction.emoji) in ["<a:check:1394360081365204993>", "<a:erro:1393619725472370859>"]

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("⏳ O tempo para responder à aposta acabou.")
            return

        if str(reaction.emoji) == "<a:erro:1393619725472370859>":
            await ctx.send(f"{opponent.mention} recusou a aposta.")
            return

        winner = random.choice([ctx.author, opponent])
        loser = opponent if winner == ctx.author else ctx.author

        await self.update_balance(winner.id, amount)
        await self.update_balance(loser.id, -amount)

        await ctx.send(f"🎉 {winner.mention} venceu a aposta contra {loser.mention} e ganhou **{amount} NOC Coins**!")

    @commands.command(name="transferir")
    async def transferir(self, ctx, recipient: discord.Member, amount: int):
        """Transfere moedas para outro jogador com imposto de 10%."""
        if amount <= 0:
            await ctx.send("<a:erro:1393619725472370859> O valor da transferência deve ser maior que zero.")
            return

        if recipient == ctx.author:
            await ctx.send("<a:erro:1393619725472370859> Você não pode transferir moedas para si mesmo!")
            return

        balance = await self.get_balance(ctx.author.id)
        if amount > balance:
            await ctx.send(f"<a:erro:1393619725472370859> {ctx.author.mention}, você não tem saldo suficiente para essa transferência!")
            return

        confirmation_message = await ctx.send(
            f"🔄 {ctx.author.mention}, você está prestes a transferir **{amount} NOC Coins** para {recipient.mention}. "
            "Reaja com <a:check:1394360081365204993> para confirmar ou <a:erro:1393619725472370859> para cancelar."
        )

        await confirmation_message.add_reaction("<a:check:1394360081365204993>")
        await confirmation_message.add_reaction("<a:erro:1393619725472370859>")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["<a:check:1394360081365204993>", "<a:erro:1393619725472370859>"]

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("⏳ O tempo para confirmar a transferência acabou.")
            return

        if str(reaction.emoji) == "<a:erro:1393619725472370859>":
            await ctx.send(f"{ctx.author.mention}, transferência cancelada.")
            return

        tax = int(amount * 0.10)
        transfer_amount = amount - tax

        await self.update_balance(ctx.author.id, -amount)
        await self.update_balance(recipient.id, transfer_amount)

        await ctx.send(
            f"<a:check:1394360081365204993> {ctx.author.mention} transferiu **{transfer_amount} NOC Coins** (após **10%** de imposto) para {recipient.mention}!"
        )

    @commands.command(name="roleta")
    async def roleta(self, ctx, valor_da_aposta: float):
        balance = await self.get_balance(ctx.author.id)
        if valor_da_aposta <=0 or valor_da_aposta > balance:
            await ctx.send("Vc não tem saldo suficiente ou o valor foi menor ou igual a 0")
            return
        else:
            pass
        cores = ["preto", "verde", "vermelho"]
        await ctx.send("escolha qual cor vc deseja entre preto, verde ou vermelho\n chances de ganhar:\n verde: 5% de chances de ganhar, multiplicando 4x do saldo do usuario\n vermelho: 25% de chance de ganhar, multiplica 3x do valor da aposta\n preto: 35% de ganhar, multiplica 2x do valor da aposta")
        def check_message(msg):
            return (
                    msg.author == ctx.author
                    and str(msg.content.lower()) in cores
                    and msg.channel == ctx.channel)
        try:
            cor_registrada = await self.bot.wait_for("message", timeout=30.0, check=check_message)
            cor_escolhida = cor_registrada.content.lower()
            def atualizar_saldo(multiplicador):
                return self.update_balance(ctx.author.id, valor_da_aposta * multiplicador)
            if cor_escolhida.lower() == "verde":
                numero_verde = random.randint(1,100)
                if numero_verde > 95:
                    await ctx.send(f"vc venceu a aposta, seu valor da aposta foi multiplicado por 4 e adicionado ao seu saldo, saldo total: {balance}")
                    await atualizar_saldo(4)
                else:
                    await ctx.send("vc perdeu a aposta, o valor da aposta foi subtraido do seu saldo")
                    await self.update_balance(ctx.author.id, -valor_da_aposta)
            elif cor_escolhida.lower() == "vermelho":
                numero_vermelho = random.randint(1,100)
                if numero_vermelho > 75:
                    await ctx.send(f"vc venceu a aposta, seu valor da aposta foi multiplicado por 3 e adicionado ao seu saldo, saldo total: {balance}")
                    await atualizar_saldo(3)
                else:
                    await ctx.send("vc perdeu a aposta, o valor da aposta foi subtraido do seu saldo")
                    await self.update_balance(ctx.author.id, -valor_da_aposta)
            elif cor_escolhida.lower() == "preto":
                numero_preto = random.randint(1,100)
                if numero_preto > 65:
                    await ctx.send(f"vc venceu a aposta, seu valor da aposta foi multiplicado por 2 e adicionado ao seu saldo, saldo total: {balance}")
                    await atualizar_saldo(2)
                else:
                    await ctx.send("vc perdeu a aposta, o valor da aposta foi subtraido do seu saldo")
                    await self.update_balance(ctx.author.id, -valor_da_aposta)
            else:
                await ctx.send("<a:erro:1393619725472370859> cor invalida escolhida")

        except asyncio.TimeoutError:
            await ctx.send("<a:erro:1393619725472370859> tempo esgotado, use o comando novamente")

    @commands.command(name="jackpot")
    async def jackpot(self, ctx, valor_da_aposta: float):
        balance = await self.get_balance(ctx.author.id)
        emojis = ["🍒", "7️⃣", "🃏", "♠️", "♦️", "♣️"]
        emj_1 = random.choice(emojis)
        emj_2 = random.choice(emojis)
        emj_3 = random.choice(emojis)
        if valor_da_aposta <=0 or valor_da_aposta > balance:
            await ctx.send("Vc não tem saldo suficiente ou o valor foi menor ou igual a 0")
            return

        msg= await ctx.send("❓❓❓")
        await asyncio.sleep(1)
        await msg.edit(content=f"{emj_1}❓❓")
        await asyncio.sleep(1)
        await msg.edit(content=f"{emj_1}, {emj_2}, ❓")
        await asyncio.sleep(1)
        await msg.edit(content=f"{emj_1}, {emj_2}, {emj_3}")
        if emj_1 == emj_2 == emj_3:
            await asyncio.sleep(1)
            await ctx.send("🎰Jackpot!")
            await self.update_balance(ctx.author.id, valor_da_aposta*5)
        else:
            await asyncio.sleep(1)
            await ctx.send("que pena, vc perdeu")
            await self.update_balance(ctx.author.id, -valor_da_aposta)


# Função de configuração para carregar a cog
async def setup(bot):
    await bot.add_cog(FinanceiroCog(bot))