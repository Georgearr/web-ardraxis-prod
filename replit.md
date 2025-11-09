# Meloria Event Registration System

## Overview
This is a Flask web application for event registration at IGS (Indonesia Global School). The system manages registrations for various competitions, workshops, and mini-games as part of the Meloria event.

## Project Structure
- **main.py**: Main Flask application with all routes and form handling
- **templates/**: HTML templates for all pages
  - **meloria/**: Event-specific registration pages
- **static/**: CSS, JavaScript, and images
- **data/**: Excel files for storing registration data
- **requirements.txt**: Python dependencies

## Technology Stack
- **Backend**: Flask 3.0.2 (Python web framework)
- **Data Storage**: Excel files using openpyxl library
- **Frontend**: HTML templates with Jinja2
- **Port**: 5000 (configured for Replit environment)

## Features
The application includes registration forms for:
- Language competitions (Mandarin, French, German, Japanese, Korean, Arabic)
- Debates (Indonesian and English)
- Creative competitions (Cosplay, Web Cloning, Poetry Reading, Infographic Design, Totebag Decoration)
- Talent show (IGS Got Talent)
- Quiz competition (Cerdas Cermat)
- Workshops (Calligraphy, Recycling)
- Mini-games (Board Games, Noraebang, Word Chain, Mystery Color)

## Recent Changes
- 2025-11-09: Initial setup for Replit environment
  - Added openpyxl to requirements.txt
  - Configured Flask to run on 0.0.0.0:5000 for Replit proxy compatibility
  - Created .gitignore for Python projects
  - Set up workflow for automatic deployment

## How It Works
1. Users visit the homepage and navigate to event pages
2. Registration forms collect participant information
3. Form data is saved to Excel files in the data/ folder
4. Each event has its own Excel file for tracking registrations
