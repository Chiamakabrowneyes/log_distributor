"""
The goal is to design a high-throughput logs distributor that will act as an initial receiver of
packets of log messages, where each packet could have multiple log messages. The distributor
receives log message packets from a number of agents that collect and transmit
application/infrastructure logs. The distributor fronts several analyzers, each analyzer being
assigned a relative weight (e.g. 0.4, 0.3, 0.1, 0.2) - if it helps you can assume that the weights
add up to 1.0. The distributor should route log message packets to analyzers, so that eventually
each analyzer analyzes a fraction of log messages roughly proportional to their relative weight.
"""


from flask import Flask, request, jsonify
from threading import Thread
import time
from datetime import timedelta
import logging


from models.analyzer import Analyzer
from models.packet import LogPacket
from models.distributor import DistributorSystem



app = Flask(__name__)
system = DistributorSystem()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)



@app.route("/upload_packet", methods = ["POST"])
def upload_packet():
    data = request.get_json()
    packet_id = data.get("packet_id")
    log = data.get("logs")
    try:
        duration = timedelta(seconds=float(data.get("duration")))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid duration"}), 400

    if not data or not packet_id or not log or not duration:
        return jsonify({"error": "Missing data"}), 404
    
    if packet_id in system.packets:
        return jsonify({"error": "Package already uploaded"}), 409
    
    packet = LogPacket(packet_id, log, duration, system)
    thread = Thread(target=system.distributeLog, args=(packet,), daemon=True)
    system.threads[packet_id] = thread
    thread.start()
    return jsonify({"success": "Package successfully uploaded"}), 201


@app.route("/register_analyzer", methods = ["POST"])
def register_analyzer():
    data = request.get_json()
    analyzer_id = data.get("analyzer_id")
    weight = data.get("weight")
    limit = data.get("limit")


    if not analyzer_id or not weight:
        return jsonify({"error": "Missing Data"}), 404
    
    if analyzer_id in system.analyzers:
        return jsonify({"error": "Analyzer has already been registered"}), 409
    
    analyzer = Analyzer(analyzer_id, float(weight), system, limit if limit else 10)
    system.initialize_round_robin_queue()
    return jsonify({"success": f"{analyzer.analyzer_id} has been registered"}), 201


@app.route("/toggle_analyzer", methods = ["POST"])
def toggle_analyzer():
    data = request.get_json()
    analyzer_id = data.get("analyzer_id")
    

    if not data or not analyzer_id:
        return jsonify({"error": "Missing data"}), 404
    
    if analyzer_id not in system.analyzers:
        return jsonify({"error": "Analyzer does not exist in system"}), 409
    
    analyzer = system.analyzers[analyzer_id]
    status = not analyzer.isOnline
    system.toggle(analyzer.analyzer_id, status)
    system.initialize_round_robin_queue()
    return jsonify({"success": f"Set {analyzer_id} to online status of {status}"}), 201


@app.route("/display_logs/<analyzer_id>", methods = ["GET"])
def display_logs(analyzer_id):
    if analyzer_id not in system.analyzers:
        return jsonify({"error": "Anaylzer does not exist"}), 409
    
    analyzer = system.analyzers[analyzer_id]
    logs = [
            {"packet_id": pid, "log": log, "finishes_at": str(time)}
            for pid, log, time in analyzer.analyzer_packets
        ]
    return jsonify({"logs": logs}), 200


@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        analyzer_id: {
            "online": analyzer.isOnline,
            "queue": len(analyzer.analyzer_packets)
        }
        for analyzer_id, analyzer in system.analyzers.items()
    })


@app.route("/reset", methods=["DELETE"])
def reset_system():
    system.analyzers.clear()
    system.locks.clear()
    system.threads.clear()
    system.packets.clear()
    system.round_robin_queue.clear()
    print("System has been reset.")
    return jsonify({"success": "System has been reset."}), 200


def analyzer_cleanup_loop(interval=5):
    while True:
        for analyzer in system.analyzers.values():
            analyzer.validateAnalyzer()
        time.sleep(interval)


if __name__ == "__main__":
    cleanup_thread = Thread(target=analyzer_cleanup_loop, daemon=True)
    cleanup_thread.start()
    app.run(host="0.0.0.0", port=5000, threaded=True)


        





