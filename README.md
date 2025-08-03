<img width="952" height="794" alt="image" src="https://github.com/user-attachments/assets/677d11a8-e3a1-4597-9d33-1dfb2ef94ae2" />

How to Run Locally-
Requirements:
•	Docker & Docker Compose
•	Git
•	Conda Environment with GDAL and POSTGIS Support
•	Virtual Environment with requirements.txt installed

📦 Clone and Set Up
git clone https://github.com/NayanVeer/3d-geo-webapp.git

Setup Pelias Geocoder-
-Download repo and essential files such as WOF, OSM, Custom CSV (in proper format), etc.

🐳Start with Docker Compose
docker-compose up --build
•	for API, Elasticsearch, CSV Importer, Libpostal, Schema, Postgis, Openstreetmap

This will start:
•	PostgreSQL + PostGIS
•	FastAPI backend
•	Pelias geocoder 

Then Run following Command from backend folder
uvicorn main:app –reload   
(This will start the FastAPI and the tools like nearby search and history)

🌍 Open Frontend

Visit: `http://localhost:8000` to explore the 3D Pune city map.

<img width="954" height="464" alt="image" src="https://github.com/user-attachments/assets/8ba75d66-9a5a-4319-b98a-bd72516198be" />

<img width="954" height="462" alt="image" src="https://github.com/user-attachments/assets/91056de8-d35c-43d0-af93-cb495ae683d4" />

<img width="1907" height="917" alt="image" src="https://github.com/user-attachments/assets/7de85207-7a1c-4431-9fcc-e0dbc9eaffe0" />


Contact:
Nayankumar Appaso Veer
M.Tech Geospatial Engineering, IIT Roorkee
Email: mailto:nayanveer6@gmail.com

For suggestions, contributions, or issues — feel free to raise an [Issue](https://github.com/3D-Geo-Webapp/issues) or open a PR.

