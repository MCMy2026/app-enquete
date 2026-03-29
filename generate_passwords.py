import streamlit_authenticator as stauth

passwords = ['1234', '1234', '1234']

hashed_passwords = stauth.Hasher().hash_list(passwords)

print(hashed_passwords)