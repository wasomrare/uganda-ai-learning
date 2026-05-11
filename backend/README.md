# Uganda Primary AI Learning System — Backend

A production-grade, AI-powered backend for Uganda primary school education (P1–P7), aligned to the UNEB curriculum.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.1 + Django REST Framework |
| Database | PostgreSQL 15 |
| Cache & Queue | Redis 7 |
| Background Tasks | Celery + Celery Beat + Flower |
| Real-time | Django Channels (WebSocket) |
| AI (Primary) | Ollama (local — DeepSeek, Llama3, Mistral) |
| AI (Fallback) | OpenAI GPT-4o-mini / Google Gemini |
| Auth | JWT (SimpleJWT) + Token Blacklist |
| API Docs | Swagger (drf-spectacular) |
| Containerization | Docker + Docker Compose |
| Web Server | Nginx + Gunicorn |
| Storage | Local / Cloudinary / AWS S3 |

---

## Quick Start (Docker)

```bash
# 1. Clone and configure environment
cp .env.example .env
# Edit .env with your values

# 2. Build and start all services
docker-compose up --build -d

# 3. Check logs
docker-compose logs -f backend

# 4. Access the API
# Swagger UI:  http://localhost/api/v1/docs/
# Admin:       http://localhost/admin/
# Flower:      http://localhost:5555/
```

### Default Admin Credentials
```
username: admin
password: Admin@Uganda2024!
```
**Change immediately after first login.**

---

## Manual Setup (Development)

```bash
# Create virtualenv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set DB, Redis, SECRET_KEY

# Run migrations
python manage.py migrate

# Load curriculum seed data
python manage.py load_curriculum

# Create super admin
python manage.py create_superadmin

# Start development server
python manage.py runserver

# Start Celery worker (separate terminal)
celery -A config worker -l info

# Start Celery Beat (separate terminal)
celery -A config beat -l info
```

---

## Environment Variables

See `.env.example` for all required variables. Key ones:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `OLLAMA_BASE_URL` | Ollama local AI server URL |
| `OPENAI_API_KEY` | OpenAI API key (optional fallback) |
| `GEMINI_API_KEY` | Google Gemini key (optional fallback) |
| `JWT_SECRET_KEY` | JWT signing key |

---

## API Endpoints

Base URL: `http://localhost/api/v1/`

| Category | Endpoint |
|---|---|
| Auth | `/auth/login/`, `/auth/logout/`, `/auth/refresh/`, `/auth/reset-password/` |
| Users | `/users/` |
| Students | `/students/`, `/students/my-profile/` |
| Teachers | `/teachers/`, `/teachers/my-profile/` |
| Classes | `/classes/` |
| Subjects | `/subjects/` |
| Curriculum | `/curriculum/topics/`, `/curriculum/resources/` |
| Questions | `/questions/` |
| Assessments | `/assessments/`, `/assessments/{id}/start-attempt/`, `/assessments/{id}/submit-attempt/` |
| AI Engine | `/ai/generate/questions/`, `/ai/chat/`, `/ai/status/`, `/ai/mark/` |
| Analytics | `/analytics/me/`, `/analytics/student/{id}/`, `/analytics/class/{id}/`, `/analytics/admin/` |
| Gamification | `/gamification/profile/`, `/gamification/badges/` |
| Leaderboards | `/leaderboards/weekly/`, `/leaderboards/admin/` |
| Notifications | `/notifications/mine/`, `/notifications/broadcast/` |
| Holidays | `/holidays/`, `/holidays/my-packages/` |
| Revision | `/revision/` |
| Live Classes | `/live-classes/` |
| Recommendations | `/recommendations/mine/` |
| Performance | `/performance/ple/{student_id}/` |
| Dashboard | `/dashboard/admin/`, `/dashboard/teacher/`, `/dashboard/student/` |
| Sync | `/sync/upload/`, `/sync/download/`, `/sync/status/` |
| Reports | `/reports/` |
| Parent Portal | `/parent/children/` |
| Settings | `/settings/` |
| Audit Logs | `/audit/` |
| Docs | `/api/v1/docs/` (Swagger) |

---

## AI Engine

The AI engine uses a **provider fallback chain**:
1. **Ollama** (local, free — DeepSeek / Llama3 / Mistral)
2. **OpenAI** (cloud fallback — GPT-4o-mini)
3. **Gemini** (cloud fallback — Gemini 1.5 Flash)
4. **Template fallback** (offline — returns safe empty/default responses)

### AI Features
- Automated question generation per subject/topic/difficulty
- AI marking of short answers, fill-in-blank, compositions
- Personalised holiday revision plans
- Learning recommendations for struggling students
- AI tutor chatbot for students
- PLE readiness prediction

---

## Apps Overview

| App | Responsibility |
|---|---|
| `authentication` | JWT auth, device tracking, login history |
| `users` | Custom User model, roles, profiles |
| `students` | Student profiles, parents/guardians, AI profiles |
| `teachers` | Teacher profiles, class/subject assignments |
| `classes` | School classes (P1–P7, terms) |
| `subjects` | UNEB subjects with class-level mapping |
| `curriculum` | Topics, subtopics, learning resources |
| `question_bank` | All question types with answers and rubrics |
| `assessments` | Exams, quizzes, attempts, student answers |
| `ai_engine` | Ollama/OpenAI/Gemini integration, prompt templates |
| `analytics` | Subject/topic mastery, daily activity, class snapshots |
| `gamification` | XP, levels, coins, badges, streaks |
| `leaderboards` | Weekly/monthly/class rankings |
| `notifications` | Push notifications, announcements, reminders |
| `holidays` | Holiday packages, daily tasks, student progress |
| `revision` | Revision sessions with XP rewards |
| `live_classes` | WebSocket live class rooms, attendance |
| `chat` | WebSocket chat per room |
| `recommendations` | AI-generated personalised study recommendations |
| `performance` | PLE readiness scoring |
| `analytics` | Student/class/admin performance dashboards |
| `offline_sync` | Sync queue for Flutter offline-first support |
| `reports` | Report generation (PDF report cards, analytics) |
| `parent_portal` | Parent view of children's performance |
| `uploads` | File upload management |
| `audit_logs` | Request/action audit trail |
| `settings_app` | System-wide configuration key-value store |
| `dashboard` | Aggregated dashboard views per role |

---

## Celery Periodic Tasks

| Task | Schedule |
|---|---|
| Generate daily AI questions | Every day at 4:00 AM |
| Send revision reminders | Every day at 6:00 AM |
| Update weekly leaderboards | Every hour |
| Process daily analytics | Every day at midnight |
| Detect struggling learners | Every day at 3:00 AM |
| Generate weekly assessments | Every Monday at 5:00 AM |
| Process offline sync queue | Every 15 minutes |
| Cleanup expired tokens | Every day at 1:00 AM |
| Calculate mastery scores | Every 2 hours |

---

## WebSocket Endpoints

| URL | Purpose |
|---|---|
| `ws/notifications/` | Real-time push notifications |
| `ws/live-class/{room_id}/` | Live class rooms (chat + events) |
| `ws/chat/{room}/` | Teacher-student chat |

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific app tests
pytest apps/authentication/tests/ -v
```

---

## Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure PostgreSQL with SSL
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure Cloudinary or AWS S3 for media storage
- [ ] Set up Sentry for error monitoring
- [ ] Configure Firebase for push notifications
- [ ] Change default super admin password
- [ ] Set up daily database backups
