# LegacyLabs Setup Guide

## Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- PostgreSQL 14+
- Redis (for background tasks)
- FFmpeg (for video processing)

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd src/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:5173

## Backend Setup

1. Navigate to the backend directory:
```bash
cd src/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file with your configuration:
```bash
# Database
DATABASE_URL=postgresql://legacylabs:legacylabs@localhost/legacylabs

# Security
SECRET_KEY=your-secret-key-here

# AWS (for file storage)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=legacylabs-media

# AI Services
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
ELEVENLABS_API_KEY=your-elevenlabs-key

# Payment
STRIPE_SECRET_KEY=your-stripe-key

# Email
SENDGRID_API_KEY=your-sendgrid-key
```

6. Create the database:
```bash
createdb legacylabs
```

7. Run migrations:
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

8. Start the backend server:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## Additional Services

### Redis
Start Redis for background task processing:
```bash
redis-server
```

### Celery Worker
In a new terminal, start the Celery worker:
```bash
celery -A app.worker worker --loglevel=info
```

## Testing the Application

1. Open http://localhost:5173 in your browser
2. Create an account
3. Upload a GEDCOM file to test the documentary generation

## Production Deployment

For production deployment, consider:
- Using Docker containers
- Setting up a reverse proxy (Nginx)
- Using a production database (AWS RDS)
- Setting up a CDN for media files
- Implementing proper monitoring and logging

## Troubleshooting

### Common Issues

1. **Frontend won't start**: Make sure you're using Node.js 18+ and have run `npm install`

2. **Backend import errors**: Ensure you've activated the virtual environment and installed all dependencies

3. **Database connection errors**: Check that PostgreSQL is running and the connection string in `.env` is correct

4. **Video processing fails**: Ensure FFmpeg is installed and accessible in your PATH

## Support

For questions or issues, please check the documentation or open an issue on GitHub.
