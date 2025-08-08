'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface Particle {
  id: number;
  left: number;
  top: number;
  animationDuration: number;
  animationDelay: number;
  moveX: number;
  moveY: number;
}

interface ShootingStar {
  id: number;
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  duration: number;
  delay: number;
}

export function BackgroundLayer() {
  const [particles, setParticles] = useState<Particle[]>([]);
  const [shootingStars, setShootingStars] = useState<ShootingStar[]>([]);

  useEffect(() => {
    // クライアントサイドでのみパーティクルを生成
    const newParticles: Particle[] = Array.from({ length: 12 }, (_, i) => ({
      id: i,
      left: Math.random() * 100,
      top: Math.random() * 100,
      animationDuration: Math.random() * 10 + 10,
      animationDelay: Math.random() * 5,
      moveX: Math.random() * 200 - 100,
      moveY: Math.random() * 200 - 100,
    }));
    setParticles(newParticles);

    // 流れ星を生成
    const newShootingStars: ShootingStar[] = Array.from({ length: 3 }, (_, i) => ({
      id: i,
      startX: Math.random() * 50 + 100, // 右側から開始
      startY: Math.random() * 30, // 上部から
      endX: Math.random() * 50 - 50, // 左側へ
      endY: Math.random() * 30 + 70, // 下部へ
      duration: Math.random() * 2 + 1, // 1-3秒
      delay: Math.random() * 20 + 5, // 5-25秒の間隔
    }));
    setShootingStars(newShootingStars);
  }, []);

  return (
    <div className="fixed inset-0 overflow-hidden -z-10">
      {/* Base gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-50 via-slate-100 to-gray-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950" />
      
      {/* Gradient Orbs */}
      <div className="absolute inset-0">
        {/* Large floating orb - purple to indigo */}
        <motion.div
          className="absolute w-96 h-96 rounded-full opacity-30 dark:opacity-20"
          style={{
            background: 'radial-gradient(circle, rgba(147, 51, 234, 0.8) 0%, rgba(79, 70, 229, 0.4) 50%, transparent 100%)'
          }}
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          initial={{ x: -100, y: 100 }}
        />

        {/* Medium floating orb - indigo to blue */}
        <motion.div
          className="absolute w-72 h-72 rounded-full opacity-25 dark:opacity-15"
          style={{
            background: 'radial-gradient(circle, rgba(79, 70, 229, 0.6) 0%, rgba(59, 130, 246, 0.3) 50%, transparent 100%)'
          }}
          animate={{
            x: [0, -80, 0],
            y: [0, 60, 0],
            scale: [1, 0.9, 1],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 5
          }}
          initial={{ x: '60vw', y: '20vh' }}
        />

        {/* Small floating orb - blue to purple */}
        <motion.div
          className="absolute w-48 h-48 rounded-full opacity-30 dark:opacity-20"
          style={{
            background: 'radial-gradient(circle, rgba(59, 130, 246, 0.5) 0%, rgba(147, 51, 234, 0.25) 50%, transparent 100%)'
          }}
          animate={{
            x: [0, 50, 0],
            y: [0, -30, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 10
          }}
          initial={{ x: '80vw', y: '70vh' }}
        />
      </div>

      {/* Flowing Lines */}
      <div className="absolute inset-0">
        <motion.svg
          className="absolute w-full h-full opacity-20 dark:opacity-15"
          viewBox="0 0 1000 1000"
          fill="none"
        >
          <motion.path
            d="M0,300 Q250,100 500,300 T1000,300"
            stroke="url(#gradient1)"
            strokeWidth="2"
            fill="none"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{
              pathLength: { duration: 8, repeat: Infinity, ease: "easeInOut" },
              opacity: { duration: 2 }
            }}
          />
          <motion.path
            d="M0,700 Q250,500 500,700 T1000,700"
            stroke="url(#gradient2)"
            strokeWidth="1.5"
            fill="none"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{
              pathLength: { duration: 12, repeat: Infinity, ease: "easeInOut", delay: 4 },
              opacity: { duration: 3, delay: 2 }
            }}
          />
          
          <defs>
            <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgb(147, 51, 234)" stopOpacity="0.8" />
              <stop offset="50%" stopColor="rgb(79, 70, 229)" stopOpacity="0.6" />
              <stop offset="100%" stopColor="rgb(59, 130, 246)" stopOpacity="0.4" />
            </linearGradient>
            <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgb(59, 130, 246)" stopOpacity="0.6" />
              <stop offset="50%" stopColor="rgb(79, 70, 229)" stopOpacity="0.5" />
              <stop offset="100%" stopColor="rgb(147, 51, 234)" stopOpacity="0.4" />
            </linearGradient>
          </defs>
        </motion.svg>
      </div>

      {/* Subtle Particles */}
      <div className="absolute inset-0">
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            className="absolute w-2 h-2 bg-indigo-400/60 dark:bg-indigo-300/40 rounded-full"
            animate={{
              x: [0, particle.moveX],
              y: [0, particle.moveY],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: particle.animationDuration,
              repeat: Infinity,
              ease: "easeInOut",
              delay: particle.animationDelay,
            }}
            style={{
              left: `${particle.left}%`,
              top: `${particle.top}%`,
            }}
          />
        ))}
      </div>

      {/* Shooting Stars */}
      <div className="absolute inset-0">
        {shootingStars.map((star) => (
          <div key={star.id}>
            {/* 流れ星の軌跡 */}
            <motion.div
              className="absolute w-px h-px"
              style={{
                left: `${star.startX}%`,
                top: `${star.startY}%`,
              }}
              animate={{
                x: `${star.endX - star.startX}vw`,
                y: `${star.endY - star.startY}vh`,
              }}
              transition={{
                duration: star.duration,
                repeat: Infinity,
                repeatDelay: star.delay,
                ease: "easeOut",
              }}
            >
              {/* 流れ星本体 */}
              <motion.div
                className="relative"
                animate={{
                  opacity: [0, 1, 1, 0],
                }}
                transition={{
                  duration: star.duration,
                  repeat: Infinity,
                  repeatDelay: star.delay,
                  times: [0, 0.1, 0.9, 1],
                }}
              >
                {/* 流れ星の光点 */}
                <div className="w-1 h-1 bg-white rounded-full shadow-lg shadow-white/50" />
                
                {/* 流れ星の尻尾 */}
                <motion.div
                  className="absolute top-0 left-0 w-12 h-px opacity-80"
                  style={{
                    background: 'linear-gradient(to left, rgba(255, 255, 255, 0.8) 0%, rgba(147, 51, 234, 0.4) 50%, transparent 100%)',
                    transformOrigin: 'right center',
                  }}
                  animate={{
                    scaleX: [0, 1, 1, 0],
                    rotate: [0, 0, 0, 0],
                  }}
                  transition={{
                    duration: star.duration,
                    repeat: Infinity,
                    repeatDelay: star.delay,
                    times: [0, 0.2, 0.8, 1],
                  }}
                />
                
                {/* 流れ星のキラキラ効果 */}
                <motion.div
                  className="absolute -top-1 -left-1 w-3 h-3 border border-white/30 rounded-full"
                  animate={{
                    scale: [0, 1.5, 0],
                    opacity: [0, 0.6, 0],
                  }}
                  transition={{
                    duration: star.duration,
                    repeat: Infinity,
                    repeatDelay: star.delay,
                    times: [0, 0.5, 1],
                  }}
                />
              </motion.div>
            </motion.div>
          </div>
        ))}
      </div>

      {/* Mesh Gradient Overlay */}
      <div 
        className="absolute inset-0 opacity-40 dark:opacity-25"
        style={{
          background: `
            radial-gradient(circle at 20% 20%, rgba(147, 51, 234, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(79, 70, 229, 0.25) 0%, transparent 50%),
            radial-gradient(circle at 40% 60%, rgba(59, 130, 246, 0.2) 0%, transparent 50%)
          `
        }}
      />
    </div>
  );
}

export default BackgroundLayer;