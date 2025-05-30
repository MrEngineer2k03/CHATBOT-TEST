from datetime import datetime
import streamlit as st
import requests
import cohere
import base64
import pandas as pd
import folium
from streamlit_folium import st_folium

# Temp Chart
def plot_temperature_chart(data):
    try:
        st.subheader("Temperature Chart")
        
        forecast_list = data['list']
        chart_data = {
            "Date": [],
            "Min Temp (°C)": [],
            "Max Temp (°C)": []
        }

        for entry in forecast_list:
            date = datetime.fromtimestamp(entry['dt']).strftime('%Y-%m-%d %H:%M')
            min_temp = entry['main']['temp_min'] - 273.15
            max_temp = entry['main']['temp_max'] - 273.15

            chart_data["Date"].append(date)
            chart_data["Min Temp (°C)"].append(min_temp)
            chart_data["Max Temp (°C)"].append(max_temp)

        df = pd.DataFrame(chart_data)
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)

        st.line_chart(df)
    except Exception as e:
        st.error("Error plotting chart: " + str(e))

# === Function to add background image ===
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
        return "WeatherBackground1.jpg"  # Optional fallback

# === Interactive Weather Map Function ===
def create_weather_map(lat, lon, city_name, weather_data):
    try:
        # Create a folium map centered on the location
        m = folium.Map(
            location=[lat, lon],
            zoom_start=11,
            tiles='OpenStreetMap',
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
        
        # Create enhanced popup content
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

# === Weather API Call ===
def get_weather_data(city, weather_api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + weather_api_key + "&q=" + city
    response = requests.get(complete_url)
    return response.json()

# === Cohere AI Weather Summary ===
co = cohere.Client("S9HZs7bl6TAoVZHrPmTfK6ywe7gUVE3hMW4M6NGN")  # Replace with your actual API key

def generate_weather_description(data):
    try:
        temperature = data['main']['temp'] - 273.15
        description = data['weather'][0]['description']
        prompt = f"The current weather is {description} with a temperature of {temperature:.1f}°C. Generate a short, friendly weather summary."

        response = co.generate(
            model='command-r-plus',
            prompt=prompt,
            max_tokens=60,
            temperature=0.7
        )

        return response.generations[0].text.strip()
    except Exception as e:
        return str(e)

# === Weekly Forecast API ===
def get_weekly_forecast(weather_api_key, lat, lon):
    complete_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={weather_api_key}"
    response = requests.get(complete_url)
    return response.json()

# === Display Weekly Forecast ===
def get_weather_icon(description):
    description = description.lower()
    if "clear" in description:
        return "☀️"
    elif "cloud" in description:
        return "☁"
    elif "rain" in description:
        return "🌧"
    elif "snow" in description:
        return "❄"
    elif "storm" in description or "thunder" in description:
        return "⛈"
    elif "fog" in description or "mist" in description:
        return "🌫"
    else:
        return "🌤"

def display_weekly_forecast(data):
    try:
        st.write("===================================================================================")
        st.write("### Weekly Weather Forecast")
        displayed_dates = set()

        c1, c2, c3, c4 = st.columns(4)

        with c1: st.write("**Day**")
        with c2: st.write("**Desc**")
        with c3: st.write("**Min Temp**")
        with c4: st.write("**Max Temp**")

        for day in data['list']:
            date = datetime.fromtimestamp(day['dt']).strftime('%A, %b %d')

            if date not in displayed_dates:
                displayed_dates.add(date)

                min_temp = day['main']['temp_min'] - 273.15
                max_temp = day['main']['temp_max'] - 273.15
                description = day['weather'][0]['description']
                icon = get_weather_icon(description)

                with c1: st.write(f"{date}")
                with c2: st.write(f"{icon} {description.capitalize()}")
                with c3: st.write(f"{min_temp:.1f}°C")
                with c4: st.write(f"{max_temp:.1f}°C")
    except Exception as e:
        st.error("Error in displaying weekly forecast: " + str(e))

# === MAIN STREAMLIT APP ===
def main():
    set_local_background("WeatherBackground1")  # Use your actual file name

    # Initialize session state
    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = None
    if 'city_name' not in st.session_state:
        st.session_state.city_name = ""
    if 'forecast_data' not in st.session_state:
        st.session_state.forecast_data = None
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False

    # Custom title for Weather Forecast AI with black stroke
    st.markdown(
        """
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <h1 style='font-size: 50px; text-align: center; color: white; 
                      text-shadow: 2px 2px 5px black, -1px -1px 5px black, 1px -1px 5px black, 
                      -1px 1px 5px black, 1px 1px 5px black;'>
                ⛅ Weather Forecast AI
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Input section - always visible
    st.markdown(
        """
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <h3 style='text-align: center; color: white; text-shadow: 1px 1px 3px black;'>Weather Forecast AI</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Create columns for better layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        city_input = st.text_input("", placeholder="Enter City Name", key="city_input")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submit = st.button("Get Weather", use_container_width=True)
        with col_btn2:
            clear = st.button("Clear Results", use_container_width=True)

    # Handle clear button
    if clear:
        st.session_state.weather_data = None
        st.session_state.city_name = ""
        st.session_state.forecast_data = None
        st.session_state.show_results = False
        st.rerun()

    # Handle submit button
    if submit and city_input:
        with st.spinner('Fetching weather data.....'):
            weather_data = get_weather_data(city_input, "2bf4686b58e818560cb0aa13c5fd0722")

            if weather_data.get("cod") == 200 and "main" in weather_data:
                # Store data in session state
                st.session_state.weather_data = weather_data
                st.session_state.city_name = city_input
                st.session_state.show_results = True
                
                # Get forecast data
                lat = weather_data['coord']['lat']
                lon = weather_data['coord']['lon']
                forecast_data = get_weekly_forecast("2bf4686b58e818560cb0aa13c5fd0722", lat, lon)
                st.session_state.forecast_data = forecast_data
                
                st.success("✅ Weather data loaded successfully!")
            else:
                st.error("‼ Error: City not found ‼")
                st.session_state.show_results = False

    # Display weather data if it exists in session state
    if st.session_state.show_results and st.session_state.weather_data:
        weather_data = st.session_state.weather_data
        city_input = st.session_state.city_name
        forecast_data = st.session_state.forecast_data
        
        # Dynamic background based on weather
        description = weather_data['weather'][0]['description']
        bg_image = get_background_image_for_weather(description)
        set_local_background(bg_image)

        # Displaying weather updates
        st.title(f"Weather Updates for {city_input}:")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperature 🌫", f"{weather_data['main']['temp'] - 273.15:.2f} °C")
            st.metric("Humidity 💧", f"{weather_data['main']['humidity']}%")
        with col2:
            st.metric("Pressure 🌌", f"{weather_data['main']['pressure']} hPa")
            st.metric("Wind Speed 🌫", f"{weather_data['wind']['speed']} m/s")

        lat = weather_data['coord']['lat']
        lon = weather_data['coord']['lon']

        weather_description = generate_weather_description(weather_data)
        st.subheader("AI Weather Summary")
        st.write(weather_description)

        # === Interactive Weather Map ===
        st.write("===================================================================================")
        st.subheader("🗺️ Interactive Weather Map")
        weather_map = create_weather_map(lat, lon, city_input, weather_data)
        if weather_map:
            st_folium(weather_map, width=700, height=400)

        # Display forecast if available
        if forecast_data and forecast_data.get("cod") != "404":
            display_weekly_forecast(forecast_data)
            plot_temperature_chart(forecast_data)
        else:
            st.error("Error fetching forecast!")

if __name__ == "__main__":
    main()