-- Editorials (解説) - 問題の解説情報
CREATE TABLE IF NOT EXISTS public.editorials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID NOT NULL REFERENCES public.problems(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(problem_id)
);

-- Editorial Contents (多言語対応の解説コンテンツ)
CREATE TABLE IF NOT EXISTS public.editorial_contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    editorial_id UUID NOT NULL REFERENCES public.editorials(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL DEFAULT 'ja',
    md_content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(editorial_id, language)
);


-- =====================================================
-- Performance
-- =====================================================

-- Editorials indexes
CREATE INDEX IF NOT EXISTS idx_editorials_problem_id
ON public.editorials(problem_id);

CREATE INDEX IF NOT EXISTS idx_editorials_created_at
ON public.editorials(created_at DESC);


-- =====================================================
-- Core Domain Row Level Security (RLS)
-- =====================================================

-- Enable RLS on all core tables
ALTER TABLE public.editorials ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.editorial_contents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "published_editorials_readable_by_all" ON public.editorials 
FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM public.problems 
        WHERE problems.id = editorials.problem_id 
        AND problems.is_published = true
    )
);

CREATE POLICY "published_editorial_contents_readable_by_all" ON public.editorial_contents 
FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM public.editorials e
        JOIN public.problems p ON p.id = e.problem_id
        WHERE e.id = editorial_contents.editorial_id 
        AND p.is_published = true
    )
);



-- =====================================================
-- Triggers for updated_at timestamps
-- =====================================================
CREATE TRIGGER handle_updated_at_editorials 
BEFORE UPDATE ON public.editorials 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_editorial_contents 
BEFORE UPDATE ON public.editorial_contents 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);
