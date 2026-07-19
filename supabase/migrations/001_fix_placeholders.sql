-- Migration for config fixed message and inactivity fields
ALTER TABLE config ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

-- Default inactivity
INSERT INTO config (key, value) VALUES 
('inactivity', '{"solicit_hours": 24, "close_hours": 48, "staff_response_hours": 2}'::jsonb)
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;