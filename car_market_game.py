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
    cost = (speed * 2000) + (aesthetics * 1500) + (reliability * 1800) + (efficiency * 1700) + (tech * 2500)
    profit = estimated_sales * (price - cost)
    
    feedback = ""
    if profit < -10000000:
        feedback = "🚨 Catastrophic Loss! Your car is losing an extreme amount of money. You need to **completely rethink** your strategy—reduce production costs, increase the price, and make sure your car matches the right market segment."
    elif profit < -1000000:
        feedback = "⚠️ Huge Loss! Your losses are very high. Consider making significant adjustments—lowering expensive features, improving efficiency, or adjusting pricing to better fit the market."
    elif profit < -100000:
        feedback = "🚨 Major Loss! Your car is losing a significant amount of money. You need to make drastic changes—consider lowering production costs, increasing the price, or improving the balance of features to appeal to buyers."
    elif profit < -50000:
        feedback = "🔴 Moderate Loss! Your car is losing money. Try reducing unnecessary costs, adjusting the price, or making the car more appealing to its target market."
    elif profit < 0:
        feedback = "Your car is losing money. Consider increasing the price or reducing costs by adjusting features like speed, aesthetics, or technology."
    elif profit < 20000:
        feedback = "⚠️ Low Profit! Your profit is minimal. Consider small adjustments to your price or features to make your car more appealing."
    elif profit < 50000:
        feedback = "Your profit is low. Try optimizing your price or enhancing the car's appeal to boost sales."
    else:
        feedback = "Your car is profitable! Maintain a balance between cost and market demand for even better results."
    
    return {
        "Feedback": feedback,
        "Best Market Segment": best_match["Segment"],
        "Estimated Sales": estimated_sales,
        "Profit": profit,
        "Cost": cost
    }

# Function to generate feedback for a profit amount
def get_feedback_for_profit(profit):
    if profit < -10000000:
        return "🚨 Catastrophic Loss! Your car is losing an extreme amount of money. You need to **completely rethink** your strategy—reduce production costs, increase the price, and make sure your car matches the right market segment."
    elif profit < -1000000:
        return "⚠️ Huge Loss! Your losses are very high. Consider making significant adjustments—lowering expensive features, improving efficiency, or adjusting pricing to better fit the market."
    elif profit < -100000:
        return "🚨 Major Loss! Your car is losing a significant amount of money. You need to make drastic changes—consider lowering production costs, increasing the price, or improving the balance of features to appeal to buyers."
    elif profit < -50000:
        return "🔴 Moderate Loss! Your car is losing money. Try reducing unnecessary costs, adjusting the price, or making the car more appealing to its target market."
    elif profit < 0:
        return "Your car is losing money. Consider increasing the price or reducing costs by adjusting features like speed, aesthetics, or technology."
    elif profit < 20000:
        return "⚠️ Low Profit! Your profit is minimal. Consider small adjustments to your price or features to make your car more appealing."
    elif profit < 50000:
        return "Your profit is low. Try optimizing your price or enhancing the car's appeal to boost sales."
    else:
        return "Your car is profitable! Maintain a balance between cost and market demand for even better results."

# AI image generation function using OpenAI DALL·E
def generate_car_image(speed, aesthetics, reliability, efficiency, tech, price):
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            return "Error: No API Key found."
        
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        
        # Enhanced prompt to strongly prevent text in images
        prompt = f"A {'sports car' if price > 80000 else 'luxury sedan' if price > 60000 else 'mid-range SUV' if price > 25000 and efficiency < 8 else 'eco-friendly SUV' if price > 25000 and efficiency >= 8 else 'eco-friendly compact' if price > 20000 and efficiency >= 8 else 'budget hatchback'} with a {'plain and basic' if aesthetics <= 3 else 'sleek and stylish' if aesthetics <= 7 else 'wild and extravagant'} design and funky color palette. The car should match its market segment: a high-performance sports car for extreme speed, a refined luxury sedan for premium comfort, a mid-range SUV for versatility, an eco-friendly SUV for sustainable family travel, an eco-friendly compact for maximum efficiency, or a budget hatchback for affordability. The car should be driving on a winding mountain road. The image should be photorealistic and highly detailed. VERY IMPORTANT: DO NOT INCLUDE ANY TEXT, LETTERS, NUMBERS, WORDS, LABELS, WATERMARKS, LOGOS, OR SYMBOLS OF ANY KIND IN THE IMAGE."
        
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "size": "1024x1024",
            "n": 1
        }
        
        response = requests.post("https://api.openai.com/v1/images/generations", json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()["data"][0]["url"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error generating image: {str(e)}"

# Streamlit UI
try:
    st.set_page_config(page_title="Business Administration Car Market Simulation Game", layout="centered", initial_sidebar_state="expanded")
except Exception as e:
    # This means the page config was already set, which is fine
    pass

# Simplified CSS with inline styles to avoid JavaScript dependencies
st.markdown("""
    <style>
    .custom-container {
        border: 2px solid #4CAF50;
        padding: 15px;
        border-radius: 10px;
        background-color: #ffffff;
        color: #000000;
        margin-bottom: 20px;
    }
    .custom-container-tariff {
        border: 2px solid #FF5733;
        padding: 15px;
        border-radius: 10px;
        background-color: #fff3e0;
        color: #000000;
        margin-bottom: 20px;
    }
    .section-divider {
        border-top: 1px solid #ccc;
        margin-top: 10px;
        padding-top: 10px;
    }
    .header-green {
        color: #4CAF50;
    }
    .header-orange {
        color: #FF5733;
    }
    </style>
""", unsafe_allow_html=True)

# Logo and header - using simpler layout
try:
    logo_path = "logo.png"  # Replace with the actual logo file path
    col1, col2 = st.columns([1, 4])
    with col1:
        try:
            st.image(logo_path, width=150)
        except:
            st.write("Logo image not found")
    with col2:
        st.markdown("<h1>Business Administration Car Market Simulation Game</h1>", unsafe_allow_html=True)
except Exception as e:
    # Fallback if columns cause issues
    st.title("Business Administration Car Market Simulation Game")

# Sidebar Inputs
st.sidebar.header("Customize Your Car")
speed = st.sidebar.slider("Speed", 1, 10, 5)
aesthetics = st.sidebar.slider("Aesthetics", 1, 10, 5)
reliability = st.sidebar.slider("Reliability", 1, 10, 5)
efficiency = st.sidebar.slider("Fuel Efficiency", 1, 10, 5)
tech = st.sidebar.slider("Technology", 1, 10, 5)
price = st.sidebar.number_input("Price ($)", min_value=10000, max_value=200000, value=30000, step=1000)

# Initialize session state
if 'result' not in st.session_state:
    st.session_state.result = None
if 'car_image_url' not in st.session_state:
    st.session_state.car_image_url = None
if 'tariff_applied' not in st.session_state:
    st.session_state.tariff_applied = False

# Simulate market button
if st.sidebar.button("Simulate Market"):
    try:
        # Reset tariff state when simulating new market
        st.session_state.tariff_applied = False
        
        sim_message = st.empty()
        progress_bar = st.progress(0)
        sim_message.write("🕒 Simulating...")
        
        # More robust progress bar
        try:
            for percent in range(1, 95, 5):
                time.sleep(0.05)  # Simulate progress delay
                progress_bar.progress(percent)
        except:
            pass  # Continue if progress bar fails
        
        # Store result in session state
        st.session_state.result = simulate_market_performance(speed, aesthetics, reliability, efficiency, tech, price)
        
        # Generate AI image
        st.session_state.car_image_url = generate_car_image(speed, aesthetics, reliability, efficiency, tech, price)
        
        try:
            for percent in range(95, 101, 1):
                time.sleep(0.1)  # Reduced delay time
                progress_bar.progress(percent)
            progress_bar.empty()
        except:
            pass  # Continue if progress bar fails
        
        sim_message.empty()  # Clear 'Simulating' message
    except Exception as e:
        st.error(f"An error occurred during simulation: {str(e)}")

# Display results if we have them
if st.session_state.result is not None:
    try:
        # Display car image if available
        if st.session_state.car_image_url and "Error" not in st.session_state.car_image_url:
            try:
                st.image(st.session_state.car_image_url, use_container_width=True)
            except:
                st.write("Unable to display car image")
        
        # Display results using plain HTML/markdown to avoid JavaScript issues
        result = st.session_state.result
        st.markdown(f"""
        <div class="custom-container">
            <h2 class="header-green">📊 Market Simulation Results</h2>
            <p><strong>Best Market Segment:</strong> {result['Best Market Segment']}</p>
            <p><strong>Estimated Sales:</strong> {result['Estimated Sales']} units</p>
            <p><strong>Estimated Profit:</strong> ${result['Profit']:,}</p>
            <div class="section-divider">
                <h3 class="header-orange">💡 Profit Feedback</h3>
                <p>{result['Feedback']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Only display tariff information if tariff has been applied
        if st.session_state.tariff_applied:
            tariffed_cost = st.session_state.result['Cost'] * 1.25  # Adding 25% tariff
            tariffed_profit = st.session_state.result['Estimated Sales'] * (price - tariffed_cost)
            tariffed_feedback = get_feedback_for_profit(tariffed_profit)
            
            # Display tariff results with plain HTML to avoid JavaScript issues
            st.markdown(f"""
            <div class="custom-container-tariff">
                <h2 class="header-orange">📊 Updated Market Results (After Tariff)</h2>
                <p><strong>Best Market Segment:</strong> {st.session_state.result['Best Market Segment']}</p>
                <p><strong>Estimated Sales:</strong> {st.session_state.result['Estimated Sales']} units</p>
                <p><strong>Original Profit:</strong> ${st.session_state.result['Profit']:,}</p>
                <p><strong>New Estimated Profit:</strong> ${tariffed_profit:,.2f}</p>
                <p><strong>Profit Change:</strong> ${tariffed_profit - st.session_state.result['Profit']:,.2f}</p>
                <div class="section-divider">
                    <h3 class="header-orange">💡 Updated Profit Feedback</h3>
                    <p>{tariffed_feedback}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")

# Custom button styling with simpler CSS
st.markdown("""
    <style>
    .stButton > button {
        background-color: #ff4d4d;
        color: white;
        font-weight: bold;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Only show the tariff button if we have simulation results and tariff has not been applied yet
if st.session_state.result is not None and not st.session_state.tariff_applied:
    if st.button("Impose Trump Tariff +25%"):
        st.session_state.tariff_applied = True
        st.rerun()
