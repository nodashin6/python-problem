-- User Stats (ユーザー統計) - パフォーマンス統計
CREATE TABLE IF NOT EXISTS public.user_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE UNIQUE,
    problems_solved INTEGER DEFAULT 0,
    submissions_count INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    rank_score DECIMAL(10, 2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Problem Status (ユーザーの問題解決状態) - 問題ごとの進捗管理
CREATE TABLE IF NOT EXISTS public.user_problem_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    problem_id UUID NOT NULL REFERENCES public.problems(id) ON DELETE CASCADE,
    solved BOOLEAN DEFAULT FALSE,
    solved_at TIMESTAMP WITH TIME ZONE,
    submission_count INTEGER DEFAULT 0,
    last_submission_id UUID,
    -- 後でjudge domainのsubmissionsテーブルと関連付け
    best_score DECIMAL(5, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, problem_id)
);

-- =====================================================
-- Performance
-- =====================================================
-- User Problem Status indexes
CREATE INDEX IF NOT EXISTS idx_user_problem_status_user_solved ON public.user_problem_status(user_id, solved);

CREATE INDEX IF NOT EXISTS idx_user_problem_status_problem ON public.user_problem_status(problem_id, solved);

CREATE INDEX IF NOT EXISTS idx_user_problem_status_solved_at ON public.user_problem_status(solved_at DESC)
WHERE
    solved = true;

-- =====================================================
-- Core Domain Row Level Security (RLS)
-- =====================================================
ALTER TABLE
    public.user_stats ENABLE ROW LEVEL SECURITY;

ALTER TABLE
    public.user_problem_status ENABLE ROW LEVEL SECURITY;

-- Allow all access for local testing (RLS disabled for local development)
-- Note: In production, these should be replaced with proper auth checks
CREATE POLICY "user_stats_all_access" ON public.user_stats FOR ALL USING (true);

CREATE POLICY "user_problem_status_all_access" ON public.user_problem_status FOR ALL USING (true);

-- =====================================================
-- Triggers for updated_at timestamps
-- =====================================================
CREATE TRIGGER handle_updated_at_user_stats BEFORE
UPDATE
    ON public.user_stats FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_user_problem_status BEFORE
UPDATE
    ON public.user_problem_status FOR EACH ROW EXECUTE PROCEDURE moddatetime (
        updated_at
    );

-- =====================================================
-- Foreign Key Constraints (After Judge Domain Tables)
-- =====================================================
-- Update user_problem_status to reference submissions
-- (この時点でsubmissionsテーブルが存在するため、外部キー制約を追加)
ALTER TABLE public.user_problem_status
ADD CONSTRAINT user_problem_status_last_submission_fkey 
FOREIGN KEY (last_submission_id) REFERENCES public.submissions(id) ON DELETE SET NULL;