from flask import Flask, render_template, request, jsonify, redirect
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

@app.route('/<short_code>', methods=['GET'])
def redirect_to_url(short_code):
    url_data = urls_collection.find_one({"shortCode": short_code})
    if not url_data:
        return jsonify({"error": "Short URL not found"}), 404

    urls_collection.update_one({"shortCode": short_code}, {"$inc": {"accessCount": 1}})
    return redirect(url_data["url"])

@app.route('/shorten/<short_code>', methods=['GET'])
def get_url_details(short_code):
    url_data = urls_collection.find_one({"shortCode": short_code})
    if not url_data:
        return jsonify({"error": "Short URL not found"}), 404

    return jsonify({
        "url": url_data["url"],
        "shortCode": url_data["shortCode"],
        "accessCount": url_data["accessCount"]
    }), 200

@app.route('/shorten/<short_code>', methods=['DELETE'])
def delete_short_url(short_code):
    result = urls_collection.delete_one({"shortCode": short_code})
    if result.deleted_count == 0:
        return jsonify({"error": "Short URL not found"}), 404

    return '', 204

if __name__ == '__main__':
    app.run(debug=True)