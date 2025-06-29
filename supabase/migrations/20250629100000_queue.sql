-- Enable PostgreSQL Message Queue extension
CREATE EXTENSION IF NOT EXISTS "pgmq";

-- Create required queues
SELECT pgmq.create('queue_test');    -- For testing purposes
SELECT pgmq.create('queue_server');  -- For server processing

