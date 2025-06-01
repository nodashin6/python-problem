-- =====================================================
-- Judge Domain Schema Migration
-- Version: 20250527110000
-- Date: 2025-05-27
-- Description: Judge domain tables for code execution and evaluation
-- =====================================================

-- =====================================================
-- Judge Domain Dependencies Check
-- =====================================================

-- Ensure core domain tables exist before creating judge domain
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users' AND table_schema = 'public') THEN
        RAISE EXCEPTION 'Core domain must be migrated first. users table not found.';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'problems' AND table_schema = 'public') THEN
        RAISE EXCEPTION 'Core domain must be migrated first. problems table not found.';
    END IF;
END $$;

-- =====================================================
-- Submission Management Tables (Judge Domain)
-- =====================================================

-- Submissions (ユーザー提出) - コード提出の管理
CREATE TABLE IF NOT EXISTS public.submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID NOT NULL REFERENCES public.problems(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    code TEXT NOT NULL,
    language VARCHAR(20) NOT NULL DEFAULT 'python',
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    score DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add enum constraints for submissions
ALTER TABLE public.submissions 
ADD CONSTRAINT submissions_status_check 
CHECK (status IN ('pending', 'judging', 'completed', 'error'));

ALTER TABLE public.submissions 
ADD CONSTRAINT submissions_language_check 
CHECK (language IN ('python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'go', 'rust'));

-- =====================================================
-- Judge Execution Tables (Judge Domain)
-- =====================================================

-- Judge Processes (ジャッジプロセス) - 実行プロセスの管理
CREATE TABLE IF NOT EXISTS public.judge_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID NOT NULL REFERENCES public.submissions(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    result VARCHAR(20),
    execution_time_ms INTEGER,
    memory_usage_kb INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add enum constraint for judge process status
ALTER TABLE public.judge_processes 
ADD CONSTRAINT judge_processes_status_check 
CHECK (status IN ('pending', 'running', 'succeeded', 'failed', 'error', 'other'));

-- Judge Case Results (テストケース結果) - 個別テストケースの実行結果
CREATE TABLE IF NOT EXISTS public.judge_case_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    judge_process_id UUID NOT NULL REFERENCES public.judge_processes(id) ON DELETE CASCADE,
    judge_case_id UUID NOT NULL REFERENCES public.judge_cases(id) ON DELETE CASCADE,
    status VARCHAR(10) NOT NULL,
    result VARCHAR(10) NOT NULL,
    error TEXT,
    warning TEXT,
    processing_time_ms INTEGER,
    memory_usage_kb INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add enum constraint for judge case result status
ALTER TABLE public.judge_case_results 
ADD CONSTRAINT judge_case_results_status_check 
CHECK (status IN ('AC', 'WA', 'RE', 'CE', 'TLE', 'MLE', 'IE'));

-- Judge Case Result Metadata (詳細メタデータ) - 実行結果の詳細情報
CREATE TABLE IF NOT EXISTS public.judge_case_result_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    judge_case_result_id UUID NOT NULL REFERENCES public.judge_case_results(id) ON DELETE CASCADE UNIQUE,
    memory_used_kb INTEGER,
    time_used_ms INTEGER,
    compile_error TEXT,
    runtime_error TEXT,
    output TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- Judge Domain Foreign Key Updates
-- =====================================================

-- Update user_problem_status to reference submissions
-- (この時点でsubmissionsテーブルが存在するため、外部キー制約を追加)
ALTER TABLE public.user_problem_status 
ADD CONSTRAINT user_problem_status_last_submission_fkey 
FOREIGN KEY (last_submission_id) REFERENCES public.submissions(id) ON DELETE SET NULL;

-- =====================================================
-- Judge Domain Indexes for Performance
-- =====================================================

-- Submissions indexes
CREATE INDEX IF NOT EXISTS idx_submissions_user_id 
ON public.submissions(user_id);

CREATE INDEX IF NOT EXISTS idx_submissions_problem_id 
ON public.submissions(problem_id);

CREATE INDEX IF NOT EXISTS idx_submissions_status 
ON public.submissions(status);

CREATE INDEX IF NOT EXISTS idx_submissions_created_at 
ON public.submissions(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_submissions_user_problem 
ON public.submissions(user_id, problem_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_submissions_language 
ON public.submissions(language);

-- Judge Processes indexes
CREATE INDEX IF NOT EXISTS idx_judge_processes_submission_id 
ON public.judge_processes(submission_id);

CREATE INDEX IF NOT EXISTS idx_judge_processes_status 
ON public.judge_processes(status);

CREATE INDEX IF NOT EXISTS idx_judge_processes_created_at 
ON public.judge_processes(created_at DESC);

-- Judge Case Results indexes
CREATE INDEX IF NOT EXISTS idx_judge_case_results_process_id 
ON public.judge_case_results(judge_process_id);

CREATE INDEX IF NOT EXISTS idx_judge_case_results_case_id 
ON public.judge_case_results(judge_case_id);

CREATE INDEX IF NOT EXISTS idx_judge_case_results_status 
ON public.judge_case_results(status);

-- Judge Case Result Metadata indexes
CREATE INDEX IF NOT EXISTS idx_judge_case_result_metadata_result_id 
ON public.judge_case_result_metadata(judge_case_result_id);

-- =====================================================
-- Judge Domain Row Level Security (RLS)
-- =====================================================

-- Enable RLS on all judge tables
ALTER TABLE public.submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.judge_processes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.judge_case_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.judge_case_result_metadata ENABLE ROW LEVEL SECURITY;

-- Allow all access for local testing (RLS disabled for local development)
-- Note: In production, these should be replaced with proper auth checks
CREATE POLICY "submissions_all_access" ON public.submissions FOR ALL USING (true);
CREATE POLICY "judge_processes_all_access" ON public.judge_processes FOR ALL USING (true);
CREATE POLICY "judge_case_results_all_access" ON public.judge_case_results FOR ALL USING (true);
CREATE POLICY "judge_case_result_metadata_all_access" ON public.judge_case_result_metadata FOR ALL USING (true);

-- System service policies for judge execution
-- (Note: これらは実際のサービス実装時にサービスアカウント用に調整が必要)
CREATE POLICY "judge_system_can_update_processes" ON public.judge_processes 
FOR UPDATE USING (
    -- TODO: 実際のジャッジサービスアカウントのIDに置き換える
    true -- 一時的に全て許可、後でサービスアカウント制限を追加
);

CREATE POLICY "judge_system_can_insert_results" ON public.judge_case_results 
FOR INSERT WITH CHECK (
    -- TODO: 実際のジャッジサービスアカウントのIDに置き換える
    true -- 一時的に全て許可、後でサービスアカウント制限を追加
);

-- =====================================================
-- Judge Domain Triggers for updated_at timestamps
-- =====================================================

CREATE TRIGGER handle_updated_at_submissions 
BEFORE UPDATE ON public.submissions 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_judge_processes 
BEFORE UPDATE ON public.judge_processes 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_judge_case_results 
BEFORE UPDATE ON public.judge_case_results 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_judge_case_result_metadata 
BEFORE UPDATE ON public.judge_case_result_metadata 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

-- =====================================================
-- Judge Domain Business Logic Triggers
-- =====================================================

-- Trigger to update user_problem_status when submission is completed
CREATE OR REPLACE FUNCTION update_user_problem_status_on_submission()
RETURNS TRIGGER AS $$
BEGIN
    -- Update submission count
    INSERT INTO public.user_problem_status (user_id, problem_id, submission_count, last_submission_id)
    VALUES (NEW.user_id, NEW.problem_id, 1, NEW.id)
    ON CONFLICT (user_id, problem_id) 
    DO UPDATE SET 
        submission_count = user_problem_status.submission_count + 1,
        last_submission_id = NEW.id,
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_problem_status_trigger
AFTER INSERT ON public.submissions
FOR EACH ROW EXECUTE FUNCTION update_user_problem_status_on_submission();

-- Trigger to update user stats and problem status when judge process completes
CREATE OR REPLACE FUNCTION update_user_stats_on_judge_completion()
RETURNS TRIGGER AS $$
DECLARE
    submission_record public.submissions%ROWTYPE;
    is_solved BOOLEAN := FALSE;
BEGIN
    -- Only process when status changes to 'succeeded'
    IF NEW.status = 'succeeded' AND (OLD.status IS NULL OR OLD.status != 'succeeded') THEN
        -- Get submission info
        SELECT * INTO submission_record 
        FROM public.submissions 
        WHERE id = NEW.submission_id;
        
        -- Check if this submission solved the problem (assuming score >= 100.0 means solved)
        IF NEW.result = 'AC' OR (submission_record.score IS NOT NULL AND submission_record.score >= 100.0) THEN
            is_solved := TRUE;
        END IF;
        
        -- Update user_problem_status if solved
        IF is_solved THEN
            UPDATE public.user_problem_status 
            SET 
                solved = TRUE,
                solved_at = NOW(),
                best_score = GREATEST(COALESCE(best_score, 0), COALESCE(submission_record.score, 0)),
                updated_at = NOW()
            WHERE user_id = submission_record.user_id 
            AND problem_id = submission_record.problem_id 
            AND solved = FALSE; -- Only update if not already solved
            
            -- Update user_stats if this is a newly solved problem
            IF FOUND THEN
                UPDATE public.user_stats 
                SET 
                    problems_solved = problems_solved + 1,
                    updated_at = NOW()
                WHERE user_id = submission_record.user_id;
            END IF;
        END IF;
        
        -- Always update total submissions count in user_stats
        UPDATE public.user_stats 
        SET 
            submissions_count = submissions_count + 1,
            updated_at = NOW()
        WHERE user_id = submission_record.user_id;
        
        -- Create user_stats if doesn't exist
        INSERT INTO public.user_stats (user_id, problems_solved, submissions_count)
        VALUES (submission_record.user_id, CASE WHEN is_solved THEN 1 ELSE 0 END, 1)
        ON CONFLICT (user_id) DO NOTHING;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_stats_trigger
AFTER UPDATE ON public.judge_processes
FOR EACH ROW EXECUTE FUNCTION update_user_stats_on_judge_completion();

-- =====================================================
-- Judge Domain Table Comments
-- =====================================================

COMMENT ON TABLE public.submissions IS 'User code submissions - ユーザーコード提出';
COMMENT ON TABLE public.judge_processes IS 'Judge execution processes - ジャッジ実行プロセス';
COMMENT ON TABLE public.judge_case_results IS 'Test case execution results - テストケース実行結果';
COMMENT ON TABLE public.judge_case_result_metadata IS 'Detailed execution metadata - 実行結果詳細メタデータ';

-- Column comments for important fields
COMMENT ON COLUMN public.submissions.status IS 'Submission status: pending, judging, completed, error';
COMMENT ON COLUMN public.submissions.language IS 'Programming language: python, javascript, etc.';
COMMENT ON COLUMN public.judge_processes.status IS 'Process status: pending, running, succeeded, failed, error, other';
COMMENT ON COLUMN public.judge_case_results.status IS 'Result status: AC, WA, RE, CE, TLE, MLE, IE';
COMMENT ON COLUMN public.judge_case_results.result IS 'Detailed result description';
