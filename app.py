from flask import Flask, request, render_template
import requests

app = Flask(__name__)

# 🔍 Obtener coordenadas y datos extendidos desde Nominatim
def obtener_coordenadas(ciudad):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={ciudad}&addressdetails=1"
    headers = {"User-Agent": "Mozilla/5.0"}  # Obligatorio para Nominatim
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return None
    data = res.json()
    if not data:
        return None

    lugar = data[0]
    return {
        "lat": float(lugar["lat"]),
        "lon": float(lugar["lon"]),
        "ciudad": lugar["address"].get("city", ciudad.title()),
        "distrito": lugar["address"].get("state", ""),
        "pais": lugar["address"].get("country", ""),
        "zona": lugar.get("display_name", "")
    }

# 🌦️ Obtener clima actual desde Open-Meteo
def obtener_clima(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    return res.json()

# 🚀 Página principal
@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    error = None

    if request.method == "POST":
        ciudad_input = request.form.get("ciudad")
        info = obtener_coordenadas(ciudad_input)

        if not info:
            error = f"No se encontró la ciudad: {ciudad_input}"
        else:
            data = obtener_clima(info["lat"], info["lon"])
            if not data or "current_weather" not in data:
                error = f"No se pudo obtener el clima de {ciudad_input}"
            else:
                resultado = {
                    "ciudad": info["ciudad"],
                    "distrito": info["distrito"],
                    "pais": info["pais"],
                    "zona": info["zona"],
                    "lat": info["lat"],
                    "lon": info["lon"],
                    "temperatura": data["current_weather"]["temperature"],
                    "viento": data["current_weather"]["windspeed"],
                    "hora": data["current_weather"]["time"],
                    "codigo": data["current_weather"]["weathercode"]
                }

    return render_template("index.html", resultado=resultado, error=error)

if __name__ == '__main__':
    app.run(debug=True)