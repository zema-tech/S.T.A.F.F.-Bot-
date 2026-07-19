import discord
from discord.ui import Select, View, Modal, TextInput
from discord import app_commands
from supabase import Client

class TicketCategorySelect(Select):
    def __init__(self, supabase: Client):
        self.supabase = supabase
        # Fetch categories
        categories = self.supabase.table('ticket_categories').select('*').execute().data
        options = [
            discord.SelectOption(
                label=cat['name'], 
                emoji=cat.get('emoji'), 
                description=cat.get('description')[:100]
            ) for cat in categories
        ]
        super().__init__(placeholder='Seleziona una categoria ticket', options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        category_name = self.values[0]
        # Open dynamic modal
        modal = DynamicTicketModal(category_name, self.supabase)
        await interaction.response.send_modal(modal)

class DynamicTicketModal(Modal):
    def __init__(self, category_name, supabase):
        self.category_name = category_name
        self.supabase = supabase
        super().__init__(title=f'Ticket {category_name}')
        
        # Fetch fields dynamically
        # ... (full logic in production)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message('Ticket creato!', ephemeral=True)