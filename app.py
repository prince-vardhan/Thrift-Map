import os
from flask import Flask, jsonify, render_template
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv() # Loads the MONGO_URI from your .env file

app = Flask(__name__)

# Connect to MongoDB Atlas
client = MongoClient(os.getenv("MONGO_URI"))
db = client.my_geodata_db

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/locations')
def get_locations():
    # Fetch data from MongoDB
    locations = list(db.markers.find({}, {'_id': 0}))
    return jsonify(locations)

if __name__ == '__main__':
    app.run(debug=True)