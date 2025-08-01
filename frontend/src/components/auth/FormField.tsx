/**
 * FormField Component
 * 再利用可能なフォームフィールドコンポーネント
 */

'use client';

import React from 'react';

interface FormFieldProps {
  id: string;
  name: string;
  type: string;
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  required?: boolean;
  autoComplete?: string;
  className?: string;
}

export function FormField({
  id,
  name,
  type,
  label,
  value,
  onChange,
  placeholder,
  required = false,
  autoComplete,
  className = "",
}: FormFieldProps) {
  return (
    <div className={`space-y-2 ${className}`}>
      <label htmlFor={id} className="block text-sm font-semibold text-gray-700 dark:text-gray-200">
        {label}
      </label>
      <input
        type={type}
        id={id}
        name={name}
        value={value}
        onChange={onChange}
        required={required}
        autoComplete={autoComplete}
        className="w-full px-4 py-3 sm:py-4 text-base border-2 border-gray-200 dark:border-slate-600 rounded-2xl 
                   bg-gray-50 dark:bg-slate-700 text-gray-900 dark:text-gray-100
                   focus:ring-4 focus:ring-indigo-100 dark:focus:ring-indigo-900 
                   focus:border-indigo-500 dark:focus:border-indigo-400 
                   transition-all duration-300 placeholder-gray-400 dark:placeholder-gray-400"
        placeholder={placeholder}
      />
    </div>
  );
}

export default FormField;