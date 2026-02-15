-- Add image and image_position columns to about_page_section table
ALTER TABLE about_page_section ADD COLUMN IF NOT EXISTS image TEXT DEFAULT '';
ALTER TABLE about_page_section ADD COLUMN IF NOT EXISTS image_position TEXT DEFAULT 'right';
