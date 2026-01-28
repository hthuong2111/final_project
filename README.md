# E-Shop Clothing 2008: User Engagement Analysis & Prediction

A comprehensive data analysis and machine learning project exploring user browsing behavior patterns in an e-commerce clothing store and predicting session engagement levels.

## 📊 Project Overview

This project analyzes clickstream data from a European e-commerce clothing website collected between April and August 2008. The analysis focuses on understanding factors that influence user engagement and building predictive models to identify high-engagement sessions.

**Key Objectives:**
- Analyze browsing patterns and user behavior across 165,474 click events
- Test hypotheses about factors influencing engagement (price, location, photography style, etc.)
- Build machine learning models to predict session engagement levels
- Provide actionable insights for e-commerce optimization

## 📁 Project Structure

```
final_project/
├── data/
│   ├── raw/                                    # Original dataset
│   │   ├── e-shop_clothing_2008.csv           # Raw clickstream data (165,474 rows)
│   │   └── e-shop_clothing_2008_data_description.txt
│   └── clean/                                  # Processed data
│       └── e-shop_clothing_2008_processed.csv # Cleaned dataset with decoded values
├── notebooks/
│   ├── cleaning_analysis_data.ipynb           # Data preprocessing & EDA
│   └── prediction.ipynb                        # ML modeling & predictions
├── figures/                                    # Generated visualizations
└── slides/                                     # Presentation materials
```

## 📈 Dataset Description

**Source:** E-commerce clothing store clickstream data (2008)  
**Size:** 165,474 click events across 24,026 unique sessions  
**Time Period:** April - August 2008  
**Geographic Coverage:** 47 countries (primarily Poland, Czech Republic, Lithuania)

### Variables

| Variable | Description | Type |
|----------|-------------|------|
| `year`, `month`, `day` | Timestamp information | Temporal |
| `order` | Click sequence within a session (1-195) | Numerical |
| `country` | User's country (47 categories) | Categorical |
| `session_id` | Unique session identifier (24,026 sessions) | ID |
| `main_category` | Product category: trousers, skirts, blouses, sale | Categorical |
| `clothing_model` | Product code (217 unique products) | Categorical |
| `colour` | Product color (14 categories) | Categorical |
| `location` | Photo position on page (6 positions) | Categorical |
| `model_photography` | Photo style: en face or profile | Categorical |
| `price_usd` | Product price in USD | Numerical |
| `price_vs_category_avg` | Above/below category average | Categorical |
| `page` | Page number within website (1-5) | Numerical |

## 🔍 Key Findings from Exploratory Data Analysis

### 1. **Product Price Influences Engagement** ✅
- Sessions with **lower-priced products** generate deeper click sequences (7.03 vs 6.75 clicks)
- Statistical significance confirmed (t-test, p < 0.05)
- **Insight:** Price-sensitive users browse more extensively, likely comparing options

### 2. **Product Presentation Affects Engagement** ✅
- **Top positions** outperform bottom positions:
  - Top in the middle: 195 max clicks
  - Top left: 193 max clicks
  - Bottom positions: 180-190 max clicks
- **Insight:** Prominent placement drives higher engagement

### 3. **Model Photography Influences Early Clicks** ✅
- **En face photography** attracts earlier clicks (mean order: 9.32 vs 11.22 for profile)
- Highly significant difference (t-test, p < 0.001)
- **Insight:** Frontal-facing images capture attention faster

### 4. **Category Drives Browsing Depth** ✅
- **Sale items** generate deepest sessions (8.81 clicks average)
- Blouses (6.97) and trousers (6.67) show moderate engagement
- Skirts have lowest engagement (5.57 clicks)
- ANOVA confirms significant differences (p < 0.001)
- **Insight:** Sale categories encourage comparison shopping

### 5. **Seasonality Affects Browsing Depth** ✅
- **August** shows highest engagement (7.35 clicks)
- April-July relatively stable (6.6-6.9 clicks)
- ANOVA confirms seasonal variation (p < 0.05)
- **Insight:** Summer period drives increased exploration

### 6. **Display Location Impacts Orders** ✅
- Top-left and top-in-the-middle positions receive most orders (34,532 and 33,383 respectively)
- Bottom-right position receives fewest orders (20,743)
- **Insight:** F-pattern reading behavior confirmed

## 🤖 Machine Learning Models

### Problem Statement
**Binary Classification:** Predict whether a session will be highly engaged (≥6 clicks)

### Dataset Preparation
- **Session-level aggregation:** 24,026 sessions
- **Features:** 29 features (9 categorical + 20 numerical)
  - Categorical: country, category preferences, color, location, photography style
  - Numerical: price statistics, diversity metrics, click patterns
- **Label:** High engagement = 1 (≥6 clicks), Low engagement = 0 (<6 clicks)
- **Class distribution:** 39.2% positive (high engagement)
- **Split:** 80% train (19,220) / 20% test (4,806), stratified

### Model Performance Comparison

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | F1 Improvement |
|-------|----------|-----------|--------|----------|---------|----------------|
| **Gradient Boosting (Tuned)** | **0.9952** | **1.0000** | **0.9878** | **0.9939** | **1.0000** | **+8.85%** |
| Random Forest (Tuned) | 0.9896 | 0.9989 | 0.9745 | 0.9866 | 0.9996 | +8.06% |
| KNN (Tuned) | 0.9401 | 0.9655 | 0.8783 | 0.9199 | 0.9859 | +0.75% |
| KNN (Baseline) | 0.9345 | 0.9505 | 0.8783 | 0.9130 | 0.9747 | baseline |

### Best Model: Gradient Boosting (Tuned)
- **Hyperparameters:** n_estimators=200, learning_rate=0.2, max_depth=3
- **Cross-validation:** 5-fold stratified CV
- **Performance:** Near-perfect classification with 99.52% accuracy and 99.39% F1-score
- **Top Features:**
  1. `unique_products` (92.7% importance)
  2. `en_face_clicks` (4.7%)
  3. `top_position_clicks` (0.6%)
  4. `trouser_clicks` (0.6%)
  5. `above_avg_price_clicks` (0.4%)

### Model Selection Rationale
- **Baseline (KNN):** Simple, non-parametric starting point
- **Random Forest:** Handles non-linear relationships, robust to outliers
- **Gradient Boosting:** Sequential error correction, best performance
- **GridSearchCV:** Systematic hyperparameter tuning with 3-fold CV

## 🛠️ Technologies Used

- **Python 3.x**
- **Data Analysis:** pandas, numpy
- **Visualization:** matplotlib, seaborn
- **Statistical Testing:** scipy.stats
- **Machine Learning:** scikit-learn
  - Models: KNN, Random Forest, Gradient Boosting
  - Preprocessing: StandardScaler, OneHotEncoder
  - Validation: StratifiedKFold, GridSearchCV