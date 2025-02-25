/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {
    // This is optional but recommended for better tree-shaking
    outputFileTracingRoot: undefined,
  },
  env: {
    API_URL: process.env.API_URL,
    WS_URL: process.env.WS_URL,
    N8N_API_URL: process.env.N8N_API_URL,
  },
  // Enable runtime configuration
  serverRuntimeConfig: {
    // Will only be available on the server side
  },
  publicRuntimeConfig: {
    // Will be available on both server and client
    API_URL: process.env.API_URL,
    WS_URL: process.env.WS_URL,
    N8N_API_URL: process.env.N8N_API_URL,
  },
}

module.exports = nextConfig
