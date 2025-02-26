# Import app from jane2.py for backward compatibility
# This way, both the old monolithic and new modular structures work
from jane2 import app

if __name__ == "__main__":
    app.run()
