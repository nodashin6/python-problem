-- Users (ユーザープロファイル) - 独立したユーザー管理
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    -- ローカル認証用
    avatar_url TEXT NULL DEFAULT NULL,
    -- アバター画像のURL
    bio TEXT NULL DEFAULT NULL,
    -- ユーザープロフィールの自己紹介
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
ALTER TABLE
    public.user_roles
ADD
    CONSTRAINT user_roles_role_check CHECK (role IN ('guest', 'user', 'moderator', 'admin'));