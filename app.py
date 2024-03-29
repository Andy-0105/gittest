from flask import Flask, render_template, jsonify
import sqlite3
import requests
from flask import request
import os
app = Flask(__name__)
api_key = 'AIzaSyCk-ZbUSppSGPaw-DJqeoik71rc3Jx-nRE'
def calculate_city_markers(coordinates):
    city_markers = {}
    for lat, lon in coordinates:
        city = reverse_geocode(lat, lon)
        if city:
            if city not in city_markers:
                city_markers[city] = 0
            city_markers[city] += 1
    return city_markers
def read_coordinates_from_database(database_file):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    cursor.execute('SELECT latitude, longitude FROM locations')
    raw_coordinates = cursor.fetchall()
    conn.close()
    coordinates = [{'latitude': lat, 'longitude': lon} for lat, lon in raw_coordinates]
    return coordinates,raw_coordinates
def reverse_geocode(latitude, longitude):
    url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}&language=zh-TW'
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data['status'] == 'OK':
        results = data.get('results', [])
        if results:
            address_components = results[0].get('address_components', [])
            for component in address_components:
                if 'administrative_area_level_1' in component['types']:
                    return component['long_name']
    return None

@app.route('/',methods=['GET', 'POST'])

def index():
    global database_path
    if request.method == 'GET':
        databaes_path = "coordinates.db"
        coordinates, raw_coordinates = read_coordinates_from_database(databaes_path)
        city_markers = calculate_city_markers(raw_coordinates)
        return render_template('map.html', coordinates=coordinates, city_markers=city_markers)
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)
            coordinates, raw_coordinates = read_coordinates_from_database(file_path)
            city_markers = calculate_city_markers(raw_coordinates)
            return render_template('map.html', coordinates=coordinates, city_markers=city_markers)
if __name__ == '__main__':
    app.run(debug=True)