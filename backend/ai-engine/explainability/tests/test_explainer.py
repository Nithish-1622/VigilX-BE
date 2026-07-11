import pytest
from explainability.explainer import RiskExplainer
from explainability.exceptions import InvalidProfileError

@pytest.fixture
def explainer():
    return RiskExplainer()

def test_explain_risk_score_success(explainer):
    profile = {
        "total_cases": 2,
        "known_associates_count": 2,
        "risk_score": 45
    }
    
    explanations = explainer.explain_risk_score(profile)
    
    assert len(explanations) == 3
    assert "Base risk score evaluated to 45" in explanations[0]
    assert "heavily elevated by +35" in explanations[1]
    assert "elevated by +10 due to connections with 2" in explanations[2]

def test_explain_risk_score_max(explainer):
    profile = {
        "total_cases": 10,
        "known_associates_count": 10,
        "risk_score": 100
    }
    
    explanations = explainer.explain_risk_score(profile)
    assert "WARNING: The risk score has reached the maximum threshold (100)" in explanations[-1]

def test_explain_risk_score_invalid_profile(explainer):
    with pytest.raises(InvalidProfileError):
        explainer.explain_risk_score({"total_cases": 1})
