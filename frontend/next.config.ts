import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  webpack(config) {
    config.module.rules.push({
      test: /\.svg$/,
      use: [{ loader : '@svgr/webpack', options: { icon : true } }],
    });
    return config;
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: process.env.NODE_ENV === "development" 
          ? "http://127.0.0.1:5000/api/:path*"
          : "/api/:path*",
      },
    ];
  },
};

export default nextConfig;
