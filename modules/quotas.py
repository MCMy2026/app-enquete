import yaml

def get_quotas():
    with open("config/quotas.yaml", "r") as f:
        return yaml.safe_load(f)