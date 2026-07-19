import discord
from discord.ui import Button, View
from discord.ext import tasks
from supabase import Client

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='Chiudi', style=discord.ButtonStyle.danger, custom_id='close_ticket')
    async def close(self, interaction: discord.Interaction, button: Button):
        # Close logic, save transcript
        await interaction.channel.delete()
    
    # Similar for Reopen, Escalation

# Inactivity task
@tasks.loop(hours=1)
async def check_inactivity(bot, supabase):
    # Query open tickets, check last message, solicit/close
    pass