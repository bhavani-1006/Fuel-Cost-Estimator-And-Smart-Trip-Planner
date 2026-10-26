# TripWise — AI Smart Fuel Cost Estimator & Smart Trip Planner

A full-stack, route-first travel fuel estimator. The main user workflow asks for only a **starting point** and **destination**. The Flask API looks up a driving route, then estimates driving distance, duration, fuel needed, and fuel cost. The page shows a Google Maps route, a cost chart, trip history, and browser-based voice input/output.

## Technology stack and project files

- **Frontend:** HTML (`templates/`), CSS (`static/style.css`), JavaScript (`static/app.js`)
- **Backend:** Python + Flask (`app.py`)
- **REST API:** `POST /api/route-estimate`, `POST /api/calculate`, `GET /api/analytics`
- **Database:** SQLite by default; MySQL supported through SQLAlchemy/PyMySQL (`schema.sql` included)
- **Route lookup:** OpenStreetMap Nominatim geocoding + public OSRM demo routing service
- **Map:** Google Maps embed and directions link
- **Chart:** Chart.js
- **Voice:** browser Web Speech APIs where supported
- **Tests:** Python `unittest` under `tests/`
- **Documentation:** `DOCUMENTATION.md` and `API_DOCUMENTATION.md`

## Run on Windows / VS Code

1. Extract the ZIP and open the extracted `TripWise_AI_Smart_Fuel_Cost_Estimator` folder in VS Code.
2. Open Terminal → New Terminal and verify `app.py` and `requirements.txt` appear when you run `dir`.
3. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat`.
4. Install dependencies: `python -m pip install -r requirements.txt`
5. Optional: copy `.env.example` to `.env` and adjust defaults.
6. Start: `python app.py`
7. Open `http://127.0.0.1:5000`.

## Route-only workflow

Enter only origin and destination, such as Hyderabad and Vijayawada. The backend geocodes both places and requests a driving route. It estimates fuel litres and fuel cost using configurable defaults:

- `DEFAULT_MILEAGE_KMPL=15` km/L
- `DEFAULT_PETROL_PRICE=105` rupees/L

Change these in `.env` if your usual vehicle or region differs. These values are **not automatically detected** and the petrol price is **not live**. The app cannot know your exact vehicle mileage unless you provide/configure it. Fuel cost is estimated as `distance_km / mileage_kmpl * fuel_price`.

The Google Maps embed/link lets you inspect the route and directions. Route distance/duration are returned by the selected route service and may differ from Google Maps. The public Nominatim/OSRM demo services need internet access and have usage limits; use a provider and terms suitable for production before deploying to many users.

## Database

SQLite is the default; the app creates its database tables on startup. To use MySQL, create a database/user and set `DATABASE_URL` in `.env`, for example:

```text
DATABASE_URL=mysql+pymysql://trip_user:YOUR_PASSWORD@localhost:3306/trip_planner
```

`schema.sql` contains an optional MySQL schema. Never commit real credentials or `.env`.

## Tests

After installing requirements, run:

```powershell
python -m unittest discover -s tests -v
```

## Honest limitations

- Fuel mileage is a configurable default, not automatically detected from a vehicle.
- Fuel price is a configurable default, not a live feed.
- Route lookup is internet-dependent and uses public demo services.
- The Google Maps display is separate from the OSRM route distance result.
- “Boss” and “Rap” voices adjust browser speech text/rate/pitch; a studio-quality voice is not guaranteed. Microphone and speech features depend on browser/device support and permissions.
- No login or per-user trip privacy is implemented yet.
- Tips are rule-based; no live LLM is connected.
- EV costs need a separate kWh/charging model and are not accurately represented by petrol mileage.

See `DOCUMENTATION.md` for project scope and roadmap, and `API_DOCUMENTATION.md` for API contracts.

## Latest UI changes
- First screen contains the Car/Bus/Bike/Auto selector, starting point, destination, editable mileage, fuel price and passenger count.
- Replaced trip type with an editable mileage input.
- Removed the “Your next adventure starts here” placeholder and “Follow your route” heading.
- Google Maps is shown on page load and updates to the chosen route after submission.
- New quote: “Every journey tells a story. Choose your ride, discover your route, and enjoy every mile along the way.”
- Added base.html and history.html templates.
- Mileage/fuel assumptions are examples, not live prices. Bus cost is vehicle fuel cost, not ticket fare. Auto uses driving directions as a map approximation.


## Install TripWise on a phone (PWA)

The header includes an **Install App** button. After you deploy this website to a public HTTPS domain, Android users can install it from a supported browser; on iPhone, open the site in Safari, tap Share, then **Add to Home Screen**. This is an installable web app (PWA), not yet a Google Play Store or Apple App Store listing. Store buttons/links must be updated with the real listing URLs only after you publish and pass each store's review.

Before public launch, configure production hosting/HTTPS, review third-party map service terms and limits, test on real Android/iPhone devices, and replace the development secret key.
