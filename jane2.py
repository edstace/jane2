# This file is kept for backward compatibility with existing deployments
# For new development, use the modular structure in the app/ directory

# Import from new app structure
from app import create_app

# Create the application
app = create_app()

# This allows direct import from jane2 for older code
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime, timedelta
import openai
import re
import os
import logging
from logging.handlers import RotatingFileHandler
import json
from functools import wraps

# The rest of this file is kept for import compatibility
# but the actual functionality is provided by the app/ directory
# The app variable is already defined above and should be used by wsgi.py
# All functionality has been moved to the modular application structure in app/
# This file is now a compatibility wrapper around the new structure
# and routes all requests to the new application.
#
# For local development, use:
#   python run.py
#
# The code below this point is intentionally empty and exists only to satisfy
# possible imports from old code.

if __name__ == "__main__":
    app.run(debug=os.getenv('FLASK_ENV') == 'development')
