# Deployment Guide - ResumeFriendly AI

This document provides step-by-step guidelines for building, configuring, and running the ResumeFriendly AI SaaS platform using Docker and Docker Compose.

---

## 1. Environment Variables configuration

Create a `.env` file in the root directory. Use these template variables:

```ini
# Global configuration
ENVIRONMENT=production

# Database config
POSTGRES_USER=resumefriendly_admin
POSTGRES_PASSWORD=SuperSecurePassword2026
POSTGRES_DB=resumefriendly_db
POSTGRES_HOST=postgres_db
POSTGRES_PORT=5432

# FastAPI Server config
BACKEND_PORT=8000
JWT_SECRET_KEY=b89e9005f32a514d33a6ea2d5e7ef3a31c5520a45b84c8a24bd6436f54dbf9ee
ACCESS_TOKEN_EXPIRE_MINUTES=60

# VectorDB config
CHROMADB_HOST=chroma_db
CHROMADB_PORT=8000

# Next.js Server config
NEXT_PUBLIC_API_URL=http://localhost:8000
PORT=3000
```

---

## 2. Docker Setup

The project relies on two main custom Dockerfiles: one for the backend (FastAPI) and one for the frontend (Next.js 15).

### 2.1 Backend Dockerfile (`backend/Dockerfile`)
```dockerfile
FROM python:3.12-slim

WORKDIR /workspace

# Install system dependencies for build tools and PDF parsing
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download local Sentence Transformers model to cache it during image build
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application files
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.2 Frontend Dockerfile (`frontend/Dockerfile`)
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]
```

---

## 3. Docker Compose Orchestration

A multi-container setup coordinates the components. See the root `docker-compose.yml` pattern below:

```yaml
version: '3.8'

services:
  postgres_db:
    image: postgres:15-alpine
    container_name: resumefriendly_postgres
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5

  chroma_db:
    image: chromadb/chroma:latest
    container_name: resumefriendly_chroma
    restart: always
    ports:
      - "8001:8000"
    volumes:
      - chromadata:/chroma/data

  backend_api:
    build: ./backend
    container_name: resumefriendly_backend
    restart: always
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=${ENVIRONMENT}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres_db:5432/${POSTGRES_DB}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}
      - CHROMADB_HOST=chroma_db
      - CHROMADB_PORT=8000
      - UPLOAD_DIR=/workspace/uploads
    volumes:
      - uploads_data:/workspace/uploads
    depends_on:
      postgres_db:
        condition: service_healthy
      chroma_db:
        condition: service_started

  frontend_app:
    build: ./frontend
    container_name: resumefriendly_frontend
    restart: always
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
    depends_on:
      - backend_api

volumes:
  pgdata:
  chromadata:
  uploads_data:
```

---

## 4. Run Commands

To deploy the application in production mode:
```bash
# 1. Spin up the cluster
docker-compose up -d --build

# 2. Check operational logs
docker-compose logs -f backend_api

# 3. Stop containers and clear active volumes
docker-compose down -v
```
