from flask import Flask, request, render_template
import requests

app = Flask(__name__)

# 🌤️ Diccionario para interpretar el código del clima
CLIMA_ESTADOS = {
    0: ("Despejado", "☀️"),
    1: ("Mayormente despejado", "🌤️"),
    2: ("Parcialmente nublado", "⛅"),
    3: ("Nublado", "☁️"),
    45: ("Niebla", "🌫️"),
    48: ("Niebla helada", "🌫️❄️"),
    51: ("Llovizna ligera", "🌦️"),
    53: ("Llovizna moderada", "🌧️"),
    55: ("Llovizna densa", "🌧️"),
    61: ("Lluvia ligera", "🌧️"),
    63: ("Lluvia moderada", "🌧️"),
    65: ("Lluvia fuerte", "🌧️"),
    80: ("Chubascos", "🌦️"),
    95: ("Tormenta", "⛈️"),
    99: ("Tormenta con granizo", "🌩️")
}

# 🔍 Obtener coordenadas desde Nominatim
def obtener_coordenadas(ciudad):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={ciudad}&addressdetails=1"
    headers = {"User-Agent": "Mozilla/5.0"}
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

# 🌦️ Obtener clima desde Open-Meteo
def obtener_clima(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    return res.json()

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
                codigo = data["current_weather"]["weathercode"]
                estado, icono = CLIMA_ESTADOS.get(codigo, ("Desconocido", "❓"))

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
                    "codigo": codigo,
                    "estado": estado,
                    "icono": icono
                }

    return render_template("index.html", resultado=resultado, error=error)

if __name__ == '__main__':
    app.run(debug=True)