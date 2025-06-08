-- Books (問題集) - 問題をグループ化するコレクション
CREATE TABLE IF NOT EXISTS public.books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    author_id UUID NULL REFERENCES public.users(id) ON DELETE SET NULL,
    published_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- Performance
-- =====================================================
-- Books indexes
CREATE INDEX IF NOT EXISTS idx_books_published_at ON public.books (published_at);

CREATE INDEX IF NOT EXISTS idx_books_author_id ON public.books (author_id);

-- =====================================================
-- Core Domain Row Level Security (RLS)
-- =====================================================
-- Enable RLS on all core tables
ALTER TABLE public.books ENABLE ROW LEVEL SECURITY;

CREATE POLICY "books_all_access" ON public.books FOR ALL USING (true);

-- =====================================================
-- Triggers for updated_at timestamps
-- =====================================================
CREATE TRIGGER handle_updated_at_books BEFORE
UPDATE ON public.books FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);