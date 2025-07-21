""" This class defines the Distributor Object and its functionalities"""

from collections import deque
from threading import Condition
import random
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


class DistributorSystem:
    def __init__(self):
        self.analyzers = {} 
        self.locks = {} 
        self.threads = {}
        self.packets = {} 
        self.round_robin_queue = deque()
        self.condition = Condition()

    #creates the round robin queue for log distribution
    def initialize_round_robin_queue(self):
        self.round_robin_queue.clear()
        for analyzer_id, analyzer in self.analyzers.items():
            if not analyzer.isOnline:
                continue
            for _ in range(int(analyzer.weight * 10)):
                self.round_robin_queue.append(analyzer_id)

        if self.round_robin_queue:
            random.shuffle(self.round_robin_queue)
            self.round_robin_queue = deque(self.round_robin_queue)

        
    #facilitates the selection of an availabile analyzer
    def select_analyzer(self, wait=True):
        while True:
            with self.condition:
                while self.round_robin_queue:
                    current_analyzer_id = self.round_robin_queue.popleft()
                    if self.analyzers[current_analyzer_id].isOnline and self.analyzers[current_analyzer_id].validateAnalyzer():
                        self.round_robin_queue.append(current_analyzer_id)
                        return self.analyzers[current_analyzer_id]
                             
                if not wait:
                    return None
                
                logger.info("No available analyzers... Waiting")
                self.condition.wait()
    

    def distributeLog(self, packet):
        analyzer = self.select_analyzer(wait=True)
        if not analyzer:
            logger.info("Log is unprocessed because no analyzers are available.")
            return 

        analyzer.uploadLog(packet)
        logger.info("Successfully distributed log packet")
        return 


    def toggle(self, analyzer_id, status):
        analyzer = self.analyzers[analyzer_id]
        analyzer.isOnline = status

        if status:
            with self.condition:
                self.condition.notify_all()

        if not status:
            while analyzer.analyzer_packets:
                new_analyzer = self.select_analyzer(wait=False)
                current_packet = analyzer.analyzer_packets.popleft()
                if new_analyzer:
                    new_analyzer.analyzer_packets.append(current_packet)
                else:
                    logger.info("No available analyzer to reassign packet:", current_packet)
        return 