import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: process.env.NODE_ENV === "development" 
          ? "http://127.0.0.1:5000/api/:path*"  // Adjust the port if your Flask app uses a different one
          : "/api/:path*",
      },
    ];
  },
};

export default nextConfig;