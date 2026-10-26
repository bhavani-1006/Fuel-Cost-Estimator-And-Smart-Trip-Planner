# Project Documentation — TripWise AI Smart Fuel Cost Estimator & Smart Trip Planner

## 1. Overview
TripWise is a full-stack route-first trip fuel estimator. A user enters a starting place and destination; the application looks up a driving route and estimates distance, drive time, fuel requirement, and fuel cost. It includes a route map, trip history, chart, and optional browser voice input/output.

## 2. Problem statement
Travelers often have to search for a route, estimate fuel consumption, and calculate a budget separately. TripWise combines these steps into one interface and gives a transparent estimate before travel.

## 3. Objectives
- Require only origin and destination for the main workflow.
- Look up driving distance and estimated duration from a route service.
- Calculate fuel quantity and cost using configurable mileage and fuel-price assumptions.
- Show Google Maps directions, a cost visualization, and optional voice readout.
- Save results in a relational database and display trip history.
- Expose REST endpoints so the UI and future clients can use the backend.

## 4. Technology stack
| Layer | Technology | Files / purpose |
|---|---|---|
| Frontend markup | HTML + Jinja templates | `templates/base.html`, `index.html`, `history.html` |
| Styling | CSS | `static/style.css`, responsive layout |
| Browser logic | JavaScript | `static/app.js`, API calls, chart, voice, map |
| Backend | Python + Flask | `app.py`, page routes and REST endpoints |
| Data access | Flask-SQLAlchemy | ORM model and database persistence |
| Database | SQLite / MySQL | SQLite default; MySQL configuration and `schema.sql` |
| Route APIs | Nominatim + OSRM demo | Place lookup, driving distance and duration |
| Map UI | Google Maps embed/directions URL | Displays route and opens navigation |
| Chart | Chart.js | Visual cost display |
| Voice | Web Speech APIs | Browser-dependent speech recognition/synthesis |
| Tests | `unittest` | `tests/test_calculations.py` |

## 5. User workflow
1. User enters origin and destination only.
2. JavaScript calls `POST /api/route-estimate`.
3. Flask validates the input and geocodes each place.
4. The routing service returns a driving route distance and estimated duration.
5. Flask uses configured mileage and fuel-price defaults to calculate fuel litres and estimated cost.
6. The frontend displays the result, Google Maps route, chart, and travel notes.
7. If “Save this estimate” is selected, the result is stored in the configured database and appears on `/history`.

## 6. Calculation
- Fuel required (litres) = driving distance (km) ÷ assumed mileage (km/L)
- Fuel cost (₹) = fuel required (litres) × assumed fuel price (₹/L)
- Total shown by the route-only flow = estimated fuel cost (tolls, parking, meals and other expenses are excluded)

Default assumptions are `DEFAULT_MILEAGE_KMPL=15` and `DEFAULT_PETROL_PRICE=105`. These are editable example values; they are not live fuel prices or vehicle-specific measurements.

## 7. API endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Main route estimator |
| GET | `/history` | Saved trip history |
| POST | `/api/route-estimate` | Route lookup + automatic fuel estimate |
| POST | `/api/calculate` | General calculation endpoint retained for tests/advanced use |
| GET | `/api/analytics` | Summary and chart data from saved estimates |

See `API_DOCUMENTATION.md` for request/response examples.

## 8. Database
The `Trip` model stores origin, destination, distance, assumed mileage and fuel price, trip type, traveler count, fuel amount/cost, additional costs, total, per-person cost, and creation timestamp. SQLite is created automatically by the app. For MySQL, configure `DATABASE_URL` in `.env`; `schema.sql` is supplied as an optional manual schema. This version does not implement accounts or per-user history.

## 9. Setup
1. Install Python 3.10+ (recommended).
2. Create a virtual environment.
3. Run `python -m pip install -r requirements.txt`.
4. Optionally copy `.env.example` to `.env`.
5. Run `python app.py` and open `http://127.0.0.1:5000`.
6. Run tests using `python -m unittest discover -s tests -v`.

## 10. Limitations
- Route lookup needs internet and uses public demo services with usage limits. Choose a provider suitable for production before public deployment.
- Google Maps is shown as a map/directions embed; the numeric route distance is provided by OSRM, so it may differ from Google's route.
- Mileage is a configurable assumption and not inferred from a user's exact vehicle.
- Fuel price is configurable but not live.
- Browser voice support and available voices vary by browser and operating system. “Boss” and “Rap” are text/rate/pitch presets, not custom studio-generated voices.
- No user authentication, live LLM, live traffic pricing, toll integration, or accurate EV calculation is implemented.

## 11. Future roadmap
1. Add a commercial/official route provider, route alternatives, provider attribution and usage controls.
2. Integrate a reliable regional fuel-price source with timestamp and manual fallback.
3. Add saved vehicle profiles and user-selectable mileage/fuel type.
4. Add secure authentication, per-user trips, CSRF/session protections and data deletion.
5. Add optional LLM-based travel Q&A with server-side secrets and spending limits.
6. Add toll/parking estimates, budget alerts, export to CSV/PDF and actual-vs-estimated comparison.
7. Add a separate EV model using kWh/100 km and electricity tariffs.
8. Deploy with production WSGI, HTTPS, database migrations, logs, monitoring, backups and debug mode disabled.

## 12. Conclusion
TripWise combines a Flask API, web interface, relational persistence, route lookup, map display, and browser voice support. It is a learning/demo project with explicit assumptions; production use requires a reliable route provider, accurate fuel data, security review, and deployment hardening.
