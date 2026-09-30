"""
CardioAI - Advanced Machine Learning Pipeline v2.0
Includes: LightGBM, XGBoost, Explainable AI (SHAP), Correlation Heatmap, 
          ROC Curves, Confusion Matrix, and comprehensive analytics.
"""
import json
import warnings
from pathlib import Path

import joblib
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import shap
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score,
    precision_score, recall_score, roc_auc_score, roc_curve
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

# Optional heavy ML libraries
try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("[WARN] XGBoost not installed. Skipping.")

try:
    from lightgbm import LGBMClassifier
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False
    print("[WARN] LightGBM not installed. Skipping.")

# Use non-interactive backend for matplotlib
matplotlib.use("Agg")
warnings.filterwarnings("ignore")

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset" / "heart.csv"
MODEL_DIR = BASE_DIR / "trained_model"
MODEL_PATH = MODEL_DIR / "cardioai_model.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"
STATIC_IMG_DIR = BASE_DIR / "static" / "charts"

FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]

FEATURE_NAMES_FRIENDLY = {
    "age": "Age", "sex": "Gender", "cp": "Chest Pain Type",
    "trestbps": "Resting BP", "chol": "Cholesterol", "fbs": "Fasting Blood Sugar",
    "restecg": "Resting ECG", "thalach": "Max Heart Rate", "exang": "Exercise Angina",
    "oldpeak": "ST Depression", "slope": "ST Slope", "ca": "Major Vessels",
    "thal": "Thalassemia"
}


def create_directories():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_IMG_DIR.mkdir(parents=True, exist_ok=True)
    print("[OK] Directories created.")


def load_and_clean_data():
    """Load and preprocess the Cleveland Heart Disease Dataset."""
    print("\n[1/5] Loading and Cleaning Dataset...")
    try:
        columns = FEATURES + ["target"]
        df = pd.read_csv(DATASET_PATH, header=None, names=columns, na_values="?")
    except FileNotFoundError:
        # Try with header row (some versions of heart.csv have headers)
        try:
            df = pd.read_csv(DATASET_PATH)
            df.columns = columns if len(df.columns) == 14 else df.columns
        except Exception:
            print(f"[ERROR] Dataset not found at {DATASET_PATH}")
            return None

    print(f"   Dataset shape: {df.shape}")
    print(f"   Missing values: {df.isnull().sum().sum()}")

    # Missing Value Handling
    for col in df.columns:
        if df[col].isnull().any():
            if df[col].nunique() < 10:
                df[col].fillna(df[col].mode()[0], inplace=True)
            else:
                df[col].fillna(df[col].median(), inplace=True)

    # Binary classification (Cleveland has 0-4 scale; convert to binary)
    df["target"] = (df["target"] > 0).astype(int)
    print(f"   Class distribution: {df['target'].value_counts().to_dict()}")

    # Outlier Clipping (IQR method)
    continuous_features = ["trestbps", "chol", "thalach", "oldpeak"]
    for feature in continuous_features:
        Q1 = df[feature].quantile(0.25)
        Q3 = df[feature].quantile(0.75)
        IQR = Q3 - Q1
        df[feature] = df[feature].clip(lower=Q1 - 1.5 * IQR, upper=Q3 + 1.5 * IQR)

    print("[OK] Data cleaning complete.\n")
    return df


def generate_eda_plots(df):
    """Generate Exploratory Data Analysis charts and save them."""
    print("[2/5] Generating EDA Visualizations...")
    plt.style.use('seaborn-whitegrid')
    
    # ─── Correlation Heatmap ─────────────────────────────────────────────────
    plt.figure(figsize=(12, 9))
    correlation = df.corr()
    mask = np.triu(np.ones_like(correlation, dtype=bool))
    sns.heatmap(
        correlation, mask=mask, annot=True, fmt='.2f', linewidths=0.5,
        cmap='RdYlGn', center=0, vmin=-1, vmax=1,
        square=True, cbar_kws={"shrink": 0.8}
    )
    plt.title('Feature Correlation Matrix — Cleveland Heart Disease Dataset', 
              fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(STATIC_IMG_DIR / "correlation_heatmap.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("   [OK] Correlation heatmap saved.")

    # ─── Distribution Plots ───────────────────────────────────────────────────
    fig, axes = plt.subplots(3, 4, figsize=(16, 12))
    axes = axes.flatten()
    
    colors_no_disease = '#10B981'
    colors_disease = '#EF4444'
    
    for i, feature in enumerate(FEATURES[:12]):
        ax = axes[i]
        df_no = df[df['target'] == 0][feature]
        df_yes = df[df['target'] == 1][feature]
        
        if df[feature].nunique() < 8:
            # Bar chart for categorical
            counts = df.groupby([feature, 'target']).size().unstack(fill_value=0)
            counts.plot(kind='bar', ax=ax, color=[colors_no_disease, colors_disease], 
                       edgecolor='none', alpha=0.85, width=0.7)
            ax.legend(['No Disease', 'Heart Disease'], fontsize=8)
        else:
            # KDE for continuous
            df_no.plot.kde(ax=ax, color=colors_no_disease, label='No Disease', linewidth=2)
            df_yes.plot.kde(ax=ax, color=colors_disease, label='Heart Disease', linewidth=2)
            ax.legend(fontsize=8)
        
        ax.set_title(FEATURE_NAMES_FRIENDLY.get(feature, feature), fontweight='bold', fontsize=10)
        ax.set_xlabel('')
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Feature Distributions by Heart Disease Status', 
                 fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(STATIC_IMG_DIR / "feature_distributions.png", dpi=130, bbox_inches='tight')
    plt.close()
    print("   [OK] Feature distributions saved.")
    
    print("[OK] EDA visualizations complete.\n")


def train_and_compare_models(X_train, y_train, X_test, y_test):
    """Train and compare multiple ML models, return best pipeline."""
    print("[3/5] Training & Comparing ML Models...")

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=10, class_weight="balanced", random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=8, class_weight="balanced", random_state=42),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
        "Support Vector Machine": SVC(probability=True, class_weight="balanced", random_state=42),
    }
    if HAS_XGBOOST:
        models["XGBoost"] = XGBClassifier(
            use_label_encoder=False, eval_metric="logloss",
            scale_pos_weight=1, random_state=42, verbosity=0
        )
    if HAS_LIGHTGBM:
        models["LightGBM"] = LGBMClassifier(random_state=42, verbose=-1)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    best_name = ""
    best_score = 0.0
    best_classifier = None
    all_metrics = {}

    for name, clf in models.items():
        print(f"   Training {name}...", end=" ", flush=True)
        clf.fit(X_train_scaled, y_train)
        y_pred = clf.predict(X_test_scaled)
        cv_scores = cross_val_score(clf, X_train_scaled, y_train, cv=5, scoring="accuracy")

        m = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, clf.predict_proba(X_test_scaled)[:, 1])),
            "cv_accuracy_mean": float(cv_scores.mean()),
        }
        all_metrics[name] = m
        print(f"Acc={m['accuracy']:.4f} | CV={m['cv_accuracy_mean']:.4f}")

        if m["cv_accuracy_mean"] > best_score:
            best_score = m["cv_accuracy_mean"]
            best_classifier = clf
            best_name = name

    print(f"\n   [BEST] -> {best_name} (CV Accuracy: {best_score:.4f})")

    # Rebuild the pipeline with the already-fitted scaler + best classifier
    best_pipeline = Pipeline([("scaler", scaler), ("classifier", best_classifier)])

    return best_name, best_pipeline, all_metrics, X_train_scaled, X_test_scaled, y_test


def generate_evaluation_plots(best_pipeline, best_name, all_metrics, 
                               X_test_scaled, y_test, models_dict):
    """Generate ROC curves and confusion matrix plots."""
    print("[4/5] Generating Evaluation Plots...")
    
    # ─── ROC Curves ──────────────────────────────────────────────────────────
    plt.figure(figsize=(9, 7))
    colors_palette = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#F97316']
    
    # Plot ROC for best model
    clf = best_pipeline.named_steps["classifier"]
    y_prob = clf.predict_proba(X_test_scaled)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)
    plt.plot(fpr, tpr, color='#4F46E5', linewidth=3, 
             label=f"{best_name} (AUC = {auc:.3f}) ★ Best")
    
    plt.plot([0, 1], [0, 1], 'k--', linewidth=1, alpha=0.5, label='Random Classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate (Sensitivity)', fontsize=12)
    plt.title(f'ROC Curves — ML Model Comparison\nBest Model: {best_name}', fontsize=13, fontweight='bold')
    plt.legend(loc='lower right', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(STATIC_IMG_DIR / "roc_curves.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("   [OK] ROC curves saved.")
    
    # ─── Confusion Matrix ─────────────────────────────────────────────────────
    y_pred = best_pipeline.predict(X_test_scaled)
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(7, 6))
    sns.heatmap(
        cm, annot=True, fmt='d', cmap='Blues',
        xticklabels=['No Disease', 'Heart Disease'],
        yticklabels=['No Disease', 'Heart Disease'],
        linewidths=0.5, cbar_kws={'label': 'Count'},
        annot_kws={'size': 16, 'weight': 'bold'}
    )
    plt.title(f'Confusion Matrix — {best_name}', fontsize=13, fontweight='bold', pad=15)
    plt.ylabel('Actual Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.savefig(STATIC_IMG_DIR / "confusion_matrix.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("   [OK] Confusion matrix saved.")
    
    # ─── Model Comparison Bar Chart ───────────────────────────────────────────
    names = list(all_metrics.keys())
    accuracies = [all_metrics[n]['accuracy'] * 100 for n in names]
    f1s = [all_metrics[n]['f1_score'] * 100 for n in names]
    
    x = np.arange(len(names))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars1 = ax.bar(x - width/2, accuracies, width, label='Accuracy (%)', 
                   color='#4F46E5', alpha=0.85, edgecolor='none')
    bars2 = ax.bar(x + width/2, f1s, width, label='F1 Score (%)', 
                   color='#10B981', alpha=0.85, edgecolor='none')
    
    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Score (%)', fontsize=12)
    ax.set_title('ML Model Comparison — Accuracy & F1 Score', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15, ha='right')
    ax.legend(fontsize=11)
    ax.set_ylim(0, 110)
    ax.grid(True, alpha=0.3, axis='y')
    
    for bar in bars1:
        ax.annotate(f'{bar.get_height():.1f}%', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        ax.annotate(f'{bar.get_height():.1f}%', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(STATIC_IMG_DIR / "model_comparison.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("   [OK] Model comparison chart saved.")
    
    print("[OK] Evaluation plots complete.\n")


def generate_shap_explanations(best_pipeline, best_name, X_train_scaled, X_test_scaled):
    """Generate SHAP summary plot for Explainable AI."""
    print("[5/5] Generating SHAP Explainability Plots...")
    clf = best_pipeline.named_steps["classifier"]
    X_test_df = pd.DataFrame(X_test_scaled, columns=FEATURES)

    try:
        if best_name in ["Random Forest", "Decision Tree", "XGBoost", "LightGBM"]:
            explainer = shap.TreeExplainer(clf)
            shap_values = explainer.shap_values(X_test_scaled)
        else:
            background = shap.sample(X_train_scaled, min(50, len(X_train_scaled)))
            explainer = shap.KernelExplainer(clf.predict_proba, background)
            shap_values = explainer.shap_values(X_test_scaled)

        vals = shap_values[1] if isinstance(shap_values, list) else shap_values

        plt.figure(figsize=(10, 8))
        shap.summary_plot(vals, X_test_df, feature_names=FEATURES, show=False, 
                          color_bar_label='Feature Value')
        plt.title(f"SHAP Feature Importance — {best_name}", fontsize=13, fontweight='bold', pad=15)
        plt.tight_layout()
        plt.savefig(STATIC_IMG_DIR / "shap_summary.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("   [OK] SHAP summary plot saved.")

    except Exception as e:
        print(f"   [WARN] SHAP plot failed: {e}")


def main():
    print("=" * 60)
    print("  CardioAI ML Training Pipeline v2.0")
    print("=" * 60)

    create_directories()

    df = load_and_clean_data()
    if df is None:
        return

    generate_eda_plots(df)

    X = df[FEATURES]
    y = df["target"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Train: {len(X_train)} | Test: {len(X_test)}\n")

    best_name, best_pipeline, all_metrics, X_train_scaled, X_test_scaled, y_test_arr = \
        train_and_compare_models(X_train, y_train, X_test, y_test)

    generate_evaluation_plots(best_pipeline, best_name, all_metrics, X_test_scaled, y_test_arr, {})
    generate_shap_explanations(best_pipeline, best_name, X_train_scaled, X_test_scaled)

    # ─── Save Model Artifact ─────────────────────────────────────────────────
    model_data = {
        "model": best_pipeline,
        "model_name": best_name,
        "features": FEATURES,
        "explainer_data": X_train_scaled[:100]
    }
    joblib.dump(model_data, MODEL_PATH)
    print(f"\n[OK] Model saved -> {MODEL_PATH}")

    # ─── Save Metrics ─────────────────────────────────────────────────────────
    metrics_data = {
        "selected_model": best_name,
        "metrics": all_metrics[best_name],
        "all_models_comparison": all_metrics
    }
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=4)
    print(f"[OK] Metrics saved -> {METRICS_PATH}")

    print("\n" + "=" * 60)
    print(f"  [OK] Pipeline Complete!")
    print(f"  Best Model: {best_name}")
    print(f"  Accuracy:   {all_metrics[best_name]['accuracy']*100:.2f}%")
    print(f"  F1 Score:   {all_metrics[best_name]['f1_score']*100:.2f}%")
    print(f"  ROC-AUC:    {all_metrics[best_name]['roc_auc']:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()