import os, json
from os.path import join, dirname
# from dotenv import load_dotenv

# dotenv_path = join(dirname(__file__), ".env")
# load_dotenv(dotenv_path)

DISCODE_BOT_TOKEN_FAMILYFINANCE = os.environ.get("DISCODE_BOT_TOKEN_FAMILYFINANCE")

# CREDENTIALS = {
#     "type": "service_account",
#     "project_id": os.environ.get("PROJECT_ID"),
#     "private_key_id": os.environ.get("PRIVATE_KEY_ID"),
#     "private_key": os.environ.get("PRIVATE_KEY"),
#     "client_email": os.environ.get("CLIENT_EMAIL"),
#     "client_id": os.environ.get("CLIENT_ID"),
#     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#     "token_uri": "https://oauth2.googleapis.com/token",
#     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#     "client_x509_cert_url": os.environ.get("CLIENT_X509_CERT_URL"),
# }

# with open("credentials.json", "w") as file:
#     json.dump(CREDENTIALS, file, indent=2)
