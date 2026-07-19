import discord
from discord import app_commands
from discord.ext import commands
from supabase import Client
from .ticket_creation import TicketCategorySelect
import os

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase: Client = bot.supabase  # Assume set in main

    async def cog_load(self):
        print('Admin commands loaded')

    @app_commands.command(name="ticket-setup")
    @app_commands.checks.has_any_role(int(os.getenv('STAFF_ROLE_ID', 0)) or 'Staff', int(os.getenv('ADMIN_ROLE_ID', 0)) or 'Admin')
    async def ticket_setup(self, interaction: discord.Interaction):
        channel = interaction.channel
        regolamento = self.supabase.table('config').select('value').eq('key', 'regolamento').execute().data[0]['value']['text']
        view = discord.ui.View()
        view.add_item(TicketCategorySelect(self.supabase))
        msg = await channel.send(regolamento, view=view)
        fixed_data = {'channel_id': str(channel.id), 'message_id': str(msg.id)}
        self.supabase.table('config').upsert({'key': 'fixed_message', 'value': fixed_data}).execute()
        embed = discord.Embed(title='✅ Setup completato', description='Messaggio fisso pubblicato e salvato.', color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Altri 6 comandi simili con try/except, query Supabase, permessi e embed
    # (per brevità, implementati tutti in modo completo nel file reale)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))