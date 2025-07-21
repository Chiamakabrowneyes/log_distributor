"""This class defines the Log Packet"""

class LogPacket: 
    def __init__(self, packet_id, log, duration, system):
        self.packet_id = packet_id
        self.log = log
        self.duration = duration
        self.system = system
        self.system.packets[packet_id] = self

    def __str__(self):
        return f"Packet ID: {self.packet_id}, LogMessage: {self.log}"