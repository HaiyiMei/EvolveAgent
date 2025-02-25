# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Create public directory if it doesn't exist
RUN mkdir -p public

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

# Set environment to production
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV API_URL=http://evolve_agent:8000/api/v1
ENV WS_URL=ws://evolve_agent:8000/api/v1
ENV N8N_PUBLIC_URL=http://n8n:5678

# Copy necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.js ./next.config.js
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/.next/standalone ./

# Expose the port the app runs on
EXPOSE 3000

# Start the application
CMD ["node", "server.js"]
