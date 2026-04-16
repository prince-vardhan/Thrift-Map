import os
from flask import Flask, jsonify, render_template
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Connect to Atlas using the URI from your .env file
client = MongoClient(os.getenv("MONGO_URI"))
db = client.my_side_project  # Your database name
pins_collection = db.pins     # Your collection name

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/pins')
def get_pins():
    # Fetch all pins from MongoDB
    pins = list(pins_collection.find({}, {'_id': 0}))
    return jsonify(pins)

from flask import request

@app.route('/api/search')
def search_pins():
    query = request.args.get('q')
    if not query:
        return jsonify([])

    # Use $text search for better matching, or $regex for partial matches
    # This finds any pin where the name or description contains the query
    results = list(pins_collection.find(
        {"$text": {"$search": query}}, 
        {"_id": 0, "score": {"$meta": "textScore"}}
    ).sort([("score", {"$meta": "textScore"})]))

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)