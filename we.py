import streamlit as st
import requests
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- 1. SETUP ---
st.set_page_config(page_title="Gemini Weather Agent", page_icon="🌤️")
st.title("🌤️ Bondili's AI Weather Agent")
st.snow()  # Just for fun!

# Initialize Gemini Client
# Assumes GEMINI_API_KEY is in your .env file
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- 2. WEATHER TOOL DEFINITION ---
def get_weather(city: str):
    """Fetches the current weather for a given city."""
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    try:
        geo_res = requests.get(geo_url).json()
        if not geo_res.get('results'):
            return {"error": "City not found"}
        
        loc = geo_res['results'][0]
        lat, lon = loc['latitude'], loc['longitude']

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
        weather_data = requests.get(weather_url).json()
        
        return {
            "city": loc['name'],
            "temperature": weather_data['current']['temperature_2m'],
            "unit": "Celsius"
        }
    except Exception as e:
        return {"error": str(e)}

# --- 3. STREAMLIT UI ---
with st.sidebar:
    st.info("Ask about the weather anywhere in the world. Gemini will use the Open-Meteo API to get real-time data.")

user_query = st.text_input("Ask something (e.g., 'What's the weather in Tokyo?')", placeholder="Enter city or question...")

if st.button("Ask AI"):
    if user_query:
        with st.spinner("Consulting the clouds..."):
            try:
                # Run the LLM with the tool attached
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_query,
                    config=types.GenerateContentConfig(
                        tools=[get_weather] # Automatic function calling
                    )
                )
                
                # Display Output
                st.subheader("AI Response")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a question first!")

# Visual Footer
st.divider()
st.caption("Powered by Gemini 2.5 Flash & Open-Meteo API")