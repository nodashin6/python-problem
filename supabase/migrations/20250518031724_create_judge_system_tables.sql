-- 基本テーブルの作成
-- books テーブル
CREATE TABLE public.books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    published_date DATE NOT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- problems テーブル
CREATE TABLE public.problems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES public.books(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    difficulty SMALLINT CHECK (difficulty BETWEEN 1 AND 5),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 問題コンテンツテーブル（多言語対応）
CREATE TABLE public.problem_contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID REFERENCES public.problems(id) ON DELETE CASCADE,
    language VARCHAR(50) NOT NULL,
    md_content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(problem_id, language)
);

-- 解説テーブル
CREATE TABLE public.editorials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID REFERENCES public.problems(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(problem_id)
);

-- 解説コンテンツテーブル（多言語対応）
CREATE TABLE public.editorial_contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    editorial_id UUID REFERENCES public.editorials(id) ON DELETE CASCADE,
    language VARCHAR(50) NOT NULL,
    md_content TEXT NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(editorial_id, language)
);

-- テストケースファイルテーブル
CREATE TABLE public.judge_case_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- テストケーステーブル
CREATE TABLE public.judge_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID REFERENCES public.problems(id) ON DELETE CASCADE,
    input_id UUID REFERENCES public.judge_case_files(id),
    output_id UUID REFERENCES public.judge_case_files(id),
    is_sample BOOLEAN DEFAULT FALSE,
    display_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 提出テーブル
CREATE TABLE public.submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID REFERENCES public.problems(id),
    user_id UUID NOT NULL,
    code TEXT NOT NULL,
    language TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ジャッジプロセステーブル
CREATE TABLE public.judge_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID REFERENCES public.submissions(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending',
    result TEXT,
    execution_time_ms INT,
    memory_usage_kb INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ジャッジケース結果テーブル
CREATE TABLE public.judge_case_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    judge_process_id UUID REFERENCES public.judge_processes(id) ON DELETE CASCADE,
    judge_case_id UUID REFERENCES public.judge_cases(id),
    status TEXT NOT NULL,
    result TEXT NOT NULL,
    error TEXT,
    warning TEXT,
    processing_time_ms INT,
    memory_usage_kb INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX idx_submissions_problem_id ON public.submissions(problem_id);
CREATE INDEX idx_submissions_user_id ON public.submissions(user_id);
CREATE INDEX idx_judge_processes_submission_id ON public.judge_processes(submission_id);
CREATE INDEX idx_judge_case_results_process_id ON public.judge_case_results(judge_process_id);
CREATE INDEX idx_judge_cases_problem_id ON public.judge_cases(problem_id);

-- トリガー設定: updated_at を自動更新
CREATE TRIGGER handle_updated_at_books BEFORE UPDATE ON public.books 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_problems BEFORE UPDATE ON public.problems 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_problem_contents BEFORE UPDATE ON public.problem_contents 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_editorials BEFORE UPDATE ON public.editorials 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_editorial_contents BEFORE UPDATE ON public.editorial_contents 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_judge_case_files BEFORE UPDATE ON public.judge_case_files 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_judge_cases BEFORE UPDATE ON public.judge_cases 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_submissions BEFORE UPDATE ON public.submissions 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_judge_processes BEFORE UPDATE ON public.judge_processes 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_judge_case_results BEFORE UPDATE ON public.judge_case_results 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

