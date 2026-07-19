-- Supabase Schema for S.T.A.F.F. Bot

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tables

-- Ticket Categories
CREATE TABLE ticket_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    emoji TEXT,
    description TEXT,
    channel_category_id TEXT, -- Discord category ID for tickets
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Modal Fields for categories
CREATE TABLE ticket_fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES ticket_categories(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('text', 'paragraph', 'number', 'select')), -- Discord modal field types
    placeholder TEXT,
    required BOOLEAN DEFAULT TRUE,
    options TEXT[], -- for select type
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ticket Logs
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    discord_ticket_channel_id TEXT UNIQUE,
    user_id TEXT NOT NULL, -- Discord user ID
    category_id UUID REFERENCES ticket_categories(id),
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'closed', 'escalated')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,
    closed_by TEXT -- Discord user ID
);

-- Ticket Messages for transcripts
CREATE TABLE ticket_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID REFERENCES tickets(id) ON DELETE CASCADE,
    discord_message_id TEXT,
    author_id TEXT NOT NULL,
    content TEXT,
    is_ai BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Staff Competences
CREATE TABLE staff_competences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL UNIQUE, -- Discord user ID
    category_id UUID REFERENCES ticket_categories(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Staff Stats
CREATE TABLE staff_stats (
    user_id TEXT PRIMARY KEY,
    tickets_handled INTEGER DEFAULT 0,
    first_response_avg_hours NUMERIC DEFAULT 0,
    response_time_total_hours NUMERIC DEFAULT 0,
    abandoned_tickets INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Custom Buttons
CREATE TABLE custom_buttons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    label TEXT NOT NULL,
    style TEXT DEFAULT 'PRIMARY' CHECK (style IN ('PRIMARY', 'SECONDARY', 'SUCCESS', 'DANGER', 'LINK')),
    action_type TEXT NOT NULL, -- e.g., 'close_ticket', 'reopen', etc.
    action_data JSONB,
    required_roles TEXT[],
    permissions TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Configuration (Regolamento, settings)
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default config
INSERT INTO config (key, value) VALUES 
('regolamento', '{"text": "Regolamento ticket qui..."}'::jsonb),
('inactivity', '{"solicit_hours": 24, "close_hours": 48}'::jsonb),
('welcome_message', '{"text": "Benvenuto! Assistenza Virtuale sta rispondendo..."}'::jsonb)
ON CONFLICT (key) DO NOTHING;

-- RLS Policies (Row Level Security)
ALTER TABLE ticket_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_fields ENABLE ROW LEVEL SECURITY;
-- etc for others, but for simplicity in setup

-- Functions for sync
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ticket_categories_timestamp BEFORE UPDATE ON ticket_categories
FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

-- Similar for others...