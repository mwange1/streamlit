import streamlit as st
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input, decode_predictions
import numpy as np
from PIL import Image

# Function to predict the species and accuracy using VGG16
def predict_species_vgg16(img):
    model = VGG16(weights='imagenet')
    x = preprocess_input(img)
    preds = model.predict(x)
    decoded_preds = decode_predictions(preds, top=1)[0]
    species_name = decoded_preds[0][1].replace('_', ' ')
    accuracy = decoded_preds[0][2]
    return species_name, accuracy

# Streamlit app for image-based prediction using VGG16
def vgmain():
    st.title("Image Species Prediction (VGG16)")

    uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        img = image.load_img(uploaded_file, target_size=(224, 224))
        st.image(img, caption="Uploaded Image.", use_column_width=True)

        if st.button("Predict"):
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)
            species_name, accuracy = predict_species_vgg16(img_array)

            st.write(f"Species: {species_name}")
            st.write(f"Accuracy: {accuracy}")

if __name__ == "__main__":
    vgmain()
