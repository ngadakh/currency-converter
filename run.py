# Run a test server.
from app.app import app, db

if __name__ == "__main__":
    # Build DB
    db.create_all()

    app.run(host='0.0.0.0', port=8080, debug=True)
