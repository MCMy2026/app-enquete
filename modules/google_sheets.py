import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd

def connect():
    creds_dict = st.secrets["google"]

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(credentials)

    return client

def read_data():
    client = connect()
    sheet = client.open("APP_ENQUETE").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def add_row(row):
    client = connect()
    sheet = client.open("APP_ENQUETE").sheet1
    sheet.append_row(row)