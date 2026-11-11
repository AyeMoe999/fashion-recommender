# 👗 AI Fashion Recommender System
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Fuzzy](https://img.shields.io/badge/Scikit--Fuzzy-0.5.0-orange)](https://github.com/scikit-fuzzy/scikit-fuzzy)
[![NumPy](https://img.shields.io/badge/NumPy-2.1.3-013243?logo=numpy&logoColor=white)](https://numpy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.10.0-11557c)](https://matplotlib.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
An intelligent, explainable AI Fashion Recommendation System built with **Flask** and **Fuzzy Logic (scikit-fuzzy)**. It evaluates user inputs including **Occasion**, **Style Preference**, **Age**, and **Cultural Context** to deliver personalized outfit suggestions alongside transparent, visual fuzzy inference insights.
---
## 🌟 Key Features
- **Explainable AI (XAI) with Fuzzy Logic**: Unlike black-box neural networks, decisions are computed using human-interpretable linguistic variables and Mamdani fuzzy rules.
- **Dual Cultural Wardrobe Support**: Seamlessly curates recommendations for both **Traditional Attire** (e.g., Burmese traditional wear like *Htamein* and lace sets) and **Western Attire** (e.g., suits, cocktail dresses, casual sets).
- **Demographic & Context Aware**: Balances age brackets (`Young` vs. `Mature`) and contextual settings (`Home`, `Outing`, `Work`, `Event`).
- **Dynamic Vibe Breakdown**: Calculates normalized percentage matches across 4 distinct fashion vibes:
  - 🛋️ **Comfort Wear** (Relaxed & at ease)
  - 🚶 **Daily Wear** (Everyday versatile look)
  - 💼 **Professional Wear** (Office & business ready)
  - ✨ **Event Wear** (Party & special occasions)
- **Visual Inference Graph**: Generates real-time fuzzy output charts with Matplotlib to show how each category score was derived.
- **Modern Responsive UI**: Clean, card-based interface with interactive sliders, expandable suggestions ("See More"), and toggleable insight panels.


## 📁 Project Structure
```text
fashion-recommender/
│
├── app.py                 # Flask web application & outfit routing logic
├── control.py             # Fuzzy Logic Controller (FLC) & graph generation
├── requirements.txt       # Python package dependencies
├── templates/
│   └── index.html         # Responsive web UI & Jinja2 template
└── static/
    └── images/            # Outfit image catalog & dynamic fuzzy graphs
🛠️ Tech Stack
Backend: Python 3, Flask 3.0
Fuzzy Inference: Scikit-Fuzzy (skfuzzy), NumPy, SciPy
Visualization: Matplotlib (Headless Agg backend)
Frontend: HTML5, CSS3, JavaScript, Outfit Font
🚀 Getting Started
Prerequisites
Python 3.9, 3.10, or 3.11 installed on your machine.
pip package manager.
Installation
Clone the repository:

bash


git clone https://github.com/AyeMoe999/fashion-recommender.git
cd fashion-recommender
Create and activate a virtual environment (recommended):

Windows:
powershell


python -m venv venv
.\venv\Scripts\activate
macOS / Linux:
bash


python3 -m venv venv
source venv/bin/activate
Install dependencies:

bash


pip install -r requirements.txt
Run the Flask application:

bash


python app.py
Open your browser: Navigate to http://127.0.0.1:5001.

💡 How to Use
Select an Occasion: Choose between Home, Outing, Work, or Event.
Adjust Style Preference: Drag the slider from Simple 
→
→ Trendy 
→
→ Elegant.
Set Age: Select age (from 15 to 80).
Choose Cultural Style: Pick Traditional (Burmese) or Western.
Click "Recommend outfit":
View your Dominant Recommended Style.
Check the Style Match by Category percentage bars.
Browse recommended outfit cards and click "See more" for extra suggestions.
Click "View insights" to inspect the match strength and Matplotlib fuzzy membership output chart.
🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request:

Fork the Project
Create your Feature Branch (git checkout -b feature/AmazingFeature)
Commit your Changes (git commit -m 'Add some AmazingFeature')
Push to the Branch (git push origin feature/AmazingFeature)
Open a Pull Request
