from app import create_app
import os

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # This is only used when running locally with python app.py
    # In Docker, this won't be executed as we use flask run or gunicorn
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0').lower() in ['true', '1', 'yes']
    app.run(host='0.0.0.0', port=port, debug=debug)
