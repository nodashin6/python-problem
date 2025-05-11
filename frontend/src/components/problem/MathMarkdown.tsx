import React from 'react';
import ReactMarkdown from 'react-markdown';
import { InlineMath, BlockMath } from 'react-katex';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

interface MathMarkdownProps {
  children: string;
}

// KaTexで数式を描画するためのカスタムコンポーネント
export const MathMarkdown: React.FC<MathMarkdownProps> = ({ children }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeKatex]}
      components={{
        // 数式内のエスケープされた文字をそのまま表示するためのカスタムレンダラー
        code: ({ className, children, ...props }) => {
          const match = /language-(\w+)/.exec(className || '');
          const value = String(children).replace(/\n$/, '');
          
          // 数式かどうかを判断
          if (match && match[1] === 'math') {
            return <BlockMath math={value} />;
          }

          // 通常のコードブロックはそのまま表示
          return (
            <code className={className} {...props}>
              {children}
            </code>
          );
        },
        // インライン数式とブロック数式は自動的にremark-mathとrehype-katexで処理されるようになる
      }}
    >
      {children}
    </ReactMarkdown>
  );
};