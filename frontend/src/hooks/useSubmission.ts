import { useState, useCallback } from 'react';
import toast from 'react-hot-toast';
import { judgeCode } from '@/lib/api';
import { useJudgeResult } from './useJudgeResult';

/**
 * コード提出と提出状態を管理するカスタムフック
 */
export const useSubmission = (problemId: string) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [judgeId, setJudgeId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [code, setCode] = useState<string>('');
  
  // コード提出処理が完了したときのコールバック
  const onJudgeComplete = useCallback(() => {
    toast.dismiss('judge-status');
    setIsSubmitting(false);
    console.log('📌 判定が完了しました');
  }, []);
  
  // ジャッジ結果を取得
  const { result, judgeStatus, isPolling, resetJudgeResult } = useJudgeResult(
    judgeId, code, problemId, onJudgeComplete
  );

  // 提出処理をリセット
  const resetSubmitting = useCallback(() => {
    setIsSubmitting(false);
  }, []);

  // コードを提出する関数
  const submit = async (submitCode: string) => {
    if (!submitCode.trim()) {
      setError('コードを入力してください');
      return null;
    }
    
    resetJudgeResult();
    setIsSubmitting(true);
    setError(null);
    
    try {
      const response = await judgeCode(problemId, submitCode);
      setJudgeId(response.judge_id);
      return response.judge_id;
    } catch (err) {
      console.error('ジャッジリクエスト失敗:', err);
      setError('ジャッジリクエストの送信に失敗しました');
      setIsSubmitting(false);
      return null;
    }
  };

  return { 
    isSubmitting, judgeId, error, submit, resetSubmitting,
    result, judgeStatus, isPolling, code, setCode
  };
};
