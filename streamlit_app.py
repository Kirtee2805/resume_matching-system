import sys
import os

# Ensure the root directory and app directory are in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, 'app')
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# Import and execute the deployment app
import app_deploy
