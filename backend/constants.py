from datetime import datetime
import os

EXCEL_FILE_CONSUMPTIONS = "BASE-2.xlsx"

EXCEL_FILE_COSTS = "BASE-3.xlsx"

# Dictionary to map month names to numbers
MONTHS = {
    "Enero": 1,
    "Febrero": 2,
    "Marzo": 3,
    "Abril": 4,
    "Mayo": 5,
    "Junio": 6,
    "Julio": 7,
    "Agosto": 8,
    "Septiembre": 9,
    "Octubre": 10,
    "Noviembre": 11,
    "Diciembre": 12
}

# CURRENT_YEAR = datetime.now().year
CURRENT_YEAR = 2024 # For testing purposes, set to a fixed year

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
