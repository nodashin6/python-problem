import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import 'katex/dist/katex.min.css';
import { Toaster } from 'react-hot-toast';
import AuthProvider from '@/components/auth/AuthProvider';
import MainLayout from '@/components/layout/MainLayout';
import { ThemeProvider } from '@/components/theme/ThemeProvider';

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Programming Problem Platform",
  description: "Comprehensive platform for competitive programming with authentication, problems, and judging",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThemeProvider>
          <AuthProvider>
            <MainLayout>
              <a href="#main" className="skip-link">
                メインコンテンツにスキップ
              </a>
              <main 
                id="main" 
                className="page-transition"
                role="main"
                aria-label="メインコンテンツ"
              >
                {children}
              </main>
              <div aria-live="polite" aria-atomic="true" className="live-region" id="live-region"></div>
            </MainLayout>
          </AuthProvider>
          <Toaster 
            position="bottom-right"
            toastOptions={{
              duration: 4000,
              className: 'card shadow-lg',
              style: {
                background: 'rgb(255 255 255)',
                color: 'rgb(71 85 105)',
                border: '1px solid rgb(226 232 240)',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#10B981',
                  secondary: 'white',
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#EF4444',
                  secondary: 'white',
                },
              },
            }} 
          />
        </ThemeProvider>
      </body>
    </html>
  );
}
