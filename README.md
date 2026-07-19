# S.T.A.F.F. Bot - Support Ticket And Filtering For Fans

Sistema completo per gestione ticket Discord + Pannello Web per Red Empire.

## Struttura Progetto

```
staff-bot/
├── bot/                # Discord Bot (Python)
├── web/                # Pannello React
├── supabase/           # Schema DB
└── README.md
```

## Setup Supabase

1. Crea progetto Supabase
2. Esegui `supabase/schema.sql`
3. Aggiungi chiavi in .env

## Bot Setup

```bash
cd bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configura DISCORD_TOKEN, SUPABASE_*, GROQ_API_KEY
python main.py
```

## Web Panel Setup

Vedi web/README.md

## Comandi Slash Disponibili

- /ticket-categoria-aggiungi
- /ticket-regolamento-set
- etc. (vedi admin_commands.py)

## Deploy

- Bot: Railway
- Web: Netlify