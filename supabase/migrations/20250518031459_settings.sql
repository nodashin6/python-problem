-- スキーマの作成
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS pgmq;

-- メッセージキュー用の拡張機能
CREATE EXTENSION IF NOT EXISTS pgmq SCHEMA pgmq;

-- タイムスタンプ自動更新用の拡張機能
CREATE EXTENSION IF NOT EXISTS moddatetime WITH SCHEMA extensions;

-- キューの作成（pgmq拡張機能がインストールされた後で実行する）
DO $$
BEGIN
    -- 少し待機して確実に拡張機能が有効になるようにする
    PERFORM pg_sleep(1);
    
    -- キューを作成
    PERFORM pgmq.create('judge_queue');
    PERFORM pgmq.create('notification_queue');
    PERFORM pgmq.create('pytest_queue');
END;
$$;