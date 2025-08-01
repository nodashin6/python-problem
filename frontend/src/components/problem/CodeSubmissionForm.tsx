import React from 'react';

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
        className={submitting 
          ? "inline-flex items-center justify-center px-6 py-3 text-sm font-medium text-indigo-600 bg-white border border-indigo-200 rounded-xl opacity-70 cursor-not-allowed" 
          : "inline-flex items-center justify-center px-6 py-3 text-sm font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl hover:shadow-lg hover:shadow-indigo-500/25 transform hover:-translate-y-0.5 focus:ring-2 focus:ring-indigo-500 transition-all duration-300"
        }
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