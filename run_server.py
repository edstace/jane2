import subprocess
import time
import sys
from flask import Flask
from ngrok import ngrok
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_flask():
    """Start Flask server in a subprocess"""
    return subprocess.Popen([sys.executable, 'wsgi.py'])

def setup_ngrok():
    """Setup and start ngrok tunnel"""
    # Start ngrok tunnel
    tunnel = ngrok.connect(5000)
    public_url = tunnel.url()
    
    print(f"\nNgrok tunnel established at: {public_url}")
    print("\nIMPORTANT: Configure your Twilio webhook:")
    print(f"1. Go to https://console.twilio.com/")
    print(f"2. Navigate to Phone Numbers -> Manage -> Active numbers")
    print(f"3. Click on your number: {os.getenv('TWILIO_PHONE_NUMBER')}")
    print(f"4. Under 'Messaging Configuration':")
    print(f"   - Set webhook URL to: {public_url}/sms")
    print(f"   - Set method to: POST")
    print("\nYour SMS endpoint is now ready to receive messages!")
    
    return tunnel

def main():
    try:
        # Start Flask server
        flask_process = start_flask()
        print("Starting Flask server...")
        time.sleep(2)  # Give Flask time to start
        
        # Setup ngrok
        tunnel = setup_ngrok()
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            # Cleanup
            flask_process.terminate()
            ngrok.disconnect(tunnel.url())
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
