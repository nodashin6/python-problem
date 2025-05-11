import React from 'react';
import ReactMarkdown from 'react-markdown';
import Link from 'next/link';

interface ProblemCardProps {
  title: string;
  markdownContent?: string;
  id?: string; // 問題一覧表示用に追加
  isListItem?: boolean; // リスト表示かどうかのフラグ
  description?: string; // 問題の説明（リスト表示用）
}

export const ProblemCard: React.FC<ProblemCardProps> = ({ 
  title, 
  markdownContent, 
  id, 
  isListItem = false,
  description
}) => {
  if (isListItem && id) {
    return (
      <Link href={`/problem/${id}`} className="block transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
        <div className="card-modern">
          <div className="card-header">
            <h2 className="text-xl font-bold text-white">{title}</h2>
          </div>
          <div className="card-body">
            <p className="line-clamp-2 text-gray-600">
              {description || '問題文がありません'}
            </p>
            <div className="mt-3 flex justify-end">
              <span className="inline-flex items-center text-indigo-600 text-sm font-medium">
                解く
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
      <div className="card-header">
        <h1 className="text-3xl font-bold text-white">{title}</h1>
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
            <ReactMarkdown>{markdownContent}</ReactMarkdown>
          ) : (
            <p>問題文がありません</p>
          )}
        </div>
      </div>
    </div>
  );
};