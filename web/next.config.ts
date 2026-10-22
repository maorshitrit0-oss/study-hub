import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Every page here is per-user and dynamic, so classic dynamic rendering is simpler than Cache Components.
  cacheComponents: false,
  serverExternalPackages: ["@google/genai", "mammoth"],
  experimental: { serverActions: { bodySizeLimit: "20mb" } },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
