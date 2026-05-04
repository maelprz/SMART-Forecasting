# SMART FORECAST  
### Predicting Urban Unemployment in Philippine Smart Cities  

---

## 📌 Overview  

SMART FORECAST is a web-based dashboard prototype designed to visualize and compare predicted urban unemployment trends in selected Philippine cities. The system aims to support data-driven decision-making for local government units by providing early insights into potential unemployment changes.

This project is developed as part of an academic research study at the University of San Jose–Recoletos, Cebu, Philippines.

---

## 🎯 Objectives  

- Provide a visual dashboard for unemployment forecasting in Philippine cities  
- Compare predictions from:  
  - A modern predictive model (SMART Forecast)  
  - A traditional statistical approach  
- Present data in an intuitive and accessible format for policymakers  

---

## 🧠 System Description  

The system is implemented as a web-based dashboard using Streamlit, allowing users to:

- View a map of the Philippines with major cities  
- Select a city to display relevant information  
- Compare unemployment predictions between two models  
- Analyze key indicators such as:
  - Population  
  - Unemployment rate (forecasted)  

---

## ⚙️ Technology Stack  

- Python  
- Streamlit – for dashboard interface  
- Pandas – for data handling  

---

## ▶️ Quick Start

1. Open a terminal in the project root folder.
2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the virtual environment:

Windows PowerShell:

```bash
.venv\Scripts\activate
```

Git Bash:

```bash
source .venv/Scripts/activate
```

4. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

5. Run the dashboard:

```bash
python -m streamlit run app.py
```

---

## 🤖 Machine Learning Approach  

This prototype does not implement a machine learning model from scratch.

Instead, it is designed to integrate with a pre-trained machine learning model (e.g., XGBoost) for generating unemployment forecasts.

This approach is suitable for the prototype stage and demonstrates how predictive analytics can be incorporated into a real-world system.

---

## 🖥️ Features  

- Interactive dashboard layout  
- Split-screen interface:
  - Left: Map visualization  
  - Right: City data panel  
- Model comparison:
  - SMART Forecast (ML-based)  
  - Traditional model (baseline)  
- Simple and user-friendly design  

---

## 📊 Sample Data (Prototype Only)  

The current version uses placeholder data for demonstration purposes.

Actual implementation can be connected to:

- Philippine Statistics Authority (PSA)  
- Bangko Sentral ng Pilipinas (BSP)  
- World Bank  

---

## 👨‍💻 Authors  

- Brian Joseph B. Aratia  
- Robert Emmanuel C. Avelino  
- Mel Stephen A. Perez  

School of Computer Studies  
University of San Jose–Recoletos  
Cebu, Philippines  

---

## 📌 Note  

This project is a prototype decision-support tool and is intended for academic and research purposes.