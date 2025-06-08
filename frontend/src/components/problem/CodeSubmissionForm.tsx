import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface CodeSubmissionFormProps {
  code: string;
  onCodeChange: (code: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  submitting: boolean;
}

export const CodeSubmissionForm: React.FC<CodeSubmissionFormProps> = ({
  code,
  onCodeChange,
  onSubmit,
  submitting
}) => {
  return (
    <form onSubmit={onSubmit}>
      <div className="mb-6">
        <label htmlFor="code" className="block text-sm font-medium text-indigo-700 mb-2">
          コード
        </label>
        <div className="relative">
          <textarea
            id="code"
            className="w-full h-64 p-5 border-2 border-indigo-200 rounded-xl font-mono text-sm focus:ring-indigo-500 focus:border-indigo-500 bg-gray-50 shadow-inner"
            value={code}
            onChange={(e) => onCodeChange(e.target.value)}
            placeholder="Pythonコードを入力してください"
            spellCheck="false"
          />
          <div className="absolute top-3 right-3 px-2 py-1 text-xs bg-indigo-100 text-indigo-600 rounded-md">
            Python
          </div>
        </div>
      </div>
      
      <button
        type="submit"
        disabled={submitting}
        className={submitting ? "btn-secondary opacity-70 cursor-not-allowed" : "btn-primary"}
      >
        {submitting ? (
          <span className="flex items-center">
            <div className="loading-spinner mr-2 !w-4 !h-4"></div>
            判定中...
          </span>
        ) : '提出する'}
      </button>
    </form>
  );
};