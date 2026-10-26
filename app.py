import os
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()
app=Flask(__name__)
app.config['SECRET_KEY']=os.getenv('SECRET_KEY','dev-only-change-me')
url=os.getenv('DATABASE_URL','sqlite:///trip_planner.db')
if url.startswith('mysql://'): url=url.replace('mysql://','mysql+pymysql://',1)
app.config['SQLALCHEMY_DATABASE_URI']=url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
class Trip(db.Model):
 id=db.Column(db.Integer,primary_key=True)
 origin=db.Column(db.String(120),nullable=False,default='Not specified')
 destination=db.Column(db.String(120),nullable=False,default='Not specified')
 distance_km=db.Column(db.Float,nullable=False); mileage_kmpl=db.Column(db.Float,nullable=False); fuel_price=db.Column(db.Float,nullable=False)
 trip_type=db.Column(db.String(20),nullable=False); travelers=db.Column(db.Integer,nullable=False)
 fuel_liters=db.Column(db.Float,nullable=False); fuel_cost=db.Column(db.Float,nullable=False); extra_cost=db.Column(db.Float,nullable=False)
 total_cost=db.Column(db.Float,nullable=False); cost_per_person=db.Column(db.Float,nullable=False)
 created_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
def calculate_trip(data):
 d=float(data.get('distance_km',0)); m=float(data.get('mileage_kmpl',0)); p=float(data.get('fuel_price',0)); e=float(data.get('extra_cost',0)); n=int(data.get('travelers',1)); kind=data.get('trip_type','one-way')
 if d<=0: raise ValueError('Distance must be greater than 0 km.')
 if m<=0: raise ValueError('Vehicle mileage must be greater than 0 km/l.')
 if p<0 or e<0: raise ValueError('Fuel price and extra expenses cannot be negative.')
 if n<1 or n>100: raise ValueError('Travelers must be between 1 and 100.')
 if kind not in ('one-way','round-trip'): raise ValueError('Choose one-way or round-trip.')
 distance=d*(2 if kind=='round-trip' else 1); liters=distance/m; fuel=liters*p; total=fuel+e
 return {'distance_km':round(distance,2),'fuel_liters':round(liters,2),'fuel_cost':round(fuel,2),'extra_cost':round(e,2),'total_cost':round(total,2),'cost_per_person':round(total/n,2),'travelers':n,'trip_type':kind}
def tips(r): return ['This estimate uses the default car mileage and petrol price shown below.','Keep a 10–15% buffer for tolls, traffic, detours, and price changes.','Actual mileage changes with traffic, AC use, load, and driving style.']

def route_details(origin, destination):
    if not origin.strip() or not destination.strip():
        raise ValueError('Enter both a starting point and a destination.')
    headers = {'User-Agent': 'TripWiseTripPlanner/1.0 (route estimate demo)'}
    def geocode(place):
        response = requests.get('https://nominatim.openstreetmap.org/search', params={'q': place, 'format': 'jsonv2', 'limit': 1, 'countrycodes': 'in'}, headers=headers, timeout=15)
        response.raise_for_status()
        items = response.json()
        if not items: raise ValueError(f'Could not find “{place}”. Try adding the city or state.')
        return float(items[0]['lon']), float(items[0]['lat']), items[0].get('display_name', place)
    start = geocode(origin); end = geocode(destination)
    route = requests.get(f'https://router.project-osrm.org/route/v1/driving/{start[0]},{start[1]};{end[0]},{end[1]}', params={'overview':'false','steps':'false'}, timeout=20)
    route.raise_for_status(); payload = route.json()
    if payload.get('code') != 'Ok' or not payload.get('routes'): raise ValueError('Could not calculate a driving route for these places.')
    item = payload['routes'][0]
    return {'distance_km': round(item['distance']/1000, 1), 'duration_minutes': round(item['duration']/60), 'origin_label': start[2], 'destination_label': end[2]}

@app.post('/api/route-estimate')
def api_route_estimate():
    data = request.get_json(silent=True) or {}
    try:
        route = route_details(str(data.get('origin', '')), str(data.get('destination', '')))
        vehicle = str(data.get('vehicle_type', 'car')).lower()
        trip_direction = str(data.get('trip_direction', 'one-way')).lower()
        travelers = int(data.get('travelers', 1))
        profiles = {
            'car': {'mileage': 15.0, 'price': float(os.getenv('DEFAULT_PETROL_PRICE', '105')), 'unit': 'L', 'fuel': 'petrol'},
            'bike': {'mileage': 40.0, 'price': float(os.getenv('DEFAULT_PETROL_PRICE', '105')), 'unit': 'L', 'fuel': 'petrol'},
            'bus': {'mileage': 4.0, 'price': float(os.getenv('DEFAULT_DIESEL_PRICE', '90')), 'unit': 'L', 'fuel': 'diesel'},
                    }
        if vehicle not in profiles:
            raise ValueError('Choose car, bus, or bike.')
        if trip_direction not in ('one-way', 'round-trip'):
            raise ValueError('Choose one-way or round trip.')
        if travelers < 1 or travelers > 100:
            raise ValueError('Passengers must be between 1 and 100.')
        profile = profiles[vehicle]
        distance = route['distance_km'] * (2 if trip_direction == 'round-trip' else 1)
        duration = route['duration_minutes'] * (2 if trip_direction == 'round-trip' else 1)
        # User-editable values override the default assumptions for the selected vehicle.
        mileage = float(data.get('mileage', profile['mileage']))
        fuel_price = float(data.get('fuel_price', profile['price']))
        if mileage <= 0:
            raise ValueError('Mileage must be greater than 0.')
        if fuel_price <= 0:
            raise ValueError('Fuel price must be greater than 0.')
        liters = distance / mileage
        cost = liters * fuel_price
        route.update({
            'distance_km': round(distance, 1), 'duration_minutes': duration,
            'vehicle_type': vehicle, 'fuel_type': profile['fuel'], 'fuel_unit': profile['unit'],
            'mileage_kmpl': mileage, 'fuel_price': fuel_price,
            'fuel_liters': round(liters, 2), 'fuel_cost': round(cost, 2),
            'total_cost': round(cost, 2), 'cost_per_person': round(cost / travelers, 2),
            'travelers': travelers, 'trip_type': trip_direction, 'extra_cost': 0,
            'recommendations': [
                f"Estimate uses an assumed {mileage:g} km per {profile['unit']} and {profile['fuel']} at ₹{fuel_price:.2f} per {profile['unit']}.",
                'Bus estimate is the estimated fuel cost for the whole bus, not a passenger ticket fare.',
                'Distance and duration are estimates from a road-routing service; use Google Maps for the selected mode, live traffic, transit options, and closures.'
            ]
        })
        if str(data.get('save_trip', 'false')).lower() in ('true', '1', 'yes'):
            trip = Trip(origin=str(data['origin'])[:120], destination=str(data['destination'])[:120], distance_km=distance, mileage_kmpl=mileage, fuel_price=fuel_price, trip_type=trip_direction, travelers=travelers, fuel_liters=route['fuel_liters'], fuel_cost=route['fuel_cost'], extra_cost=0, total_cost=route['total_cost'], cost_per_person=route['cost_per_person'])
            db.session.add(trip); db.session.commit(); route['saved_trip_id'] = trip.id
        return jsonify(route)
    except (ValueError, TypeError, requests.RequestException) as ex:
        return jsonify({'error': str(ex) if isinstance(ex, ValueError) else 'Route lookup failed. Check your internet connection and try again.'}), 400
@app.route('/')
def index(): return render_template('index.html')

@app.get('/service-worker.js')
def service_worker():
    from flask import send_from_directory
    response = send_from_directory(app.static_folder, 'service-worker.js', mimetype='application/javascript')
    response.headers['Service-Worker-Allowed'] = '/'
    response.headers['Cache-Control'] = 'no-cache'
    return response
@app.route('/history')
def history(): return render_template('history.html',trips=Trip.query.order_by(Trip.created_at.desc()).limit(100).all())
@app.post('/api/calculate')
def api_calculate():
 data=request.get_json(silent=True) or request.form.to_dict()
 try:
  r=calculate_trip(data)
  if str(data.get('save_trip','false')).lower() in ('true','1','yes'):
   t=Trip(origin=(data.get('origin') or 'Not specified')[:120],destination=(data.get('destination') or 'Not specified')[:120],distance_km=r['distance_km'],mileage_kmpl=float(data['mileage_kmpl']),fuel_price=float(data['fuel_price']),trip_type=r['trip_type'],travelers=r['travelers'],fuel_liters=r['fuel_liters'],fuel_cost=r['fuel_cost'],extra_cost=r['extra_cost'],total_cost=r['total_cost'],cost_per_person=r['cost_per_person']); db.session.add(t); db.session.commit(); r['saved_trip_id']=t.id
  r['recommendations']=tips(r); return jsonify(r)
 except (ValueError,TypeError,KeyError) as ex: return jsonify({'error':str(ex) or 'Please check the entered values.'}),400
@app.get('/api/analytics')
def analytics():
 ts=Trip.query.order_by(Trip.created_at.asc()).all(); return jsonify({'count':len(ts),'total_spend':round(sum(t.total_cost for t in ts),2),'average_cost':round(sum(t.total_cost for t in ts)/len(ts),2) if ts else 0,'labels':[t.created_at.strftime('%d %b %H:%M') for t in ts[-20:]],'costs':[t.total_cost for t in ts[-20:]]})
with app.app_context(): db.create_all()
if __name__=='__main__': app.run(debug=os.getenv('FLASK_DEBUG','false').lower()=='true')
