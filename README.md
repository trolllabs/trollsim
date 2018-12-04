Troll simulator
===============

Part of master project prototype fall 2018. The name "Troll simulator" comes from the name of our lab, Trolllabs. The project itself revolves around human machine interactions in the context of a cockpit simulator. With the prototypes, we aim to show possibilities for different types of interfacing between backend/frontend/X-Plane.

The current architecture allows arduino data to be sent to X-Plane as datarefs (X-Plane's packet structure), but also for X-Plane to write to arduino. It is also possible to manipulate and visualize the data before it reaches either of the endpoint through a web server/client (frontend).

    .
    ├── arduino                 # Sensor/actuator codebase
    ├── backend                 # Written in python 3, handles the data parsing between endpoints
    ├── frontend                # node webserver and webclient. Visualizes data and have options
    │                             for data mutation
    ├── snippets                # Generalized code snippets from discarded prototypes
    └── README.md

