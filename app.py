import streamlit as st
import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
import airportsdata
import pydeck as pdk
import math
import requests
from datetime import date, time, timedelta


# ==================================================
# SƏHİFƏ PARAMETRLƏRİ
# ==================================================

st.set_page_config(
    page_title="Flight Delay Predictor",
    page_icon="✈️",
    layout="wide"
)


# ==================================================
# MODEL VƏ MƏLUMATLARIN YÜKLƏNMƏSİ
# ==================================================

@st.cache_resource
def load_components():
    preprocessor = joblib.load("models/flight_preprocessor.joblib")

    model = xgb.XGBClassifier()
    model.load_model("models/flight_xgboost.json")

    threshold = joblib.load("models/optimal_threshold (2).pkl")

    airports = airportsdata.load("IATA")

    return preprocessor, model, threshold, airports


preprocessor, model, threshold, airports = load_components()


# ==================================================
# SÖZLÜKLƏR VƏ XƏRİTƏLƏŞDİRMƏ
# ==================================================

AIRLINE_NAMES = {
    "AA": "American Airlines",
    "DL": "Delta Air Lines",
    "UA": "United Airlines",
    "WN": "Southwest Airlines",
    "B6": "JetBlue Airways",
    "AS": "Alaska Airlines",
    "NK": "Spirit Airlines",
    "F9": "Frontier Airlines",
    "G4": "Allegiant Air",
    "HA": "Hawaiian Airlines",
    "EV": "ExpressJet",
    "OO": "SkyWest Airlines",
    "MQ": "Envoy Air",
    "YX": "Republic Airways"
}

WMO_WEATHER_MAP = {
    0: "Clear",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Drizzle",
    61: "Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Snowfall",
    73: "Moderate Snowfall",
    75: "Heavy Snowfall",
    77: "Snow Grains",
    80: "Rain Showers",
    85: "Snow Showers",
    95: "Thunderstorm"
}

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


# ==================================================
# SEÇİLMİŞ TARİX VƏ SAAT ÜZRƏ HAVA PROQNOZU (Open-Meteo)
# ==================================================

@st.cache_data(ttl=1800)
def fetch_scheduled_weather(lat, lon, target_date, target_hour):
    try:
        date_str = target_date.strftime("%Y-%m-%d")
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": [
                "surface_pressure",
                "wind_direction_10m",
                "wind_gusts_10m",
                "weather_code",
                "snowfall"
            ],
            "start_date": date_str,
            "end_date": date_str,
            "timezone": "auto"
        }
        res = requests.get(url, params=params, timeout=4)
        if res.status_code == 200:
            data = res.json()
            hourly = data.get("hourly", {})
            h_idx = min(max(target_hour, 0), 23)

            wmo_codes = hourly.get("weather_code", [])
            wmo_code = wmo_codes[h_idx] if len(wmo_codes) > h_idx else 0
            cond_name = WMO_WEATHER_MAP.get(wmo_code, "Clear")

            pressures = hourly.get("surface_pressure", [])
            wind_dirs = hourly.get("wind_direction_10m", [])
            wind_gusts = hourly.get("wind_gusts_10m", [])
            snows = hourly.get("snowfall", [])

            return {
                "pressure": pressures[h_idx] if len(pressures) > h_idx else np.nan,
                "wind_dir": wind_dirs[h_idx] if len(wind_dirs) > h_idx else np.nan,
                "wind_gusts": wind_gusts[h_idx] if len(wind_gusts) > h_idx else np.nan,
                "snowfall": snows[h_idx] if len(snows) > h_idx else 0.0,
                "condition": cond_name,
                "success": True
            }
    except Exception:
        pass
    return None


# ==================================================
# MƏSAFƏ VƏ XƏRİTƏ HESABLAMALARI
# ==================================================

def calculate_distance_miles(lat1, lon1, lat2, lon2):
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c)


def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    diff_lon = math.radians(lon2 - lon1)
    x = math.sin(diff_lon) * math.cos(lat2)
    y = (
        math.cos(lat1) * math.sin(lat2)
        - math.sin(lat1) * math.cos(lat2) * math.cos(diff_lon)
    )
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def create_flight_map(origin, destination):
    origin_airport = airports.get(origin)
    destination_airport = airports.get(destination)

    if not origin_airport or not destination_airport:
        return None

    origin_lat, origin_lon = origin_airport["lat"], origin_airport["lon"]
    destination_lat, destination_lon = destination_airport["lat"], destination_airport["lon"]

    route_data = [{"path": [[origin_lon, origin_lat], [destination_lon, destination_lat]]}]
    airport_points = pd.DataFrame({
        "lon": [origin_lon, destination_lon],
        "lat": [origin_lat, destination_lat],
        "airport": [origin, destination]
    })

    plane_lon = (origin_lon + destination_lon) / 2
    plane_lat = (origin_lat + destination_lat) / 2
    plane_angle = calculate_bearing(origin_lat, origin_lon, destination_lat, destination_lon)

    plane_data = pd.DataFrame({
        "lon": [plane_lon],
        "lat": [plane_lat],
        "angle": [plane_angle],
        "label": ["✈"]
    })

    route_layer = pdk.Layer(
        "PathLayer",
        data=route_data,
        get_path="path",
        get_color=[65, 155, 255],
        width_scale=20,
        width_min_pixels=4,
        pickable=False
    )

    points_layer = pdk.Layer(
        "ScatterplotLayer",
        data=airport_points,
        get_position="[lon, lat]",
        get_fill_color=[255, 255, 255],
        get_line_color=[65, 155, 255],
        line_width_min_pixels=2,
        get_radius=45000,
        radius_min_pixels=7,
        stroked=True
    )

    text_layer = pdk.Layer(
        "TextLayer",
        data=airport_points,
        get_position="[lon, lat]",
        get_text="airport",
        get_color=[255, 255, 255],
        get_size=18,
        get_pixel_offset=[0, -22],
        get_alignment_baseline="'bottom'",
        billboard=True
    )

    plane_layer = pdk.Layer(
        "TextLayer",
        data=plane_data,
        get_position="[lon, lat]",
        get_text="label",
        get_color=[75, 170, 255],
        get_size=42,
        get_angle="angle",
        get_pixel_offset=[0, 0],
        billboard=True
    )

    center_lat = (origin_lat + destination_lat) / 2
    center_lon = (origin_lon + destination_lon) / 2
    lat_diff = destination_lat - origin_lat
    lon_diff = destination_lon - origin_lon
    dist_deg = math.sqrt(lat_diff ** 2 + lon_diff ** 2)

    zoom = 3 if dist_deg > 50 else (4 if dist_deg > 20 else 5)

    return pdk.Deck(
        layers=[route_layer, points_layer, text_layer, plane_layer],
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=zoom,
            pitch=25,
            bearing=0
        ),
        map_style="dark"
    )


# ==================================================
# SHAP MODEL İZAHI
# ==================================================

def explain_prediction(processed_data):
    try:
        booster = model.get_booster()
        contributions = booster.predict(xgb.DMatrix(processed_data), pred_contribs=True)[0]
        feature_names = preprocessor.get_feature_names_out()

        contributions = contributions[:-1]
        if len(feature_names) != len(contributions):
            return None

        explanation = pd.DataFrame({
            "Feature": feature_names,
            "Contribution": contributions
        })
        explanation["Absolute_Contribution"] = explanation["Contribution"].abs()
        explanation = (
            explanation
            .sort_values("Absolute_Contribution", ascending=False)
            .head(6)
            .copy()
        )

        def readable_name(name):
            name = name.replace("num__", "").replace("cat__", "")
            replacements = {
                "DISTANCE": "Flight Distance",
                "DEP_HOUR": "Departure Hour",
                "WEATHER_SURFACE_PRESSURE": "Surface Pressure",
                "WEATHER_WIND_DIRECTION": "Wind Direction",
                "WEATHER_SNOWFALL": "Snowfall",
                "WEATHER_WIND_GUSTS": "Wind Gusts",
                "AIRLINE": "Airline",
                "MONTH": "Month",
                "DAY_OF_WEEK": "Day of Week",
                "WEATHER_CONDITION_NAME": "Weather Condition",
                "IS_WEEKEND": "Weekend",
                "IS_LONG_DISTANCE": "Long Distance",
                "PREV_FLIGHT_IS_DELAYED": "Previous Flight Delayed",
                "ORIGIN_AIRPORT": "Origin Airport",
                "DESTINATION_AIRPORT": "Destination Airport"
            }
            for key, value in replacements.items():
                if name == key:
                    return value
                if name.startswith(key + "_"):
                    return f"{value} ({name[len(key) + 1:]})"
            return name

        explanation["Feature"] = explanation["Feature"].map(readable_name)
        return explanation
    except Exception:
        return None


# ==================================================
# WHAT-IF SSENARİ ANALİZİ
# ==================================================

def run_what_if_analysis(base_row, current_prob):
    suggestions = []
    current_hour = base_row["DEP_HOUR"].values[0]
    current_airline = base_row["AIRLINE"].values[0]

    alternative_hours = [7, 10, 14, 20]
    for h in alternative_hours:
        if abs(h - current_hour) >= 2:
            sim_row = base_row.copy()
            sim_row["DEP_HOUR"] = h
            p_transformed = preprocessor.transform(sim_row)
            p_prob = model.predict_proba(p_transformed)[0][1]
            if p_prob < current_prob:
                suggestions.append({
                    "type": "Hour Change",
                    "text": f"Change departure time to {h:02d}:00",
                    "new_prob": p_prob,
                    "delta": current_prob - p_prob
                })

    alt_airlines = [a for a in airline_options if a != current_airline][:5]
    for a in alt_airlines:
        sim_row = base_row.copy()
        sim_row["AIRLINE"] = a
        p_transformed = preprocessor.transform(sim_row)
        p_prob = model.predict_proba(p_transformed)[0][1]
        if p_prob < current_prob - 0.05:
            suggestions.append({
                "type": "Airline Switch",
                "text": f"Switch airline to {AIRLINE_NAMES.get(a, a)} ({a})",
                "new_prob": p_prob,
                "delta": current_prob - p_prob
            })

    if suggestions:
        return sorted(suggestions, key=lambda x: x["delta"], reverse=True)[:3]
    return []


# ==================================================
# CSS DİZAYN TƏNZİMLƏMƏLƏRİ
# ==================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #07172F, #0A1D3B, #08152B);
    color: white;
}

.block-container {
    max-width: 1750px;
    padding-top: 4.5rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

h1, h2, h3, p, label {
    color: white !important;
}

.main-title {
    display: block;
    font-size: clamp(26px, 2.5vw, 36px);
    font-weight: 800;
    color: #F4F7FF;
    line-height: 1.3;
}

.title-highlight {
    color: #55A5FF;
}

.tagline {
    color: #B9C9E1 !important;
    font-size: 14px;
    font-style: italic;
    text-align: right;
    padding-top: 12px;
}

.header-line {
    height: 1px;
    background: linear-gradient(90deg, #24517D, #438DDF, #24517D);
    margin-top: 10px;
    margin-bottom: 18px;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: white;
    margin-bottom: 2px;
}

.section-subtitle {
    font-size: 13px;
    color: #B8C9DF;
    margin-bottom: 12px;
}

div[data-testid="stDeckGlJsonChart"] {
    border: 1px solid #29496D;
    border-radius: 14px;
    overflow: hidden;
}

.stSelectbox div[data-baseweb="select"] > div {
    background-color: #172E4D;
    color: white;
    border-color: #35577E;
}

.stDateInput input, .stTimeInput input {
    background-color: #172E4D !important;
    color: white !important;
    border-color: #35577E !important;
}

.distance-badge {
    background: #172E4D;
    border: 1px solid #35577E;
    border-radius: 8px;
    padding: 8px 12px;
    color: #91C7FF;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 12px;
}

.weather-forecast-badge {
    background: #0E2A47;
    border: 1px solid #3672AC;
    border-radius: 8px;
    padding: 9px 12px;
    font-size: 12px;
    color: #9CD0FF;
    margin-top: 6px;
    margin-bottom: 14px;
}

div.stButton > button {
    background: linear-gradient(90deg, #318CF0, #1766CE) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    height: 48px !important;
    width: 100% !important;
    margin-top: 15px !important;
}

div.stButton > button:hover {
    background: #55A5FF !important;
    color: #ffffff !important;
}

div.stButton > button p {
    color: #ffffff !important;
}

.result-panel {
    background: linear-gradient(145deg, #102543, #0D1D35);
    border: 1px solid #29496D;
    border-radius: 14px;
    padding: 18px;
    margin-top: 20px;
}

.result-box {
    background: #0D1E37;
    border: 1px solid #29496D;
    border-radius: 12px;
    padding: 14px;
    min-height: 95px;
    text-align: center;
}

.result-label {
    color: #B9C9E1;
    font-size: 12px;
    margin-bottom: 6px;
}

.result-value {
    color: white;
    font-size: 28px;
    font-weight: 800;
}

.status-box {
    background: #15243C;
    border: 1px solid #5A3449;
    border-radius: 12px;
    padding: 14px;
    min-height: 95px;
}

.status-danger {
    color: #FF6575;
    font-size: 17px;
    font-weight: 700;
}

.status-safe {
    color: #4DD3A7;
    font-size: 17px;
    font-weight: 700;
}

.status-description {
    color: #D2DDEC;
    font-size: 12px;
    margin-top: 6px;
}

.whatif-card {
    background: #0D2644;
    border-left: 4px solid #38A2FF;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 13px;
    color: #E6F0FA;
}

.footer {
    color: #8EA6C5;
    text-align: center;
    font-size: 12px;
    padding: 20px 0 5px 0;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# MODEL KATEQORİYALARI
# ==================================================

encoder = preprocessor.named_transformers_["cat"].named_steps["encoder"]

airline_options = list(encoder.categories_[0])
weather_options = list(encoder.categories_[1])
month_options = list(encoder.categories_[2])
origin_options = list(encoder.categories_[3])
destination_options = list(encoder.categories_[4])


# ==================================================
# KÖMƏKÇİ FORMATLAMALAR
# ==================================================

def format_airport(code):
    info = airports.get(code)
    if info:
        name = info.get("name", "")
        city = info.get("city", "")
        return f"{code} — {name} ({city})" if city else f"{code} — {name}"
    return code


def format_airline(code):
    full_name = AIRLINE_NAMES.get(code)
    return f"{code} — {full_name}" if full_name else code


# ==================================================
# HEADER
# ==================================================

h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.markdown("""
    <div class="main-title">
        ✈️ Flight Delay <span class="title-highlight">Predictor & Optimizer</span>
    </div>
    """, unsafe_allow_html=True)

with h_col2:
    st.markdown("""
    <div class="tagline">
        Plan smarter. Travel better.
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)


# ==================================================
# ƏSAS EKRAN: SOLDA XƏRİTƏ | SAĞDA PARAMETRLƏR
# ==================================================

map_col, form_col = st.columns([1.65, 1.35], gap="large")

with form_col:
    st.markdown('<div class="section-title">✈️ Flight Parameters</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Configure route, schedule & date</div>', unsafe_allow_html=True)

    col_orig, col_dest = st.columns(2)
    with col_orig:
        origin = st.selectbox(
            "🛫 Departure (Origin)",
            origin_options,
            index=origin_options.index("JFK") if "JFK" in origin_options else 0,
            format_func=format_airport
        )
    with col_dest:
        destination = st.selectbox(
            "🛬 Arrival (Destination)",
            destination_options,
            index=destination_options.index("LAX") if "LAX" in destination_options else 0,
            format_func=format_airport
        )

    origin_data = airports.get(origin)
    dest_data = airports.get(destination)

    if origin != destination and origin_data and dest_data:
        flight_distance = calculate_distance_miles(
            origin_data["lat"], origin_data["lon"],
            dest_data["lat"], dest_data["lon"]
        )
        st.markdown(
            f'<div class="distance-badge">📏 <b>Calculated Distance:</b> {flight_distance:,} miles</div>',
            unsafe_allow_html=True
        )
    else:
        flight_distance = 0
        st.markdown(
            '<div class="distance-badge" style="color:#FFA0A0;">Select different airports</div>',
            unsafe_allow_html=True
        )

    airline = st.selectbox(
        "Operating Airline",
        airline_options,
        format_func=format_airline
    )

    # Dəqiq Tarix və Saat Seçimi (Open-Meteo Forecast 16 günə qədər dəstəkləyir)
    col_date, col_time = st.columns(2)
    today = date.today()
    max_forecast_date = today + timedelta(days=15)

    with col_date:
        flight_date = st.date_input(
            "Scheduled Flight Date",
            value=today,
            min_value=today - timedelta(days=5),
            max_value=max_forecast_date
        )

    with col_time:
        dep_time_val = st.time_input(
            "Scheduled Departure Time",
            value=time(14, 0),
            step=1800
        )

    departure_hour = dep_time_val.hour

    # Tarixdən avtomatik Ay və Həftənin gününün çıxarılması
    month = MONTH_NAMES[flight_date.month - 1]
    day_of_week = flight_date.isoweekday()  # 1: Bazar ertəsi, 7: Bazar
    day_name = flight_date.strftime("%A")

    # Seçilmiş gün və saat üçün Open-Meteo proqnozunun çəkilməsi
    forecast_weather = None
    if origin_data:
        forecast_weather = fetch_scheduled_weather(
            origin_data["lat"],
            origin_data["lon"],
            flight_date,
            departure_hour
        )

    current_weather_cond = "Clear"
    if forecast_weather and forecast_weather.get("success"):
        cand_cond = forecast_weather["condition"]
        if cand_cond in weather_options:
            current_weather_cond = cand_cond
        elif "Clear" in weather_options:
            current_weather_cond = "Clear"
        else:
            current_weather_cond = weather_options[0]

        st.markdown(
            f"""
            <div class="weather-forecast-badge">
                🌦️ <b>Forecast ({flight_date.strftime('%b %d')} at {departure_hour:02d}:00):</b> {current_weather_cond} &nbsp;|&nbsp;
                Wind: {forecast_weather.get('wind_dir', 0):.0f}° &nbsp;|&nbsp;
                Gusts: {forecast_weather.get('wind_gusts', 0):.1f} km/h
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="weather-forecast-badge" style="color:#C6D8EE;">
                ℹ️ <b>Flight Schedule:</b> {day_name}, {month} {flight_date.day} (Historical/Average baseline used)
            </div>
            """,
            unsafe_allow_html=True
        )

    predict_btn = st.button(
        "✈️ PREDICT FLIGHT DELAY",
        use_container_width=True
    )


with map_col:
    st.markdown('<div class="section-title">🌎 Route Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Real-time path and airport alignment</div>', unsafe_allow_html=True)

    flight_map = create_flight_map(origin, destination)
    if flight_map:
        st.pydeck_chart(flight_map, use_container_width=True, height=620)
    else:
        st.warning("Airport coordinates unavailable for route mapping.")


# ==================================================
# MODEL TƏXMİNİ (INFERENCE)
# ==================================================

if predict_btn:
    if origin == destination:
        st.error("Origin and Destination airports must be different.")
    else:
        is_weekend = int(day_of_week in [6, 7])
        is_long_distance = int(flight_distance > 1500)

        p_pressure = forecast_weather["pressure"] if forecast_weather else np.nan
        p_wind_dir = forecast_weather["wind_dir"] if forecast_weather else np.nan
        p_wind_gusts = forecast_weather["wind_gusts"] if forecast_weather else np.nan
        p_snowfall = forecast_weather["snowfall"] if forecast_weather else np.nan

        input_df = pd.DataFrame([{
            "DISTANCE": flight_distance,
            "DEP_HOUR": departure_hour,
            "WEATHER_SURFACE_PRESSURE": p_pressure,
            "WEATHER_WIND_DIRECTION": p_wind_dir,
            "WEATHER_SNOWFALL": p_snowfall,
            "WEATHER_WIND_GUSTS": p_wind_gusts,
            "AIRLINE": airline,
            "MONTH": month,
            "DAY_OF_WEEK": day_of_week,
            "WEATHER_CONDITION_NAME": current_weather_cond,
            "IS_WEEKEND": is_weekend,
            "IS_LONG_DISTANCE": is_long_distance,
            "PREV_FLIGHT_IS_DELAYED": 0,
            "ORIGIN_AIRPORT": origin,
            "DESTINATION_AIRPORT": destination
        }])

        try:
            processed_data = preprocessor.transform(input_df)
            prob = float(model.predict_proba(processed_data)[0][1])
            is_delayed = int(prob >= threshold)
            shap_df = explain_prediction(processed_data)
            what_if_list = run_what_if_analysis(input_df, prob)

            st.session_state["res_prob"] = prob
            st.session_state["res_pred"] = is_delayed
            st.session_state["res_shap"] = shap_df
            st.session_state["res_whatif"] = what_if_list
            st.session_state["res_active"] = True

        except Exception as e:
            st.error(f"Prediction Pipeline Error: {e}")


# ==================================================
# NƏTİCƏLƏRİN ƏKS OLUNMASI
# ==================================================

if st.session_state.get("res_active", False):
    prob = st.session_state["res_prob"]
    pred = st.session_state["res_pred"]
    shap_df = st.session_state["res_shap"]
    what_if_list = st.session_state["res_whatif"]

    st.markdown('<div class="result-panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Prediction & Risk Diagnosis</div>', unsafe_allow_html=True)

    r_col1, r_col2, r_col3 = st.columns([1, 1, 1.5], gap="medium")

    with r_col1:
        st.markdown(
            f"""
            <div class="result-box">
                <div class="result-label">Estimated Delay Probability</div>
                <div class="result-value">{prob:.1%}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with r_col2:
        st.markdown(
            f"""
            <div class="result-box">
                <div class="result-label">Decision Threshold</div>
                <div class="result-value">{threshold:.0%}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with r_col3:
        if pred == 1:
            status_markup = """
            <div class="status-danger">⚠️ Flight is Likely to be Delayed</div>
            <div class="status-description">The probability reaches or exceeds the model's risk threshold. Proactive schedule buffering recommended.</div>
            """
        else:
            status_markup = """
            <div class="status-safe">✓ Flight is Expected On-Time</div>
            <div class="status-description">The risk is below the critical threshold under current flight and weather conditions.</div>
            """
        st.markdown(f'<div class="status-box">{status_markup}</div>', unsafe_allow_html=True)

    st.write("")
    st.progress(prob)

    exp_col, whatif_col = st.columns([1.5, 1.2], gap="large")

    with exp_col:
        st.markdown("#### 🔍 Key Risk Factors (Feature Impact)")
        if shap_df is not None and not shap_df.empty:
            for _, row in shap_df.iterrows():
                val = row["Contribution"]
                is_pos = val > 0
                color = "#FF5C6D" if is_pos else "#2ED573"
                badge_bg = "rgba(255, 92, 109, 0.15)" if is_pos else "rgba(46, 213, 115, 0.15)"
                label_text = "Increases delay risk" if is_pos else "Reduces delay risk"
                bar_pct = min(max(int(abs(val) * 120), 10), 100)

                st.markdown(
                    f"""
                    <div style="background:#0D1E37; border:1px solid #1F3A5E; border-radius:8px; padding:10px 12px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <span style="font-weight:600; font-size:13px; color:#F4F7FF;">{row['Feature']}</span>
                            <span style="background:{badge_bg}; color:{color}; border:1px solid {color}40; font-size:11px; padding:2px 8px; border-radius:12px; font-weight:600;">
                                {label_text} ({val:+.2f})
                            </span>
                        </div>
                        <div style="background-color:#172E4D; border-radius:4px; height:6px; width:100%; overflow:hidden;">
                            <div style="background-color:{color}; width:{bar_pct}%; height:6px; border-radius:4px;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            st.caption("🔴 Red: Factors increasing delay risk | 🟢 Green: Factors mitigating delay risk")
        else:
            st.info("Feature contributions could not be calculated.")

    with whatif_col:
        st.markdown("#### 💡 What-If Optimization Engine")
        if what_if_list:
            st.write("Alternative options to reduce your delay risk:")
            for item in what_if_list:
                st.markdown(
                    f"""
                    <div class="whatif-card">
                        <b>{item['type']}:</b> {item['text']}<br>
                        New Risk: <b>{item['new_prob']:.1%}</b>
                        <span style="color:#4DD3A7;">(↓ {item['delta']:.1%} lower)</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div class="whatif-card" style="border-left-color: #2ED573;">
                    Current flight selection already has an optimal schedule profile. No better alternative detected.
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# FOOTER
# ==================================================

st.markdown("""
<div class="footer">
    FLIGHT DELAY PREDICTION & OPTIMIZATION SYSTEM | ML CAPSTONE
</div>
""", unsafe_allow_html=True)