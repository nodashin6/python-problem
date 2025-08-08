'use client';

import './globals.css';
import 'katex/dist/katex.min.css';
import { ThemeProvider } from '@/components/theme/ThemeProvider';
import { AuthProvider } from '@/components/auth/AuthProvider';
import { BackgroundLayer } from '@/components/ui/BackgroundLayer';
import DemoHeader from './components/DemoHeader';
import DemoSidebar from './components/DemoSidebar';
import { useState } from 'react';

export default function DemoLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <ThemeProvider>
      <AuthProvider>
        {/* Background Layer - Fixed to viewport */}
        <BackgroundLayer />
        
        <div className="h-screen flex flex-col overflow-hidden relative">
          
          {/* Demo Header Component */}
          <DemoHeader onToggleSidebar={toggleSidebar} />

          {/* Middle Section - Content with padding container */}
          <div className="flex-1 overflow-hidden">
            
            {/* Mobile Sidebar */}
            <div className="lg:hidden">
              <DemoSidebar isOpen={sidebarOpen} onClose={closeSidebar} />
            </div>
            
            {/* Desktop Sidebar */}
            <div className="hidden lg:block">
              <DemoSidebar isOpen={sidebarOpen} onClose={closeSidebar} />
            </div>

            {/* Padding Container for large screens */}
            <div className="h-full lg:p-16 p-4">
              {/* Main Content Area */}
              <main className="h-full bg-black/10 dark:bg-black/20 rounded-lg overflow-auto relative backdrop-blur-sm">
                {/* Content */}
                <div className="relative z-10 p-4 w-full">
                  {children}
                </div>
              </main>
            </div>
          </div>

        </div>
      </AuthProvider>
    </ThemeProvider>
  );
}