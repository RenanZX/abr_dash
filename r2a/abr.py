
from player.parser import *
from r2a.ir2a import IR2A

class ABR(IR2A):
    def __init__(self, id):
      IR2A.__init__(self,id)

    @abstractmethod
    def handle_xml_request(self, msg):
        pass

    @abstractmethod
    def handle_xml_response(self, msg):
        pass

    @abstractmethod
    def handle_segment_size_request(self, msg):
        pass

    @abstractmethod
    def handle_segment_size_response(self, msg):
        pass

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def finalization(self):
        pass
