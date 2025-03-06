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
    st.set_page_config(page_title="Business Administration Car Market Simulation Game", layout="wide", initial_sidebar_state="collapsed")
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
    .instructions-container {
        border: 2px solid #3498db;
        padding: 20px;
        border-radius: 10px;
        background-color: #e8f4f8;
        color: #000000;
        margin-bottom: 20px;
    }
    .attempt-counter {
        font-weight: bold;
        color: #3498db;
        font-size: 18px;
        text-align: center;
        margin: 10px 0;
        padding: 10px;
        background-color: #e8f4f8;
        border-radius: 5px;
    }
    .prev-attempt {
        font-size: 14px;
        padding: 10px;
        background-color: #f0f0f0;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .stButton button {
        width: 100%;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    /* Mobile optimization */
    @media (max-width: 768px) {
        .custom-container, .custom-container-tariff, .instructions-container {
            padding: 10px;
        }
    }
    /* Button colors */
    .blue-button {
        background-color: #3498db !important;
        color: white !important;
    }
    .red-button {
        background-color: #ff4d4d !important;
        color: white !important;
    }
    .green-button {
        background-color: #4CAF50 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = "instructions"  # States: instructions, design_1, result_1, design_2, result_2, design_3, result_3, tariff, summary
if 'result' not in st.session_state:
    st.session_state.result = None
if 'car_image_url' not in st.session_state:
    st.session_state.car_image_url = None
if 'tariff_applied' not in st.session_state:
    st.session_state.tariff_applied = False
if 'attempts_used' not in st.session_state:
    st.session_state.attempts_used = 0
if 'attempts_results' not in st.session_state:
    st.session_state.attempts_results = []
if 'car_designs' not in st.session_state:
    st.session_state.car_designs = []

# Function to reset the game
def reset_game():
    st.session_state.game_state = "instructions"
    st.session_state.result = None
    st.session_state.car_image_url = None
    st.session_state.tariff_applied = False
    st.session_state.attempts_used = 0
    st.session_state.attempts_results = []
    st.session_state.car_designs = []

# Logo and header - using simpler layout for mobile
st.markdown("<h1 style='text-align: center;'>Car Market Simulation Game</h1>", unsafe_allow_html=True)

try:
    logo_path = "logo.png"  # Replace with the actual logo file path
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image(logo_path, width=150, use_column_width=True)
        except:
            pass  # Skip if logo doesn't load
except:
    pass  # Continue without logo if columns fail

# Instructions screen
if st.session_state.game_state == "instructions":
    st.markdown("""
    <div class="instructions-container">
        <h2 style="color: #3498db; text-align: center;">Welcome to the Car Market Simulator!</h2>
        <hr>
        <h3>Game Instructions:</h3>
        <ol>
            <li><strong>Objective:</strong> Design a profitable car by adjusting its features and price.</li>
            <li><strong>You have 3 attempts</strong> to create a profitable car design.</li>
            <li>Customize your car's specifications using the sliders.</li>
            <li>Click "Simulate Market" to see how your car performs.</li>
            <li>Learn from each attempt and adjust your strategy.</li>
            <li>After your third attempt, you'll see an AI-generated image of your final car design.</li>
            <li>The "Impose Trump Tariff" button lets you see how a 25% tariff would affect your profits.</li>
        </ol>
        <p style="text-align: center; font-weight: bold;">Good luck with your car design!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Simple Streamlit button
    if st.button("Start Game", key="start_game_button", help="Click to start the game", type="primary"):
        st.session_state.game_state = "design_1"
        st.rerun()

# Design screen for Attempt 1
elif st.session_state.game_state == "design_1":
    st.markdown("<div class='attempt-counter'>Attempt 1 of 3</div>", unsafe_allow_html=True)
    st.markdown("### Customize Your Car")
    
    # Car design inputs
    col1, col2 = st.columns(2)
    with col1:
        speed = st.slider("Speed", 1, 10, 5, help="Higher speed increases cost but appeals to Sports segment")
        aesthetics = st.slider("Aesthetics", 1, 10, 5, help="Higher aesthetics increases cost but appeals to Luxury segment")
        reliability = st.slider("Reliability", 1, 10, 5, help="Higher reliability increases cost but appeals to Budget & Eco segments")
    
    with col2:
        efficiency = st.slider("Fuel Efficiency", 1, 10, 5, help="Higher efficiency increases cost but appeals to Eco-Friendly segment")
        tech = st.slider("Technology", 1, 10, 5, help="Higher tech increases cost but appeals to Luxury segment")
        price = st.number_input("Price ($)", min_value=10000, max_value=200000, value=30000, step=1000)
    
    # Simulate market button
    if st.button("Simulate Market", key="simulate_market_1", type="primary"):
        with st.spinner("Simulating market performance..."):
            # Store design for future reference
            st.session_state.car_designs.append({
                "Speed": speed,
                "Aesthetics": aesthetics,
                "Reliability": reliability,
                "Efficiency": efficiency,
                "Tech": tech,
                "Price": price
            })
            
            # Simulate market
            st.session_state.result = simulate_market_performance(speed, aesthetics, reliability, efficiency, tech, price)
            st.session_state.attempts_results.append(st.session_state.result)
            st.session_state.attempts_used += 1
            
            # Move to results
            st.session_state.game_state = "result_1"
            st.rerun()

# Results for Attempt 1
elif st.session_state.game_state == "result_1":
    st.markdown("<div class='attempt-counter'>Attempt 1 Results</div>", unsafe_allow_html=True)
    
    # Display results
    result = st.session_state.attempts_results[0]
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
    
    # Continue to next attempt
    if st.button("Continue to Attempt 2", key="continue_to_2", type="primary"):
        st.session_state.game_state = "design_2"
        st.rerun()

# Design screen for Attempt 2
elif st.session_state.game_state == "design_2":
    st.markdown("<div class='attempt-counter'>Attempt 2 of 3</div>", unsafe_allow_html=True)
    
    # Show previous attempt for reference
    prev_design = st.session_state.car_designs[0]
    prev_result = st.session_state.attempts_results[0]
    
    with st.expander("Previous Attempt Summary", expanded=True):
        st.markdown(f"""
        <div class="prev-attempt">
            <p><strong>Profit:</strong> ${prev_result['Profit']:,}</p>
            <p><strong>Best Segment:</strong> {prev_result['Best Market Segment']}</p>
            <p><strong>Settings:</strong> Speed: {prev_design['Speed']}, Aesthetics: {prev_design['Aesthetics']}, 
            Reliability: {prev_design['Reliability']}, Efficiency: {prev_design['Efficiency']}, 
            Tech: {prev_design['Tech']}, Price: ${prev_design['Price']:,}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Customize Your Car")
    
    # Car design inputs
    col1, col2 = st.columns(2)
    with col1:
        speed = st.slider("Speed", 1, 10, prev_design['Speed'], help="Higher speed increases cost but appeals to Sports segment")
        aesthetics = st.slider("Aesthetics", 1, 10, prev_design['Aesthetics'], help="Higher aesthetics increases cost but appeals to Luxury segment")
        reliability = st.slider("Reliability", 1, 10, prev_design['Reliability'], help="Higher reliability increases cost but appeals to Budget & Eco segments")
    
    with col2:
        efficiency = st.slider("Fuel Efficiency", 1, 10, prev_design['Efficiency'], help="Higher efficiency increases cost but appeals to Eco-Friendly segment")
        tech = st.slider("Technology", 1, 10, prev_design['Tech'], help="Higher tech increases cost but appeals to Luxury segment")
        price = st.number_input("Price ($)", min_value=10000, max_value=200000, value=prev_design['Price'], step=1000)
    
    # Simulate market button
    if st.button("Simulate Market", key="simulate_market_2", type="primary"):
        with st.spinner("Simulating market performance..."):
            # Store design for future reference
            st.session_state.car_designs.append({
                "Speed": speed,
                "Aesthetics": aesthetics,
                "Reliability": reliability,
                "Efficiency": efficiency,
                "Tech": tech,
                "Price": price
            })
            
            # Simulate market
            st.session_state.result = simulate_market_performance(speed, aesthetics, reliability, efficiency, tech, price)
            st.session_state.attempts_results.append(st.session_state.result)
            st.session_state.attempts_used += 1
            
            # Move to results
            st.session_state.game_state = "result_2"
            st.rerun()

# Results for Attempt 2
elif st.session_state.game_state == "result_2":
    st.markdown("<div class='attempt-counter'>Attempt 2 Results</div>", unsafe_allow_html=True)
    
    # Display results
    result = st.session_state.attempts_results[1]
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
    
    # Continue to next attempt
    if st.button("Continue to Final Attempt", key="continue_to_3", type="primary"):
        st.session_state.game_state = "design_3"
        st.rerun()

# Design screen for Attempt 3
elif st.session_state.game_state == "design_3":
    st.markdown("<div class='attempt-counter'>Final Attempt (3 of 3)</div>", unsafe_allow_html=True)
    
    # Show previous attempts for reference
    with st.expander("Previous Attempts Summary", expanded=True):
        for i in range(2):
            prev_design = st.session_state.car_designs[i]
            prev_result = st.session_state.attempts_results[i]
            
            st.markdown(f"""
            <div class="prev-attempt">
                <p><strong>Attempt {i+1} Profit:</strong> ${prev_result['Profit']:,}</p>
                <p><strong>Best Segment:</strong> {prev_result['Best Market Segment']}</p>
                <p><strong>Settings:</strong> Speed: {prev_design['Speed']}, Aesthetics: {prev_design['Aesthetics']}, 
                Reliability: {prev_design['Reliability']}, Efficiency: {prev_design['Efficiency']}, 
                Tech: {prev_design['Tech']}, Price: ${prev_design['Price']:,}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if i == 0:
                st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### Customize Your Car")
    
    # Use the better of previous two designs as default
    better_attempt = 1 if st.session_state.attempts_results[1]['Profit'] > st.session_state.attempts_results[0]['Profit'] else 0
    prev_design = st.session_state.car_designs[better_attempt]
    
    # Car design inputs
    col1, col2 = st.columns(2)
    with col1:
        speed = st.slider("Speed", 1, 10, prev_design['Speed'], help="Higher speed increases cost but appeals to Sports segment")
        aesthetics = st.slider("Aesthetics", 1, 10, prev_design['Aesthetics'], help="Higher aesthetics increases cost but appeals to Luxury segment")
        reliability = st.slider("Reliability", 1, 10, prev_design['Reliability'], help="Higher reliability increases cost but appeals to Budget & Eco segments")
    
    with col2:
        efficiency = st.slider("Fuel Efficiency", 1, 10, prev_design['Efficiency'], help="Higher efficiency increases cost but appeals to Eco-Friendly segment")
        tech = st.slider("Technology", 1, 10, prev_design['Tech'], help="Higher tech increases cost but appeals to Luxury segment")
        price = st.number_input("Price ($)", min_value=10000, max_value=200000, value=prev_design['Price'], step=1000)
    
    # Simulate market button
    if st.button("Simulate Market", key="simulate_market_3", type="primary"):
        with st.spinner("Simulating market performance and generating car image..."):
            # Store design for future reference
            st.session_state.car_designs.append({
                "Speed": speed,
                "Aesthetics": aesthetics,
                "Reliability": reliability,
                "Efficiency": efficiency,
                "Tech": tech,
                "Price": price
            })
            
            # Simulate market
            st.session_state.result = simulate_market_performance(speed, aesthetics, reliability, efficiency, tech, price)
            st.session_state.attempts_results.append(st.session_state.result)
            st.session_state.attempts_used += 1
            
            # Generate car image for final design
            st.session_state.car_image_url = generate_car_image(speed, aesthetics, reliability, efficiency, tech, price)
            
            # Move to results
            st.session_state.game_state = "result_3"
            st.rerun()

# Results for Attempt 3
elif st.session_state.game_state == "result_3":
    st.markdown("<div class='attempt-counter'>Final Results</div>", unsafe_allow_html=True)
    
    # Display car image if available
    if st.session_state.car_image_url and "Error" not in st.session_state.car_image_url:
        try:
            st.image(st.session_state.car_image_url, use_column_width=True)
            st.markdown("<p style='text-align: center; font-style: italic;'>Your final car design</p>", unsafe_allow_html=True)
        except:
            st.write("Unable to display car image")
    
    # Display results
    result = st.session_state.attempts_results[2]
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
    
    # Options to check tariff or see summary
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Check Tariff Impact", key="check_tariff", type="secondary"):
            st.session_state.game_state = "tariff"
            st.rerun()
    
    with col2:
        if st.button("View Game Summary", key="view_summary", type="primary"):
            st.session_state.game_state = "summary"
            st.rerun()

# Tariff impact screen
elif st.session_state.game_state == "tariff":
    st.markdown("<div class='attempt-counter'>Tariff Impact Analysis</div>", unsafe_allow_html=True)
    
    # Get the final design
    final_design = st.session_state.car_designs[2]
    final_result = st.session_state.attempts_results[2]
    
    # Calculate tariff impact
    tariffed_cost = final_result['Cost'] * 1.25  # Adding 25% tariff
    tariffed_profit = final_result['Estimated Sales'] * (final_design['Price'] - tariffed_cost)
    tariffed_feedback = get_feedback_for_profit(tariffed_profit)
    
    # Display tariff results
    st.markdown(f"""
    <div class="custom-container-tariff">
        <h2 class="header-orange">📊 Trump Tariff Impact (25% Increase)</h2>
        <p><strong>Best Market Segment:</strong> {final_result['Best Market Segment']}</p>
        <p><strong>Estimated Sales:</strong> {final_result['Estimated Sales']} units</p>
        <p><strong>Original Profit:</strong> ${final_result['Profit']:,}</p>
        <p><strong>New Estimated Profit:</strong> ${tariffed_profit:,.2f}</p>
        <p><strong>Profit Change:</strong> ${tariffed_profit - final_result['Profit']:,.2f}</p>
        <div class="section-divider">
            <h3 class="header-orange">💡 Updated Profit Feedback</h3>
            <p>{tariffed_feedback}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Continue to summary
    if st.button("View Game Summary", key="to_summary", type="primary"):
        st.session_state.game_state = "summary"
        st.rerun()

# Game summary screen
elif st.session_state.game_state == "summary":
    st.markdown("<div class='attempt-counter'>Game Summary</div>", unsafe_allow_html=True)
    
    # Calculate best attempt
    profits = [result['Profit'] for result in st.session_state.attempts_results]
    best_attempt_index = profits.index(max(profits))
    best_design = st.session_state.car_designs[best_attempt_index]
    best_result = st.session_state.attempts_results[best_attempt_index]
    
    # Display car image again if available
    if st.session_state.car_image_url and "Error" not in st.session_state.car_image_url:
        try:
            st.image(st.session_state.car_image_url, use_column_width=True)
            st.markdown("<p style='text-align: center; font-style: italic;'>Your final car design</p>", unsafe_allow_html=True)
        except:
            pass
    
    # Best design callout
    st.markdown(f"""
    <div style="background-color: #e8f4f8; padding: 15px; border-radius: 10px; border: 2px solid #3498db; margin-bottom: 20px;">
        <h3 style="color: #3498db; text-align: center;">🏆 Best Performing Design: Attempt {best_attempt_index+1}</h3>
        <p><strong>Profit:</strong> ${best_result['Profit']:,}</p>
        <p><strong>Market Segment:</strong> {best_result['Best Market Segment']}</p>
        <p><strong>Settings:</strong> Speed: {best_design['Speed']}, Aesthetics: {best_design['Aesthetics']}, 
        Reliability: {best_design['Reliability']}, Efficiency: {best_design['Efficiency']}, 
        Tech: {best_design['Tech']}, Price: ${best_design['Price']:,}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a DataFrame for the summary
    import pandas as pd
    summary_data = []
    for i, (design, result) in enumerate(zip(st.session_state.car_designs, st.session_state.attempts_results)):
        is_best = i == best_attempt_index
        best_badge = "🏆 " if is_best else ""
        summary_data.append({
            "Attempt": f"{best_badge}Attempt {i+1}",
            "Market Segment": result['Best Market Segment'],
            "Sales": result['Estimated Sales'],
            "Profit": f"${result['Profit']:,}",
            "Speed": design['Speed'],
            "Aesthetics": design['Aesthetics'],
            "Reliability": design['Reliability'],
            "Efficiency": design['Efficiency'],
            "Tech": design['Tech'],
            "Price": f"${design['Price']:,}"
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Display the summary table
    st.markdown("### All Attempts Comparison")
    st.dataframe(summary_df, use_container_width=True)
    
    # New game button
    if st.button("Start New Game", key="new_game_button", type="primary"):
        reset_game()
        st.rerun()
