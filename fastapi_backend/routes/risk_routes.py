"""
Risk Prediction API Routes
Endpoints for ML-based risk prediction and model management
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional, List
from pydantic import BaseModel
from services.risk_prediction_service import get_risk_service
from services.chat_service import get_chat_service
import os

router = APIRouter(prefix="/api/risk", tags=["Risk Prediction"])


# === REQUEST/RESPONSE MODELS ===

class PredictionRequest(BaseModel):
    project_id: str


class TrainModelRequest(BaseModel):
    force_retrain: Optional[bool] = False


class RiskSummaryRequest(BaseModel):
    project_id: str
    prediction_data: dict


# === ENDPOINTS ===

@router.get("/model/status")
def get_model_status():
    """
    Get ML model status and metadata
    
    Returns information about the trained model including:
    - Training date
    - Accuracy metrics
    - Feature importance
    - Model type
    """
    try:
        risk_service = get_risk_service()
        status = risk_service.get_model_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model status: {str(e)}")


@router.post("/model/train")
def train_model(
    request: TrainModelRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Train or retrain the risk prediction model
    
    Training Process:
    1. Extract features from historical projects
    2. Generate synthetic data if needed
    3. Train Random Forest classifier
    4. Evaluate with cross-validation
    5. Save model and metadata
    
    This can take a few seconds depending on data volume.
    """
    try:
        risk_service = get_risk_service()
        
        # Train model
        result = risk_service.train_model(db, force_retrain=request.force_retrain)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")


@router.post("/predict")
def predict_project_risk(
    request: PredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Predict risk for a specific project
    
    Returns:
    - Risk category (LOW, MEDIUM, HIGH, CRITICAL)
    - Risk score (0-100)
    - Probability distribution
    - Top risk factors
    - Dimension scores (schedule, quality, resource, dependency, team)
    """
    try:
        risk_service = get_risk_service()
        
        # Check if model is trained
        status = risk_service.get_model_status()
        if status.get('status') == 'not_trained':
            raise HTTPException(
                status_code=400,
                detail="Model not trained. Please train the model first using /api/risk/model/train"
            )
        
        # Predict risk
        prediction = risk_service.predict_risk(db, request.project_id)
        
        if prediction.get('status') == 'error':
            raise HTTPException(status_code=400, detail=prediction.get('message'))
        
        return prediction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting risk: {str(e)}")


@router.get("/predict/all")
def predict_all_projects_risk(db: Session = Depends(get_db)):
    """
    Predict risk for all active projects
    
    Returns a list of risk predictions for all projects
    """
    try:
        from models.database_models import ProjectMetadata
        
        risk_service = get_risk_service()
        
        # Check if model is trained
        status = risk_service.get_model_status()
        if status.get('status') == 'not_trained':
            raise HTTPException(
                status_code=400,
                detail="Model not trained. Please train the model first."
            )
        
        # Get all active projects
        projects = db.query(ProjectMetadata).filter(
            ProjectMetadata.status.in_(['Planning', 'In Progress'])
        ).all()
        
        predictions = []
        for project in projects:
            try:
                prediction = risk_service.predict_risk(db, project.project_id)
                if prediction.get('status') == 'success':
                    predictions.append({
                        'project_id': project.project_id,
                        'project_name': project.project_name,
                        'risk_category': prediction.get('risk_category'),
                        'risk_score': prediction.get('risk_score'),
                        'confidence': prediction.get('confidence')
                    })
            except Exception as e:
                print(f"Error predicting for {project.project_id}: {e}")
                continue
        
        return {
            'status': 'success',
            'predictions': predictions,
            'total_projects': len(predictions)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting risks: {str(e)}")


@router.post("/summary/generate")
def generate_risk_summary(
    request: RiskSummaryRequest,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered summary of risk prediction using LLM
    
    Uses Gemini to create a human-readable summary of:
    - Overall risk assessment
    - Key risk factors
    - Recommendations
    - Action items
    """
    try:
        chat_service = get_chat_service()
        if not chat_service.genai_client:
            raise HTTPException(
                status_code=400,
                detail="AI service not available. Please configure GEMINI_API_KEY."
            )
        
        prediction_data = request.prediction_data
        
        # Create detailed prompt for summary
        prompt = f"""Analyze this project risk prediction and provide a comprehensive summary:

**Risk Assessment:**
- Risk Category: {prediction_data.get('risk_category')}
- Risk Score: {prediction_data.get('risk_score'):.1f}/100
- Confidence: {prediction_data.get('confidence', 0) * 100:.1f}%

**Probability Distribution:**
- LOW: {prediction_data.get('probabilities', {}).get('LOW', 0) * 100:.1f}%
- MEDIUM: {prediction_data.get('probabilities', {}).get('MEDIUM', 0) * 100:.1f}%
- HIGH: {prediction_data.get('probabilities', {}).get('HIGH', 0) * 100:.1f}%
- CRITICAL: {prediction_data.get('probabilities', {}).get('CRITICAL', 0) * 100:.1f}%

**Top Risk Factors:**
{chr(10).join([f"- {rf['feature']}: {rf['value']:.2f} (importance: {rf['importance']:.2%})" for rf in prediction_data.get('top_risk_factors', [])[:5]])}

**Dimension Scores:**
- Schedule Risk: {prediction_data.get('dimension_scores', {}).get('schedule_risk', 0):.1f}/100
- Quality Risk: {prediction_data.get('dimension_scores', {}).get('quality_risk', 0):.1f}/100
- Resource Risk: {prediction_data.get('dimension_scores', {}).get('resource_risk', 0):.1f}/100
- Dependency Risk: {prediction_data.get('dimension_scores', {}).get('dependency_risk', 0):.1f}/100
- Team Risk: {prediction_data.get('dimension_scores', {}).get('team_risk', 0):.1f}/100

Please provide:
1. **Executive Summary**: 2-3 sentences summarizing the overall risk situation
2. **Key Concerns**: Top 3 risk factors that need immediate attention
3. **Impact Assessment**: What could happen if these risks materialize
4. **Recommendations**: 3-5 specific actionable recommendations to mitigate risks
5. **Monitoring**: What metrics should be tracked closely

Keep the tone professional but accessible. Use bullet points for clarity."""

        response = chat_service.genai_client.models.generate_content(
            model=chat_service.model,
            contents=prompt
        )
        
        summary = response.text.strip()
        
        return {
            'status': 'success',
            'summary': summary,
            'model_used': chat_service.model,
            'risk_category': prediction_data.get('risk_category'),
            'risk_score': prediction_data.get('risk_score')
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@router.post("/model/auto-train")
def check_and_auto_train(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Check if auto-training is needed and trigger if necessary
    
    Auto-training is triggered when:
    - Model is more than 7 days old
    - New historical data is available (20% increase)
    """
    try:
        risk_service = get_risk_service()
        
        needs_training = risk_service.check_auto_training_needed(db)
        
        if needs_training:
            # Train in background
            background_tasks.add_task(risk_service.train_model, db, False)
            return {
                'status': 'training_scheduled',
                'message': 'Auto-training has been scheduled in the background'
            }
        else:
            return {
                'status': 'no_training_needed',
                'message': 'Model is up to date'
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking auto-training: {str(e)}")


@router.get("/health")
def risk_service_health():
    """Check if risk prediction service is healthy"""
    try:
        risk_service = get_risk_service()
        status = risk_service.get_model_status()
        
        # Check if scikit-learn is installed
        try:
            import sklearn
            sklearn_version = sklearn.__version__
            sklearn_available = True
        except ImportError:
            sklearn_version = None
            sklearn_available = False
        
        return {
            'status': 'healthy',
            'model_status': status.get('status'),
            'sklearn_available': sklearn_available,
            'sklearn_version': sklearn_version,
            'model_trained': status.get('status') == 'ready'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


@router.get("/features/explain")
def explain_features():
    """
    Get detailed explanation of all features used in the model
    
    Returns documentation about each feature and how it's calculated
    """
    features_explanation = {
        "schedule_features": {
            "task_completion_rate": "Percentage of tasks marked as 'Done' vs total tasks",
            "overdue_task_ratio": "Percentage of tasks overdue (> 14 days old and not done)",
            "critical_task_ratio": "Percentage of tasks marked as 'Critical' priority",
            "project_progress_ratio": "Time elapsed vs total project duration",
            "tasks_per_remaining_day": "Remaining tasks divided by remaining days"
        },
        "quality_features": {
            "build_failure_rate": "Percentage of PRs with failed builds",
            "avg_test_coverage_delta": "Average change in test coverage across PRs",
            "avg_pr_age_days": "Average age of open PRs in days"
        },
        "resource_features": {
            "overtime_ratio": "Overtime hours vs total logged hours",
            "workload_variance": "Statistical variance in workload across team members",
            "team_size": "Number of team members allocated to project"
        },
        "dependency_features": {
            "dependency_risk_ratio": "Percentage of dependencies 'At Risk' or 'Delayed'",
            "external_dependency_ratio": "Percentage of external dependencies",
            "blocked_task_ratio": "Percentage of tasks blocked by dependencies"
        },
        "team_features": {
            "overall_sentiment_score": "Team sentiment score from communication analysis (0-1)",
            "negative_sentiment_ratio": "Percentage of negative sentiment messages",
            "weekly_message_count": "Number of team messages in last 7 days",
            "blocker_signal_count": "Number of blocker-related messages in last 7 days"
        }
    }
    
    return {
        'status': 'success',
        'features': features_explanation,
        'total_features': sum(len(cat) for cat in features_explanation.values()),
        'ml_model': 'Random Forest Classifier',
        'risk_categories': ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    }
