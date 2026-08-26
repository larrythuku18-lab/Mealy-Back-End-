"""
Convenience script to start the development server.
Usage: python run.py
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print('Starting Mealy Backend API...')
    print('API: http://localhost:5000')
    print('Health: http://localhost:5000/health')
    app.run(debug=True, host='0.0.0.0', port=5000)
