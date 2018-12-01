Troll simulator (python backend/ node frontend)
===============

Usage
-----

To run backend, get the dependencies from requirements.txt and run main

	python3 main.py

The program will wait for frontend to connect at port 8005 before doing anything.
While a dummy TCP client can work, but a dedicated frontend is written in the frontend directory.
Get the npm dependencies in frontend before running index.js from the frontend directory.

	node index.js

The webserver is set up to be accessed at address 127.0.0.1:8000
