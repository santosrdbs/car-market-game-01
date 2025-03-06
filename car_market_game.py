import streamlit as st
import pandas as pd
import requests
import os
import time

# Simulated market data
market_data = pd.DataFrame({
    "Segment": ["Budget", "Family", "Luxury", "Sports", "Eco-Friendly"],
    "Avg_Price": [20000, 30000, 60000, 80000, 35000],
    "Preferred_Speed": [4, 5, 7, 10, 5],
    "Preferred_Aesthetics": [5, 6, 9, 8, 7],
    "Preferred_Reliability": [8, 7, 6, 5, 9],
    "Preferred_Efficiency": [7, 6, 4, 3, 10],
    "Preferred_Tech": [6, 7, 10, 9, 8],
    "Market_Size": [50000, 40000, 15000, 10000, 25000]
})

# Market simulation function
def simulate_market_performance(speed, aesthetics, reliability, efficiency, tech, price):
    market_data["Score"] = (
        abs(market_data["Preferred_Speed"] - speed) +
        abs(market_data["Preferred_Aesthetics"] - aesthetics) +
        abs(market_data["Preferred_Reliability"] - reliability) +
        abs(market_data["Preferred_Efficiency"] - efficiency) +
        abs(market_data["Preferred_Tech"] - tech)
    )
    best_match = market_data.loc[market_data["Score"].idxmin()]
    
    price_factor = max(0, 1 - abs(price - best_match["Avg_Price"]) / best_match["Avg_Price"])
    estimated_sales = int(best_match["Market_Size"] * (1 - best_match["Score"] / 50) * price_factor)
    profit = estimated_sales * (price * 0.5)
    
    return {
        "Best Market Segment": best_match["Segment"],
        "Estimated Sales": estimated_sales,
        "Profit": profit
    }

# AI image generation function using OpenAI DALL·E
def generate_car_image(speed, aesthetics, reliability, efficiency, tech, price):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        return "Error: No API Key found."
    
    
    
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"A {'luxury' if price > 60000 else 'budget' if price < 25000 else 'mid-range'} futuristic car priced at ${price}, with speed {speed}/10, aesthetics {aesthetics}/10, reliability {reliability}/10, fuel efficiency {efficiency}/10, and technology {tech}/10. The car should match its price range and have a sleek, realistic design with appropriate features."
    
    data = {
        
        "prompt": prompt,
        "size": "1024x1024",
        "n": 1
    }
    
    response = requests.post("https://api.openai.com/v1/images/generations", json={"model": "dall-e-2", **data}, headers=headers)
    
    
    
    
    if response.status_code == 200:
        return response.json()["data"][0]["url"]
    else:
        return f"Error: {response.status_code} - {response.text}"

# Streamlit UI
st.title("🚗 Car Market Simulation Game")

# Sidebar Inputs
st.sidebar.header("Customize Your Car")
speed = st.sidebar.slider("Speed", 1, 10, 5)
aesthetics = st.sidebar.slider("Aesthetics", 1, 10, 5)
reliability = st.sidebar.slider("Reliability", 1, 10, 5)
efficiency = st.sidebar.slider("Fuel Efficiency", 1, 10, 5)
tech = st.sidebar.slider("Technology", 1, 10, 5)
price = st.sidebar.number_input("Price ($)", min_value=10000, max_value=200000, value=30000, step=1000)

if st.sidebar.button("Simulate Market"):
    sim_message = st.empty()
    sim_message.write("🕒 Simulating...")
    st.write("🕒 Simulating...")
    result = simulate_market_performance(speed, aesthetics, reliability, efficiency, tech, price)
    
    
    
    # Generate AI image
    st.subheader("🎨 AI-Generated Car Image")
    car_image_url = generate_car_image(speed, aesthetics, reliability, efficiency, tech, price)
    sim_message.empty()  # Clear 'Simulating' message
    if car_image_url and "Error" not in car_image_url:
        st.image(car_image_url, use_container_width=True)
        st.markdown(f"**📊 Market Simulation Results**
- **Best Market Segment:** {result['Best Market Segment']}
- **Estimated Sales:** {result['Estimated Sales']} units
- **Estimated Profit:** ${result['Profit']:,}")
    else:
        st.write("Failed to generate AI image. Try again later.")
