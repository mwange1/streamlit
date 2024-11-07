import streamlit as st
from tensorflow.keras.applications.resnet50 import ResNet50 # type: ignore
from tensorflow.keras.preprocessing import image # type: ignore
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions # type: ignore
import numpy as np
import csv
import os
from datetime import datetime
import base64
import pandas as pd
import requests  # For EONET API requests
from vg16 import vgmain

# NASA EONET API base URL
EONET_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"

# Coordinates for Lusaka National Park Bounding Box (minLon, minLat, maxLon, maxLat)
bbox_coords = {
    'min_lon': 28.0,
    'min_lat': -16.0,
    'max_lon': 29.0,
    'max_lat': -15.0
}

# Function to predict the species and accuracy
def predict_species(img):
    model = ResNet50(weights='imagenet')
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)

    decoded_preds = decode_predictions(preds, top=1)[0]
    species_names = [pred[1].replace('_', ' ') for pred in decoded_preds]
    accuracies = [pred[2] for pred in decoded_preds]

    return species_names[0], accuracies[0]

# Function to save the results in a CSV file with the current date and time
def save_results_to_csv(results):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H-%M-%S")  # Remove colons from the timestamp
    file_name = "results.csv"
    with open(file_name, "a+", newline="") as f:
        writer = csv.writer(f)
        for result in results:
            writer.writerow([result[0], result[1], result[2], result[3]])
    return file_name

# Function to display previous results
def display_previous_results():
    try:
        df = pd.read_csv("results.csv")
        st.write("Previous Results:")
        st.write(df)
    except FileNotFoundError:
        st.warning("No previous results found.")

# Function to fetch events from NASA's EONET API for Lusaka National Park
def fetch_eonet_events():
    params = {
        'status': 'open',   # Only fetch ongoing events
        'limit': 5,         # Limit to 5 results
        'bbox': f"{bbox_coords['min_lon']},{bbox_coords['min_lat']},{bbox_coords['max_lon']},{bbox_coords['max_lat']}",  # Bounding box for Lusaka National Park
        'api_key': 'pohh7btt5Wh5tIpahDfc6eUHNDCYFTcOU'  # Replace with your NASA API key
    }
    response = requests.get(EONET_URL, params=params)
    
    if response.status_code == 200:
        return response.json().get('events', [])
    else:
        return None

# Function to display the fetched events in Streamlit
def display_eonet_events(events):
    if events:
        st.write("Events happening around Lusaka National Park:")
        for event in events:
            st.write(f"**Event:** {event['title']}")
            st.write(f"**Category:** {event['categories'][0]['title']}")
            st.write(f"**Date:** {event['geometry'][0]['date']}")
            
            # Get the coordinates of the event
            coordinates = event['geometry'][0]['coordinates']
            longitude, latitude = coordinates
            st.write(f"**Coordinates:** Latitude {latitude}, Longitude {longitude}")
            st.write("---")
    else:
        st.write("No ongoing events in this area.")

# Streamlit app
def main():
    st.title("Wildlife Monitoring System")

    uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        img = image.load_img(uploaded_file, target_size=(224, 224))
        st.image(img, caption="Uploaded Image.", use_column_width=True)

        if st.button("Predict"):
            species_name, accuracy = predict_species(img)
            st.write(f"Species: {species_name}")
            st.write(f"Accuracy: {accuracy}")

            # Save the results with the current date and time
            results = [(datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"), species_name, accuracy)]
            file_name = save_results_to_csv(results)
            st.success(f"Results saved to {file_name}")

            # Store the CSV file path in session state
            st.session_state.results = file_name

    # Button to fetch and display EONET events around Lusaka National Park
    if st.button("Generate Events around Lusaka National Park"):
        events = fetch_eonet_events()
        if events:
            display_eonet_events(events)
        else:
            st.error("No Ongoing Events Around Lusaka National Park.")

# Button for accessing Raspberry Pi live feed
    if st.sidebar.button("Access Live Feed"):
        pi_ip_address = "http://192.168.1.197:7123"  # Replace with your actual IP address and port
        st.write(f"Live Feed: [Click here to access the live stream]({pi_ip_address})")
    
    # Sidebar buttons
    st.sidebar.button("Display Previous Results", on_click=display_previous_results)
    selected_model = st.sidebar.selectbox("Select Model", ["VGG16", "ResNet50"])

if __name__ == "__main__":
    main()
