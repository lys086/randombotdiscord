import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os
import time
from database import db

class Db_Get():
    def __init__(self, bot, user_id, points_add):
        self.bot = bot
        self.user_id = user_id
        self.points_add = points_add
        self.db = db

    async def get_user_data(self):
        result = await self.db.fetchone("SELECT points_number FROM halloween_data WHERE user_id = ?", (self.user_id,))
        return result[0] if result else 0
    async def add_user_data(self):
        result = await self.db.fetchone("SELECT user_id FROM halloween_data WHERE user_id = ?", (self.user_id,))
        if not result:  # Usuário não existe, criar novo registro
            await self.db.execute("INSERT INTO halloween_data (user_id, points_number) VALUES (?, ?)", (self.user_id, self.points_add))
        else:  # Usuário existe, atualizar pontos
            await self.db.execute("UPDATE halloween_data SET points_number = points_number + ? WHERE user_id = ?", (self.points_add, self.user_id))
    async def update_user_data(self):
        await self.db.execute("UPDATE halloween_data SET points_number = ? WHERE user_id = ?", (self.points_add, self.user_id))
    async def delete_user_data(self):
        await self.db.execute("DELETE FROM halloween_data WHERE user_id = ?", (self.user_id,))

class Halooween_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = db
    @commands.command(name="pontos")
    async def pontos(self, ctx):
            user_data = await Db_Get(self.bot, ctx.author.id, 0).get_user_data()
            await ctx.send(f"Você possui {user_data} pontos")
    @commands.command(name="rank_halloween")
    async def rank_halloween(self, ctx):
        results = await self.db.fetchall("SELECT user_id, points_number FROM halloween_data ORDER BY points_number DESC LIMIT 10")
        
        if not results:
            embed = discord.Embed(
                title="🎃 Ranking Halloween",
                description="Nenhum usuário possui pontos ainda!",
                color=0xFF8C00
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="🎃 Ranking Halloween - Top 10",
            description="Os melhores coletores de doces!",
            color=0xFF8C00
        )
        
        ranking_text = ""
        for i, (user_id, points) in enumerate(results, 1):
            try:
                user = self.bot.get_user(user_id)
                if user:
                    username = user.display_name
                else:
                    username = f"Usuário {user_id}"
            except:
                username = f"Usuário {user_id}"
            
            # Adicionar emojis para as posições
            if i == 1:
                position_emoji = "🥇"
            elif i == 2:
                position_emoji = "🥈"
            elif i == 3:
                position_emoji = "🥉"
            else:
                position_emoji = f"{i}."
            
            ranking_text += f"{position_emoji} **{username}** - {points} pontos\n"
        
        embed.add_field(
            name="🏆 Ranking",
            value=ranking_text,
            inline=False
        )
        
        embed.set_footer(text=f"Total de {len(results)} usuários no ranking")
        
        await ctx.send(embed=embed)
    async def check_cooldown(self, user_id):
        """Verifica se o usuário está em cooldown"""
        result = await self.db.fetchone("SELECT last_used FROM halloween_cooldowns WHERE user_id = ?", (user_id,))
        if not result:
            return True  # Usuário nunca usou o comando, pode usar
        
        last_used = result[0]
        current_time = int(time.time())
        cooldown_duration = 3600  # 1 hora em segundos
        
        if current_time - last_used >= cooldown_duration:
            return True  # Cooldown expirado, pode usar
        else:
            return False  # Ainda em cooldown

    async def set_cooldown(self, user_id):
        """Define o cooldown para o usuário"""
        current_time = int(time.time())
        await self.db.execute(
            "INSERT OR REPLACE INTO halloween_cooldowns (user_id, last_used) VALUES (?, ?)",
            (user_id, current_time)
        )

    @commands.command(name="doces")
    async def doces(self, ctx):
        user_id = ctx.author.id
        
        # Verificar cooldown
        if not await self.check_cooldown(user_id):
            await ctx.send("você só pode usar dnv em 1 hora")
            return
        
        # Definir cooldown
        await self.set_cooldown(user_id)
        
        await ctx.send(f"Você tocou a campainha da casa, uma luz saiu de dentro da porta, e...")
        doces_ou_travessuras = random.choices(["doces", "travessuras"], weights=[0.45, 0.50], k=1)[0]
        if doces_ou_travessuras == "doces":
            await ctx.send(f"Um homem desconhecido saiu da casa, e te deu um doce, voce ficou surpreso e agora esta curioso para saber o que é esse doce")
            raridade_escolhida = random.choices(["comum", "raro", "epico", "legendario", "magico"], weights=[0.45, 0.35, 0.15, 0.05, 0.001], k=1)[0]
            if raridade_escolhida == "comum":
                db_handler = Db_Get(self.bot, user_id, 1)
                await db_handler.add_user_data()
                await ctx.send(f"Você ganhou 1 doce comum, e acumulou um total de 1 ponto, parabens!")
                await db_handler.update_user_data()
            elif raridade_escolhida == "raro":
                db_handler = Db_Get(self.bot, user_id, 2)
                await db_handler.add_user_data()
                await ctx.send(f"Você ganhou 1 doce raros, e acumulou um total de 2 pontos, parabens!")
                await db_handler.update_user_data()
            elif raridade_escolhida == "epico":
                db_handler = Db_Get(self.bot, user_id, 3)
                await db_handler.add_user_data()
                await ctx.send(f"Você ganhou 1 doce epicos, e acumulou um total de 3 pontos, parabens!")
                await db_handler.update_user_data()
            elif raridade_escolhida == "legendario":
                db_handler = Db_Get(self.bot, user_id, 4)
                await db_handler.add_user_data()
                await ctx.send(f"Você ganhou 1 doce legendarios, e acumulou um total de 4 pontos, parabens!")
                await db_handler.update_user_data()
            elif raridade_escolhida == "magico":
                db_handler = Db_Get(self.bot, user_id, 30)
                await db_handler.add_user_data()
                await ctx.send(f"WOW! esse doce está brilhando e saindo faiscas de magia, parabens! voce ganhou um doce magico, valendo 30 pontos! sortudo!")
                await db_handler.update_user_data()
        elif doces_ou_travessuras == "travessuras":
            messages = ["Um homem desconhecido saiu da casa, peidou em voce, e foi embora, que ousadia!", "saiu rolos de papei magicos da casa e te enrolou todo, da proxima tenha mais sorte!", "uma bruxa saiu da casa e te lançou uma maldição, que azar!"]
            await ctx.send(f"{random.choice(messages)}")


async def setup(bot):
    await bot.add_cog(Halooween_command(bot))