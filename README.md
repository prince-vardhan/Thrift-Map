# Thrift-Map

A Flask + Leaflet thrift shop locator backed by MongoDB.

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Add a `.env` file with `MONGO_URI=your-mongodb-connection-string`.
4. Make sure your MongoDB database is named `ThriftMap` and your collection is `shops`.
5. Run the app with `python app.py`.
6. Open [http://localhost:5000](http://localhost:5000).

## Supported pin formats

The app accepts either of these document shapes:

```json
{
  "name": "Store Name",
  "description": "Vintage and thrift finds",
  "lat": 12.9716,
  "lng": 77.5946
}
```

```json
{
  "name": "Store Name",
  "description": "Vintage and thrift finds",
  "location": {
    "type": "Point",
    "coordinates": [77.5946, 12.9716]
  }
}
```

## Useful API routes

- `GET /api/pins` returns all pins as GeoJSON.
- `GET /api/search?q=term` returns matching pins as GeoJSON.
- `GET /api/pins?bbox=minLng,minLat,maxLng,maxLat` filters pins to a map viewport.
