# SpaceX Launch Dashboard (Dash + Plotly)

An interactive dashboard built with **Dash** and **Plotly** to explore SpaceX launch outcomes by launch site and payload range.

## Features
- Filter by **Launch Site** (All Sites or a single site)
- Pie chart: **Successful launches by site** or **Success vs Failure** for a selected site
- Filter by **Payload Mass (kg)** using a range slider
- Scatter plot: **Payload vs Outcome**, colored by **Booster Version Category**

## Tech Stack
- Python, Pandas
- Dash, Plotly Express

## Run Locally
```bash
pip install -r requirements.txt
python app.py