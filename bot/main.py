import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import asyncio
from groq import Groq

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# Load modules
async def load_modules():
    for filename in os.listdir('./modules'):
        if filename.endswith('.py'):
            await bot.load_extension(f'modules.{filename[:-3]}')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await load_modules()
    try:
        synced = await tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)

# Run bot
bot.run(os.getenv('DISCORD_TOKEN'))