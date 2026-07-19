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
        await close_ticket(interaction.channel, self.ticket_id, self.supabase, closed_by=str(interaction.user.id))
        await interaction.response.send_message('Ticket chiuso e trascrizione salvata.', ephemeral=True)

    @discord.ui.button(label='Riapri', style=discord.ButtonStyle.success, custom_id='reopen_ticket')
    async def reopen(self, interaction: discord.Interaction, button: Button):
        self.supabase.table('tickets').update({'status': 'open'}).eq('id', self.ticket_id).execute()
        await interaction.response.send_message('Ticket riaperto.', ephemeral=True)

    @discord.ui.button(label='Escalation', style=discord.ButtonStyle.primary, custom_id='escalate_ticket')
    async def escalate(self, interaction: discord.Interaction, button: Button):
        self.supabase.table('tickets').update({'status': 'escalated'}).eq('id', self.ticket_id).execute()
        await interaction.channel.send('@everyone Admin: Escalation richiesta!')
        await interaction.response.send_message('Escalation inviata.', ephemeral=True)

async def close_ticket(channel, ticket_id, supabase, closed_by='sistema-inattività'):
    # Save transcript
    messages = []
    async for msg in channel.history(limit=None):
        messages.append({
            'ticket_id': ticket_id,
            'discord_message_id': str(msg.id),
            'author_id': str(msg.author.id),
            'content': msg.content,
            'is_ai': msg.author.bot
        })
    if messages:
        supabase.table('ticket_messages').insert(messages).execute()
    # Update ticket
    supabase.table('tickets').update({
        'status': 'closed',
        'closed_at': datetime.datetime.now().isoformat(),
        'closed_by': closed_by
    }).eq('id', ticket_id).execute()
    await channel.delete()

# Inactivity task
@tasks.loop(minutes=30)
async def check_inactivity(bot, supabase: Client):
    inactivity_resp = supabase.table('config').select('value').eq('key', 'inactivity').execute()
    inactivity = inactivity_resp.data[0]['value'] if inactivity_resp.data else {'solicit_hours': 24, 'close_hours': 48}
    solicit_hours = inactivity.get('solicit_hours', 24)
    close_hours = inactivity.get('close_hours', 48)

    open_tickets = supabase.table('tickets').select('*').eq('status', 'open').execute().data
    for t in open_tickets:
        channel = bot.get_channel(int(t.get('discord_ticket_channel_id', 0)))
        if not channel:
            continue
        try:
            last_msg = [msg async for msg in channel.history(limit=1)][0]
            hours_since = (datetime.datetime.now(datetime.timezone.utc) - last_msg.created_at).total_seconds() / 3600

            if hours_since > solicit_hours and not t.get('solicited_at'):
                await channel.send('Sei ancora presente? Il ticket verrà chiuso automaticamente se non rispondi.')
                supabase.table('tickets').update({'solicited_at': datetime.datetime.now().isoformat()}).eq('id', t['id']).execute()

            if hours_since > close_hours:
                await close_ticket(channel, t['id'], supabase, closed_by='sistema-inattività')
        except:
            continue