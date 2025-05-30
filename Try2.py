from datetime import datetime
import streamlit as st
import requests
import cohere
import base64
import pandas as pd
import folium
from streamlit_folium import st_folium

# === Enhanced UI Styling ===
def apply_custom_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    /* Weather card styling */
    .weather-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: white;
    }
    
    /* Metric card styling */
    .metric-card {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
        padding: 15px;
        border-radius: 12px;
        margin: 8px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Forecast card styling */
    .forecast-card {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05));
        padding: 15px;
        border-radius: 10px;
        margin: 5px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
    }
    
    /* AI Summary styling */
    .ai-summary {
        background: linear-gradient(145deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(255, 154, 158, 0.3);
        border-left: 5px solid #ff6b6b;
        color: #2c3e50;
        font-size: 16px;
        font-weight: 500;
    }
    
    /* Map container */
    .map-container {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    /* Title styling */
    .weather-title {
        font-size: 28px;
        font-weight: bold;
        color: white;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Enhanced Temperature Chart
def plot_enhanced_temperature_chart(data):
    try:
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Temperature Trends")
        
        forecast_list = data['list']
        chart_data = {
            "DateTime": [],
            "Temperature (°C)": [],
            "Feels Like (°C)": [],
            "Humidity (%)": []
        }

        for entry in forecast_list:
            date = datetime.fromtimestamp(entry['dt'])
            temp = entry['main']['temp'] - 273.15
            feels_like = entry['main']['feels_like'] - 273.15
            humidity = entry['main']['humidity']

            chart_data["DateTime"].append(date)
            chart_data["Temperature (°C)"].append(temp)
            chart_data["Feels Like (°C)"].append(feels_like)
            chart_data["Humidity (%)"].append(humidity)

        df = pd.DataFrame(chart_data)
        df.set_index("DateTime", inplace=True)

        # Create tabs for different charts
        tab1, tab2 = st.tabs(["🌡️ Temperature", "💧 Humidity"])
        
        with tab1:
            st.line_chart(df[["Temperature (°C)", "Feels Like (°C)"]])
        
        with tab2:
            st.line_chart(df[["Humidity (%)"]])
            
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error plotting enhanced chart: {str(e)}")

# Enhanced Weather Map
def create_weather_map(lat, lon, city_name, weather_data):
    try:
        # Create a folium map centered on the location with better tile options
        m = folium.Map(
            location=[lat, lon],
            zoom_start=11,
            tiles='OpenStreetMap',  # We'll add tiles manually for better control
            prefer_canvas=True
        )
        
        # Add multiple tile layer options
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='Street Map',
            overlay=False,
            control=True
        ).add_to(m)
        
        folium.TileLayer(
            tiles='CartoDB Positron',
            name='Light Map',
            overlay=False,
            control=True
        ).add_to(m)
        
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Get weather info for popup
        temp = weather_data['main']['temp'] - 273.15
        description = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        
        # Create enhanced popup content with better styling
        popup_content = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    width: 220px; padding: 10px; background: white; border-radius: 8px;">
            <h3 style="color: #2c3e50; margin: 0 0 10px 0; text-align: center; 
                       border-bottom: 2px solid #3498db; padding-bottom: 5px;">
                📍 {city_name}
            </h3>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; color: #e74c3c;">🌡️ Temperature:</span>
                    <span style="color: #2c3e50; font-weight: bold;">{temp:.1f}°C</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; color: #3498db;">☁️ Condition:</span>
                    <span style="color: #2c3e50;">{description.title()}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; color: #9b59b6;">💧 Humidity:</span>
                    <span style="color: #2c3e50;">{humidity}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; color: #1abc9c;">💨 Wind:</span>
                    <span style="color: #2c3e50;">{wind_speed} m/s</span>
                </div>
            </div>
        </div>
        """
        
        # Add weather marker with custom icon
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_content, max_width=250),
            tooltip=folium.Tooltip(f"🌤️ {city_name} Weather", sticky=True),
            icon=folium.Icon(
                color='red', 
                icon='cloud',
                prefix='fa'
            )
        ).add_to(m)
        
        # Add a styled circle to highlight the area
        folium.Circle(
            location=[lat, lon],
            radius=8000,
            popup=f"🌍 {city_name} Weather Zone",
            color='#3498db',
            fill=True,
            fillColor='#3498db',
            fillOpacity=0.2,
            opacity=0.8,
            weight=3
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None

# Enhanced Background Function
def set_local_background(WeatherBackground1):
    try:
        with open(WeatherBackground1, "rb") as img_file:
            b64_img = base64.b64encode(img_file.read()).decode()

        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{b64_img}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        # Fallback gradient background if image not found
        st.markdown(
            """
            <style>
            .stApp {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            </style>
            """,
            unsafe_allow_html=True
        )

def get_background_image_for_weather(description):
    description = description.lower()
    if "clear" in description:
        return "sunny.jpg"
    elif "cloud" in description:
        return "cloudy.webp"
    elif "rain" in description:
        return "rainy.jpg"
    elif "storm" in description or "thunder" in description:
        return "stormy.jpg"
    elif "snow" in description:
        return "snowy.webp"
    else:
        return "WeatherBackground1.jpg"

# Weather API Functions (Enhanced)
def get_weather_data(city, weather_api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + weather_api_key + "&q=" + city
    response = requests.get(complete_url)
    return response.json()

# Cohere AI Weather Summary
co = cohere.Client("S9HZs7bl6TAoVZHrPmTfK6ywe7gUVE3hMW4M6NGN")

def generate_weather_description(data):
    try:
        temperature = data['main']['temp'] - 273.15
        description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        
        prompt = f"""Generate a friendly, conversational weather summary for: 
        - Weather: {description} 
        - Temperature: {temperature:.1f}°C
        - Humidity: {humidity}%
        - Wind: {wind_speed} m/s
        
        Make it engaging and include practical advice for the day."""

        response = co.generate(
            model='command-r-plus',
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )

        return response.generations[0].text.strip()
    except Exception as e:
        return f"Current weather: {data['weather'][0]['description']} at {(data['main']['temp'] - 273.15):.1f}°C"

# Weekly Forecast Functions
def get_weekly_forecast(weather_api_key, lat, lon):
    complete_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={weather_api_key}"
    response = requests.get(complete_url)
    return response.json()

def get_weather_icon(description):
    description = description.lower()
    icons = {
        "clear": "☀️",
        "cloud": "☁️",
        "rain": "🌧️",
        "snow": "❄️",
        "storm": "⛈️",
        "thunder": "⛈️",
        "fog": "🌫️",
        "mist": "🌫️",
        "drizzle": "🌦️"
    }
    
    for key, icon in icons.items():
        if key in description:
            return icon
    return "🌤️"

def display_enhanced_weekly_forecast(data):
    try:
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)
        st.markdown("### 📅 7-Day Weather Forecast")
        
        displayed_dates = set()
        forecast_cards = []

        for day in data['list']:
            date_str = datetime.fromtimestamp(day['dt']).strftime('%A, %b %d')
            
            if date_str not in displayed_dates and len(forecast_cards) < 7:
                displayed_dates.add(date_str)
                
                min_temp = day['main']['temp_min'] - 273.15
                max_temp = day['main']['temp_max'] - 273.15
                description = day['weather'][0]['description']
                icon = get_weather_icon(description)
                
                forecast_cards.append({
                    'date': date_str,
                    'icon': icon,
                    'description': description.title(),
                    'min_temp': min_temp,
                    'max_temp': max_temp
                })

        # Display forecast cards in columns
        cols = st.columns(min(len(forecast_cards), 4))
        
        for i, card in enumerate(forecast_cards):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="forecast-card">
                    <h4>{card['date']}</h4>
                    <div style="font-size: 2em;">{card['icon']}</div>
                    <p><b>{card['description']}</b></p>
                    <p>🌡️ {card['max_temp']:.1f}°C / {card['min_temp']:.1f}°C</p>
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying enhanced forecast: {str(e)}")

# Enhanced Main App
def main():
    # Apply custom CSS
    apply_custom_css()
    
    # Set background
    set_local_background("WeatherBackground1.jpg")

    # Initialize session state
    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = None
    if 'city_name' not in st.session_state:
        st.session_state.city_name = ""
    if 'forecast_data' not in st.session_state:
        st.session_state.forecast_data = None

    # Enhanced title
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1 style='font-size: 60px; color: white; text-shadow: 3px 3px 6px black;
                   background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   background-clip: text;'>
            🌤️ Weather Forecast AI
        </h1>
        <p style='font-size: 20px; color: white; text-shadow: 1px 1px 3px black;'>
            Get detailed weather information with interactive maps
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced input section
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="weather-card">', unsafe_allow_html=True)
            city_input = st.text_input(
                "", 
                placeholder="🏙️ Enter city name (e.g., Manila, Philippines)",
                key="city_input",
                help="Enter any city name worldwide"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit = st.button("🔍 Get Weather Forecast", use_container_width=True)
            with col_btn2:
                clear = st.button("🔄 Clear Results", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Handle clear button
    if clear:
        st.session_state.weather_data = None
        st.session_state.city_name = ""
        st.session_state.forecast_data = None
        st.rerun()

    # Handle submit button
    if submit and city_input:
        with st.spinner('🌍 Fetching weather data and preparing map...'):
            weather_data = get_weather_data(city_input, "2bf4686b58e818560cb0aa13c5fd0722")

            if weather_data.get("cod") == 200 and "main" in weather_data:
                # Store data in session state
                st.session_state.weather_data = weather_data
                st.session_state.city_name = city_input
                
                # Get forecast data
                lat = weather_data['coord']['lat']
                lon = weather_data['coord']['lon']
                forecast_data = get_weekly_forecast("2bf4686b58e818560cb0aa13c5fd0722", lat, lon)
                st.session_state.forecast_data = forecast_data
                
                st.success("✅ Weather data loaded successfully!")
            else:
                st.error("🚫 City not found! Please check the spelling and try again.")
                
    # Display weather data if it exists in session state
    if st.session_state.weather_data:
        weather_data = st.session_state.weather_data
        city_input = st.session_state.city_name
        forecast_data = st.session_state.forecast_data
        
        # Dynamic background based on weather
        description = weather_data['weather'][0]['description']
        bg_image = get_background_image_for_weather(description)
        set_local_background(bg_image)

        # City header
        st.markdown(f"""
        <div class="weather-title">
            🌍 Weather Updates for {city_input.title()}
        </div>
        """, unsafe_allow_html=True)

        # Enhanced weather metrics
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)
        st.markdown("### 🌡️ Current Weather Conditions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        temp = weather_data['main']['temp'] - 273.15
        feels_like = weather_data['main']['feels_like'] - 273.15
        humidity = weather_data['main']['humidity']
        pressure = weather_data['main']['pressure']
        wind_speed = weather_data['wind']['speed']

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🌡️</h3>
                <h2>{temp:.1f}°C</h2>
                <p>Temperature</p>
                <small>Feels like {feels_like:.1f}°C</small>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>💧</h3>
                <h2>{humidity}%</h2>
                <p>Humidity</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🌀</h3>
                <h2>{pressure}</h2>
                <p>Pressure (hPa)</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>💨</h3>
                <h2>{wind_speed}</h2>
                <p>Wind (m/s)</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

        # AI Weather Summary
        weather_description = generate_weather_description(weather_data)
        st.markdown(f"""
        <div class="ai-summary">
            <h3>🤖 AI Weather Insights</h3>
            <p>{weather_description}</p>
        </div>
        """, unsafe_allow_html=True)

        # Weather Map
        lat = weather_data['coord']['lat']
        lon = weather_data['coord']['lon']
        
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        st.markdown("### 🗺️ Interactive Weather Map")
        
        weather_map = create_weather_map(lat, lon, city_input, weather_data)
        if weather_map:
            st_folium(weather_map, width=700, height=400)
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Enhanced forecasts
        if forecast_data and forecast_data.get("cod") != "404":
            display_enhanced_weekly_forecast(forecast_data)
            plot_enhanced_temperature_chart(forecast_data)
        else:
            st.error("❌ Error fetching forecast data!")

if __name__ == "__main__":
    main()