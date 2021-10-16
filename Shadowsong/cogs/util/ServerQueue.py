import collections


class Video:
    def __init__(self, id:str, title:str, length:int):
        self.id = id
        self.title = title
        self.length = length

def nested_dict():
        return collections.defaultdict(nested_dict)

class ServerQueue:
    # Create a 'database' for queue and loop_queue       
    __database = nested_dict()
    #
    def __init__(self, server_id:int):
        self.server_id = server_id

    def register(self):
        self.__database[self.server_id] = {
            "queue":[],
            "loop":[]
        }
        print(f"[{self.server_id}] Registered")

    def dispose(self):
        del(self.__database[self.server_id])
        print(f"[{self.server_id}] Disposed")

    #-------------Normal queue's functions-------------
    def add_to_queue(self, vid:Video):
        self.__database[self.server_id]["queue"].append(vid)

    def get_length(self):
        return int(len(self.__database[self.server_id]["queue"]))
    
    def get_current_playing(self):
        if self.get_length() == 0:
            result = None
        else:
            result = self.__database[self.server_id]["queue"][0]
        return result

    def get_item(self, index:int):
        result = self.__database[self.server_id]["queue"][index]
        if result is None:
            raise IndexError
        else:
            return result

    def remove_in_queue(self, index:int):
        del self.__database[self.server_id]["queue"][index]

    def skip_current(self): #this is only for $skip command
        if self.get_length() <= 1:
            raise IndexError
        else:
            next_item = self.__database[self.server_id]["queue"][1]
            self.remove_in_queue(0)
            self.__database[self.server_id]["queue"].insert(1, next_item)

    
    #-------------Transfer functions-------------
    def transfer_to_loop(self):
        pass

    def transfer_to_queue(self):
        pass

    #-------------Loop queue's functions-------------

    def get_loop(self):
        pass