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
  
  // APIからのレスポンス内容をデバッグする
  const debugResponse = useCallback((resp: unknown) => {
    console.log('🔍 API応答の詳細分析:', {
      status: resp.status,
      hasResults: resp.results !== undefined,
      resultsType: resp.results ? typeof resp.results : 'undefined',
      resultsIsArray: resp.results ? Array.isArray(resp.results) : false,
      resultsDetail: resp.results,
      error: resp.error
    });
  }, []);

  const fetchJudgeStatusEffect = useCallback(async () => {
    if (!judgeId || isFetching || processedIdsRef.current.has(judgeId)) {
      return;
    }
    
    try {
      setIsFetching(true);
      const status = await fetchJudgeStatus(judgeId);
      console.log('🔍 ジャッジステータス取得:', status);
      debugResponse(status);
      setJudgeStatus(status);
    } catch (error) {
      console.error('ジャッジ状態の取得に失敗:', error);
    } finally {
      setIsFetching(false);
    }
  }, [judgeId, isFetching, debugResponse]);

  // ジャッジIDが変わったら状態をリセット
  useEffect(() => {
    if (judgeId && !processedIdsRef.current.has(judgeId)) {
      console.log('🔎 新しいジャッジID検出:', judgeId);
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
  
  // 重要修正: ジャッジステータスからの結果取得部分を完全に書き直し
  useEffect(() => {
    if (!judgeId || !judgeStatus) return;
    
    // 完了またはエラー状態のとき
    if (judgeStatus.status === 'completed' || judgeStatus.status === 'error') {
      console.log('🔍 ジャッジが完了または失敗:', judgeStatus);
      processedIdsRef.current.add(judgeId);
      
      // バックエンドからの応答形式を詳細に分析
      if (judgeStatus.results) {
        console.log('🔍 results構造:', judgeStatus.results);
        
        // 結果がオブジェクトで、その中にresultsプロパティがある場合
        if (typeof judgeStatus.results === 'object' && 'results' in judgeStatus.results) {
          console.log('🔍 resultsはオブジェクトでresultsプロパティを持つ');
          setResult(judgeStatus.results);
        } 
        // 結果が直接配列の場合 (またはresults自体が結果オブジェクトの場合)
        else {
          console.log('🔍 結果を標準形式に変換');
          // 標準的な形式に変換して設定
          setResult({
            id: judgeId,
            problem: { id: problemId },
            code: code,
            results: Array.isArray(judgeStatus.results) ? judgeStatus.results : [judgeStatus.results],
            error: null
          });
        }
      } else if (judgeStatus.error) {
        console.warn('🔍 ジャッジエラー:', judgeStatus.error);
        setResult({
          id: 'error',
          problem: { id: problemId },
          code: code,
          results: [],
          error: judgeStatus.error
        });
      } else {
        console.error('🔍 結果とエラーの両方がない完了状態:', judgeStatus);
        // エラー状態として処理
        setResult({
          id: 'error',
          problem: { id: problemId },
          code: code,
          results: [],
          error: '結果の形式が不正です'
        });
      }
      
      onComplete?.();
    }
  }, [judgeId, judgeStatus, code, problemId, onComplete]);

  // 結果をリセットするための関数
  const resetJudgeResult = useCallback(() => {
    setResult(null);
    setJudgeStatus(null);
    console.log('🔎 ジャッジ結果をリセットしました');
  }, []);

  return { judgeStatus, result, isPolling, resetJudgeResult };
};
