-- =====================================================
-- Core Domain Schema Migration
-- Version: 20250527100000
-- Date: 2025-05-27
-- Description: Core domain tables for problem and user management
-- =====================================================

-- =====================================================
-- Problem Management Tables (Core Domain)
-- =====================================================

-- Books (問題集) - 問題をグループ化するコレクション
CREATE TABLE IF NOT EXISTS public.books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    published_date DATE NOT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Problems (問題) - 個別の問題定義
CREATE TABLE IF NOT EXISTS public.problems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES public.books(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    difficulty_level VARCHAR(20) DEFAULT 'beginner' NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add enum constraints for problems
ALTER TABLE public.problems 
ADD CONSTRAINT problems_difficulty_level_check 
CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced', 'expert'));

ALTER TABLE public.problems 
ADD CONSTRAINT problems_status_check 
CHECK (status IN ('draft', 'published', 'archived'));

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
-- 注意: "test_cases"ではなく"judge_cases"を使用（pytest との競合回避）
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
ALTER TABLE public.judge_cases 
ADD CONSTRAINT judge_cases_type_check 
CHECK (judge_case_type IN ('sample', 'normal', 'edge', 'stress'));

-- =====================================================
-- User Management Tables (Core Domain)
-- =====================================================

-- Users (ユーザープロファイル) - 独立したユーザー管理
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- ローカル認証用
    avatar_url TEXT,
    bio TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Roles (ユーザーロール) - 権限管理
CREATE TABLE IF NOT EXISTS public.user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, role)
);

-- Add enum constraint for user roles
ALTER TABLE public.user_roles 
ADD CONSTRAINT user_roles_role_check 
CHECK (role IN ('guest', 'user', 'moderator', 'admin'));

-- User Stats (ユーザー統計) - パフォーマンス統計
CREATE TABLE IF NOT EXISTS public.user_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE UNIQUE,
    problems_solved INTEGER DEFAULT 0,
    submissions_count INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    rank_score DECIMAL(10,2) DEFAULT 0.0,
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
    last_submission_id UUID, -- 後でjudge domainのsubmissionsテーブルと関連付け
    best_score DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, problem_id)
);

-- =====================================================
-- Core Domain Indexes for Performance
-- =====================================================

-- Books indexes
CREATE INDEX IF NOT EXISTS idx_books_published 
ON public.books(is_published, published_date);

CREATE INDEX IF NOT EXISTS idx_books_author 
ON public.books(author);

-- Problems indexes
CREATE INDEX IF NOT EXISTS idx_problems_book_id 
ON public.problems(book_id);

CREATE INDEX IF NOT EXISTS idx_problems_status 
ON public.problems(status);

CREATE INDEX IF NOT EXISTS idx_problems_difficulty 
ON public.problems(difficulty_level);

CREATE INDEX IF NOT EXISTS idx_problems_status_published 
ON public.problems(status, difficulty_level) 
WHERE status = 'published';

-- Problem Contents indexes
CREATE INDEX IF NOT EXISTS idx_problem_contents_problem_language 
ON public.problem_contents(problem_id, language);

-- Judge Cases indexes
CREATE INDEX IF NOT EXISTS idx_judge_cases_problem_id 
ON public.judge_cases(problem_id);

CREATE INDEX IF NOT EXISTS idx_judge_cases_display_order 
ON public.judge_cases(problem_id, display_order);

CREATE INDEX IF NOT EXISTS idx_judge_cases_sample 
ON public.judge_cases(problem_id, is_sample);

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_username 
ON public.users(username);

CREATE INDEX IF NOT EXISTS idx_users_email 
ON public.users(email);

-- User Roles indexes
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id 
ON public.user_roles(user_id);

CREATE INDEX IF NOT EXISTS idx_user_roles_role 
ON public.user_roles(role);

-- User Problem Status indexes
CREATE INDEX IF NOT EXISTS idx_user_problem_status_user_solved 
ON public.user_problem_status(user_id, solved);

CREATE INDEX IF NOT EXISTS idx_user_problem_status_problem 
ON public.user_problem_status(problem_id, solved);

CREATE INDEX IF NOT EXISTS idx_user_problem_status_solved_at 
ON public.user_problem_status(solved_at DESC) 
WHERE solved = true;

-- =====================================================
-- Core Domain Row Level Security (RLS)
-- =====================================================

-- Enable RLS on all core tables
ALTER TABLE public.books ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.problems ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.problem_contents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.editorials ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.editorial_contents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.case_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.judge_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_problem_status ENABLE ROW LEVEL SECURITY;

-- Public read access for published content
CREATE POLICY "published_books_readable_by_all" ON public.books 
FOR SELECT USING (is_published = true);

CREATE POLICY "published_problems_readable_by_all" ON public.problems 
FOR SELECT USING (status = 'published');

CREATE POLICY "published_problem_contents_readable_by_all" ON public.problem_contents 
FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM public.problems 
        WHERE problems.id = problem_contents.problem_id 
        AND problems.status = 'published'
    )
);

CREATE POLICY "published_editorials_readable_by_all" ON public.editorials 
FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM public.problems 
        WHERE problems.id = editorials.problem_id 
        AND problems.status = 'published'
    )
);

CREATE POLICY "published_editorial_contents_readable_by_all" ON public.editorial_contents 
FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM public.editorials e
        JOIN public.problems p ON p.id = e.problem_id
        WHERE e.id = editorial_contents.editorial_id 
        AND p.status = 'published'
    )
);

-- Judge cases readable by all (no auth restriction for local testing)
CREATE POLICY "judge_cases_readable_by_all" ON public.judge_cases 
FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM public.problems 
        WHERE problems.id = judge_cases.problem_id 
        AND problems.status = 'published'
    )
);

-- Allow all access for local testing (RLS disabled for local development)
-- Note: In production, these should be replaced with proper auth checks
CREATE POLICY "users_all_access" ON public.users FOR ALL USING (true);
CREATE POLICY "user_stats_all_access" ON public.user_stats FOR ALL USING (true);
CREATE POLICY "user_problem_status_all_access" ON public.user_problem_status FOR ALL USING (true);
CREATE POLICY "books_all_access" ON public.books FOR ALL USING (true);
CREATE POLICY "problems_all_access" ON public.problems FOR ALL USING (true);

-- =====================================================
-- Core Domain Triggers for updated_at timestamps
-- =====================================================

CREATE TRIGGER handle_updated_at_books 
BEFORE UPDATE ON public.books 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_problems 
BEFORE UPDATE ON public.problems 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_problem_contents 
BEFORE UPDATE ON public.problem_contents 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_editorials 
BEFORE UPDATE ON public.editorials 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_editorial_contents 
BEFORE UPDATE ON public.editorial_contents 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_case_files 
BEFORE UPDATE ON public.case_files 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_judge_cases 
BEFORE UPDATE ON public.judge_cases 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_users 
BEFORE UPDATE ON public.users 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_user_roles 
BEFORE UPDATE ON public.user_roles 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_user_stats 
BEFORE UPDATE ON public.user_stats 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

CREATE TRIGGER handle_updated_at_user_problem_status 
BEFORE UPDATE ON public.user_problem_status 
FOR EACH ROW EXECUTE PROCEDURE moddatetime (updated_at);

-- =====================================================
-- Core Domain Sample Data
-- =====================================================

-- Sample book for development
INSERT INTO public.books (id, title, author, published_date, is_published) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'Getting Started', 'Judge System Team', CURRENT_DATE, true)
ON CONFLICT (id) DO NOTHING;

-- Sample problems
INSERT INTO public.problems (id, title, description, book_id, difficulty_level, status, tags) VALUES 
('550e8400-e29b-41d4-a716-446655440001', 'Hello World', 'Print "Hello, World!" to the console', '550e8400-e29b-41d4-a716-446655440000', 'beginner', 'published', ARRAY['basic', 'output']),
('550e8400-e29b-41d4-a716-446655440002', 'Sum of Two Numbers', 'Read two integers and output their sum', '550e8400-e29b-41d4-a716-446655440000', 'beginner', 'published', ARRAY['math', 'input'])
ON CONFLICT (id) DO NOTHING;

-- Sample problem contents (Japanese)
INSERT INTO public.problem_contents (problem_id, language, md_content) VALUES 
('550e8400-e29b-41d4-a716-446655440001', 'ja', '# Hello World\n\n"Hello, World!"を出力してください。\n\n## 入力\n\n入力はありません。\n\n## 出力\n\n`Hello, World!` を1行で出力してください。'),
('550e8400-e29b-41d4-a716-446655440002', 'ja', '# 二つの数の和\n\n二つの整数を読み込んで、その和を出力してください。\n\n## 入力\n\n1行に2つの整数 A, B が空白区切りで与えられます。\n\n## 出力\n\nA + B の値を出力してください。')
ON CONFLICT (problem_id, language) DO NOTHING;

-- =====================================================
-- Core Domain Table Comments
-- =====================================================

COMMENT ON TABLE public.books IS 'Problem collections/books - グループ化された問題集';
COMMENT ON TABLE public.problems IS 'Individual problems - 個別の問題定義';
COMMENT ON TABLE public.problem_contents IS 'Multi-language problem content - 多言語対応問題コンテンツ';
COMMENT ON TABLE public.editorials IS 'Problem editorials/solutions - 問題解説';
COMMENT ON TABLE public.editorial_contents IS 'Multi-language editorial content - 多言語対応解説コンテンツ';
COMMENT ON TABLE public.case_files IS 'Test case input/output files - テストケースファイル';
COMMENT ON TABLE public.judge_cases IS 'Test case definitions - テストケース定義 (pytest競合回避のためjudge_cases)';
COMMENT ON TABLE public.users IS 'User profiles extending Supabase auth - ユーザープロファイル';
COMMENT ON TABLE public.user_roles IS 'User role assignments - ユーザーロール管理';
COMMENT ON TABLE public.user_stats IS 'User performance statistics - ユーザー統計';
COMMENT ON TABLE public.user_problem_status IS 'User progress on problems - ユーザー問題進捗状況';
