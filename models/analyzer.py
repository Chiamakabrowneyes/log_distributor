
""" This class defines the Analyzer Object and its functionalities"""
from collections import deque
import time
from datetime import datetime
from threading import Lock


class Analyzer:
    #Initializes the Anaylzer object parameters
    def __init__(self, analyzer_id, weight, system, limit = 10):
        self.analyzer_id = analyzer_id
        self.weight = weight
        self.isOnline = True
        self.analyzer_packets = deque()
        self.limit = limit
        self.system = system

        self.system.locks[analyzer_id] = Lock()
        self.system.analyzers[analyzer_id] = self

    #Updates the Analyzer queue with a new log packet
    def uploadLog(self, packet):
        packet_id = packet.packet_id
        log = packet.log
        duration = packet.duration
        with self.system.locks[self.analyzer_id]:
            finishing_time = datetime.now() + duration
            self.analyzer_packets.append([packet_id, log, finishing_time])
            print(f"Analyzer {self.analyzer_id}: Recieved {log}")
            time.sleep(0.01)

    
    #Validates the analyzer queue, ensuring that its within limit and doesn't contain expired packets
    def validateAnalyzer(self):
        current_time = datetime.now()
        self.analyzer_packets = deque(
                packet for packet in self.analyzer_packets if packet[2] > current_time
            )
        return len(self.analyzer_packets) < self.limit