'use client';

import React, { useState, useEffect, useRef } from 'react';

// Mock test cases data - Generate up to 100 test cases dynamically
const generateTestCases = (count: number) => {
  const testTypes = ['SAMPLE', 'BASIC', 'EDGE', 'STRESS', 'COMPLEX', 'CORNER', 'LARGE', 'RANDOM', 'EXTREME', 'FINAL'];
  return Array.from({ length: count }, (_, i) => ({
    id: `tc${i + 1}`,
    name: testTypes[Math.floor(i / (count / testTypes.length))] || 'TEST'
  }));
};

const MOCK_TEST_CASES = generateTestCases(36); // Default 36, easily scalable to 100

type TestCaseStatus = 'pending' | 'running' | 'passed' | 'failed';

interface TestCaseResult {
  id: string;
  name: string;
  status: TestCaseStatus;
  executionTime?: number;
  score?: number;
}

interface LightParticle {
  id: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  maxLife: number;
  size: number;
  color: string;
  character: string;
}

export default function SubmitAnimationDemo() {
  const [code, setCode] = useState('def solve(n):\n    return n * 2\n\nprint(solve(42))');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [testResults, setTestResults] = useState<TestCaseResult[]>([]);
  const [currentTestIndex, setCurrentTestIndex] = useState(-1);
  const [overallStatus, setOverallStatus] = useState<'idle' | 'transforming' | 'floating' | 'executing' | 'completed'>('idle');
  const [lightParticles, setLightParticles] = useState<LightParticle[]>([]);
  const [codeTransformProgress, setCodeTransformProgress] = useState(0);
  const [floatingCodeElements, setFloatingCodeElements] = useState<string[]>([]);
  const animationFrameRef = useRef<number | null>(null);

  // Initialize floating code elements from the actual code
  useEffect(() => {
    const codeLines = code.split('\\n').filter(line => line.trim());
    const words = codeLines.flatMap(line =>
      line.split(/\\s+/).filter(word => word.length > 0)
    );
    setFloatingCodeElements(words.slice(0, 20)); // Limit to 20 elements
  }, [code]);

  // Light particle animation
  useEffect(() => {
    if (overallStatus === 'floating' || overallStatus === 'executing') {
      const animate = () => {
        setLightParticles(prevParticles => {
          return prevParticles
            .map(particle => ({
              ...particle,
              x: particle.x + particle.vx,
              y: particle.y + particle.vy,
              life: particle.life - 1,
              vy: particle.vy + 0.02, // Slight gravity
            }))
            .filter(particle => particle.life > 0);
        });
        animationFrameRef.current = requestAnimationFrame(animate);
      };
      animationFrameRef.current = requestAnimationFrame(animate);
    }
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [overallStatus]);

  // Generate light particles from code transformation
  const generateLightParticles = () => {
    const particles: LightParticle[] = [];
    const colors = ['#00FFFF', '#FF00FF', '#FFFF00', '#00FF00', '#FF6B6B'];

    floatingCodeElements.forEach((element, index) => {
      const centerX = window.innerWidth / 2;
      const centerY = window.innerHeight / 2;
      const angle = (index / floatingCodeElements.length) * Math.PI * 2;
      const radius = 100 + Math.random() * 200;

      particles.push({
        id: `particle-${index}`,
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius,
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
        life: 300 + Math.random() * 200,
        maxLife: 300 + Math.random() * 200,
        size: 3 + Math.random() * 5,
        color: colors[Math.floor(Math.random() * colors.length)],
        character: element[Math.floor(Math.random() * element.length)] || '0'
      });
    });

    setLightParticles(particles);
  };

  // Reset function
  const resetSubmission = () => {
    setIsSubmitting(false);
    setTestResults([]);
    setCurrentTestIndex(-1);
    setOverallStatus('idle');
    setLightParticles([]);
    setCodeTransformProgress(0);
  };

  // Epic submission process
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting) return;

    setIsSubmitting(true);
    setTestResults(MOCK_TEST_CASES.map(tc => ({
      id: tc.id,
      name: tc.name,
      status: 'pending' as TestCaseStatus
    })));

    // Phase 1: Code Transformation (2 seconds)
    setOverallStatus('transforming');
    for (let i = 0; i <= 100; i += 2) {
      setCodeTransformProgress(i);
      await new Promise(resolve => setTimeout(resolve, 40));
    }

    // Phase 2: Code becomes light and floats to center (1 second)
    setOverallStatus('floating');
    generateLightParticles();
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Phase 3: Test execution with synchronized blocks
    setOverallStatus('executing');
    for (let i = 0; i < MOCK_TEST_CASES.length; i++) {
      setCurrentTestIndex(i);

      // Update current test to running
      setTestResults(prev => prev.map((result, idx) =>
        idx === i ? { ...result, status: 'running' } : result
      ));

      // Dynamic execution time based on test complexity
      const executionTime = 800 + (i * 200) + Math.random() * 400;
      await new Promise(resolve => setTimeout(resolve, executionTime));

      // Results with increasing difficulty
      const difficulty = i / (MOCK_TEST_CASES.length - 1);
      const failRate = 0.05 + (difficulty * 0.25);
      const passed = Math.random() > failRate;
      const status = passed ? 'passed' : 'failed';
      const score = passed
        ? Math.round(Math.random() * 10 + 90 - (difficulty * 5))
        : Math.round(Math.random() * 30 + 20);

      setTestResults(prev => prev.map((result, idx) =>
        idx === i ? {
          ...result,
          status,
          executionTime: Math.round(executionTime),
          score
        } : result
      ));

      // Add explosion effect for completed test
      if (passed) {
        const explosionParticles: LightParticle[] = [];
        for (let j = 0; j < 10; j++) {
          explosionParticles.push({
            id: `explosion-${i}-${j}`,
            x: window.innerWidth / 2 + (Math.random() - 0.5) * 100,
            y: window.innerHeight / 2 + (Math.random() - 0.5) * 100,
            vx: (Math.random() - 0.5) * 8,
            vy: (Math.random() - 0.5) * 8,
            life: 100,
            maxLife: 100,
            size: 2 + Math.random() * 3,
            color: '#00FF00',
            character: '✓'
          });
        }
        setLightParticles(prev => [...prev, ...explosionParticles]);
      }
    }

    setOverallStatus('completed');
    setIsSubmitting(false);
    setCurrentTestIndex(-1);
  };

  const getBlockColor = (status: TestCaseStatus, isActive: boolean) => {
    if (isActive && status === 'running') {
      return 'bg-gradient-to-br from-cyan-400 via-blue-500 to-purple-600 shadow-lg shadow-cyan-500/70';
    }
    switch (status) {
      case 'pending': return 'bg-slate-800/60 border border-slate-600/20';
      case 'running': return 'bg-gradient-to-br from-cyan-400 to-blue-500 shadow-md shadow-cyan-500/50';
      case 'passed': return 'bg-gradient-to-br from-green-400 to-emerald-500 shadow-md shadow-green-500/50';
      case 'failed': return 'bg-gradient-to-br from-red-400 to-pink-500 shadow-md shadow-red-500/50';
    }
  };

  return (
    <div className="h-screen bg-gradient-to-br from-black via-slate-900 to-black relative overflow-hidden">
      {/* Cosmic Background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-purple-900/30 via-transparent to-transparent"></div>
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_var(--tw-gradient-stops))] from-cyan-900/30 via-transparent to-transparent"></div>
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-transparent via-transparent to-black/50"></div>
      </div>

      {/* Floating Light Particles */}
      {lightParticles.length > 0 && (
        <div className="absolute inset-0 pointer-events-none">
          {lightParticles.map(particle => (
            <div
              key={particle.id}
              className="absolute rounded-full mix-blend-screen font-mono font-bold text-xs flex items-center justify-center"
              style={{
                left: particle.x,
                top: particle.y,
                width: particle.size * 2,
                height: particle.size * 2,
                background: `radial-gradient(circle, ${particle.color}, transparent)`,
                opacity: particle.life / particle.maxLife,
                boxShadow: `0 0 ${particle.size * 4}px ${particle.color}`,
                color: particle.color,
                transform: `scale(${particle.life / particle.maxLife})`,
                transition: 'all 0.1s ease-out'
              }}
            >
              {particle.character}
            </div>
          ))}
        </div>
      )}

      {/* Fixed Grid Layout */}
      <div className="relative z-10 h-full grid grid-rows-[auto_1fr_auto] p-8">
        {/* Header Section - Fixed */}
        <div className="text-center">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4 font-mono tracking-wider">
            ⟨ QUANTUM JUDGE ⟩
          </h1>
          <p className="text-cyan-300/60 text-lg font-mono">
            Code Transformation Engine
          </p>
        </div>

        {/* Main Content Container - Fixed */}
        <div className="flex items-center justify-center w-full">
          <div className="w-full max-w-6xl">

            {/* Content changes based on status but container stays fixed */}
            {overallStatus === 'idle' && (
              <div className="flex justify-center">
                <div className="w-full max-w-2xl">
                  {/* Code Input Terminal */}
                  <div className="bg-black/60 backdrop-blur-xl rounded-2xl border border-cyan-500/20 shadow-2xl overflow-hidden">
                    <div className="bg-gradient-to-r from-slate-900 to-slate-800 p-4 border-b border-cyan-500/20">
                      <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                        <div className="w-3 h-3 bg-yellow-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                        <span className="ml-4 text-cyan-400 font-mono text-sm">quantum-compiler.exe</span>
                      </div>
                    </div>

                    <div className="p-6">
                      <form onSubmit={handleSubmit}>
                        <div className="mb-6">
                          <textarea
                            className="w-full h-48 p-4 bg-black/80 border border-cyan-500/30 rounded-lg font-mono text-green-400 text-sm resize-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 focus:outline-none"
                            value={code}
                            onChange={(e) => setCode(e.target.value)}
                            placeholder="# Enter your quantum code here..."
                            disabled={isSubmitting}
                            style={{
                              textShadow: '0 0 10px rgba(34, 197, 94, 0.3)',
                            }}
                          />
                        </div>

                        <button
                          type="submit"
                          disabled={isSubmitting}
                          className="w-full py-4 bg-gradient-to-r from-cyan-600 via-purple-600 to-pink-600 text-white font-mono font-bold text-lg rounded-xl hover:from-cyan-500 hover:via-purple-500 hover:to-pink-500 transform hover:scale-105 transition-all duration-300 shadow-2xl shadow-cyan-500/25 relative overflow-hidden"
                        >
                          <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/20 via-purple-400/20 to-pink-400/20 animate-pulse"></div>
                          <span className="relative z-10 tracking-wider">⚡ TRANSMUTE CODE ⚡</span>
                        </button>
                      </form>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Code Transformation Phase */}
            {overallStatus === 'transforming' && (
              <div className="text-center">
                <div className="mb-8">
                  <div className="text-2xl font-mono text-cyan-300 mb-4">
                    ⟨ CODE TRANSMUTATION IN PROGRESS ⟩
                  </div>
                  <div className="w-96 h-2 bg-slate-800/50 rounded-full overflow-hidden mx-auto">
                    <div
                      className="h-full bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 transition-all duration-100 shadow-lg"
                      style={{ width: `${codeTransformProgress}%` }}
                    ></div>
                  </div>
                  <div className="mt-2 text-cyan-400/70 font-mono text-sm">
                    {codeTransformProgress}% QUANTUM CONVERSION
                  </div>
                </div>

                {/* Code disintegration effect */}
                <div className="font-mono text-green-400/60 text-sm space-y-1">
                  {floatingCodeElements.slice(0, 5).map((element, index) => (
                    <div
                      key={index}
                      className="animate-pulse"
                      style={{
                        animationDelay: `${index * 0.1}s`,
                        opacity: Math.max(0, 1 - (codeTransformProgress / 100) + Math.random() * 0.3)
                      }}
                    >
                      {element}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Floating Phase */}
            {overallStatus === 'floating' && (
              <div className="text-center">
                <div className="text-3xl font-mono text-cyan-300 mb-8 animate-pulse">
                  ⟨ QUANTUM FIELD ACTIVE ⟩
                </div>
                <div className="text-cyan-400/60 font-mono">
                  Code particles floating in dimensional space...
                </div>
              </div>
            )}

            {/* Test Execution Phase */}
            {(overallStatus === 'executing' || overallStatus === 'completed') && (
              <div className="text-center w-full">
                {/* Status Display */}
                <div className="mb-12">
                  <div className={`text-3xl font-mono mb-4 ${overallStatus === 'completed' ? 'text-green-300' : 'text-orange-300'}`}>
                    {overallStatus === 'completed' ? '⟨ QUANTUM ANALYSIS COMPLETE ⟩' : '⟨ QUANTUM ANALYSIS RUNNING ⟩'}
                  </div>

                  {overallStatus === 'executing' && (
                    <div className="text-cyan-400/70 font-mono">
                      Processing test matrix [{currentTestIndex + 1}/{MOCK_TEST_CASES.length}]
                    </div>
                  )}

                  {overallStatus === 'completed' && (
                    <div className="text-green-400/70 font-mono">
                      Analysis complete • {testResults.filter(r => r.status === 'passed').length}/{testResults.length} tests passed
                    </div>
                  )}
                </div>

                {/* Compact Progress Matrix */}
                <div className="mb-12">
                  {/* Progress Summary */}
                  <div className="flex justify-center items-center space-x-8 mb-6">
                    <div className="text-cyan-400/70 font-mono text-sm">
                      <span className="text-green-400 font-bold">{testResults.filter(r => r.status === 'passed').length}</span>
                      <span className="text-slate-400 mx-1">/</span>
                      <span className="text-white font-bold">{testResults.length}</span>
                      <span className="ml-2">PASSED</span>
                    </div>
                    {overallStatus === 'executing' && (
                      <div className="text-orange-400/70 font-mono text-sm">
                        RUNNING: <span className="text-orange-400 font-bold">#{currentTestIndex + 1}</span>
                      </div>
                    )}
                  </div>

                  {/* Micro Progress Blocks Grid */}
                  <div className="flex justify-center mb-8">
                    <div
                      className="grid gap-0.5 w-full max-w-7xl px-4 gap-y-4"
                      style={{
                        gridTemplateColumns: testResults.length <= 25
                          ? `repeat(${testResults.length}, 1fr)`
                          : testResults.length <= 50
                            ? 'repeat(25, 1fr)'
                            : 'repeat(20, 1fr)',
                        gridTemplateRows: testResults.length > 25
                          ? `repeat(${Math.ceil(testResults.length / (testResults.length <= 50 ? 25 : 20))}, 1fr)`
                          : 'none'
                      }}
                    >
                      {testResults.map((result, index) => (
                        <div
                          key={result.id}
                          className={`relative w-4 h-4 rounded-sm transition-all duration-300 ${getBlockColor(result.status, index === currentTestIndex)
                            }`}
                          style={{
                            transform: index === currentTestIndex ? 'scale(1.3)' : 'scale(1)',
                            zIndex: index === currentTestIndex ? 10 : 1,
                          }}
                          title={`Test ${index + 1}: ${result.name} ${result.score ? `(${result.score}pt)` : ''} ${result.executionTime ? `${result.executionTime}ms` : ''}`}
                        >
                          {/* Active test indicator */}
                          {result.status === 'running' && index === currentTestIndex && (
                            <div className="absolute inset-0 border border-white animate-ping rounded-sm"></div>
                          )}

                          {/* Success/Fail icons for larger active blocks */}
                          {index === currentTestIndex && result.status === 'passed' && (
                            <div className="absolute inset-0 flex items-center justify-center text-white text-xs font-bold">✓</div>
                          )}
                          {index === currentTestIndex && result.status === 'failed' && (
                            <div className="absolute inset-0 flex items-center justify-center text-white text-xs font-bold">✗</div>
                          )}

                          {/* Pulse effect for active test */}
                          {index === currentTestIndex && result.status === 'running' && (
                            <div className="absolute inset-0 bg-white/20 animate-pulse rounded-sm"></div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>

        {/* Footer Section - Fixed */}
        <div className="flex justify-center">
          {overallStatus === 'completed' && (
            <div className="flex space-x-4">
              <button
                onClick={() => {
                  resetSubmission();
                  // Regenerate with 100 test cases for demo
                  const newTests = generateTestCases(100);
                  setTestResults(newTests.map(tc => ({
                    id: tc.id,
                    name: tc.name,
                    status: 'pending' as TestCaseStatus
                  })));
                }}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-mono font-bold rounded-lg hover:from-purple-500 hover:to-pink-500 transition-all duration-300 shadow-lg"
              >
                🚀 TEST 100 CASES
              </button>
              <button
                onClick={resetSubmission}
                className="px-6 py-3 bg-gradient-to-r from-slate-700 to-slate-600 text-cyan-300 font-mono font-bold rounded-lg hover:from-slate-600 hover:to-slate-500 transition-all duration-300 shadow-lg border border-cyan-500/30"
              >
                ↻ RESET QUANTUM FIELD
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}