-- ============================================================================
-- Header цэсний translation-уудын FK constraint-г ON DELETE CASCADE болгох
-- Энэ SQL-г PostgreSQL дээр нэг удаа ажиллуулна
-- ============================================================================

-- 1. header_menu_translation.menu → header_menu.id
ALTER TABLE header_menu_translation
  DROP CONSTRAINT IF EXISTS header_menu_translation_menu_fkey;
ALTER TABLE header_menu_translation
  ADD CONSTRAINT header_menu_translation_menu_fkey
  FOREIGN KEY (menu) REFERENCES header_menu(id) ON DELETE CASCADE;

-- 2. header_submenu_translation.submenu → header_submenu.id
ALTER TABLE header_submenu_translation
  DROP CONSTRAINT IF EXISTS header_submenu_translation_submenu_fkey;
ALTER TABLE header_submenu_translation
  ADD CONSTRAINT header_submenu_translation_submenu_fkey
  FOREIGN KEY (submenu) REFERENCES header_submenu(id) ON DELETE CASCADE;

-- 3. header_tertiary_menu_translation.tertiary_menu → header_tertiary_menu.id
ALTER TABLE header_tertiary_menu_translation
  DROP CONSTRAINT IF EXISTS header_tertiary_menu_translation_tertiary_menu_fkey;
ALTER TABLE header_tertiary_menu_translation
  ADD CONSTRAINT header_tertiary_menu_translation_tertiary_menu_fkey
  FOREIGN KEY (tertiary_menu) REFERENCES header_tertiary_menu(id) ON DELETE CASCADE;

-- 4. header_submenu.header_menu → header_menu.id (ensure CASCADE)
ALTER TABLE header_submenu
  DROP CONSTRAINT IF EXISTS header_submenu_header_menu_fkey;
ALTER TABLE header_submenu
  ADD CONSTRAINT header_submenu_header_menu_fkey
  FOREIGN KEY (header_menu) REFERENCES header_menu(id) ON DELETE CASCADE;

-- 5. header_tertiary_menu.header_submenu → header_submenu.id (ensure CASCADE)
ALTER TABLE header_tertiary_menu
  DROP CONSTRAINT IF EXISTS header_tertiary_menu_header_submenu_fkey;
ALTER TABLE header_tertiary_menu
  ADD CONSTRAINT header_tertiary_menu_header_submenu_fkey
  FOREIGN KEY (header_submenu) REFERENCES header_submenu(id) ON DELETE CASCADE;

-- 6. header_menu.header → header.id (ensure CASCADE)
ALTER TABLE header_menu
  DROP CONSTRAINT IF EXISTS header_menu_header_fkey;
ALTER TABLE header_menu
  ADD CONSTRAINT header_menu_header_fkey
  FOREIGN KEY (header) REFERENCES header(id) ON DELETE CASCADE;

-- ============================================================================
-- header_style хүснэгтэд дутуу багануудыг нэмэх
-- max_width болон logo_size нь шинээр нэмэгдсэн тул production DB-д байхгүй
-- IF NOT EXISTS ашиглан аль хэдийн байгаа бол давтахгүй
-- ============================================================================

-- 7. max_width багана нэмэх (header-ийн max-width тохиргоо)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'header_style' AND column_name = 'max_width'
    ) THEN
        ALTER TABLE header_style ADD COLUMN max_width TEXT DEFAULT '1240px';
        RAISE NOTICE 'max_width багана нэмэгдлээ';
    ELSE
        RAISE NOTICE 'max_width багана аль хэдийн байна';
    END IF;
END $$;

-- 8. logo_size багана нэмэх (логоны хэмжээ тохиргоо)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'header_style' AND column_name = 'logo_size'
    ) THEN
        ALTER TABLE header_style ADD COLUMN logo_size SMALLINT DEFAULT 44;
        RAISE NOTICE 'logo_size багана нэмэгдлээ';
    ELSE
        RAISE NOTICE 'logo_size багана аль хэдийн байна';
    END IF;
END $$;

-- ============================================================================
-- header_logo_history хүснэгт үүсгэх (логоны түүхийг DB-д хадгалах)
-- ============================================================================
CREATE TABLE IF NOT EXISTS header_logo_history (
    id BIGSERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
