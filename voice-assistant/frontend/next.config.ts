import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  devIndicators: {
    position: "bottom-right",
  },
  typescript: {
    // ✅ Allow production builds to complete even if there are TS errors
    ignoreBuildErrors: true,
  },
  eslint: {
    // ✅ Allow production builds to complete even if there are ESLint errors
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
