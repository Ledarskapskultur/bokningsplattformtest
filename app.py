import streamlit as st
import pandas as pd
import os
import pickle
from datetime import datetime
import requests

# Paths
DATA_FILE = 'kurser.pkl'

# Load or initialize data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'rb') as f:
            return pickle.load(f)
    else:
        return {}

def save_data(data):
    with open(DATA_FILE, 'wb') as f:
        pickle.dump(data, f)

# Send SMS
def send_sms(to, message):
    response = requests.post('https://api.46elks.com/a1/sms',
        auth=('uc9ebbbf8541d29fcbbd04c310a174f69', 'C92D0F039B88E7961EC9B72B17C3BAE8'),
        data={
            'from': 'ElksWelcome',
            'to': to,
            'message': message
        })
    return response.text

# App setup
st.set_page_config(page_title="Kursbyggare", layout="wide")
st.title("📚 Kursbyggare")

# Load stored data
data = load_data()

# Upload and parse Excel file
st.sidebar.header("1. Ladda upp kursfil")
uploaded_file = st.sidebar.file_uploader("Välj en Excel-fil", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    data['kurser'] = df
    save_data(data)
    st.success("Fil uppladdad och sparad!")

# Display current data
if 'kurser' in data:
    df = data['kurser']

    # Filtrera på vecka och ort
    st.sidebar.header("2. Filtrera")
    vecka = st.sidebar.number_input("Vecka", min_value=1, max_value=52, step=1)
    ort = st.sidebar.text_input("Ort")
    max_tid = st.sidebar.number_input("Max resetid (minuter)", min_value=0, max_value=300, step=10)

    filtrerad_df = df.copy()
    if vecka:
        filtrerad_df = filtrerad_df[filtrerad_df['Vecka'] == vecka]
    if ort:
        filtrerad_df = filtrerad_df[filtrerad_df['Ort'].str.contains(ort, case=False, na=False)]
    if max_tid > 0 and 'Resetid' in filtrerad_df.columns:
        filtrerad_df = filtrerad_df[filtrerad_df['Resetid'] <= max_tid]

    st.subheader("📚 Kurser")
    st.dataframe(filtrerad_df)

# Kommunikation
st.sidebar.header("3. Kommunikation")
recipient_type = st.sidebar.selectbox("Mottagare", ["Kund", "Kursledare"])
telefonnummer = st.sidebar.text_input("Telefonnummer (ex: +4670xxxxxxx)")
meddelande = st.sidebar.text_area("Meddelande")

if st.sidebar.button("Skicka SMS"):
    if telefonnummer and meddelande:
        sms_logg = data.get('sms_logg', [])
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sms_logg.append({'tid': timestamp, 'till': telefonnummer, 'meddelande': meddelande, 'typ': recipient_type})
        data['sms_logg'] = sms_logg
        save_data(data)
        response = send_sms(telefonnummer, meddelande)
        st.sidebar.success("SMS skickat!")
    else:
        st.sidebar.warning("Fyll i både telefonnummer och meddelande.")

# Historik
if 'sms_logg' in data:
    st.subheader("🕓 Kommunikationshistorik")
    st.dataframe(pd.DataFrame(data['sms_logg']))
