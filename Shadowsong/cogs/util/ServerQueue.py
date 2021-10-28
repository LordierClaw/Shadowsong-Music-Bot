import re
from termcolor import colored

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
    def loop(self):
        return self.__database[self.server_id]["is_loop"]
    
    @loop.setter
    def loop(self, args:bool):
        self.__database[self.server_id]["is_loop"] = args

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
        self.__database[self.server_id] = {"queue": Queue(), "loopqueue": LoopQueue(), "is_loop":False}
        print(colored(f"[{self.server_id}]", "yellow"), colored("Registered", "green"), f"- Active Server: {len(self.__database)}")

    def dispose(self):
        if self.server_id in self.__database:
            self.Queue.clear()
            self.LoopQueue.clear()
            self.__database.pop(self.server_id)
            print(colored(f"[{self.server_id}]", "yellow"), colored("Registered", "red"), f"- Active Server: {len(self.__database)}")
        else:
            pass
    
    #-------------Transfer functions-------------
    def transfer_to_loop(self):
        if self.loop == False:
            for item in self.Queue.list:
                self.LoopQueue.add(item)
            self.Queue.clear()
            self.loop = True
            print(colored(f"[{self.server_id}]", "yellow"), "Loop on")

    def transfer_to_queue(self):
        if self.loop == True:
            if self.LoopQueue.length == 1:
                self.Queue.add(self.LoopQueue.now_playing)
            else:
                for i in range(self.LoopQueue.location, self.LoopQueue.length):
                    self.Queue.add(self.LoopQueue.get(i))
                for i in range(0, self.LoopQueue.location):
                    self.Queue.add(self.LoopQueue.get(i))
            self.LoopQueue.clear()
            self.loop = False
            print(colored(f"[{self.server_id}]", "yellow"), "Loop off")

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

#----------------LoopQueue--------------------
class LoopQueue:
    def __init__(self):
        self._loopqueue = []
        self._location = 0

    @property
    def location(self):
        return self._location

    @property
    def is_empty(self):
        return not self._loopqueue
    
    @property
    def list(self):
        if not self._loopqueue:
            raise err.QueueIsEmpty
        return self._loopqueue

    @property
    def length(self):
        return len(self._loopqueue)

    @property
    def now_playing(self):
        if not self._loopqueue:
            raise err.QueueIsEmpty
        return self._loopqueue[self._location]

    @property
    def upcoming(self):
        if not self._loopqueue:
            raise err.QueueIsEmpty
        if len(self._loopqueue) == 1:
            #single loop
            next_track = self._loopqueue[0]
        else:
            #queue loop
            if self._location == len(self._loopqueue) - 1:
                next_track = self._loopqueue[0]
            else:
                next_track = self._loopqueue[self._location + 1]
        return next_track
    
    def advance(self):
        if len(self._loopqueue) == 1:
            #single loop
            pass
        else:
            #queue loop
            if self._location == len(self._loopqueue) - 1:
                self._location = 0
            else:
                self._location += 1

    def add(self, item:Track):
        self._loopqueue.append(item)

    def remove(self, index:int):
        if index >= self.length or index < 0:
            raise err.TrackNotExist
        if index < self._location:
            self._location -= 1
        self._loopqueue.pop(index)

    def get(self, index:int):
        if index >= self.length or index < 0:
            raise err.TrackNotExist

        return self._loopqueue[index]

    def clear(self):
        self._loopqueue.clear()
        self._location = 0