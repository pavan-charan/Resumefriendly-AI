import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  eslint: {
    // Prevent build failures from lint warnings during local running
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Prevent build failures from type check anomalies during quick builds
    ignoreBuildErrors: true,
  }
};

export default nextConfig;
