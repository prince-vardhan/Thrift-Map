import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from pymongo import GEOSPHERE, MongoClient, TEXT
from pymongo.errors import OperationFailure

load_dotenv()

app = Flask(__name__)

client = MongoClient(os.getenv("MONGO_URI"))
db = client.ThriftMap
pins_collection = db.shops


def ensure_indexes():
    """Create indexes once so the app can scale as the dataset grows."""
    try:
        pins_collection.create_index([("name", TEXT), ("description", TEXT)])
    except OperationFailure:
        pass

    try:
        pins_collection.create_index([("location", GEOSPHERE)])
    except OperationFailure:
        pass


def get_coordinates(pin):
    """Support both current lat/lng documents and future GeoJSON-style storage."""
    geometry = pin.get("geometry")
    if isinstance(geometry, dict) and geometry.get("type") == "Point":
        coordinates = geometry.get("coordinates", [])
        if len(coordinates) == 2:
            return coordinates

    location = pin.get("location")
    if isinstance(location, dict) and location.get("type") == "Point":
        coordinates = location.get("coordinates", [])
        if len(coordinates) == 2:
            return coordinates

    lat = pin.get("lat")
    lng = pin.get("lng")
    if lat is not None and lng is not None:
        return [float(lng), float(lat)]

    return None


def pin_to_feature(pin):
    coordinates = get_coordinates(pin)
    if not coordinates:
        return None

    properties = {
        "name": pin.get("name", "Unnamed pin"),
        "description": pin.get("description", ""),
        "category": pin.get("category", ""),
        "address": pin.get("address", ""),
    }

    for key, value in pin.items():
        if key in {"_id", "lat", "lng", "location", "geometry"}:
            continue
        if key not in properties:
            properties[key] = value

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": coordinates,
        },
        "properties": properties,
    }


def build_feature_collection(pins):
    features = []
    for pin in pins:
        feature = pin_to_feature(pin)
        if feature:
            features.append(feature)

    return {"type": "FeatureCollection", "features": features}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/pins")
def get_pins():
    bbox = request.args.get("bbox")
    pins = list(pins_collection.find({}, {"_id": 0}))

    if bbox:
        try:
            min_lng, min_lat, max_lng, max_lat = map(float, bbox.split(","))
        except ValueError:
            return jsonify({"error": "Invalid bbox format"}), 400

        filtered_pins = []
        for pin in pins:
            coordinates = get_coordinates(pin)
            if not coordinates:
                continue

            lng, lat = coordinates
            if min_lng <= lng <= max_lng and min_lat <= lat <= max_lat:
                filtered_pins.append(pin)

        pins = filtered_pins

    return jsonify(build_feature_collection(pins))


@app.route("/api/search")
def search_pins():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"type": "FeatureCollection", "features": []})

    try:
        results = list(
            pins_collection.find(
                {"$text": {"$search": query}},
                {"_id": 0, "score": {"$meta": "textScore"}},
            ).sort([("score", {"$meta": "textScore"})])
        )
    except OperationFailure:
        regex = {"$regex": query, "$options": "i"}
        results = list(
            pins_collection.find(
                {"$or": [{"name": regex}, {"description": regex}]},
                {"_id": 0},
            )
        )

    return jsonify(build_feature_collection(results))


ensure_indexes()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
