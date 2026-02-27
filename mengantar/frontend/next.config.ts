import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/static/:path*",
        destination: "http://localhost:8000/static/:path*",
      },
    ];
  },
};

export default nextConfig;
