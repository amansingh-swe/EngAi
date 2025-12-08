/**
 * Aman singh(67401334)
 * Sanmith Kurian (22256557)
 * Yash Agarwal (35564877)
 * Swapnil Nagras (26761683)
 */
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig


