import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning)

import streamlit as st
import numpy as np
import pandas as pd
import pickle
import plotly.express as px
from PIL import Image
import base64

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Vehicle Price Prediction")

# --------------------------------------------------
# Background Image Function
# --------------------------------------------------
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.85);
            z-index: -1;
        }}

        /* Bright & Bold Price Box */
        .price-box {{
            background: linear-gradient(135deg, #00ff99, #00ccff);
    color: #003333;
    font-size: 28px;        /* ⬅ smaller text */
    font-weight: 800;
    padding: 16px;          /* ⬅ reduced padding */
    border-radius: 14px;
    text-align: center;
    margin-top: 15px;
    box-shadow: 0px 0px 18px rgba(0, 255, 200, 0.7);
    animation: glow 1.5s infinite alternate;
        }}

        @keyframes glow {{
            from {{
                box-shadow: 0px 0px 15px rgba(0, 255, 200, 0.5);
            }}
            to {{
                box-shadow: 0px 0px 35px rgba(0, 255, 200, 1);
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local("image.png")

# --------------------------------------------------
# Load trained model
# --------------------------------------------------
with open('linear_model.pkl', 'rb') as f:
    lm2 = pickle.load(f)

# --------------------------------------------------
# Load feature importance
# --------------------------------------------------
def load_feature_importance(file_path):
    return pd.read_excel(file_path)

final_fi = load_feature_importance("feature_importance.xlsx")

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
image_sidebar = Image.open('pic 1.PNG')
st.sidebar.image(image_sidebar, use_container_width=True)
st.sidebar.header('Vehicle Features')

def get_user_input():
    horsepower = st.sidebar.number_input('Horsepower', 0, 1000, 300)
    torque = st.sidebar.number_input('Torque', 0, 1500, 400)

    make = st.sidebar.selectbox(
        'Make', ['Aston Martin', 'Audi', 'BMW', 'Bentley', 'Ford', 'Mercedes-Benz', 'Nissan']
    )
    body_size = st.sidebar.selectbox('Body Size', ['Compact', 'Large', 'Midsize'])
    body_style = st.sidebar.selectbox(
        'Body Style',
        [
            'Cargo Minivan', 'Cargo Van', 'Convertible', 'Convertible SUV',
            'Coupe', 'Hatchback', 'Passenger Minivan', 'Passenger Van',
            'Pickup Truck', 'SUV', 'Sedan', 'Wagon'
        ]
    )
    engine_aspiration = st.sidebar.selectbox(
        'Engine Aspiration',
        [
            'Electric Motor', 'Naturally Aspirated', 'Supercharged',
            'Turbocharged', 'Twin-Turbo', 'Twincharged'
        ]
    )
    drivetrain = st.sidebar.selectbox('Drivetrain', ['4WD', 'AWD', 'FWD', 'RWD'])
    transmission = st.sidebar.selectbox('Transmission', ['automatic', 'manual'])

    return {
        'Horsepower_No': horsepower,
        'Torque_No': torque,
        f'Make_{make}': 1,
        f'Body Size_{body_size}': 1,
        f'Body Style_{body_style}': 1,
        f'Engine Aspiration_{engine_aspiration}': 1,
        f'Drivetrain_{drivetrain}': 1,
        f'Transmission_{transmission}': 1,
    }

# --------------------------------------------------
# Title
# --------------------------------------------------
st.markdown(
    "<h1 style='text-align:center;'>🚗 Vehicle Price Prediction App</h1>",
    unsafe_allow_html=True
)

# --------------------------------------------------
# Layout
# --------------------------------------------------
left_col, right_col = st.columns(2)

# --------------------------------------------------
# Feature Importance
# --------------------------------------------------
with left_col:
    st.header(" Feature Importance")

    final_fi_sorted = final_fi.sort_values(
        by='Feature Importance Score', ascending=True
    )

    fig = px.bar(
        final_fi_sorted,
        x='Feature Importance Score',
        y='Variable',
        orientation='h',
        text='Feature Importance Score',
        color_discrete_sequence=["#eaf2f3"]
    )

    fig.update_layout(
        template="plotly_white",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# Prediction
# --------------------------------------------------
with right_col:
    st.header(" Predict Vehicle Price")

    user_data = get_user_input()

    def prepare_input(data, feature_list):
        return np.array([[data.get(f, 0) for f in feature_list]])

    features = [
        'Horsepower_No', 'Torque_No',
        'Make_Aston Martin', 'Make_Audi', 'Make_BMW', 'Make_Bentley',
        'Make_Ford', 'Make_Mercedes-Benz', 'Make_Nissan',
        'Body Size_Compact', 'Body Size_Large', 'Body Size_Midsize',
        'Body Style_Cargo Minivan', 'Body Style_Cargo Van',
        'Body Style_Convertible', 'Body Style_Convertible SUV',
        'Body Style_Coupe', 'Body Style_Hatchback',
        'Body Style_Passenger Minivan', 'Body Style_Passenger Van',
        'Body Style_Pickup Truck', 'Body Style_SUV',
        'Body Style_Sedan', 'Body Style_Wagon',
        'Engine Aspiration_Electric Motor',
        'Engine Aspiration_Naturally Aspirated',
        'Engine Aspiration_Supercharged',
        'Engine Aspiration_Turbocharged',
        'Engine Aspiration_Twin-Turbo',
        'Engine Aspiration_Twincharged',
        'Drivetrain_4WD', 'Drivetrain_AWD',
        'Drivetrain_FWD', 'Drivetrain_RWD',
        'Transmission_automatic', 'Transmission_manual'
    ]

    if st.button("Predict "):
        prediction = lm2.predict(prepare_input(user_data, features))

        st.subheader("Predicted Price")
        st.markdown(
            f"<div class='price-box'>💵 ${prediction[0]:,.2f}</div>",
            unsafe_allow_html=True
        )

# --------------------------------------------------
# Run:
# streamlit run Regr_model_cars.py
# --------------------------------------------------