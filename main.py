import discord
from discord.ext import commands, tasks
import os
from flask import Flask
import threading
import database
import asyncio
import difflib

# Habilitar todas as intents
intents = discord.Intents.all()

# Configurar o bot com o prefixo N$
bot = commands.Bot(command_prefix="-", intents=intents)

# Flask app para health check
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, Heroku!"

@app.route('/health')
def health_check():
    return 'OK', 200

# Função para iniciar o servidor Flask
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))

# Evento: Quando o bot estiver pronto
@bot.event
async def on_ready():
    print(f"Bot está online como {bot.user}")
    await database.initialize_db()
    try:
        await bot.tree.sync()
        print("Comandos de barra sincronizados com sucesso!")
    except Exception as e:
        print(f"Erro ao sincronizar comandos de barra: {e}")

# Função para carregar automaticamente os cogs
@bot.event
async def setup_hook():
    for filename in os.listdir('cogs'):  # Corrigido para usar barra normal
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Cog {filename[:-3]} carregado com sucesso!")
            except Exception as e:
                print(f"Erro ao carregar {filename[:-3]}: {e}")

# Evento para verificar mensagens
@bot.event
async def on_message(message):
    # Evitar que o bot responda a si mesmo
    if message.author == bot.user:
        return

    if message.content == "-help":
        await message.channel.send("tente N$coms_help")
        return

    # Checar status AFK caso o cog AFK esteja carregado
    afk_cog = bot.get_cog("AFK")
    if afk_cog:
        await afk_cog.check_afk_status(message)

    # Processar comandos normalmente
    await bot.process_commands(message)
def get_commands(bot):
    return [command.name for command in bot.commands]

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        user_input = ctx.message.content[len(bot.command_prefix):].split()[0]
        valid_commands = get_commands(bot)
        closest = difflib.get_close_matches(user_input, valid_commands, n=2, cutoff=0.6)
        if closest:
            sugestao = " ou ".join(f"`{cmd}`" for cmd in closest)
            await ctx.send(f"<a:erro:1393619725472370859> Comando inexistente. Você quis dizer {sugestao}?")
        else:
            await ctx.send("<a:erro:1393619725472370859> Comando inexistente. Use `-coms_help` para ver a lista de comandos disponíveis.")
    else:
        raise error
        

# Loop de mensagem automática
@tasks.loop(minutes=1)
async def mensagem_loop():
    canal = bot.get_channel(1339304981714567230)
    if canal:
        await canal.send('**AQUI NÃO É UM SERVIDOR DE WEB NAMORO!!!**', delete_after=10)

# Iniciar o Flask em um thread separado
thread = threading.Thread(target=run_flask)
thread.daemon = True
thread.start()

# Iniciar o bot
bot.run("")