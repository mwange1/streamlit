import streamlit as st
from time import sleep

# Set up session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Define the login function
def login():
    st.title("Wildlife Monitoring System - Login")

    # Username and password input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log in"):
        if username == "admin" and password == "password":  # Replace with your desired credentials
            st.session_state.logged_in = True
            st.success("Successfully logged in!")
            sleep(1)
            st.experimental_set_query_params(logged_in=True)  # Simulate page reload
        else:
            st.error("Incorrect username or password")

# Define the logout function
def logout():
    st.session_state.logged_in = False
    st.success("You have been logged out.")
    sleep(1)
    st.experimental_set_query_params(logged_in=False)  # Simulate page reload

# App logic depending on login status
if st.session_state.logged_in:
    # Call the main function of your app.py here
    from app import main
    main()

    # Provide a logout button in the sidebar
    if st.sidebar.button("Log out"):
        logout()
else:
    login()
