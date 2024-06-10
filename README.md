# RoadQuest Documentation

## Overview

...

## Installation

Before running RoadQuest, ensure that the following dependencies are installed:

- Django: `pip install django`
- Python-dotenv: `pip install python-dotenv`
- Requests: `pip install requests`

## Usage

1. Clone the RoadQuest repository to your local machine.
2. Navigate to the project directory.
3. Create a virtual environment (optional but recommended).
4. Install the required dependencies using the commands mentioned in the Installation section.
5. Create a `.env` file in the project directory and add your API keys to it.

Example `.env` file:
OWM_KEY=YOUR_OPENWEATHERMAP_API_KEY
GOOGLE_MAPS_KEY=YOUR_GOOGLE_MAPS_API_KEY

6. Start the Django development server by running `python manage.py runserver`.
7. Access RoadQuest in your web browser at `http://localhost:8000`.
