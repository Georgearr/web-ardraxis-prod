# Meloria Event Registration System

## Overview
This is a Flask web application for event registration at IGS (Indonesia Global School). The system manages registrations for various competitions, workshops, and mini-games as part of the Meloria event. Data is stored in real-time to Google Sheets with automatic popup notifications including LINE group links.

## Project Structure
- **main.py**: Main Flask application with all routes, Google Sheets integration, and form handling
- **templates/**: HTML templates for all pages
  - **meloria/**: Event-specific registration pages with AJAX form submission and popup
- **static/**: CSS, JavaScript, and images
- **line_groups.json**: Configuration file storing LINE group links for each event
- **requirements.txt**: Python dependencies

## Technology Stack
- **Backend**: Flask 3.0.2 (Python web framework)
- **Data Storage**: Google Sheets API (gspread) - real-time storage with separate sheets per event
- **Frontend**: HTML templates with Jinja2, vanilla JavaScript for AJAX forms
- **Port**: 5000 (configured for Replit environment)

## Features
The application includes registration forms for:
- Language competitions (Mandarin, French, German, Japanese, Korean, Arabic)
- Debates (Indonesian and English)
- Creative competitions (Cosplay, Web Cloning, Poetry Reading, Infographic Design, Totebag Decoration, **Competitive Programming**)
- Talent show (IGS Got Talent)
- Quiz competition (Cerdas Cermat)
- Workshops (Calligraphy, Recycling)
- Mini-games (Board Games, Noraebang, Word Chain, Mystery Color)

### Key Features:
- ✅ Real-time data sync to Google Sheets
- ✅ Separate worksheet for each event type
- ✅ Success popup after registration with clickable LINE group link
- ✅ Responsive design with overflow fixes
- ✅ AJAX form submission (no page reload)

## Environment Variables Required
- **GOOGLE_SHEETS_CREDENTIALS**: JSON credentials from Google Cloud service account
- **GOOGLE_SPREADSHEET_NAME** (optional): Name of the Google Spreadsheet (default: "Meloria Event Registration")

## Recent Changes
- 2025-11-09: Major update - Google Sheets integration
  - Migrated from Excel (openpyxl) to Google Sheets API (gspread)
  - Added real-time data synchronization
  - Created line_groups.json for LINE group link management
  - Implemented success popup with LINE group link after registration
  - Added competitive programming event template
  - Fixed overflow issues on meloria event page (e_meloria.css)
  - Removed Excel files from data folder
  - Updated all registration forms to use AJAX for smooth UX

- 2025-11-09: Initial setup for Replit environment
  - Configured Flask to run on 0.0.0.0:5000 for Replit proxy compatibility
  - Created .gitignore for Python projects
  - Set up workflow for automatic deployment

## How It Works
1. Users visit the homepage and navigate to event pages
2. Registration forms collect participant information via AJAX
3. Form data is saved to Google Sheets in real-time (each event gets its own worksheet)
4. Upon successful registration, a popup appears with the LINE group link
5. Users can click the link to join the event's LINE group
