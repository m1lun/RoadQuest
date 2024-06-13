# RoadQuest Documentation

## Overview

RoadQuest is an AI-assisted roadtrip planner that provides hotel and restaurant recommendations. 

## Installation

Before running RoadQuest, ensure that the following dependencies are installed:

- Django: `pip install django`
- Amadeus: `pip install amadeus`
- Python-dotenv: `pip install python-dotenv`
- Requests: `pip install requests`

## Usage

1. Clone the RoadQuest repository to your local machine.
2. Navigate to the project directory.
3. Create a virtual environment (optional but recommended).
4. Install the required dependencies using the commands mentioned in the Installation section.
5. Create a `.env` file in the project directory and add your API keys to it.

Example `.env` file: <br />
OWM_KEY=YOUR_OPENWEATHERMAP_API_KEY <br />
google_key=YOUR_GOOGLE_MAPS_API_KEY
mapbox_key =YOUR_MAPBOX_API_KEY

6. Before starting the server, migrate by running `python manage.py makemigrations` and `python manage.py migrate`.
7. Start the Django development server by running `python manage.py runserver`.
8. Access RoadQuest in your web browser at `http://localhost:8000`.
