/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverComponentsExternalPackages: ["socket.io", "ioredis", "bullmq"]
  }
};

export default nextConfig;
