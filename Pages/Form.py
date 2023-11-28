import streamlit as st
import pandas as pd

def save_to_excel(data):
    file_path = 'user_data.csv'
    columns = ['Name', 'Phone Number', 'Email', 'Comment']
    
    try:
        with open(file_path, 'a') as f:
            f.write(','.join(map(str, data)) + '\n')
        st.success('Data saved successfully!')
    except Exception as e:
        st.error(f"An error occurred: {e}")

st.title('User Feedback')

if 'form_data' not in st.session_state:
    st.session_state.form_data = {'name': '', 'phone_number': '', 'email': '', 'comment': ''}

# Form for user input
with st.form(key='user_input_form', clear_on_submit=True):
    name = st.text_input('Name', value=st.session_state.form_data['name'])
    phone_number = st.text_input('Phone Number', value=st.session_state.form_data['phone_number'])
    email = st.text_input('Email Address', value=st.session_state.form_data['email'])
    comment = st.text_area('Comment', value=st.session_state.form_data['comment'])
    submit_button = st.form_submit_button(label='Submit')
    # reset_button = st.form_submit_button(label='Reset')

    # if reset_button:
    #     # Reset all input values
    #     name = st.empty()
    #     st.session_state.form_data = {'name': '', 'phone_number': '', 'email': '', 'comment': ''}

    if submit_button:
        # Validate the phone number
        if len(phone_number) != 10 or not phone_number.isdigit():
            st.error("Please enter a valid 10-digit phone number.")
        else:
            user_data = [name, phone_number, email, comment]
            save_to_excel(user_data)
            st.session_state.form_data = {'name': '', 'phone_number': '', 'email': '', 'comment': ''}

