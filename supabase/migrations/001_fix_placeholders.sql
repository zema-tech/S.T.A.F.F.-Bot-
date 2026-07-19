-- Update migration for fixed_message
INSERT INTO config (key, value) VALUES 
('fixed_message', '{"channel_id": null, "message_id": null}'::jsonb)
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;