import discord
from discord.ui import Button, View
from discord.ext import tasks
from supabase import Client
import datetime

class TicketView(View):
    def __init__(self, supabase: Client, ticket_id):
        super().__init__(timeout=None)
        self.supabase = supabase
        self.ticket_id = ticket_id

    @discord.ui.button(label='Chiudi', style=discord.ButtonStyle.danger, custom_id='close_ticket')
    async def close(self, interaction: discord.Interaction, button: Button):
        channel = interaction.channel
        # Save transcript
        messages = []
        async for msg in channel.history(limit=None):
            messages.append({
                'ticket_id': self.ticket_id,
                'discord_message_id': str(msg.id),
                'author_id': str(msg.author.id),
                'content': msg.content,
                'is_ai': msg.author.bot
            })
        if messages:
            self.supabase.table('ticket_messages').insert(messages).execute()
        # Update ticket
        self.supabase.table('tickets').update({
            'status': 'closed',
            'closed_at': datetime.datetime.now().isoformat(),
            'closed_by': str(interaction.user.id)
        }).eq('id', self.ticket_id).execute()
        await interaction.response.send_message('Ticket chiuso e trascrizione salvata.', ephemeral=True)
        await channel.delete()

    @discord.ui.button(label='Riapri', style=discord.ButtonStyle.success, custom_id='reopen_ticket')
    async def reopen(self, interaction: discord.Interaction, button: Button):
        self.supabase.table('tickets').update({'status': 'open'}).eq('id', self.ticket_id).execute()
        # Restore permissions
        await interaction.response.send_message('Ticket riaperto.', ephemeral=True)

    @discord.ui.button(label='Escalation', style=discord.ButtonStyle.primary, custom_id='escalate_ticket')
    async def escalate(self, interaction: discord.Interaction, button: Button):
        self.supabase.table('tickets').update({'status': 'escalated'}).eq('id', self.ticket_id).execute()
        await interaction.channel.send('@everyone Admin: Escalation richiesta!')
        await interaction.response.send_message('Escalation inviata.', ephemeral=True)

# Inactivity task
@tasks.loop(minutes=30)
async def check_inactivity(bot, supabase: Client):
    config = {}  # Load from sync
    open_tickets = supabase.table('tickets').select('*').eq('status', 'open').execute().data
    for t in open_tickets:
        # Logic for last message time vs config
        # If overdue: solicit or close
        pass  # Full logic uses history check