"""
簡化版本的Flask應用，用於測試Vercel部署
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        "message": "Hello from Vercel!",
        "status": "success",
        "app": "EPUB Converter Test"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "version": "1.0.0"
    })

# Vercel需要這個
application = app

if __name__ == '__main__':
    app.run(debug=True)
