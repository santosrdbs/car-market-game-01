import streamlit as st
import pandas as pd
import requests

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

# AI image generation function (DALL·E API)
def generate_car_image(speed, aesthetics, reliability, efficiency, tech):
    prompt = f"A car with speed rating {speed}/10, aesthetics {aesthetics}/10, reliability {reliability}/10, fuel efficiency {efficiency}/10, and technology {tech}/10. The car should have a sleek design with a futuristic look and bold, eye-catching color options."
    dalle_api_url = "https://api.openai.com/v1/images/generations"  # Replace with actual API if using OpenAI
    headers = {"Authorization": "Bearer YOUR_OPENAI_API_KEY"}  # Add your OpenAI key here
    
    response = requests.post(dalle_api_url, json={"prompt": prompt, "size": "1024x1024"}, headers=headers)
    
    if response.status_code == 200:
        return response.json()["data"][0]["url"]
    else:
        return None

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
    result = simulate_market_performance(speed, aesthetics, reliability, efficiency, tech, price)
    
    st.subheader("📊 Market Simulation Results")
    st.write(f"**Best Market Segment:** {result['Best Market Segment']}")
    st.write(f"**Estimated Sales:** {result['Estimated Sales']} units")
    st.write(f"**Estimated Profit:** ${result['Profit']:,}")
    
    # Generate AI image
    st.subheader("🎨 AI-Generated Car Image")
    car_image_url = generate_car_image(speed, aesthetics, reliability, efficiency, tech)
    if car_image_url:
        st.image(car_image_url, caption="Your Designed Car", use_column_width=True)
    else:
        st.write("Failed to generate AI image. Check your API key.")
