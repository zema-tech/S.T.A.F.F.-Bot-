import discord
from discord.ext import tasks
from supabase import Client
import os
import datetime

async def assign_staff(channel: discord.TextChannel, category_id, supabase: Client):
    resp = supabase.table('staff_competences').select('user_id').eq('category_id', category_id).execute()
    staff_ids = [row['user_id'] for row in resp.data]
    if staff_ids:
        mentions = ' '.join([f'<@{uid}>' for uid in staff_ids])
        await channel.send(f'**Staff assegnato per questa categoria:** {mentions}')
        for uid in staff_ids:
            member = channel.guild.get_member(int(uid))
            if member:
                await channel.set_permissions(member, read_messages=True, send_messages=True)

@tasks.loop(minutes=15)
async def check_escalation(bot, supabase: Client):
    admin_role_id = os.getenv('ADMIN_ROLE_ID')
    inactivity = supabase.table('config').select('value').eq('key', 'inactivity').execute().data[0]['value']
    # Logic to check assigned staff response time vs staff_response_hours
    # For simplicity, check ticket age
    open_tickets = supabase.table('tickets').select('*').eq('status', 'open').execute().data
    for t in open_tickets:
        created = datetime.datetime.fromisoformat(t['created_at'].replace('Z', '+00:00'))
        if (datetime.datetime.now(datetime.timezone.utc) - created).total_seconds() / 3600 > inactivity.get('staff_response_hours', 2):
            channel = bot.get_channel(int(t['discord_ticket_channel_id']))
            if channel:
                await channel.send(f'<@&{admin_role_id}> Escalation automatica: nessun staff ha risposto in tempo!')
                supabase.table('tickets').update({'status': 'escalated'}).eq('id', t['id']).execute()