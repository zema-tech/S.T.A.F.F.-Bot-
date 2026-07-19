import discord
from discord.ext import tasks, commands
from supabase import Client
import asyncio

class ConfigSync:
    def __init__(self, bot, supabase: Client):
        self.bot = bot
        self.supabase = supabase
        self.config_cache = {}
        self.fixed_message_id = None  # Will store in config or separate table
        self.sync_task.start()

    @tasks.loop(seconds=45)
    async def sync_task(self):
        try:
            resp = self.supabase.table('config').select('*').execute()
            new_config = {row['key']: row['value'] for row in resp.data}
            if new_config.get('regolamento') != self.config_cache.get('regolamento'):
                self.config_cache = new_config
                print('Regolamento updated - editing fixed message')
                # Find fixed message (assume stored in config or hard-coded channel for simplicity)
                ticket_channel_id = 1234567890  # Replace with real logic/DB lookup
                channel = self.bot.get_channel(ticket_channel_id)
                if channel and self.fixed_message_id:
                    msg = await channel.fetch_message(self.fixed_message_id)
                    new_text = new_config['regolamento']['text']
                    # Rebuild view with categories
                    view = discord.ui.View()
                    view.add_item(TicketCategorySelect(self.supabase))
                    await msg.edit(content=new_text, view=view)
        except Exception as e:
            print(f'Config sync error: {e}')

    def get(self, key, default=None):
        return self.config_cache.get(key, default)