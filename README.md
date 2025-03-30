# Mochasa — Inventory Policy Visualization System

**Mochasa** is a web application built with **FastAPI** and **React (Vite + TypeScript)** that visualizes dashboards generated from Excel files as the data source. It is focused on generating inventory policies for food production companies.

---

## Features

- Backend API built with **FastAPI** and **Pandas**
- Frontend in **React + TypeScript** with interactive visualizations
- Line charts, pie charts, and analytical tables
- Data loaded from Excel files
- Filters by year, SKU, and warehouse
- Paginated table results

---

## Project Structure

```
mochasa/
├── backend/         # FastAPI backend
│   ├── main.py
│   ├── utils.py
│   ├── constants.py
│   └── requirements.txt
│   └── .env
├── frontend/        # React + Vite frontend
│   ├── src/
│   ├── public/
│   └── .env
├── .gitignore
└── README.md
```

---

## Technologies

- **Frontend**: React, Vite, TypeScript, ApexCharts, TailwindCSS
- **Backend**: Python, FastAPI, Pandas, Uvicorn
- **Deployment**: Fly.io (API), Vercel or Netlify (Frontend)

---

## Author

Maybelline Frere  
[LinkedIn](https://www.linkedin.com/in/maybelline-stefany-frere-quintero-51a763172/) | [GitHub](https://github.com/maysfrer)

---

## License

This project is part of an academic work and does not currently hold a commercial license. For more information, contact the author.
