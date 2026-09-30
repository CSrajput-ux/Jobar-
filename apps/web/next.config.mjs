/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@jobpilot/shared"],
  images: {
    domains: ["images.unsplash.com", "storage.jobpilot.dev", "lh3.googleusercontent.com"],
  },
  async rewrites() {
    return [
      {
        source: "/api/py/:path*",
        destination: "http://127.0.0.1:8000/api/v1/:path*",
      },
    ];
  },
};

export default nextConfig;
