Log Distributor
A simulation and backend system for routing log packets to registered analyzers.
Built with Flask and containerized using Docker.

Setup Instructions
1. Build the Docker Image:
In the project root directory, run:
docker build -t resolve_ai .

2. Run the Backend Container:
docker run -p 5000:5000 resolve_ai
This exposes the backend server at:
http://localhost:5000

3. Run the Simulation:
Open a new terminal (outside the container) and run:
python simulation/simulate.py
Make sure BASE_URL inside simulate.py is set to:
BASE_URL = "http://localhost:5000"

4. View Analyzer Status:
You can monitor the live status of analyzers (including queue size and online state) by visiting:
http://localhost:5000/status
Refresh this page periodically to see updates.
