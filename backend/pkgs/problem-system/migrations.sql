-- Books (問題集) - 問題をグループ化するコレクション
CREATE TABLE IF NOT EXISTS public.books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    author_id UUID NULL REFERENCES public.users(id) ON DELETE SET NULL,
    published_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
    archived_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
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




-- =====================================================
-- Problem Management Tables (Core Domain)
-- =====================================================

-- Problem Headers (問題ヘッダー) - 個別の問題のメタデータ
CREATE TABLE IF NOT EXISTS public.problem_headers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES public.books(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    published_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
    archived_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Problem Contents (多言語対応の問題コンテンツ)
CREATE TABLE IF NOT EXISTS public.problem_contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID NOT NULL REFERENCES public.problem_headers(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL DEFAULT 'ja',
    markdown TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(problem_id, language)
);

-- =====================================================
-- Performance
-- =====================================================
-- Problem Headers indexes
CREATE INDEX IF NOT EXISTS idx_problem_headers_book_id ON public.problem_headers(book_id);

CREATE INDEX IF NOT EXISTS idx_problem_headers_published_at ON public.problem_headers(published_at);

-- Problem Contents indexes
CREATE INDEX IF NOT EXISTS idx_problem_contents_problem_language ON public.problem_contents(problem_id, language);

-- =====================================================
-- Core Domain Row Level Security (RLS)
-- =====================================================
-- Enable RLS on all core tables
ALTER TABLE
    public.problem_headers ENABLE ROW LEVEL SECURITY;

ALTER TABLE
    public.problem_contents ENABLE ROW LEVEL SECURITY;

-- Public read access for published content
CREATE POLICY "published_books_readable_by_all" ON public.books FOR
SELECT
    USING (published_at IS NOT NULL);

CREATE POLICY "published_problem_headers_readable_by_all" ON public.problem_headers FOR
SELECT
    USING (published_at IS NOT NULL);

CREATE POLICY "published_problem_contents_readable_by_all" ON public.problem_contents FOR
SELECT
    USING (
        EXISTS (
            SELECT
                1
            FROM
                public.problem_headers
            WHERE
                problem_headers.id = problem_contents.problem_id
                AND problem_headers.published_at IS NOT NULL
        )
    );

CREATE POLICY "problem_headers_all_access" ON public.problem_headers FOR ALL USING (true);

-- =====================================================
-- Triggers for updated_at timestamps
-- =====================================================
CREATE TRIGGER handle_updated_at_problem_headers BEFORE
UPDATE
    ON public.problem_headers FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_problem_contents BEFORE
UPDATE
    ON public.problem_contents FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);