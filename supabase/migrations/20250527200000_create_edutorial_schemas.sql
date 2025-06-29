-- edutorial_headers (解説) - 問題の解説情報
CREATE TABLE IF NOT EXISTS public.edutorial_headers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID NOT NULL REFERENCES public.problem_headers(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(problem_id)
);

-- edutorial Contents (多言語対応の解説コンテンツ)
CREATE TABLE IF NOT EXISTS public.edutorial_contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    edutorial_id UUID NOT NULL REFERENCES public.edutorial_headers(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL DEFAULT 'ja',
    md_content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(edutorial_id, language)
);


-- =====================================================
-- Performance
-- =====================================================

-- edutorial_headers indexes
CREATE INDEX IF NOT EXISTS idx_edutorial_headers_problem_id
ON public.edutorial_headers(problem_id);

CREATE INDEX IF NOT EXISTS idx_edutorial_headers_created_at
ON public.edutorial_headers(created_at DESC);


-- =====================================================
-- Core Domain Row Level Security (RLS)
-- =====================================================

-- Enable RLS on all core tables
ALTER TABLE public.edutorial_headers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.edutorial_contents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "published_edutorial_headers_readable_by_all" ON public.edutorial_headers 
FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM public.problem_headers 
        WHERE problem_headers.id = edutorial_headers.problem_id 
        AND problem_headers.published_at IS NOT NULL
    )
);

CREATE POLICY "published_edutorial_contents_readable_by_all" ON public.edutorial_contents 
FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM public.edutorial_headers e
        JOIN public.problem_headers p ON p.id = e.problem_id
        WHERE e.id = edutorial_contents.edutorial_id 
        AND p.published_at IS NOT NULL
    )
);



-- =====================================================
-- Triggers for updated_at timestamps
-- =====================================================
CREATE TRIGGER handle_updated_at_edutorial_headers 
BEFORE UPDATE ON public.edutorial_headers 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_edutorial_contents 
BEFORE UPDATE ON public.edutorial_contents 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);
