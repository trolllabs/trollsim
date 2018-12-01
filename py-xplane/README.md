Troll simulator
===============

Part of master project prototype fall 2018, where we want to show possibilities for different types
of interfacing between backend/frontend/X-Plane.

Usage
-----

To run backend, get the dependencies from requirements.txt and run main

	python3 main.py

The program will wait for frontend to connect before doing anything.
A dummy TCP client can work, but a dedicated frontend is written in the frontend directory.
Get the npm dependencies in frontend before running index.js from the frontend directory.

	node index.js

The webserver is set up to be accessed at address 127.0.0.1:8005
