# 📊 Mochasa — Inventory Policy Visualization System

**Mochasa** is a web application built with **FastAPI** and **React (Vite + TypeScript)** that visualizes dashboards generated from Excel files as the data source. It is focused on generating inventory policies for food production companies.

---

## 🚀 Features

- ✅ Backend API built with **FastAPI** and **Pandas**
- ✅ Frontend in **React + TypeScript** with interactive visualizations
- ✅ Line charts, pie charts, and analytical tables
- ✅ Data loaded from Excel files
- ✅ Filters by year, SKU, and warehouse
- ✅ Paginated table results

---

## 📁 Project Structure

```
mochasa/
├── backend/         # FastAPI backend
│   ├── main.py
│   ├── utils.py
│   ├── constants.py
│   └── requirements.txt
├── frontend/        # React + Vite frontend
│   ├── src/
│   ├── public/
│   └── .env
├── .gitignore
└── README.md
```

---

## ⚙️ Technologies

- **Frontend**: React, Vite, TypeScript, ApexCharts, TailwindCSS
- **Backend**: Python, FastAPI, Pandas, Uvicorn
- **Deployment**: Fly.io (API), Vercel or Netlify (Frontend)

---

## 🧪 Running Locally

### 🔧 Requirements

- Node.js 18+ and npm
- Python 3.11+
- pip

### 1. Clone the repository

```bash
git clone https://github.com/your-username/mochasa.git
cd mochasa
```

### 2. Run Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend will be available at: [http://localhost:8000](http://localhost:8000)

### 3. Run Frontend (React)

```bash
cd ../frontend
npm install
npm run dev
```

Frontend will be available at: [http://localhost:5173](http://localhost:5173)

> Make sure the `.env` file in the frontend contains:
>
> ```env
> VITE_API_URL=http://localhost:8000
> ```

---

## 🌐 Production

- **Backend** deployed on Fly.io → `https://mochasa-api.fly.dev`
- **Frontend** deployed on Vercel or Netlify → `https://mochasa.vercel.app`

---

## 📌 Notes

- Data is automatically loaded on backend startup from Excel files.
- Auxiliary folders like `__archive__/` are Git-ignored and contain reference materials.

---

## 👨‍💼 Author

Maybelline Frere  
[LinkedIn](https://www.linkedin.com/in/maybelline-stefany-frere-quintero-51a763172/) | [GitHub](https://github.com/maysfrer)

---

## 📚 License

This project is part of an academic work and does not currently hold a commercial license. For more information, contact the author.
