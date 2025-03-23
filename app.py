from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import random
import string

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["url_shortener"]
urls_collection = db["urls"]

# Utility function to generate a random short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def create_short_url():
    data = request.json
    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    short_code = generate_short_code()
    url_data = {"url": original_url, "shortCode": short_code, "accessCount": 0}
    result = urls_collection.insert_one(url_data)

    return jsonify({"id": str(result.inserted_id), "shortCode": short_code}), 201

if __name__ == '__main__':
    app.run(debug=True)