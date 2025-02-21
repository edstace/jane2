# JANE - Job Assistance and Navigation Expert

JANE is an AI-powered job coaching assistant specializing in advising individuals with disabilities. It provides thoughtful, empathetic, and practical advice through both web interface and SMS.

## Features

- Web-based chat interface
- SMS integration via Twilio
- Conversation memory and context awareness
- Security checks for sensitive information
- Rate limiting and CSRF protection
- Redis caching

## Deployment to DigitalOcean

1. Create a new Droplet on DigitalOcean
2. Install required packages:
```bash
sudo apt update
sudo apt install python3-pip python3-venv redis-server nginx
```

3. Clone the repository:
```bash
git clone [your-repo-url]
cd [repo-name]
```

4. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

5. Install dependencies:
```bash
pip install -r requirements.txt
```

6. Create production environment file:
```bash
cp .env.example .env
# Edit .env with your production settings:
# - Set FLASK_ENV=production
# - Add your OpenAI API key
# - Add your Twilio credentials
# - Configure Redis settings
```

7. Configure Nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

8. Start the application:
```bash
gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 60
```

9. Configure Twilio webhook:
- Go to Twilio Console
- Navigate to Phone Numbers → Manage → Active numbers
- Click on your number
- Under 'Messaging Configuration':
  - Set webhook URL to: `https://your-domain.com/sms`
  - Set method to: POST

## Environment Variables

Create a `.env` file with the following variables:

```
# API Configuration
OPENAI_API_KEY=your_openai_api_key

# Security
SECRET_KEY=your_secret_key
FLASK_ENV=production

# Rate Limiting
RATELIMIT_DEFAULT=100 per day
RATELIMIT_STORAGE_URL=redis://localhost:6379/0

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL=3600

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

## Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start Redis server:
```bash
redis-server
```

3. Run the development server:
```bash
python jane2.py
```

## Security Notes

- Never commit `.env` file to version control
- Use HTTPS in production
- Keep Redis server secured and not publicly accessible
- Regularly update dependencies
- Monitor logs for suspicious activities
