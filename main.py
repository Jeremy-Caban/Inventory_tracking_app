from app import app
import os
import subprocess



port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)
    subprocess.run(["voila", "--enable_nbextensions=True", "--port=$PORT", "--no-browser", "frontend.ipynb"])