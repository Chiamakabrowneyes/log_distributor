Log distributor 
A simulation and backend system for routing log packets to registered analyzers, built with Flask and Docker

1. Build the Image

In the project root:

docker build -t resolve_ai .

2. Run the Container

docker run -p 5000:5000 resolve_ai

This exposes the backend at http://localhost:5000

3. Run the Simulation

Open a new terminal (outside the container):
python simulation/simulate.py
Make sure BASE_URL in simulate.py is: BASE_URL = "http://localhost:5000"

4. View the simulation 
keep refreshing this page for status updates on all the analyzers: "http://localhost:5000/status"