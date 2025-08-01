/**
 * API Test Page
 * Page for testing API endpoints and connections
 */

'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api-client';

interface TestResult {
  endpoint: string;
  status: 'pending' | 'success' | 'error';
  data?: unknown;
  error?: string;
  duration?: number;
}

export default function ApiTestPage() {
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const updateResult = (endpoint: string, updates: Partial<TestResult>) => {
    setTestResults(prev => prev.map(result => 
      result.endpoint === endpoint 
        ? { ...result, ...updates }
        : result
    ));
  };

  const testEndpoint = async (endpoint: string, testFn: () => Promise<unknown>) => {
    const startTime = Date.now();
    updateResult(endpoint, { status: 'pending' });
    
    try {
      const data = await testFn();
      const duration = Date.now() - startTime;
      updateResult(endpoint, { 
        status: 'success', 
        data, 
        duration 
      });
    } catch (error) {
      const duration = Date.now() - startTime;
      updateResult(endpoint, { 
        status: 'error', 
        error: error instanceof Error ? error.message : 'Unknown error',
        duration 
      });
    }
  };

  const runTests = async () => {
    setIsRunning(true);
    
    // Initialize test results
    const endpoints = [
      'System Health',
      'Books List',
      'Problems List',
      'Judge Status',
    ];
    
    setTestResults(endpoints.map(endpoint => ({
      endpoint,
      status: 'pending' as const
    })));

    // Run tests
    await Promise.allSettled([
      testEndpoint('System Health', () => apiClient.getSystemHealth()),
      testEndpoint('Books List', () => apiClient.getBooks()),
      testEndpoint('Problems List', () => apiClient.getProblems()),
      testEndpoint('Judge Status', () => 
        fetch('http://localhost:8901/api/judge/status').then(r => r.json())
      ),
    ]);

    setIsRunning(false);
  };

  const getStatusColor = (status: TestResult['status']) => {
    switch (status) {
      case 'pending': return 'text-yellow-600 bg-yellow-50';
      case 'success': return 'text-green-600 bg-green-50';
      case 'error': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'pending': return '⏳';
      case 'success': return '✅';
      case 'error': return '❌';
      default: return '⚪';
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">API Connection Test</h1>
          <button
            onClick={runTests}
            disabled={isRunning}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-md transition-colors"
          >
            {isRunning ? 'Running Tests...' : 'Run Tests'}
          </button>
        </div>

        <div className="space-y-4">
          {testResults.map((result) => (
            <div key={result.endpoint} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <span className="text-lg">{getStatusIcon(result.status)}</span>
                  <h3 className="font-semibold text-gray-900">{result.endpoint}</h3>
                </div>
                <div className="flex items-center space-x-2">
                  {result.duration && (
                    <span className="text-sm text-gray-500">
                      {result.duration}ms
                    </span>
                  )}
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(result.status)}`}>
                    {result.status.toUpperCase()}
                  </span>
                </div>
              </div>

              {result.error && (
                <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-700 font-medium">Error:</p>
                  <p className="text-sm text-red-600">{result.error}</p>
                </div>
              )}

              {result.data ? (
                <div className="mt-2">
                  <details className="cursor-pointer">
                    <summary className="text-sm font-medium text-gray-700 hover:text-gray-900">
                      View Response Data
                    </summary>
                    <pre className="mt-2 p-3 bg-gray-50 border rounded-md text-xs overflow-auto max-h-40">
                      {JSON.stringify(result.data, null, 2)}
                    </pre>
                  </details>
                </div>
              ) : null}
            </div>
          ))}
        </div>

        {testResults.length === 0 && !isRunning && (
          <div className="text-center py-8">
            <p className="text-gray-500">Click &ldquo;Run Tests&rdquo; to test API connections</p>
          </div>
        )}
      </div>

      {/* System Info */}
      <div className="mt-6 bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">System Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <strong>API Base URL:</strong>
            <br />
            <code className="text-blue-600">http://localhost:8901</code>
          </div>
          <div>
            <strong>Available Endpoints:</strong>
            <ul className="mt-1 space-y-1">
              <li>• <code>/api/auth</code> - Authentication</li>
              <li>• <code>/api/problems</code> - Problems & Books</li>
              <li>• <code>/api/judge</code> - Code Judging</li>
              <li>• <code>/health</code> - System Health</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}