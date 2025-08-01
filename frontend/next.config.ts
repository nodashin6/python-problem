import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 実験的機能の有効化
  experimental: {
    // TypeScript設定の最適化
    typedRoutes: true,
  },
  
  // パフォーマンス最適化
  compiler: {
    // 本番環境でのconsole.log削除
    removeConsole: process.env.NODE_ENV === 'production',
  },
  
  // 画像最適化設定
  images: {
    formats: ['image/webp', 'image/avif'],
    domains: [],
  },
  
  // バンドル分析の設定
  webpack: (config, { dev, isServer }) => {
    // 本番環境でのバンドルサイズ最適化
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            enforce: true,
          },
        },
      };
    }
    
    return config;
  },
  
  // プロダクション最適化は自動的に有効化されます
  
  // 静的最適化
  trailingSlash: false,
  
  // セキュリティヘッダー
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
