import React from 'react';
import ReactMarkdown from 'react-markdown';
import Link from 'next/link';
import { MathMarkdown } from './MathMarkdown';

interface ProblemCardProps {
  title: string;
  markdownContent?: string;
  id?: string; // 問題一覧表示用に追加
  isListItem?: boolean; // リスト表示かどうかのフラグ
  description?: string; // 問題の説明（リスト表示用）
  level?: number; // 問題の難易度 (1-10)
  solved?: boolean; // 解いた問題かどうか
  submission_count?: number; // 提出回数
}

// 難易度に応じた色とテキストを返す関数
const getLevelInfo = (level: number = 1) => {
  if (level <= 2) return { color: 'bg-green-100 text-green-800', text: '入門' };
  if (level <= 4) return { color: 'bg-yellow-100 text-blue-800', text: '初級' };
  if (level <= 6) return { color: 'bg-yellow-100 text-yellow-800', text: '中級' };
  return { color: 'bg-red-100 text-red-800', text: '上級' };
};

export const ProblemCard: React.FC<ProblemCardProps> = ({ 
  title, 
  markdownContent, 
  id, 
  isListItem = false,
  description,
  level = 1,
  solved = false,
  submission_count = 0
}) => {
  const levelInfo = getLevelInfo(level);
  
  if (isListItem && id) {
    return (
      <Link href={`/problem/${id}`} className="block transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
        <div className={`card-modern ${solved ? 'border-l-4 border-green-500' : ''}`}>
          <div className="card-header flex justify-between items-center">
            <h2 className="text-xl font-bold text-white flex items-center">
              {solved && (
                <span className="mr-2 bg-green-500 p-1 rounded-full text-white">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </span>
              )}
              {title}
            </h2>
            <div className="flex items-center">
              <span className={`text-xs font-semibold px-2.5 py-0.5 rounded ${levelInfo.color}`}>
                Lv.{level} {levelInfo.text}
              </span>
            </div>
          </div>
          <div className="card-body">
            <p className="line-clamp-2 text-gray-600">
              {description || '問題文がありません'}
            </p>
            <div className="mt-3 flex justify-between items-center">
              {submission_count > 0 && (
                <span className="text-sm text-gray-500">
                  提出回数: {submission_count}回
                </span>
              )}
              <span className="inline-flex items-center text-indigo-600 text-sm font-medium">
                {solved ? '再度解く' : '解く'}
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </span>
            </div>
          </div>
        </div>
      </Link>
    );
  }

  return (
    <div className="card-modern mb-8">
      <div className="card-header flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white flex items-center">
          {solved && (
            <span className="mr-2 bg-green-500 p-1 rounded-full text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </span>
          )}
          {title}
        </h1>
        <div className="flex items-center space-x-3">
          {submission_count > 0 && (
            <span className="text-sm text-gray-100">
              提出回数: {submission_count}回
            </span>
          )}
          <span className={`text-xs font-semibold px-2.5 py-0.5 rounded ${levelInfo.color}`}>
            Lv.{level} {levelInfo.text}
          </span>
        </div>
      </div>
      
      <div className="card-body">
        <h2 className="text-2xl font-bold text-indigo-800 mb-6 flex items-center">
          <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          問題文
        </h2>
        <div className="prose max-w-none">
          {markdownContent ? (
            <MathMarkdown>{markdownContent}</MathMarkdown>
          ) : (
            <p>問題文がありません</p>
          )}
        </div>
      </div>
    </div>
  );
};