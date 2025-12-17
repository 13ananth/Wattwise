from flask import Flask, render_template, request, jsonify
import random
import numpy as np
from sklearn.linear_model import LinearRegression
import os

app = Flask(__name__, template_folder='templates')

# ---------------- 1. DATA GENERATION ----------------
def generate_energy_data():
    return [round(random.uniform(1.5, 5.5), 2) for _ in range(24)]

# Global variable to hold data
energy_data = generate_energy_data()

# ---------------- 2. HELPER FUNCTIONS ----------------
def get_prediction():
    try:
        X = np.array(range(len(energy_data))).reshape(-1, 1)
        y = np.array(energy_data)
        model = LinearRegression()
        model.fit(X, y)
        val = model.predict([[len(energy_data)]])[0]
        # Ensure prediction is positive and within reasonable range
        val = max(1.5, min(5.5, round(val, 2)))
        return val
    except Exception as e:
        print(f"Prediction error: {e}")
        return round(np.mean(energy_data), 2)

def get_average():
    return round(sum(energy_data) / len(energy_data), 2)

def calculate_cost():
    # Assuming 1 Unit = ₹7
    avg = get_average()
    daily_cost = round(avg * 24 * 7, 2)
    return daily_cost

# ---------------- 3. INTELLIGENT RESPONSE SYSTEM ----------------
def get_dynamic_response(intent_type):
    
    if intent_type == "usage":
        val = get_average()
        responses = [
            f"Your average energy usage is currently {val} units.",
            f"I've analyzed the data: you are consuming about {val} units on average.",
            f"Current status: {val} units. You are doing okay.",
            f"You're using {val} units per hour based on the latest readings."
        ]
        return random.choice(responses)

    elif intent_type == "predict":
        val = get_prediction()
        responses = [
            f"Based on the trend, next hour consumption will be {val} units.",
            f"I forecast your usage will hit {val} units in the next hour.",
            f"Prediction model output: expect approximately {val} units.",
            f"Prepare for about {val} units of usage coming up."
        ]
        return random.choice(responses)

    elif intent_type == "cost":
        val = calculate_cost()
        responses = [
            f"At this rate, your daily cost is estimated at {val} rupees.",
            f"You are spending roughly {val} rupees per day on electricity.",
            f"Your projected daily bill is {val} rupees."
        ]
        return random.choice(responses)

    elif intent_type == "save":
        tips = [
            "Try turning off the AC for just 15 minutes to save power.",
            "Switching to LED bulbs can save up to 80% on lighting.",
            "Unplug chargers when not in use to stop phantom drain.",
            "Run your washing machine with full loads only."
        ]
        return random.choice(tips)
    
    elif intent_type == "greeting":
        greetings = [
            "Hello! I am WattWise. How can I help you?",
            "Hi there! Ready to analyze your power usage.",
            "Greetings! Ask me about usage, predictions, or saving tips."
        ]
        return random.choice(greetings)

    return "I'm not sure how to answer that. Try asking about usage or predictions."

# ---------------- 4. FLASK ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html", data=energy_data)

@app.route("/predict")
def predict():
    try:
        return jsonify({"prediction": get_prediction()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/voice-command", methods=["POST"])
def voice_command():
    try:
        command = request.json.get("command", "").lower().strip()
        
        if not command:
            return jsonify({"response": "I didn't catch that. Please try again.", "intent": "unknown"}), 400
        
        intent_detected = "unknown"

        # --- KEYWORD MATCHING LOGIC ---
        if any(word in command for word in ["usage", "use", "current", "reading"]):
            intent_detected = "usage"
        
        elif any(word in command for word in ["predict", "future", "next", "tomorrow"]):
            intent_detected = "predict"
        
        elif any(word in command for word in ["bill", "cost", "price", "money", "rupees"]):
            intent_detected = "cost"

        elif any(word in command for word in ["save", "reduce", "less", "tips"]):
            intent_detected = "save"

        elif any(word in command for word in ["hello", "hi", "hey"]):
            intent_detected = "greeting"

        response_text = get_dynamic_response(intent_detected)

        return jsonify({
            "response": response_text,
            "intent": intent_detected,
            "raw_value": get_average() if intent_detected == "usage" else None
        })
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}", "intent": "error"}), 500

# ---------------- 5. SERVER START ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)