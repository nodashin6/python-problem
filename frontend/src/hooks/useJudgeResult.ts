import { useState, useRef, useCallback, useEffect } from 'react';
import { fetchJudgeStatus, JudgeStatus } from '@/lib/api';
import type { JudgeResponse } from '@/types/judge';

/**
 * ジャッジ結果の取得とポーリングを管理するカスタムフック
 */
export const useJudgeResult = (judgeId: string | null, code: string, problemId: string, onComplete?: () => void) => {
  const [judgeStatus, setJudgeStatus] = useState<JudgeStatus | null>(null);
  const [result, setResult] = useState<JudgeResponse | null>(null); 
  
  const isPolling = judgeId !== null && !result;
  const [isFetching, setIsFetching] = useState(false);
  const processedIdsRef = useRef<Set<string>>(new Set());
  
  const fetchJudgeStatusEffect = useCallback(async () => {
    if (!judgeId || isFetching || processedIdsRef.current.has(judgeId)) {
      return;
    }
    
    try {
      setIsFetching(true);
      const status = await fetchJudgeStatus(judgeId);
      setJudgeStatus(status);
    } catch (error) {
      console.error('ジャッジ状態の取得に失敗:', error);
    } finally {
      setIsFetching(false);
    }
  }, [judgeId, isFetching]);

  // ジャッジIDが変わったら状態をリセット
  useEffect(() => {
    if (judgeId && !processedIdsRef.current.has(judgeId)) {
      setResult(null);
      setJudgeStatus(null);
    }
  }, [judgeId]);
  
  // ポーリング設定
  useEffect(() => {
    if (!judgeId || processedIdsRef.current.has(judgeId) || result) {
      return;
    }
    
    fetchJudgeStatusEffect();
    
    const intervalId = setInterval(fetchJudgeStatusEffect, 2000);
    console.log('📌 ポーリング開始: ID =', judgeId);
    
    return () => {
      clearInterval(intervalId);
      console.log('📌 ポーリング停止: ID =', judgeId); 
    };
  }, [judgeId, result, fetchJudgeStatusEffect]);
  
  // ステータス更新を検知して結果を生成
  useEffect(() => {
    if (!judgeId || !judgeStatus) return;
    
    if (judgeStatus.status === 'completed' || judgeStatus.status === 'error') {
      processedIdsRef.current.add(judgeId);
      
      if (judgeStatus.results) {
        setResult(judgeStatus.results);
      } else if (judgeStatus.error) {
        setResult({
          id: 'error',
          problem: { id: problemId },
          code: code,
          results: [],
          error: judgeStatus.error
        });
      }
      
      onComplete?.();
      console.log('📌 ジャッジ完了:', judgeId);
    }
  }, [judgeId, judgeStatus, code, problemId, onComplete]);

  // 結果をリセットするための関数
  const resetJudgeResult = useCallback(() => {
    setResult(null);
    setJudgeStatus(null);
    console.log('📌 ジャッジ結果をリセットしました');
  }, []);

  return { judgeStatus, result, isPolling, resetJudgeResult };
};
