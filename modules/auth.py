import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def load_auth():
    with open("users.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        'app_cookie',
        'abcdef',
        cookie_expiry_days=1
    )

    return authenticator, config


def save_users(config):
    with open("users.yaml", "w") as file:
        yaml.dump(config, file)