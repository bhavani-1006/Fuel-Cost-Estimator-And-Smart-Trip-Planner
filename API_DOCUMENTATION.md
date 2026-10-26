# TripWise API Documentation

The Flask backend serves the HTML application and exposes JSON endpoints. Start the server with `python app.py`. Base URL for local development: `http://127.0.0.1:5000`.

## 1. Find route and estimate fuel

`POST /api/route-estimate`

Request JSON (only the two places are required):

```json
{
  "origin": "Hyderabad",
  "destination": "Vijayawada",
  "save_trip": true
}
```

`save_trip` is optional and defaults to false if omitted. The route lookup uses OpenStreetMap Nominatim for place search and the public OSRM demo routing service for driving distance/duration. The map displayed in the browser is a Google Maps embed/link.

Successful response example (values are illustrative, not a live route result):

```json
{
  "distance_km": 275.0,
  "duration_minutes": 240,
  "mileage_kmpl": 15.0,
  "fuel_price": 105.0,
  "fuel_liters": 18.33,
  "fuel_cost": 1925.0,
  "total_cost": 1925.0,
  "origin_label": "Hyderabad, Telangana, India",
  "destination_label": "Vijayawada, Andhra Pradesh, India",
  "recommendations": ["..."]
}
```

Defaults are configured with `DEFAULT_MILEAGE_KMPL` and `DEFAULT_PETROL_PRICE` in `.env`. These are assumptions, not vehicle detection or live fuel prices. Tolls, parking, meals and traffic-related changes are not included.

Errors return a JSON object with an `error` message and a 400 status. Route lookup needs an internet connection; public demo services have usage limits and are not intended for high-volume production use.

## 2. Manual calculation endpoint

`POST /api/calculate`

Accepts `distance_km`, `mileage_kmpl`, `fuel_price`, and optional `extra_cost`, `travelers`, `trip_type`, `origin`, `destination`, `save_trip`. This endpoint is retained for testing and advanced use; the main page uses the route-only endpoint.

## 3. Trip analytics

`GET /api/analytics` returns saved-trip count, total spend, average cost, and chart labels/costs.

## 4. Web pages

- `GET /` — route estimator UI
- `GET /history` — latest saved estimates

## 5. Database

SQLite is the default and is created automatically. To use MySQL, configure `DATABASE_URL` in `.env`, for example:

```text
DATABASE_URL=mysql+pymysql://trip_user:YOUR_PASSWORD@localhost:3306/trip_planner
```

You may use `schema.sql` to create the MySQL table manually. Do not commit real passwords or secrets.
