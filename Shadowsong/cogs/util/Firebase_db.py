import os
import firebase_admin
from firebase_admin import credentials, db

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
DATABASE_URL = os.getenv("DATABASE_URL")

cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
firebase_admin.initialize_app(cred, {
    'databaseURL': DATABASE_URL
})

class ServerQueue:
    def __init__(self, server_id:str):
        self.server_id = server_id

    class Song:
        def __init__(self, id:str, length:int, title:str):
            self.id = id #video_id
            self.length = length
            self.title = title
    
    def dispose(self):
        ref = db.reference(f"/{self.server_id}/")
        ref.set({})

    #-------------Normal queue's functions-------------
    def get_queue(self):
        ref = db.reference(f"/{self.server_id}/queue/")
        return ref.get()

    def add_to_queue(self, song_item:Song):
        ref = db.reference(f"/{self.server_id}/queue/")
        new_index = len(ref.get())
        ref.update({
            new_index:{
                "id":song_item.id,
                "length":song_item.length,
                "title":song_item.title
            }
        })
    
    def get_current_playing(self):
        ref = db.reference(f"/{self.server_id}/queue/0/")
        data = ref.get()
        return ServerQueue.Song(data["id"], data["length"], data["title"])

    def remove_in_queue(self, index:int):
        ref = db.reference(f"/{self.server_id}/queue/{index}/")
        ref.set({})
    
    #-------------Transfer functions-------------
    def transfer_to_loop(self):
        #transfer all items to ./loop/queue/
        ref = db.reference(f"/{self.server_id}/queue/")
        data = ref.get()
        loop_queue = db.reference(f"/{self.server_id}/loop/queue/")
        loop_queue.set(data)
        #change is_loop in ./loop/
        loop_queue = db.reference(f"/{self.server_id}/loop/")
        loop_queue.update({
            "is_loop":"True"
        })

    def transfer_to_queue(self):
        #transfer all items to ./queue/
        loop_queue = db.reference(f"/{self.server_id}/loop/queue/")
        data = loop_queue.get()
        ref = db.reference(f"/{self.server_id}/queue/")
        ref.set(data)
        #change is_loop in ./loop/
        loop_queue = db.reference(f"/{self.server_id}/loop/")
        loop_queue.update({
            "is_loop":"False"
        })

    #-------------Loop queue's functions-------------
    def get_loop(self):
        ref = db.reference(f"/{self.server_id}/loop/")
        return ref.get()
# ref.update({
#     0:{
#         "id":"ShZ978fBl6Y",
#         "length":204,
#         "title":"Calum Scott - You Are The Reason"
#     },

#     1:{
#         "id":"F4nuUUJ1XlM",
#         "length":253,
#         "title":"You Don't Know - Katelyn Tarver"
#     },

#     2:{
#         "id":"RBumgq5yVrA",
#         "length":234,
#         "title":"Passenger | Let Her Go"
#     }
# })