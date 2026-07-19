import discord
from discord.ext import tasks, commands
from supabase import Client
import asyncio

class ConfigSync:
    def __init__(self, bot, supabase: Client):
        self.bot = bot
        self.supabase = supabase
        self.config_cache = {}
        self.sync_task.start()

    @tasks.loop(seconds=45)
    async def sync_task(self):
        try:
            resp = self.supabase.table('config').select('*').execute()
            new_config = {row['key']: row['value'] for row in resp.data}
            if new_config != self.config_cache:
                self.config_cache = new_config
                print('Config updated from Supabase')
                # Republish fixed message if regolamento changed
                # Logic to find and edit message in ticket channel
        except Exception as e:
            print(f'Config sync error: {e}')

    def get(self, key, default=None):
        return self.config_cache.get(key, default)