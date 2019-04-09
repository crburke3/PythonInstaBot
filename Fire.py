from firebase_admin import firestore
from firebase_admin import credentials
import firebase_admin


class Fire:
    db = ""

    def __init__(self):
        cred = credentials.Certificate('instabot-bee53-firebase-adminsdk-uuob3-43254d1074.json')
        firebase_admin.initialize_app(cred, {
          'projectId': "instabot-bee53",
        })
        self.db = firestore.client()


