import discord
from discord.ext import tasks
from supabase import Client
from .ticket_creation import TicketCategorySelect

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
            if new_config.get('regolamento') != self.config_cache.get('regolamento'):
                self.config_cache = new_config
                fixed = new_config.get('fixed_message', {})
                channel_id = fixed.get('channel_id')
                message_id = fixed.get('message_id')
                if channel_id and message_id:
                    channel = self.bot.get_channel(int(channel_id))
                    if channel:
                        msg = await channel.fetch_message(int(message_id))
                        new_text = new_config['regolamento']['text']
                        view = discord.ui.View()
                        view.add_item(TicketCategorySelect(self.supabase))
                        await msg.edit(content=new_text, view=view)
        except Exception as e:
            print(f'Config sync error: {e}')

    def get(self, key, default=None):
        return self.config_cache.get(key, default)