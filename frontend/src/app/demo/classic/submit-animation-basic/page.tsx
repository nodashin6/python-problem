'use client';

import React, { useState, useEffect } from 'react';

// Mock test cases data - simplified for performance
const MOCK_TEST_CASES = [
  { id: 'tc1', name: 'SAMPLE_01' },
  { id: 'tc2', name: 'SAMPLE_02' },
  { id: 'tc3', name: 'BASIC_TEST_01' },
  { id: 'tc4', name: 'BASIC_TEST_02' },
  { id: 'tc5', name: 'EDGE_CASE_01' },
  { id: 'tc6', name: 'COMPLEX_MATRIX' },
  { id: 'tc7', name: 'STRESS_TEST' },
  { id: 'tc8', name: 'BOUNDARY_CHECK' },
];

type TestCaseStatus = 'pending' | 'running' | 'passed' | 'failed';

interface TestCaseResult {
  id: string;
  name: string;
  status: TestCaseStatus;
  executionTime?: number;
  memoryUsage?: number;
  score?: number;
}

export default function SubmitAnimationDemo() {
  const [code, setCode] = useState('print("Hello World")');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [testResults, setTestResults] = useState<TestCaseResult[]>([]);
  const [currentTestIndex, setCurrentTestIndex] = useState(-1);
  const [overallStatus, setOverallStatus] = useState<'idle' | 'compiling' | 'running' | 'completed' | 'failed'>('idle');
  const [matrixRain, setMatrixRain] = useState<string[]>([]);

  // Matrix rain effect
  useEffect(() => {
    if (isSubmitting) {
      const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
      const generateRain = () => {
        return Array.from({ length: 20 }, () => 
          Array.from({ length: Math.floor(Math.random() * 10) + 5 }, () => 
            chars[Math.floor(Math.random() * chars.length)]
          ).join('')
        );
      };
      setMatrixRain(generateRain());
      const interval = setInterval(() => setMatrixRain(generateRain()), 150);
      return () => clearInterval(interval);
    }
  }, [isSubmitting]);

  // Reset function
  const resetSubmission = () => {
    setIsSubmitting(false);
    setTestResults([]);
    setCurrentTestIndex(-1);
    setOverallStatus('idle');
  };

  // Simulate submission process
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting) return;

    setIsSubmitting(true);
    setOverallStatus('compiling');
    setTestResults(MOCK_TEST_CASES.map(tc => ({
      id: tc.id,
      name: tc.name,
      status: 'pending' as TestCaseStatus
    })));

    // Compilation phase
    await new Promise(resolve => setTimeout(resolve, 1500));
    setOverallStatus('running');

    // Execute test cases with dramatic pacing
    for (let i = 0; i < MOCK_TEST_CASES.length; i++) {
      setCurrentTestIndex(i);
      
      // Update current test to running
      setTestResults(prev => prev.map((result, idx) => 
        idx === i ? { ...result, status: 'running' } : result
      ));

      // Varied execution time for tension (faster early tests, slower complex ones)
      const baseTime = 300 + (i * 100); // Progressively slower
      const variance = Math.random() * 400 + 200; // 200-600ms variance
      const executionTime = Math.min(baseTime + variance, 1200); // Cap at 1.2s
      await new Promise(resolve => setTimeout(resolve, executionTime));

      // Dynamic difficulty - later tests more likely to fail for tension
      const difficulty = i / (MOCK_TEST_CASES.length - 1); // 0 to 1
      const failRate = 0.1 + (difficulty * 0.25); // 10% to 35% fail rate
      const passed = Math.random() > failRate;
      const status = passed ? 'passed' : 'failed';
      
      // Realistic performance metrics
      const memoryUsage = Math.round(Math.random() * 64 + 16 + (i * 8)); // Increasing memory usage
      const score = passed 
        ? Math.round(Math.random() * 15 + 85 - (difficulty * 5)) // 80-100 early, 75-95 late
        : Math.round(Math.random() * 40 + 10); // 10-50 for failures

      setTestResults(prev => prev.map((result, idx) => 
        idx === i ? {
          ...result,
          status,
          executionTime: Math.round(executionTime),
          memoryUsage,
          score
        } : result
      ));
    }

    setOverallStatus('completed');
    setIsSubmitting(false);
    setCurrentTestIndex(-1);
  };

  const getStatusIcon = (status: TestCaseStatus) => {
    switch (status) {
      case 'pending':
        return (
          <div className="w-5 h-5 border border-cyan-500/50 rounded-full bg-slate-900/50 backdrop-blur-sm">
            <div className="w-2 h-2 bg-cyan-500/30 rounded-full m-auto mt-1.5 animate-pulse"></div>
          </div>
        );
      case 'running':
        return (
          <div className="relative w-5 h-5">
            <div className="w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
            <div className="absolute inset-0 w-5 h-5 border border-cyan-300/30 rounded-full animate-ping"></div>
          </div>
        );
      case 'passed':
        return (
          <div className="relative w-5 h-5 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full flex items-center justify-center shadow-lg shadow-green-400/50">
            <svg className="w-3 h-3 text-black" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            <div className="absolute inset-0 bg-green-400 rounded-full animate-ping opacity-20"></div>
          </div>
        );
      case 'failed':
        return (
          <div className="relative w-5 h-5 bg-gradient-to-r from-red-400 to-pink-500 rounded-full flex items-center justify-center shadow-lg shadow-red-400/50">
            <svg className="w-3 h-3 text-black" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            <div className="absolute inset-0 bg-red-400 rounded-full animate-ping opacity-20"></div>
          </div>
        );
    }
  };

  const getStatusColor = (status: TestCaseStatus) => {
    switch (status) {
      case 'pending': return 'border-slate-700/50 bg-slate-900/20 backdrop-blur-sm';
      case 'running': return 'border-cyan-500/50 bg-cyan-950/30 backdrop-blur-sm shadow-lg shadow-cyan-500/20';
      case 'passed': return 'border-green-500/50 bg-green-950/30 backdrop-blur-sm shadow-lg shadow-green-500/20';
      case 'failed': return 'border-red-500/50 bg-red-950/30 backdrop-blur-sm shadow-lg shadow-red-500/20';
    }
  };

  const getOverallStatusDisplay = () => {
    switch (overallStatus) {
      case 'idle': return null;
      case 'compiling': return (
        <div className="relative flex items-center space-x-4 p-6 bg-gradient-to-r from-blue-950/50 to-cyan-950/50 border border-cyan-500/50 rounded-xl backdrop-blur-sm overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-blue-500/10 animate-pulse"></div>
          <div className="relative w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
          <div className="relative">
            <span className="text-cyan-300 font-bold font-mono tracking-wide text-lg">
              COMPILING_NEURAL_MATRIX...
            </span>
            <div className="text-cyan-500/70 text-sm font-mono mt-1">
              &gt; Analyzing code structure... OK
            </div>
          </div>
          <div className="ml-auto flex space-x-1">
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-ping"></div>
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-ping" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-purple-400 rounded-full animate-ping" style={{ animationDelay: '0.4s' }}></div>
          </div>
        </div>
      );
      case 'running': return (
        <div className="relative flex items-center space-x-4 p-6 bg-gradient-to-r from-orange-950/50 to-red-950/50 border border-orange-500/50 rounded-xl backdrop-blur-sm overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-orange-500/10 to-red-500/10 animate-pulse"></div>
          <div className="relative w-6 h-6 border-2 border-orange-400 border-t-transparent rounded-full animate-spin"></div>
          <div className="relative">
            <span className="text-orange-300 font-bold font-mono tracking-wide text-lg">
              EXECUTING_TEST_MATRIX...
            </span>
            <div className="text-orange-500/70 text-sm font-mono mt-1">
              &gt; Running test case [{currentTestIndex + 1}/{MOCK_TEST_CASES.length}]
            </div>
          </div>
          <div className="ml-auto">
            <div className="text-orange-400 font-mono text-sm">
              {Math.round(((currentTestIndex + 1) / MOCK_TEST_CASES.length) * 100)}%
            </div>
          </div>
        </div>
      );
      case 'completed': 
        const passedCount = testResults.filter(r => r.status === 'passed').length;
        const allPassed = passedCount === testResults.length;
        return (
          <div className={`relative flex items-center space-x-4 p-6 rounded-xl backdrop-blur-sm overflow-hidden border ${
            allPassed 
              ? 'bg-gradient-to-r from-green-950/50 to-emerald-950/50 border-green-500/50' 
              : 'bg-gradient-to-r from-yellow-950/50 to-orange-950/50 border-yellow-500/50'
          }`}>
            <div className={`absolute inset-0 animate-pulse ${
              allPassed 
                ? 'bg-gradient-to-r from-green-500/10 to-emerald-500/10' 
                : 'bg-gradient-to-r from-yellow-500/10 to-orange-500/10'
            }`}></div>
            <div className={`relative w-6 h-6 rounded-full flex items-center justify-center shadow-lg ${
              allPassed ? 'bg-gradient-to-r from-green-400 to-emerald-400 shadow-green-400/50' : 'bg-gradient-to-r from-yellow-400 to-orange-400 shadow-yellow-400/50'
            }`}>
              <svg className="w-4 h-4 text-black" fill="currentColor" viewBox="0 0 20 20">
                {allPassed ? (
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                ) : (
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                )}
              </svg>
            </div>
            <div className="relative">
              <span className={`font-bold font-mono tracking-wide text-lg ${
                allPassed ? 'text-green-300' : 'text-yellow-300'
              }`}>
                {allPassed ? 'MATRIX_VALIDATION_COMPLETE' : 'PARTIAL_SUCCESS_DETECTED'}
              </span>
              <div className={`text-sm font-mono mt-1 ${
                allPassed ? 'text-green-500/70' : 'text-yellow-500/70'
              }`}>
                &gt; Tests passed: {passedCount}/{testResults.length}
              </div>
            </div>
            {allPassed && (
              <div className="ml-auto flex space-x-1">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-ping"></div>
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-ping" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-green-400 rounded-full animate-ping" style={{ animationDelay: '0.4s' }}></div>
              </div>
            )}
          </div>
        );
      case 'failed': return (
        <div className="relative flex items-center space-x-4 p-6 bg-gradient-to-r from-red-950/50 to-pink-950/50 border border-red-500/50 rounded-xl backdrop-blur-sm overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 to-pink-500/10 animate-pulse"></div>
          <div className="relative w-6 h-6 bg-gradient-to-r from-red-400 to-pink-500 rounded-full flex items-center justify-center shadow-lg shadow-red-400/50">
            <svg className="w-4 h-4 text-black" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="relative">
            <span className="text-red-300 font-bold font-mono tracking-wide text-lg">
              COMPILATION_MATRIX_ERROR
            </span>
            <div className="text-red-500/70 text-sm font-mono mt-1">
              &gt; Neural network compilation failed
            </div>
          </div>
        </div>
      );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-gray-900 to-black relative overflow-hidden">
      {/* Cyberpunk Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-purple-900/20 via-transparent to-transparent"></div>
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_var(--tw-gradient-stops))] from-cyan-900/20 via-transparent to-transparent"></div>
      
      {/* Matrix Rain Effect */}
      {isSubmitting && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-10">
          {matrixRain.map((column, i) => (
            <div
              key={i}
              className="absolute text-green-400 text-xs font-mono whitespace-pre animate-pulse"
              style={{
                left: `${(i * 5) % 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 2}s`
              }}
            >
              {column}
            </div>
          ))}
        </div>
      )}
      
      {/* Grid Pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.03)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
      
      <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Cyberpunk Header */}
        <div className="mb-12 text-center">
          <div className="relative inline-block">
            <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4 font-mono tracking-wider">
              ［ NEURAL JUDGE ］
            </h1>
            <div className="absolute -top-2 -left-2 w-full h-full border border-cyan-500/30 rounded-lg animate-pulse"></div>
          </div>
          <p className="text-cyan-300/80 text-lg font-mono tracking-wide">
            &gt; INITIATING_CODE_EXECUTION_SEQUENCE.exe
          </p>
          <div className="mt-4 flex justify-center space-x-1">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-ping"></div>
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-ping" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-purple-400 rounded-full animate-ping" style={{ animationDelay: '0.4s' }}></div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Cyberpunk Code Terminal */}
          <div className="bg-black/40 backdrop-blur-xl rounded-2xl border border-cyan-500/30 shadow-2xl shadow-cyan-500/20 relative overflow-hidden">
            {/* Terminal Header */}
            <div className="bg-gradient-to-r from-slate-800/80 to-slate-900/80 p-4 border-b border-cyan-500/30">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                </div>
                <div className="text-cyan-400 font-mono text-sm ml-4">
                  neural-judge-terminal.exe
                </div>
              </div>
            </div>
            
            <div className="p-6">
              <h2 className="text-xl font-semibold text-cyan-400 mb-4 font-mono tracking-wide flex items-center">
                <span className="text-green-400 mr-2">$</span>
                CODE_INPUT_INTERFACE
              </h2>
              
              <form onSubmit={handleSubmit}>
                <div className="mb-6">
                  <label htmlFor="code" className="block text-sm font-medium text-cyan-300/80 mb-3 font-mono">
                    &gt; PYTHON_SOURCE_CODE
                  </label>
                  <div className="relative">
                    <textarea
                      id="code"
                      className="w-full h-64 p-4 border border-cyan-500/50 rounded-lg font-mono text-sm focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 bg-black/60 text-green-400 resize-none backdrop-blur-sm shadow-inner placeholder:text-green-600/50"
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      placeholder="# Enter your Python code here...
# The neural network is watching..."
                      spellCheck="false"
                      disabled={isSubmitting}
                      style={{
                        textShadow: '0 0 10px rgba(34, 197, 94, 0.5)'
                      }}
                    />
                    <div className="absolute top-3 right-3 px-3 py-1 text-xs bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full font-mono shadow-lg">
                      PYTHON.exe
                    </div>
                    {/* Scan line effect */}
                    <div className="absolute inset-0 pointer-events-none">
                      <div className="h-0.5 w-full bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-pulse opacity-30"></div>
                    </div>
                  </div>
                </div>
                
                <div className="flex space-x-3">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className={`flex-1 flex items-center justify-center px-8 py-4 text-sm font-bold font-mono rounded-xl transition-all duration-300 relative overflow-hidden ${
                      isSubmitting
                        ? 'bg-slate-800/50 text-slate-500 cursor-not-allowed border border-slate-700'
                        : 'bg-gradient-to-r from-cyan-600 via-purple-600 to-pink-600 text-white hover:from-cyan-500 hover:via-purple-500 hover:to-pink-500 shadow-2xl shadow-cyan-500/25 transform hover:scale-105 border border-cyan-500/50'
                    }`}
                  >
                    {!isSubmitting && (
                      <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/20 via-purple-400/20 to-pink-400/20 animate-pulse"></div>
                    )}
                    <div className="relative z-10 flex items-center">
                      {isSubmitting ? (
                        <>
                          <div className="w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mr-3"></div>
                          <span className="tracking-wider">EXECUTING...</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                          <span className="tracking-wider">EXECUTE_CODE</span>
                        </>
                      )}
                    </div>
                  </button>
                  
                  {(overallStatus === 'completed' || overallStatus === 'failed') && (
                    <button
                      type="button"
                      onClick={resetSubmission}
                      className="px-6 py-4 text-sm font-bold font-mono text-orange-400 bg-black/60 border border-orange-500/50 rounded-xl hover:bg-orange-950/30 hover:border-orange-400 hover:text-orange-300 transition-all duration-300 shadow-lg shadow-orange-500/10 tracking-wider"
                    >
                      RESET_SYS
                    </button>
                  )}
                </div>
              </form>
            </div>
          </div>

          {/* Cyberpunk Results Panel */}
          <div className="bg-black/40 backdrop-blur-xl rounded-2xl border border-purple-500/30 shadow-2xl shadow-purple-500/20 relative overflow-hidden">
            {/* Results Header */}
            <div className="bg-gradient-to-r from-purple-900/80 to-pink-900/80 p-4 border-b border-purple-500/30">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-purple-300 font-mono tracking-wide flex items-center">
                  <span className="text-green-400 mr-2">◉</span>
                  NEURAL_TEST_RESULTS
                </h2>
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse" style={{ animationDelay: '0.3s' }}></div>
                  <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse" style={{ animationDelay: '0.6s' }}></div>
                </div>
              </div>
            </div>
            
            <div className="p-6">
              {/* Cyberpunk Overall Status */}
              <div className="mb-8">
                {getOverallStatusDisplay()}
              </div>

              {/* Cyberpunk Test Cases - Compact Results */}
              <div className="space-y-3">
                {testResults.map((result, index) => (
                  <div
                    key={result.id}
                    className={`relative p-4 border rounded-lg transition-all duration-300 ${getStatusColor(result.status)}`}
                    style={{
                      boxShadow: result.status === 'running' ? '0 0 15px rgba(6, 182, 212, 0.4)' : result.status === 'passed' ? '0 0 10px rgba(34, 197, 94, 0.3)' : result.status === 'failed' ? '0 0 10px rgba(239, 68, 68, 0.3)' : 'none'
                    }}
                  >
                    {/* Intense scanning effect for running tests */}
                    {result.status === 'running' && (
                      <>
                        <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-pulse"></div>
                        <div className="absolute -top-px left-0 w-8 h-0.5 bg-cyan-400 animate-bounce" style={{ animationDuration: '0.8s' }}></div>
                      </>
                    )}
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        {getStatusIcon(result.status)}
                        <div className="flex-1">
                          <div className="font-mono font-bold text-white tracking-wide text-sm">
                            {result.name}
                          </div>
                          <div className="flex items-center space-x-4 mt-1">
                            {result.executionTime && (
                              <div className="text-xs text-cyan-400/70 font-mono">
                                {result.executionTime}ms
                              </div>
                            )}
                            {result.memoryUsage && (
                              <div className="text-xs text-purple-400/70 font-mono">
                                {result.memoryUsage}MB
                              </div>
                            )}
                            {result.score !== undefined && (
                              <div className={`text-xs font-mono font-bold ${
                                result.score >= 80 ? 'text-green-400' : result.score >= 60 ? 'text-yellow-400' : 'text-red-400'
                              }`}>
                                {result.score}pt
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {result.status === 'running' && (
                          <>
                            <div className="flex space-x-1">
                              <div className="w-1 h-4 bg-cyan-400 animate-pulse" style={{ animationDelay: '0s' }}></div>
                              <div className="w-1 h-4 bg-cyan-400 animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                              <div className="w-1 h-4 bg-cyan-400 animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                            </div>
                            <div className="text-xs text-cyan-400 font-mono font-bold animate-pulse ml-2">
                              ANALYZING
                            </div>
                          </>
                        )}
                        
                        {result.status === 'passed' && (
                          <div className="flex items-center space-x-2">
                            <div className="text-green-400 font-mono text-xs font-bold">
                              ACCEPTED
                            </div>
                            <div className="flex space-x-0.5">
                              <div className="w-1 h-1 bg-green-400 rounded-full animate-ping"></div>
                              <div className="w-1 h-1 bg-green-400 rounded-full animate-ping" style={{ animationDelay: '0.1s' }}></div>
                              <div className="w-1 h-1 bg-green-400 rounded-full animate-ping" style={{ animationDelay: '0.2s' }}></div>
                            </div>
                          </div>
                        )}
                        
                        {result.status === 'failed' && (
                          <div className="flex items-center space-x-2">
                            <div className="text-red-400 font-mono text-xs font-bold">
                              REJECTED
                            </div>
                            <div className="w-2 h-2 border border-red-400 rounded rotate-45 animate-pulse"></div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                
                {testResults.length === 0 && overallStatus === 'idle' && (
                  <div className="text-center py-12 relative">
                    <div className="relative">
                      <div className="w-12 h-12 mx-auto mb-4 border-2 border-cyan-500/50 rounded-lg flex items-center justify-center">
                        <div className="w-6 h-6 border border-cyan-400/30 rounded animate-pulse"></div>
                      </div>
                    </div>
                    <p className="text-cyan-400/80 font-mono tracking-wide">
                      &gt; NEURAL_MATRIX_STANDBY
                    </p>
                    <p className="text-cyan-600/60 font-mono text-xs mt-1">
                      Ready to process code execution
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Cyberpunk Demo Information */}
        <div className="mt-12 relative">
          <div className="bg-gradient-to-r from-slate-950/80 to-gray-900/80 backdrop-blur-xl border border-cyan-500/20 rounded-2xl p-8 relative overflow-hidden">
            {/* Background grid */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.05)_1px,transparent_1px)] bg-[size:20px_20px]"></div>
            
            <div className="relative">
              <h3 className="text-2xl font-bold font-mono bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-6 flex items-center">
                <span className="text-green-400 mr-3">◉</span>
                DEMO_SYSTEM_INFO
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full mt-2 animate-pulse"></div>
                    <div className="text-cyan-300/90 font-mono text-sm">
                      <span className="text-cyan-400 font-bold">COMPILE_TIME:</span> 1.5s neural processing
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-purple-400 rounded-full mt-2 animate-pulse"></div>
                    <div className="text-cyan-300/90 font-mono text-sm">
                      <span className="text-purple-400 font-bold">TEST_CASES:</span> 8 progressive difficulty
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-green-400 rounded-full mt-2 animate-pulse"></div>
                    <div className="text-cyan-300/90 font-mono text-sm">
                      <span className="text-green-400 font-bold">DIFFICULTY:</span> Adaptive scaling
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-orange-400 rounded-full mt-2 animate-pulse"></div>
                    <div className="text-cyan-300/90 font-mono text-sm">
                      <span className="text-orange-400 font-bold">METRICS:</span> Time, Memory, Score
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-black/40 border border-cyan-500/30 rounded-lg">
                <div className="text-cyan-400/70 text-xs font-mono mb-2">&gt; SYSTEM_STATUS:</div>
                <div className="text-green-400 font-mono text-sm">
                  Optimized for performance - results only, no heavy data output
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}