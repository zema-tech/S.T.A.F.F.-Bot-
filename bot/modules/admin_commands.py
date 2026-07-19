import discord
from discord import app_commands
from discord.ext import commands
from supabase import Client
from .ticket_creation import TicketCategorySelect
import os

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase: Client = getattr(bot, 'supabase', None)

    @app_commands.command(name="ticket-setup")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticket_setup(self, interaction: discord.Interaction):
        try:
            channel = interaction.channel
            regolamento_resp = self.supabase.table('config').select('value').eq('key', 'regolamento').execute()
            regolamento = regolamento_resp.data[0]['value']['text']
            view = discord.ui.View()
            view.add_item(TicketCategorySelect(self.supabase))
            msg = await channel.send(regolamento, view=view)
            fixed_data = {'channel_id': str(channel.id), 'message_id': str(msg.id)}
            self.supabase.table('config').upsert({'key': 'fixed_message', 'value': fixed_data}).execute()
            embed = discord.Embed(title='✅ Setup completato', description='Messaggio fisso pubblicato e salvato in config.', color=0x00ff00)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Errore: {str(e)}', ephemeral=True)

    @app_commands.command(name="ticket-categoria-aggiungi")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticket_categoria_aggiungi(self, interaction: discord.Interaction, nome: str, emoji: str = None, descrizione: str = None, canale_categoria: discord.CategoryChannel = None):
        try:
            data = {'name': nome, 'emoji': emoji, 'description': descrizione, 'channel_category_id': str(canale_categoria.id) if canale_categoria else None}
            self.supabase.table('ticket_categories').upsert(data).execute()
            embed = discord.Embed(title='✅ Categoria aggiunta', description=f'Nome: {nome}', color=0x00ff00)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Errore: {str(e)}', ephemeral=True)

    @app_commands.command(name="ticket-categoria-rimuovi")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticket_categoria_rimuovi(self, interaction: discord.Interaction, nome: str):
        try:
            resp = self.supabase.table('ticket_categories').delete().eq('name', nome).execute()
            if resp.data:
                await interaction.response.send_message(f'✅ Categoria {nome} rimossa.', ephemeral=True)
            else:
                await interaction.response.send_message('❌ Categoria non trovata.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Errore: {str(e)}', ephemeral=True)

    @app_commands.command(name="ticket-campo-aggiungi")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticket_campo_aggiungi(self, interaction: discord.Interaction, categoria: str, label: str, tipo: str = 'text', obbligatorio: bool = True):
        try:
            cat_resp = self.supabase.table('ticket_categories').select('id').eq('name', categoria).execute()
            if not cat_resp.data:
                await interaction.response.send_message('❌ Categoria non trovata.', ephemeral=True)
                return
            cat_id = cat_resp.data[0]['id']
            fields_count = len(self.supabase.table('ticket_fields').select('id').eq('category_id', cat_id).execute().data)
            if fields_count >= 5:
                await interaction.response.send_message('❌ Limite di 5 campi raggiunto.', ephemeral=True)
                return
            data = {'category_id': cat_id, 'label': label, 'type': tipo, 'required': obbligatorio, 'position': fields_count + 1}
            self.supabase.table('ticket_fields').insert(data).execute()
            await interaction.response.send_message(f'✅ Campo {label} aggiunto.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Errore: {str(e)}', ephemeral=True)

    @app_commands.command(name="ticket-regolamento-set")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticket_regolamento_set(self, interaction: discord.Interaction):
        class RegModal(discord.ui.Modal):
            testo = discord.ui.TextInput(label='Nuovo Regolamento', style=discord.TextStyle.paragraph, max_length=2000)
            async def on_submit(self, modal_inter: discord.Interaction):
                new_value = {'text': self.testo.value}
                self.supabase.table('config').upsert({'key': 'regolamento', 'value': new_value}).execute()  # self from outer?
                await modal_inter.response.send_message('✅ Regolamento aggiornato. Sync lo propagherà.', ephemeral=True)
        await interaction.response.send_modal(RegModal(title='Imposta Regolamento'))

    @app_commands.command(name="staff-competenza-set")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def staff_competenza_set(self, interaction: discord.Interaction, utente: discord.Member, categoria: str):
        try:
            cat_resp = self.supabase.table('ticket_categories').select('id').eq('name', categoria).execute()
            if not cat_resp.data:
                await interaction.response.send_message('❌ Categoria non trovata.', ephemeral=True)
                return
            data = {'user_id': str(utente.id), 'category_id': cat_resp.data[0]['id']}
            self.supabase.table('staff_competences').upsert(data).execute()
            await interaction.response.send_message(f'✅ Competenza assegnata a {utente.name}.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Errore: {str(e)}', ephemeral=True)

    @app_commands.command(name="ticket-inattivita-set")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticket_inattivita_set(self, interaction: discord.Interaction, ore_sollecito: int, ore_chiusura: int):
        try:
            inactivity = self.supabase.table('config').select('value').eq('key', 'inactivity').execute().data[0]['value']
            inactivity['solicit_hours'] = ore_sollecito
            inactivity['close_hours'] = ore_chiusura
            self.supabase.table('config').upsert({'key': 'inactivity', 'value': inactivity}).execute()
            await interaction.response.send_message(f'✅ Inattività aggiornata: sollecito {ore_sollecito}h, chiusura {ore_chiusura}h.', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Errore: {str(e)}', ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))