from flask import Flask, request, render_template
import requests

app = Flask(__name__)

def obtener_coordenadas(ciudad):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={ciudad}"
    res = requests.get(url)
    data = res.json()
    if not data:
        return None, None
    return float(data[0]['lat']), float(data[0]['lon'])

def obtener_clima(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    res = requests.get(url)
    return res.json()

@app.route("/", methods=["GET", "POST"])
def index():
    clima = None
    error = None

    if request.method == "POST":
        ciudad = request.form.get("ciudad")
        lat, lon = obtener_coordenadas(ciudad)
        if lat is None or lon is None:
            error = f"No se encontró la ciudad: {ciudad}"
        else:
            data = obtener_clima(lat, lon)
            clima = {
                "ciudad": ciudad.title(),
                "temperatura": data["current_weather"]["temperature"],
                "viento": data["current_weather"]["windspeed"],
                "hora": data["current_weather"]["time"],
                "codigo": data["current_weather"]["weathercode"]
            }

    return render_template("index.html", clima=clima, error=error)

if __name__ == '__main__':
    app.run(debug=True)