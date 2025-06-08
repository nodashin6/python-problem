-- =====================================================
-- Database Schema and Extensions Setup
-- =====================================================

-- スキーマの作成
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS pgmq;

-- メッセージキュー用の拡張機能
CREATE EXTENSION IF NOT EXISTS pgmq SCHEMA pgmq;

-- タイムスタンプ自動更新用の拡張機能
CREATE EXTENSION IF NOT EXISTS moddatetime WITH SCHEMA extensions;

-- =====================================================
-- Message Queue Setup
-- =====================================================

-- キューの作成 (pgmq拡張機能がインストールされた後で実行する) 
DO $$
BEGIN
    -- 少し待機して確実に拡張機能が有効になるようにする
    PERFORM pg_sleep(1);
    
    -- 各システム用のキューを作成
    PERFORM pgmq.create('judge_queue');      -- ジャッジシステム用
    PERFORM pgmq.create('notification_queue'); -- 通知システム用
    PERFORM pgmq.create('pytest_queue');     -- テスト実行用
END;
$$;