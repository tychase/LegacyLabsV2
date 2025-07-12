# LegacyLabs - AI-Powered Family History Documentaries

Transform your family history data into beautiful, professionally narrated documentary videos using AI.

![LegacyLabs](https://img.shields.io/badge/LegacyLabs-AI%20Family%20Stories-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![React](https://img.shields.io/badge/React-18.2-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)

## 🎬 Overview

LegacyLabs transforms genealogical data (GEDCOM files) into emotionally compelling documentary videos. By leveraging AI technology, we create personalized narratives that bring family histories to life.

### Key Features

- 📊 **GEDCOM Processing**: Upload family tree data from Ancestry.com, MyHeritage, or any genealogy platform
- 🤖 **AI-Powered Narratives**: Claude/GPT-4 creates compelling stories from your data
- 🎙️ **Professional Narration**: Multiple voice options via ElevenLabs
- 🎨 **Smart Visuals**: Period-appropriate imagery and animations
- ✂️ **Editing Portal**: Customize your documentary after generation
- 💼 **B2B Solutions**: White-label options for funeral homes and genealogy services

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL 14+
- Redis
- FFmpeg

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tychase/LegacyLabsV2.git
   cd LegacyLabsV2
   ```

2. **Set up the frontend**
   ```bash
   cd src/frontend
   npm install
   cp .env.example .env
   npm run dev
   ```

3. **Set up the backend**
   ```bash
   cd src/backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   
   # Set up database
   createdb legacylabs
   alembic init alembic
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   
   # Run the server
   uvicorn app.main:app --reload
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🏗️ Architecture

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with custom theme
- **State Management**: Zustand
- **Data Fetching**: React Query
- **UI Components**: Custom components based on shadcn/ui

### Backend (FastAPI + Python)
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens
- **File Storage**: AWS S3
- **Background Tasks**: Celery with Redis
- **AI Services**: Claude API, OpenAI API, ElevenLabs API

### AI Pipeline
1. **GEDCOM Parser**: Extracts family relationships and events
2. **Narrative Engine**: AI generates compelling storylines
3. **Voice Synthesis**: ElevenLabs creates professional narration
4. **Visual Generation**: Selects period-appropriate imagery
5. **Video Assembly**: FFmpeg combines all elements

## 📁 Project Structure

```
LegacyLabsV2/
├── src/
│   ├── frontend/          # React application
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── stores/
│   │   │   └── lib/
│   │   └── package.json
│   └── backend/           # FastAPI application
│       ├── app/
│       │   ├── api/       # API endpoints
│       │   ├── core/      # Core configuration
│       │   ├── db/        # Database setup
│       │   ├── models/    # SQLAlchemy models
│       │   ├── schemas/   # Pydantic schemas
│       │   ├── services/  # Business logic
│       │   └── utils/     # Utilities
│       └── requirements.txt
├── docs/                  # Documentation
├── tests/                 # Test files
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create `.env` files in both frontend and backend directories:

**Frontend (.env)**
```env
VITE_API_URL=http://localhost:8000/api/v1
```

**Backend (.env)**
```env
DATABASE_URL=postgresql://user:password@localhost/legacylabs
SECRET_KEY=your-secret-key
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
ANTHROPIC_API_KEY=your-anthropic-key
# ... see .env.example for full list
```

## 🧪 Testing

```bash
# Frontend tests
cd src/frontend
npm test

# Backend tests
cd src/backend
pytest
```

## 📊 API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

- `POST /api/v1/auth/signup` - Create new account
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/projects` - List user's projects
- `POST /api/v1/projects` - Create new project (upload GEDCOM)
- `GET /api/v1/projects/{id}` - Get project details

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI components inspired by [shadcn/ui](https://ui.shadcn.com/)
- AI powered by [Anthropic Claude](https://anthropic.com/) and [OpenAI](https://openai.com/)
- Voice synthesis by [ElevenLabs](https://elevenlabs.io/)

## 📞 Contact

For questions or support, please open an issue on GitHub.

---

**LegacyLabs** - Where Every Family's Story Deserves to be Told
