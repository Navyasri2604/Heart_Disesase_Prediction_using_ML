# ❤️ CardioAI - Enterprise Heart Disease Prediction Platform

CardioAI is a modern, production-ready healthcare web application that predicts the likelihood of heart disease using an ensemble of Machine Learning algorithms. It features a stunning glassmorphism UI, interactive visual analytics, Explainable AI (SHAP), and automated PDF clinical reporting.

## 🌟 Key Features

*   **Ensemble Machine Learning:** Trains and automatically selects the best model from XGBoost, LightGBM, Random Forest, SVM, Logistic Regression, Decision Tree, and KNN.
*   **Explainable AI (SHAP):** Every prediction includes a SHAP summary showing exactly which clinical factors contributed to the risk score and by how much.
*   **Visual Analytics:** Interactive Chart.js and Seaborn visualizations exploring the Cleveland dataset (correlation heatmaps, disease distributions, etc.).
*   **PDF Clinical Reports:** Export comprehensive diagnostic reports generated dynamically with ReportLab.
*   **BMI & Health Score Calculator:** Built-in tools for risk stratification.
*   **AI Health Assistant:** Integrated rule-based chatbot for answering common heart health questions.
*   **Premium Glassmorphism UI:** Stunning dark/light mode responsive design built with HTML5, CSS3, Bootstrap 5, and AOS animations.

## 🛠️ Technology Stack

*   **Backend:** Python 3.12, Django 4.2
*   **Machine Learning:** scikit-learn, XGBoost, LightGBM, SHAP, Pandas, NumPy, Joblib
*   **Data Visualization:** Matplotlib, Seaborn, Chart.js
*   **Frontend:** HTML5, CSS3 (Custom Glassmorphism), Bootstrap 5, FontAwesome, AOS

## 🚀 Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/cardioai.git
    cd cardioai
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On macOS/Linux
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Train the Machine Learning Models:**
    Before running the app, you must train the models and generate the static charts.
    ```bash
    python train_model.py
    ```
    *This script will process the `dataset/heart.csv`, train all models, select the best one, save it to `trained_model/cardioai_model.joblib`, and generate the SHAP/EDA charts in `static/charts/`.*

5.  **Run Database Migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Create a Superuser (Optional):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```

8.  **Access the Application:**
    Open your browser and navigate to `http://127.0.0.1:8000/`.

## 📁 Project Structure

*   `accounts/`: User authentication and profile management.
*   `dashboard/`: Analytics, KPI tracking, and performance metrics.
*   `prediction/`: ML inference, SHAP evaluation, and PDF report generation.
*   `trained_model/`: Stores the active `.joblib` model and `metrics.json`.
*   `static/`: Custom CSS, JS, and generated ML charts.
*   `templates/`: HTML templates with Bootstrap 5 and Chart.js integrations.
*   `dataset/`: The Cleveland Heart Disease Dataset (`heart.csv`).
*   `train_model.py`: The core ML pipeline script.

## 🩺 Dataset Information

This project uses the **Cleveland Heart Disease Dataset**, which contains 13 clinical features to predict the presence of heart disease (binary classification). Features include Age, Sex, Chest Pain Type, Resting BP, Cholesterol, Fasting Blood Sugar, Resting ECG, Max Heart Rate, Exercise Angina, ST Depression, ST Slope, Major Vessels, and Thalassemia.

---
*Disclaimer: CardioAI is an educational and research tool. It is not intended to substitute for professional medical advice, diagnosis, or treatment.*