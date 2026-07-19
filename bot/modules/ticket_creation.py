import discord
from discord.ui import Select, View, Modal, TextInput
from discord import app_commands
from supabase import Client
import asyncio

class TicketCategorySelect(Select):
    def __init__(self, supabase: Client):
        self.supabase = supabase
        response = self.supabase.table('ticket_categories').select('*').execute()
        categories = response.data
        options = [
            discord.SelectOption(
                label=cat['name'],
                emoji=cat.get('emoji'),
                description=cat.get('description', '')[:100]
            ) for cat in categories
        ]
        super().__init__(placeholder='Seleziona una categoria ticket', options=options[:25], min_values=1, max_values=1)  # Discord limit

    async def callback(self, interaction: discord.Interaction):
        category_name = self.values[0]
        modal = DynamicTicketModal(category_name, self.supabase)
        await interaction.response.send_modal(modal)

class DynamicTicketModal(Modal):
    def __init__(self, category_name: str, supabase: Client):
        self.category_name = category_name
        self.supabase = supabase
        super().__init__(title=f'Nuovo Ticket - {category_name}')
        
        # Fetch category ID
        cat_resp = supabase.table('ticket_categories').select('id').eq('name', category_name).execute()
        if not cat_resp.data:
            return
        cat_id = cat_resp.data[0]['id']
        
        # Fetch fields
        fields_resp = supabase.table('ticket_fields').select('*').eq('category_id', cat_id).order('position').execute()
        self.fields_data = fields_resp.data
        
        for i, field in enumerate(self.fields_data[:5]):  # Max 5
            style = discord.TextStyle.paragraph if field['type'] == 'paragraph' else discord.TextStyle.short
            self.add_item(TextInput(
                label=field['label'],
                style=style,
                placeholder=field.get('placeholder', ''),
                required=field.get('required', True),
                custom_id=f'field_{i}'
            ))

    async def on_submit(self, interaction: discord.Interaction):
        # Collect responses
        responses = {item.label: item.value for item in self.children}
        
        # Create ticket channel
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        # Add staff with competence later in manager
        
        cat_resp = self.supabase.table('ticket_categories').select('channel_category_id').eq('name', self.category_name).execute()
        category_id = cat_resp.data[0]['channel_category_id'] if cat_resp.data else None
        category = discord.utils.get(guild.categories, id=int(category_id)) if category_id else None
        
        channel = await guild.create_text_channel(
            f'ticket-{self.category_name.lower()}-{interaction.user.name}',
            category=category,
            overwrites=overwrites
        )
        
        # Save to DB
        ticket_data = {
            'discord_ticket_channel_id': str(channel.id),
            'user_id': str(interaction.user.id),
            'category_id': self.supabase.table('ticket_categories').select('id').eq('name', self.category_name).execute().data[0]['id']
        }
        ticket_resp = self.supabase.table('tickets').insert(ticket_data).execute()
        
        # Embed riepilogo
        embed = discord.Embed(title='Ticket Creato', description='Assistenza Virtuale sta rispondendo...', color=0x00ff00)
        for label, value in responses.items():
            embed.add_field(name=label, value=value[:1024] or 'N/A', inline=False)
        await channel.send(embed=embed)
        
        await interaction.response.send_message(f'Ticket creato in {channel.mention}!', ephemeral=True)
        
        # Trigger AI triage
        from .ai_triage import send_ai_triage
        await send_ai_triage(channel, self.category_name, self.supabase)