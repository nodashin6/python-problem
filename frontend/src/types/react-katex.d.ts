declare module 'react-katex';
declare module 'react-markdown/lib/ast-to-react' {
  import { ReactNode } from 'react';
  
  export interface CodeProps {
    node?: unknown;
    inline?: boolean;
    className?: string;
    children: ReactNode;
    [key: string]: unknown;
  }
}