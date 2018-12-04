Acts like a hub between user interface (webclient), arduino and X-Plane.

Usage
-----

To run backend, get the dependencies from requirements.txt and run main

	python3 main.py

The program will wait for frontend to connect at port 8005 before doing anything.
While a dummy TCP client can work, but a dedicated frontend is written in the frontend directory.
