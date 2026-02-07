// Configuration for GitHub Pages deployment
// This configures Next.js for static export compatible with GitHub Pages

/** @type {import('next').NextConfig} */
const nextConfig = {
  // output: 'export', // This enables static exports
  trailingSlash: true, // Recommended for GitHub Pages

  // Images need to be handled differently in static export
  images: {
    unoptimized: true, // Disable Next.js image optimization for static export
  },

  // GitHub Pages serves from a subdirectory if using project pages
  // Change this if you're using a custom domain or user pages
  basePath: '', // Set to '/repository-name' if deploying to project pages

  experimental: {
    serverActions: {
      allowedOrigins: [
        "localhost:3001",
        "10.255.255.254:3001",
        "frontendnew-iota.vercel.app",
        "frontend-7ee5ntc8y-abdul-qadir-khans-projects.vercel.app",
        
      ],
    },
  },
};

module.exports = nextConfig;