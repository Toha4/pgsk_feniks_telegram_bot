from datetime import datetime, timedelta


class BlockTimer:
    def __init__(self, seconds_block: int):
        self.__delta = timedelta(seconds=seconds_block)
        self.__stop = None

    def start_block(self):
        self.__stop = datetime.now() + self.__delta

    def is_block(self) -> bool:
        return self.__stop != None and datetime.now() < self.__stop
    
    def get_time_left(self):
        if self.is_block():
            return (self.__stop - datetime.now()).seconds # type: ignore
        
        return None
