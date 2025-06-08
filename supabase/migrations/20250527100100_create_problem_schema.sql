-- =====================================================
-- Problem Management Tables (Core Domain)
-- =====================================================

-- Problems (問題) - 個別の問題定義
CREATE TABLE IF NOT EXISTS public.problems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES public.books(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    published_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Problem Contents (多言語対応の問題コンテンツ)
CREATE TABLE IF NOT EXISTS public.problem_contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID NOT NULL REFERENCES public.problems(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL DEFAULT 'ja',
    md_content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(problem_id, language)
);

-- =====================================================
-- Performance
-- =====================================================
-- Problems indexes
CREATE INDEX IF NOT EXISTS idx_problems_book_id ON public.problems(book_id);

CREATE INDEX IF NOT EXISTS idx_problems_published_at ON public.problems(published_at);

-- Problem Contents indexes
CREATE INDEX IF NOT EXISTS idx_problem_contents_problem_language ON public.problem_contents(problem_id, language);

-- =====================================================
-- Core Domain Row Level Security (RLS)
-- =====================================================
-- Enable RLS on all core tables
ALTER TABLE
    public.problems ENABLE ROW LEVEL SECURITY;

ALTER TABLE
    public.problem_contents ENABLE ROW LEVEL SECURITY;

-- Public read access for published content
CREATE POLICY "published_books_readable_by_all" ON public.books FOR
SELECT
    USING (is_published = true);

CREATE POLICY "published_problems_readable_by_all" ON public.problems FOR
SELECT
    USING (is_published = true);

CREATE POLICY "published_problem_contents_readable_by_all" ON public.problem_contents FOR
SELECT
    USING (
        EXISTS (
            SELECT
                1
            FROM
                public.problems
            WHERE
                problems.id = problem_contents.problem_id
                AND problems.is_published = true
        )
    );

CREATE POLICY "problems_all_access" ON public.problems FOR ALL USING (true);

-- =====================================================
-- Triggers for updated_at timestamps
-- =====================================================
CREATE TRIGGER handle_updated_at_problems BEFORE
UPDATE
    ON public.problems FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_problem_contents BEFORE
UPDATE
    ON public.problem_contents FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);