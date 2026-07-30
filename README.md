# 🌍 Carbon Footprint Analyzer

A Streamlit web app that estimates your household's carbon emissions from
**electricity usage**, **vehicle travel**, and **food habits** — then uses
a small regression model to **project your yearly impact**, benchmarks you
against national/global averages, and gives a ranked improvement plan.

## ✨ Features

- Emission breakdown (pie chart) across electricity / travel / food
- Benchmark comparison vs. Average Indian, Global Average, Paris Agreement target
- **AI trend projection**: a scikit-learn regression model (trained on synthetic
  data generated at runtime) projects your footprint 1–10 years ahead, factoring
  in gradual grid decarbonisation
- Eco Score (A–F grade)
- Ranked, personalised improvement tips
- "What-if" simulator — drag sliders to see the impact of behaviour changes
- Downloadable plain-text report

**No external dataset download is required.** All emission factors are
well-established public constants (see `app.py`), and the "AI" trend model
trains itself on synthetically generated data each time the app starts
(see `model.py`).

## 🗂️ Project Structure

```
carbon-footprint-analyzer/
├── app.py              # Streamlit UI + calculations
├── model.py            # Synthetic-data regression model (the "AI" part)
├── requirements.txt    # Python dependencies
├── .gitignore
└── README.md
```

## 🖥️ Running it locally in VS Code

Yes — this project runs perfectly in VS Code. Steps:

1. **Install prerequisites**
   - [Python 3.9+](https://www.python.org/downloads/)
   - [VS Code](https://code.visualstudio.com/) with the official **Python extension** installed.

2. **Open the project folder in VS Code**
   `File → Open Folder…` → select `carbon-footprint-analyzer`.

3. **Create a virtual environment** (open a VS Code terminal: `` Ctrl+` ``)
   ```bash
   python -m venv venv
   ```
   Activate it:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
   VS Code will usually prompt "Select this environment" — click yes.

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the app**
   ```bash
   streamlit run app.py
   ```
   It opens automatically at `http://localhost:8501`.

## ⬆️ Uploading this project to GitHub

Checklist of what a project needs before pushing (all already included here):
`README.md`, `.gitignore`, `requirements.txt`, and clean, working source code.

Steps:

1. Create a new repository on GitHub (don't initialize it with a README, since
   you already have one) → copy its URL, e.g.
   `https://github.com/<your-username>/carbon-footprint-analyzer.git`

2. In the VS Code terminal, from inside the project folder:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Carbon Footprint Analyzer"
   git branch -M main
   git remote add origin https://github.com/<your-username>/carbon-footprint-analyzer.git
   git push -u origin main
   ```

3. Refresh your GitHub repo page — your project is live.

4. (Optional, recommended) Deploy it for free on
   [Streamlit Community Cloud](https://share.streamlit.io/) by connecting your
   GitHub repo — this gives you a live demo link to put in your README/resume.

## 📌 Notes on emission factors

Values used are widely cited approximations (grid electricity ≈ 0.82 kg CO₂e/kWh,
vehicle factors per km by type, diet factors per day by type). They're meant for
educational/estimation purposes, not certified carbon accounting.
