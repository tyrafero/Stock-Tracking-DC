# Stock Tracking DC - Frontend Dockerfile
# Multi-stage build for React + Vite application
# Based on InvenTree pattern

# ===========================
# Base Stage - Node.js
# ===========================
FROM node:20-alpine AS base

# Set working directory
WORKDIR /app

# Copy package files
COPY src/frontend/package*.json ./

# ===========================
# Development Target
# ===========================
FROM base AS development

# Install dependencies (including devDependencies)
RUN npm install

# Copy application code (will be mounted as volume in dev)
COPY src/frontend .

# Expose Vite dev server port
EXPOSE 5173

# Start Vite dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ===========================
# Builder Stage - Build React app
# ===========================
FROM base AS builder

# Install ALL dependencies (including devDependencies needed for build)
RUN npm ci

# Copy application code
COPY src/frontend .

# Set build-time environment variables
# Vite requires VITE_ prefixed vars at build time
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=${VITE_API_URL}
ENV DOCKER_BUILD=true

# Build the application
RUN npm run build

# ===========================
# Production Target - nginx
# ===========================
FROM nginx:alpine AS production

# Copy custom nginx configuration
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
