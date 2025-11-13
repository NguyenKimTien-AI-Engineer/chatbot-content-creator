import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  allowedDevOrigins: ['*'],
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  experimental: {
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
    proxyTimeout: 300000, // 5 minutes timeout for proxy requests
  },
  // Disable WebSocket HMR in production
  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      // Disable HMR WebSocket in production
      config.plugins = config.plugins || [];
    }
    return config;
  },
  async rewrites() {
    // Use environment variables for API proxy in development
    const apiHost = process.env.NEXT_PUBLIC_SERVER_HOST || 'localhost';
    const apiPort = process.env.NEXT_PUBLIC_API_PORT || '8001';
    
    return [
      {
        source: '/api/:path*',
        destination: `http://${apiHost}:${apiPort}/api/:path*`,
      },
    ];
  },
  
  // Configure server options for better timeout handling
  serverRuntimeConfig: {
    // Increase timeout for API requests (5 minutes)
    timeout: 300000,
  },
};

export default nextConfig;
