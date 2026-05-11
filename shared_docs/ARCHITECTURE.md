# Uganda Primary AI Learning System — Architecture Overview

## System Overview
AI-powered primary school learning ecosystem for P.1–P.7 learners following the Ugandan UNEB curriculum.

## Stack Summary

| Layer | Technology |
|-------|-----------|
| Backend | Django 5 + DRF + PostgreSQL + Redis + Celery + Channels |
| AI Engine | Ollama (local) + DeepSeek/Llama3/Mistral (primary), OpenAI/Gemini (optional) |
| Frontend | Next.js 14 + TypeScript + TailwindCSS + ShadCN |
| Mobile | Flutter (clean arch + Riverpod + Dio + Hive/Isar) |
| Realtime | Django Channels + WebSockets |
| Storage | Cloudinary / AWS S3 |
| Container | Docker + Docker Compose |

## Folder Structure
```
/project-root
  /backend        → Django REST API, AI engine, background jobs
  /frontend       → Next.js admin + teacher dashboard
  /flutter_app    → Student Flutter mobile app
  /shared_docs    → Architecture, API docs, ERDs
```

## Key Design Principles
- **AI-First**: System auto-generates questions, exams, holiday work, recommendations
- **Admin-Only Account Creation**: No public registration
- **Offline-First**: Flutter app fully functional offline with sync queues
- **Clean Architecture**: Each layer is modular and testable
- **Uganda-Optimized**: Low data usage, low-end Android support

## User Roles
1. **Super Admin** — Full system control, creates all accounts
2. **Teacher** — Reviews AI content, manages classes, overrides marks
3. **Student** — Uses Flutter app only
4. **Parent** — Future-ready (read-only portal)

## AI Engine Architecture
- Primary: Ollama running local models (DeepSeek, Llama3, Mistral)
- Secondary: OpenAI / Gemini API (optional, configurable)
- Fallback: Pre-generated template responses for offline mode
- Embeddings: SentenceTransformers for similarity/marking

## Data Flow
```
Student (Flutter) ──→ Django API ──→ PostgreSQL
                           ↓
                     AI Engine (Ollama/OpenAI)
                           ↓
                     Redis Cache + Celery Tasks
                           ↓
                     Analytics + Gamification
```
