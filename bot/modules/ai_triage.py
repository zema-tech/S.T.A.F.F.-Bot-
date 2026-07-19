import discord
from supabase import Client
from groq import Groq
import os

groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

async def send_ai_triage(channel: discord.TextChannel, category: str, supabase: Client):
    config = {}  # from sync
    welcome = 'Benvenuto nel ticket! Assistenza Virtuale sta analizzando...'
    
    # Simple Groq call
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": f"Rispondi come supporto per categoria {category}. Sii utile e breve."},
                      {"role": "user", "content": "Fornisci aiuto iniziale per ticket."}],
            model="llama3-8b-8192",
        )
        response = chat_completion.choices[0].message.content
    except:
        response = 'Non riesco a rispondere ora. Staff umano arriverà presto.'
    
    await channel.send(f'**🤖 Assistenza Virtuale:** {response}')
    # Save message to ticket_messages
    # ...