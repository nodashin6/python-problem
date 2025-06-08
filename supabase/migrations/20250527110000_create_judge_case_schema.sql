-- =====================================================
-- Test Case Management Tables (Core Domain)
-- =====================================================
-- Case Files (テストケースファイル) - 入出力ファイルの管理
CREATE TABLE IF NOT EXISTS public.case_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Judge Cases (テストケース定義) - 問題のテストケース
-- 注意: "test_cases"ではなく"judge_cases"を使用 (pytest との競合回避) 
CREATE TABLE IF NOT EXISTS public.judge_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID NOT NULL REFERENCES public.problems(id) ON DELETE CASCADE,
    input_id UUID NOT NULL REFERENCES public.case_files(id) ON DELETE CASCADE,
    output_id UUID NOT NULL REFERENCES public.case_files(id) ON DELETE CASCADE,
    is_sample BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    judge_case_type VARCHAR(20) DEFAULT 'normal' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add enum constraint for judge_case_type
ALTER TABLE
    public.judge_cases
ADD
    CONSTRAINT judge_cases_type_check CHECK (
        judge_case_type IN ('sample', 'normal', 'edge', 'stress')
    );

-- =====================================================
-- Performance
-- =====================================================
-- Judge Cases indexes
CREATE INDEX IF NOT EXISTS idx_judge_cases_problem_id ON public.judge_cases(problem_id);

CREATE INDEX IF NOT EXISTS idx_judge_cases_display_order ON public.judge_cases(problem_id, display_order);

CREATE INDEX IF NOT EXISTS idx_judge_cases_sample ON public.judge_cases(problem_id, is_sample);

-- =====================================================
-- Core Domain Row Level Security (RLS)
-- =====================================================
-- Enable RLS on all core tables
ALTER TABLE
    public.case_files ENABLE ROW LEVEL SECURITY;

ALTER TABLE
    public.judge_cases ENABLE ROW LEVEL SECURITY;

-- Judge cases readable by all (no auth restriction for local testing)
CREATE POLICY "judge_cases_readable_by_all" ON public.judge_cases FOR
SELECT
    USING (
        EXISTS (
            SELECT
                1
            FROM
                public.problems
            WHERE
                problems.id = judge_cases.problem_id
                AND problems.is_published = true
        )
    );

-- =====================================================
-- Triggers for updated_at timestamps
-- =====================================================
CREATE TRIGGER handle_updated_at_case_files BEFORE
UPDATE
    ON public.case_files FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_judge_cases BEFORE
UPDATE
    ON public.judge_cases FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);