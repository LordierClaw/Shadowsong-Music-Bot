import os
import firebase_admin
from firebase_admin import credentials, db

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
DATABASE_URL = os.getenv("DATABASE_URL")

cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
firebase_admin.initialize_app(cred, {
    'databaseURL': DATABASE_URL
})

ref = db.reference("/")
reponse = ref.get()