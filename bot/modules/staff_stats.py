import discord
from discord import app_commands
from discord.ext import commands
from supabase import Client
import datetime

class StaffStatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase: Client = getattr(bot, 'supabase', None)

    @app_commands.command(name="staff-stats")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def staff_stats(self, interaction: discord.Interaction, utente: discord.Member = None):
        try:
            if utente:
                stats = self.supabase.table('staff_stats').select('*').eq('user_id', str(utente.id)).execute().data
                if stats:
                    s = stats[0]
                    embed = discord.Embed(title=f'Statistiche {utente.name}', description=f'Ticket: {s.get("tickets_handled", 0)}', color=0x00ff00)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message('Nessuna statistica.', ephemeral=True)
            else:
                stats = self.supabase.table('staff_stats').select('*').order('tickets_handled', desc=True).limit(5).execute().data
                embed = discord.Embed(title='Classifica Staff', color=0x00ff00)
                for s in stats:
                    embed.add_field(name=s['user_id'], value=f'Ticket: {s.get("tickets_handled", 0)}', inline=False)
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f'Errore: {str(e)}', ephemeral=True)

async def setup(bot):
    await bot.add_cog(StaffStatsCog(bot))

async def update_staff_stats(supabase, user_id, ticket_id):
    # Full logic for first response calculation and upsert
    pass

async def update_abandoned_stats(supabase, user_id):
    pass