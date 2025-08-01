/**
 * Login Form Component
 * Modern form for user authentication
 */

'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/hooks/useAuth';
import FormField from './FormField';
import PasswordField from './PasswordField';
import ErrorMessage from './ErrorMessage';
import LoadingButton from './LoadingButton';
import AuthNavigation from './AuthNavigation';

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
}

export function LoginForm({ onSuccess, onSwitchToRegister }: LoginFormProps) {
  const { login, isLoading } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      await login(formData.email, formData.password);
      onSuccess?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'ログインに失敗しました');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
    if (error) setError(null);
  };


  return (
    <motion.div
      className="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl border border-gray-100 dark:border-slate-700 w-full overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="p-6 sm:p-8 lg:p-10">
        <form onSubmit={handleSubmit} className="space-y-6">
          <FormField
            id="email"
            name="email"
            type="email"
            label="メールアドレス"
            value={formData.email}
            onChange={handleChange}
            placeholder="example@email.com"
            // icon={emailIcon}
            required
            autoComplete="email"
          />

          <PasswordField
            id="password"
            name="password"
            label="パスワード"
            value={formData.password}
            onChange={handleChange}
            required
          />

          <ErrorMessage message={error} />

          <LoadingButton
            type="submit"
            isLoading={isLoading}
            loadingText="ログイン中..."
          >
            <div className="flex items-center justify-center space-x-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
              <span>ログイン</span>
            </div>
          </LoadingButton>
        </form>

        {onSwitchToRegister && (
          <AuthNavigation
            text="アカウントをお持ちでないですか？"
            linkText="新規登録はこちら"
            onLinkClick={onSwitchToRegister}
          />
        )}
      </div>
    </motion.div>
  );
}

export default LoginForm;