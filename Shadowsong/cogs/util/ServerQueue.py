class Track:
    def __init__(self, id:str, title:str, length:int):
        self.id = id
        self.title = title
        self.length = length

#---------------Exception-----------------
class err:
    class QueueIsEmpty(Exception):
        pass

    class NoMoreTracks(Exception):
        pass

    class CantRemoveCurrentTrack(Exception):
        pass

    class TrackNotExist(Exception):
        pass

    class ServerNotRegistered(Exception):
        pass

class Server:
    __database = {}

    def __init__(self, server_id:int):
        self.server_id = server_id

    @property
    def Queue(self):
        if not self.server_id in self.__database:
            raise err.ServerNotRegistered
        return self.__database[self.server_id]["queue"]

    @property
    def LoopQueue(self):
        if not self.server_id in self.__database:
            raise err.ServerNotRegistered
        return self.__database[self.server_id]["loopqueue"]
    
    def is_registered(self):
        return self.server_id in self.__database
    
    def register(self):
        self.__database[self.server_id] = {"queue": Queue(), "loopqueue": LoopQueue()}
        print(f"[{self.server_id}] Registered - Active Server: {len(self.__database)}")

    def dispose(self):
        if self.server_id in self.__database:
            self.Queue.clear()
            self.LoopQueue.clear()
            self.__database.pop(self.server_id)
            print(f"[{self.server_id}] Disposed - Active Server: {len(self.__database)}")
        else:
            pass
    
    #-------------Transfer functions-------------
    def transfer_to_loop(self):
        pass

    def transfer_to_queue(self):
        pass
#----------------Queue--------------------

class Queue:
    def __init__(self):
        self._queue = []
    
    @property
    def is_empty(self):
        return not self._queue
    
    @property
    def list(self):
        if not self._queue:
            raise err.QueueIsEmpty
        return self._queue

    @property
    def length(self):
        return len(self._queue)

    @property
    def now_playing(self):
        if not self._queue:
            raise err.QueueIsEmpty
        return self._queue[0]

    @property
    def upcoming(self):
        if not self._queue:
            raise err.QueueIsEmpty
        if not self._queue[1]:
            raise err.NoMoreTracks
        return self._queue[1]
    
    def add(self, item:Track):
        self._queue.append(item)
    
    def get(self, index:int):
        if index >= self.length or index < 0:
            raise err.TrackNotExist

        return self._queue[index]

    def remove(self, index:int):
        if index >= self.length or index < 0:
            raise err.TrackNotExist

        self._queue.pop(index)

    def clear(self):
        self._queue.clear()


class LoopQueue:
    def clear(self):
        pass