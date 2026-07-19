import discord
from supabase import Client

async def assign_staff(channel: discord.TextChannel, category_id, supabase: Client):
    resp = supabase.table('staff_competences').select('user_id').eq('category_id', category_id).execute()
    staff_ids = [row['user_id'] for row in resp.data]
    if staff_ids:
        mentions = ' '.join([f'<@{uid}>' for uid in staff_ids[:5]])
        await channel.send(f'**Staff assegnato:** {mentions} - Pronti per assistere!')
        # Update permissions
        for uid in staff_ids:
            member = channel.guild.get_member(int(uid))
            if member:
                await channel.set_permissions(member, read_messages=True, send_messages=True)

async def check_escalation(channel, supabase: Client):
    # Timer logic or task-based
    config = supabase.table('config').select('value').eq('key', 'inactivity').execute().data[0]['value']
    # If no response: notify admin role
    await channel.send('<@&ADMIN_ROLE_ID> Nessuna risposta staff - Escalation!')