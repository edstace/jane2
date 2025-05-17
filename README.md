# JANE - Job Assistance and Navigation Expert

JANE is an AI-powered job coaching assistant specializing in advising individuals with disabilities. It provides thoughtful, empathetic, and practical advice through both web interface and SMS.

## Features

- Web-based chat interface
- SMS integration via Twilio
- Conversation memory and context awareness
- Security checks for sensitive information
- Rate limiting and CSRF protection
- MongoDB persistence and caching

## Deployment to DigitalOcean App Platform

1. Create MongoDB Database:
- Sign up for a free MongoDB Atlas account
- Create a new cluster
- Create a database user
- Get your connection string
- Create a database named 'jane_db'

2. Deploy to DigitalOcean:
- Go to https://cloud.digitalocean.com/apps
- Click "Create App"
- Connect your GitHub repository
- Select the main branch
- Select "Python" environment
- Configure Environment Variables:
  ```
  OPENAI_API_KEY=[your OpenAI key]
  FLASK_ENV=production
  SECRET_KEY=[generate a random string]
  MONGODB_URI=[your MongoDB connection string]
  TWILIO_ACCOUNT_SID=AC421d20ff98444b02f243e3a405f650db
  TWILIO_AUTH_TOKEN=c0c23d99054be6704a90438be7feb917
  TWILIO_PHONE_NUMBER=+18504981386
  ```
- Under "Run Command" enter:
  ```
  gunicorn wsgi:app --workers 4 --threads 2 --timeout 60
  ```

3. Configure Resources:
- Choose "Basic" plan ($5/month)
- Enable auto-deploy if desired
- Select region closest to your users

4. Configure Domain:
- Add your domain in the app settings
- Update DNS records as instructed
- Wait for SSL certificate to be issued

5. Configure Twilio webhook:
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
RATELIMIT_STORAGE_URI=redis://localhost:6379/0

# MongoDB Configuration
MONGODB_URI=your_mongodb_connection_string
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

2. Set up MongoDB:
- Create a free MongoDB Atlas account
- Create a cluster and database
- Add your connection string to .env file

3. Run the development server:
```bash
python run.py
```
## Running Tests

Run the unit tests with:
```bash
pytest
```


## Security Notes

- Never commit `.env` file to version control
- Use HTTPS in production
- Use strong MongoDB Atlas passwords
- Enable IP whitelist in MongoDB Atlas
- Regularly update dependencies
- Monitor logs for suspicious activities
