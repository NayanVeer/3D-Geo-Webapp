<img width="952" height="794" alt="image" src="https://github.com/user-attachments/assets/677d11a8-e3a1-4597-9d33-1dfb2ef94ae2" />

How to Run Locally- <br/>
Requirements:<br/>
•	Docker & Docker Compose<br/>
•	Git<br/>
•	Conda Environment with GDAL and POSTGIS Support<br/>
•	Virtual Environment with requirements.txt installed<br/>

📦 Clone and Set Up<br/>
git clone https://github.com/NayanVeer/3d-geo-webapp.git
<br/>
Setup Pelias Geocoder-<br/>
-Download repo and essential files such as WOF, OSM, Custom CSV (in proper format), etc.<br/>

🐳Start with Docker Compose<br/>
docker-compose up --build<br/>
•	for API, Elasticsearch, CSV Importer, Libpostal, Schema, Postgis, Openstreetmap<br/>

This will start:<br/>
•	PostgreSQL + PostGIS<br/>
•	FastAPI backend<br/>
•	Pelias geocoder <br/>

Then Run following Command from backend folder<br/>
uvicorn main:app –reload   <br/>
(This will start the FastAPI and the tools like nearby search and history)<br/>

🌍 Open Frontend<br/>

Visit: `http://localhost:8000` to explore the 3D Pune city map.<br/>

<img width="954" height="464" alt="image" src="https://github.com/user-attachments/assets/8ba75d66-9a5a-4319-b98a-bd72516198be" />

<img width="954" height="462" alt="image" src="https://github.com/user-attachments/assets/91056de8-d35c-43d0-af93-cb495ae683d4" />

<img width="1907" height="917" alt="image" src="https://github.com/user-attachments/assets/7de85207-7a1c-4431-9fcc-e0dbc9eaffe0" />


Contact:<br/>
Nayankumar Appaso Veer<br/>
M.Tech Geospatial Engineering, IIT Roorkee<br/>
Email: mailto:nayanveer6@gmail.com<br/>

For suggestions, contributions, or issues — feel free to raise an [Issue](https://github.com/3D-Geo-Webapp/issues) or open a PR.

