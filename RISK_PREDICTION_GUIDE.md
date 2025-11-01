# Risk Prediction Engine Documentation

## Overview

The **Risk Prediction Engine** is a comprehensive ML-powered system that predicts project risks in real-time using historical data, current metrics, and advanced machine learning algorithms. It provides actionable insights to project managers and teams to proactively mitigate risks.

---

## 🤖 Machine Learning Architecture

### Primary Model: Random Forest Classifier

**Why Random Forest?**
- **Ensemble Learning**: Combines predictions from 100 decision trees for robust predictions
- **Handles Non-linearity**: Captures complex relationships between features
- **Feature Importance**: Automatically identifies which factors contribute most to risk
- **Resistant to Overfitting**: Ensemble approach reduces overfitting compared to single trees
- **Handles Missing Data**: Can work with incomplete feature sets
- **No Feature Scaling Required**: Works with features of different scales (though we still scale for better performance)

**Model Configuration:**
```python
RandomForestClassifier(
    n_estimators=100,        # 100 decision trees in the forest
    max_depth=10,            # Maximum depth of each tree
    min_samples_split=5,     # Minimum samples required to split a node
    min_samples_leaf=2,      # Minimum samples in leaf nodes
    random_state=42,         # Reproducibility
    class_weight='balanced'  # Handle imbalanced risk categories
)
```

### Risk Categories

The model classifies projects into 4 risk levels:

1. **LOW (0)**: Risk Score < 20
   - Projects on track with minimal issues
   - Good test coverage, no blockers
   - Team sentiment positive

2. **MEDIUM (1)**: Risk Score 20-50
   - Some minor delays or quality issues
   - Manageable workload
   - Few blocked tasks

3. **HIGH (2)**: Risk Score 50-80
   - Significant delays or quality problems
   - High overtime, sentiment issues
   - Multiple blockers

4. **CRITICAL (3)**: Risk Score > 80
   - Project in serious trouble
   - Major delays, failed builds
   - Team burnout, dependency crises

---

## 📊 Feature Engineering

The model uses **18 carefully engineered features** across 5 dimensions:

### 1. Schedule Features (5 features)

| Feature | Description | Risk Indicator |
|---------|-------------|----------------|
| `task_completion_rate` | % of tasks marked as 'Done' | Low values = HIGH RISK |
| `overdue_task_ratio` | % of tasks > 14 days old and not done | High values = HIGH RISK |
| `critical_task_ratio` | % of 'Critical' priority tasks | High values = HIGH RISK |
| `project_progress_ratio` | Time elapsed / Total duration | Helps normalize by project phase |
| `tasks_per_remaining_day` | Remaining tasks / Remaining days | High values = SCHEDULE PRESSURE |

### 2. Quality Features (3 features)

| Feature | Description | Risk Indicator |
|---------|-------------|----------------|
| `build_failure_rate` | % of PRs with failed builds | High values = QUALITY RISK |
| `avg_test_coverage_delta` | Average change in test coverage | Negative values = DEGRADING QUALITY |
| `avg_pr_age_days` | Average age of open PRs | High values = REVIEW BOTTLENECK |

### 3. Resource Features (3 features)

| Feature | Description | Risk Indicator |
|---------|-------------|----------------|
| `overtime_ratio` | Overtime hours / Total logged hours | High values = TEAM BURNOUT |
| `workload_variance` | Variance in hours across team members | High values = IMBALANCED WORKLOAD |
| `team_size` | Number of team members | Context for other metrics |

### 4. Dependency Features (3 features)

| Feature | Description | Risk Indicator |
|---------|-------------|----------------|
| `dependency_risk_ratio` | % of dependencies 'At Risk' or 'Delayed' | High values = DEPENDENCY RISK |
| `external_dependency_ratio` | % of external dependencies | High values = EXTERNAL RISK |
| `blocked_task_ratio` | % of tasks blocked by dependencies | High values = BLOCKING ISSUES |

### 5. Team/Sentiment Features (4 features)

| Feature | Description | Risk Indicator |
|---------|-------------|----------------|
| `overall_sentiment_score` | Team sentiment score (0-1) | Low values = MORALE ISSUES |
| `negative_sentiment_ratio` | % of negative sentiment messages | High values = TEAM PROBLEMS |
| `weekly_message_count` | Messages in last 7 days | Very high/low = COMMUNICATION ISSUES |
| `blocker_signal_count` | Blocker-related messages in last 7 days | High values = ACTIVE BLOCKERS |

---

## 🔄 Auto-Training System

### When Does the Model Retrain?

The system automatically retrains when:

1. **Time-based**: Model is > 7 days old
2. **Data-based**: New historical data increases by 20%
3. **Manual**: User clicks "Train Model" button

### Training Process

1. **Data Collection**:
   - Fetches historical project performance data
   - Generates synthetic data if < 50 samples available
   - Calculates risk scores from historical outcomes

2. **Feature Preparation**:
   - Extracts 18 features for each historical project
   - Creates feature matrix (X) and labels (y)
   - Splits data: 80% training, 20% testing

3. **Model Training**:
   - Standardizes features using `StandardScaler`
   - Trains Random Forest on training set
   - Performs 5-fold cross-validation
   - Evaluates on test set

4. **Model Persistence**:
   - Saves model to `ml_models/risk_model.pkl`
   - Saves scaler to `ml_models/scaler.pkl`
   - Saves metadata to `ml_models/model_metadata.json`

### Training Data Sources

**Primary**: Historical Project Performance Table
- Real completed projects with outcomes
- Delay days, defect density, integration issues
- Compliance audit results, root causes

**Synthetic**: Generated when insufficient data
- Creates realistic training samples
- Correlates features with risk categories
- Adds noise for robustness

---

## 🎯 Risk Scoring Methodology

### Overall Risk Score (0-100)

```python
risk_score = (
    P(MEDIUM) * 35 + 
    P(HIGH) * 65 + 
    P(CRITICAL) * 100
)
```

Where P(X) is the predicted probability of risk category X.

### Dimension Scores

Each dimension is calculated independently:

**Schedule Risk:**
```python
schedule_risk = (
    overdue_task_ratio * 40 +
    tasks_per_remaining_day * 10 +
    (1 - task_completion_rate) * 50
)
```

**Quality Risk:**
```python
quality_risk = (
    build_failure_rate * 50 +
    max(0, -avg_test_coverage_delta) * 5 +
    avg_pr_age_days * 3
)
```

**Resource Risk:**
```python
resource_risk = (
    overtime_ratio * 60 +
    workload_variance * 0.5
)
```

**Dependency Risk:**
```python
dependency_risk = (
    dependency_risk_ratio * 50 +
    blocked_task_ratio * 50
)
```

**Team Risk:**
```python
team_risk = (
    (1 - overall_sentiment_score) * 60 +
    negative_sentiment_ratio * 30 +
    blocker_signal_count * 2
)
```

---

## 🧠 AI-Powered Summaries (LLM Integration)

### How It Works

When you click "Generate AI Summary", the system:

1. **Sends prediction data to Gemini 2.0 Flash**:
   - Risk scores and categories
   - Top risk factors with importance
   - Dimension breakdown
   - Probability distribution

2. **LLM analyzes the data** and generates:
   - **Executive Summary**: 2-3 sentence overview
   - **Key Concerns**: Top 3 risk factors needing attention
   - **Impact Assessment**: What could go wrong
   - **Recommendations**: 3-5 actionable mitigation strategies
   - **Monitoring Plan**: Metrics to track closely

3. **Response is displayed** in natural language

**Model Used**: `gemini-2.0-flash-exp`
- Fast inference (< 2 seconds)
- Excellent at structured analysis
- Provides actionable insights

---

## 📡 API Endpoints

### Model Management

#### `GET /api/risk/model/status`
Get current model status and metadata

**Response:**
```json
{
  "status": "ready",
  "metadata": {
    "trained_at": "2025-11-01T10:30:00",
    "n_samples": 75,
    "n_features": 18,
    "accuracy": 0.89,
    "cv_mean_score": 0.85,
    "model_type": "RandomForestClassifier"
  }
}
```

#### `POST /api/risk/model/train`
Train or retrain the model

**Request:**
```json
{
  "force_retrain": false
}
```

**Response:**
```json
{
  "status": "success",
  "accuracy": 0.89,
  "cv_score": 0.85,
  "n_samples": 75,
  "feature_importance": [...]
}
```

### Predictions

#### `POST /api/risk/predict`
Predict risk for a specific project

**Request:**
```json
{
  "project_id": "PROJ-001"
}
```

**Response:**
```json
{
  "status": "success",
  "project_id": "PROJ-001",
  "risk_category": "MEDIUM",
  "risk_score": 42.3,
  "confidence": 0.76,
  "probabilities": {
    "LOW": 0.15,
    "MEDIUM": 0.56,
    "HIGH": 0.24,
    "CRITICAL": 0.05
  },
  "top_risk_factors": [...],
  "dimension_scores": {...},
  "features": {...}
}
```

#### `GET /api/risk/predict/all`
Predict risk for all active projects

### AI Summaries

#### `POST /api/risk/summary/generate`
Generate AI-powered summary using LLM

**Request:**
```json
{
  "project_id": "PROJ-001",
  "prediction_data": { ... }
}
```

**Response:**
```json
{
  "status": "success",
  "summary": "...",
  "model_used": "gemini-2.0-flash-exp"
}
```

---

## 💡 Sentiment Analysis Integration

### How Sentiment Analysis Works

The risk prediction system integrates with the **Sentiment Analysis Service** to assess team morale:

#### Sentiment Scoring (0-1 scale)

**Positive Keywords** (score: 0.7-1.0):
- "great", "excellent", "good", "awesome", "perfect"
- "thanks", "appreciate", "helpful", "smooth"
- "resolved", "fixed", "completed", "success"

**Neutral Keywords** (score: 0.4-0.6):
- "update", "meeting", "review", "status"
- "working", "testing", "implementing"

**Negative Keywords** (score: 0.0-0.3):
- "issue", "problem", "error", "bug", "fail"
- "blocker", "delay", "delayed", "late"
- "concern", "worried", "confusing", "stuck"
- "urgent", "critical", "blocked", "waiting"

#### Sentiment Feature Extraction

```python
# Overall team sentiment
sentiment_data = sentiment_service.analyze_project_sentiment(
    db, project_id, days_back=30
)

features['overall_sentiment_score'] = sentiment_data['overall_sentiment_score']
features['negative_sentiment_ratio'] = sentiment_data['negative_ratio']
```

#### Impact on Risk Prediction

- **Low sentiment (<0.4)**: +15-20 points to team risk
- **High negative ratio (>0.3)**: Indicates active problems
- **Blocker signals**: Direct indicator of project blockers

---

## 🎨 UI Features

### Main Dashboard

1. **Model Status Banner**:
   - Shows if model is trained and ready
   - Displays accuracy and sample count
   - Quick access to train model

2. **Overall Risk Card**:
   - Large risk category display (LOW/MEDIUM/HIGH/CRITICAL)
   - Color-coded borders and icons
   - Risk score out of 100
   - Confidence percentage
   - Probability distribution for all categories

3. **AI Summary Section**:
   - One-click LLM analysis
   - Natural language insights
   - Recommendations and action items

4. **Risk Dimensions**:
   - 5 independent dimension scores
   - Visual progress bars
   - Icons for each dimension

5. **Top Risk Factors**:
   - Top 5 features contributing to risk
   - Current values and importance scores
   - Highlighted in red for visibility

6. **Model Information Panel**:
   - Architecture details
   - Performance metrics
   - Feature importance rankings
   - Training metadata

7. **All Features View**:
   - Expandable section showing all 18 features
   - Current values for selected project
   - Searchable and filterable

---

## 🚀 Getting Started

### Backend Setup

1. **Install dependencies**:
```bash
pip install scikit-learn==1.5.2 joblib==1.4.2
```

2. **Train the model** (first time):
```bash
curl -X POST http://localhost:8000/api/risk/model/train \
  -H "Content-Type: application/json" \
  -d '{"force_retrain": false}'
```

3. **Check model status**:
```bash
curl http://localhost:8000/api/risk/model/status
```

### Frontend Setup

1. Navigate to Risk Prediction page from Tools menu
2. If model not trained, click "Train Model"
3. Select a project from dropdown
4. View risk prediction and generate AI summary

---

## 📈 Best Practices

### For Accurate Predictions

1. **Keep historical data updated**: Add completed projects to `historical_project_performance` table
2. **Regular retraining**: Model auto-retrains every 7 days
3. **Accurate feature data**: Ensure Jira, GitHub, and resource data is synced
4. **Sentiment tracking**: Encourage team communication logging

### For Action Planning

1. **Focus on top risk factors**: Address highest importance features first
2. **Monitor dimension scores**: Target specific problem areas
3. **Use AI summaries**: Get context and recommendations
4. **Track trends**: Monitor risk score over time

### For Model Improvement

1. **Add more historical data**: More training samples = better accuracy
2. **Feature feedback**: Track which features correlate with actual outcomes
3. **Retrain after major changes**: When project structure changes significantly

---

## 🔬 Model Performance

### Expected Accuracy

- **With 50+ samples**: 80-90% accuracy
- **With 100+ samples**: 85-92% accuracy
- **With real historical data**: Even higher accuracy

### Cross-Validation

The model uses 5-fold cross-validation to ensure generalization:
- Data split into 5 parts
- Trained on 4, tested on 1
- Repeated 5 times
- Average score reported

### Feature Importance

Top 5 most important features (typical):
1. `task_completion_rate` (15-20%)
2. `overdue_task_ratio` (12-18%)
3. `build_failure_rate` (10-15%)
4. `overtime_ratio` (8-12%)
5. `overall_sentiment_score` (8-12%)

---

## 🐛 Troubleshooting

### Model not training?

**Issue**: "Insufficient training data"
**Solution**: 
- Add more historical projects
- System will generate synthetic data if < 50 samples
- At least 10 samples required minimum

### Low accuracy?

**Issue**: Model accuracy < 70%
**Solution**:
- Add more real historical data
- Ensure feature data quality
- Check for data imbalance in risk categories

### Features all zeros?

**Issue**: Predictions showing all 0 values
**Solution**:
- Ensure project has Jira tasks
- Sync GitHub and Jira data
- Check that resource allocation exists

### LLM summary fails?

**Issue**: "AI service not available"
**Solution**:
- Set `GEMINI_API_KEY` in environment
- Check API key is valid
- Verify network connectivity

---

## 📚 Technical References

### Libraries Used

- **scikit-learn**: ML framework
- **joblib**: Model serialization
- **numpy**: Numerical operations
- **Gemini 2.0 Flash**: LLM for summaries

### Algorithms

- **Random Forest**: Ensemble decision trees
- **StandardScaler**: Feature normalization
- **Cross-Validation**: K-fold validation (k=5)

### Data Sources

- `project_metadata`: Project info and timelines
- `jira_tasks`: Task status and priorities
- `github_activity`: PR metrics and builds
- `resource_allocation`: Time and workload
- `task_dependencies`: Blocking relationships
- `team_communication_logs`: Sentiment data
- `historical_project_performance`: Training data

---

## 🎓 Understanding the Results

### How to Read Risk Scores

- **0-20**: All clear, project on track
- **20-40**: Minor issues, watch closely
- **40-60**: Moderate risk, take action
- **60-80**: High risk, urgent intervention
- **80-100**: Critical, immediate escalation

### Confidence Levels

- **>80%**: Very confident prediction
- **60-80%**: Reasonably confident
- **40-60%**: Moderate uncertainty
- **<40%**: Low confidence, gather more data

### Acting on Predictions

**LOW Risk**: Maintain current trajectory
**MEDIUM Risk**: Monitor closely, plan mitigations
**HIGH Risk**: Active intervention required
**CRITICAL Risk**: Emergency measures, escalate

---

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review API responses for error messages
3. Check backend logs for training/prediction errors
4. Verify data quality and completeness

---

**Last Updated**: November 1, 2025
**Version**: 1.0.0
**Author**: AutoPM Risk Prediction Team
