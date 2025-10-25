# backend/app/tools/cognitive_test_tools.py

from crewai_tools import tool
from typing import Dict, List, Tuple

@tool("Administer TICS Test")
def administer_tics_test() -> dict:
    """
    Provide TICS test questions and scoring instructions.
    This tool returns the test structure for the agent to follow.
    
    Returns:
        Dictionary with test sections and questions
    """
    return {
        "test_name": "Telephone Interview for Cognitive Status (TICS)",
        "total_points": 41,
        "sections": {
            "orientation": {
                "points": 5,
                "questions": [
                    "What is today's date? (day, month, year)",
                    "What day of the week is it?",
                    "What season are we in?"
                ],
                "scoring": "1 point for each correct answer"
            },
            "registration": {
                "points": 3,
                "instruction": "I'm going to say 3 words. Please repeat them: APPLE, TABLE, PENNY",
                "scoring": "1 point for each word repeated immediately"
            },
            "attention_calculation": {
                "points": 5,
                "instruction": "Starting at 100, subtract 7. What is 100 minus 7?",
                "followup": "Continue subtracting 7 from each answer (93, 86, 79, 72, 65)",
                "scoring": "1 point for each correct subtraction"
            },
            "recall": {
                "points": 3,
                "instruction": "Do you remember those 3 words I asked you to repeat earlier?",
                "answers": ["apple", "table", "penny"],
                "scoring": "1 point for each word recalled"
            },
            "naming": {
                "points": 2,
                "questions": [
                    "What do you call the thing you use to tell time? (watch/clock)",
                    "What do you call the thing you write with? (pen/pencil)"
                ],
                "scoring": "1 point for each correct answer"
            },
            "repetition": {
                "points": 1,
                "instruction": "Please repeat this phrase: NO IFS, ANDS, OR BUTS",
                "scoring": "1 point if repeated correctly"
            },
            "comprehension": {
                "points": 3,
                "instruction": "Listen carefully to these instructions:",
                "commands": [
                    "With your right hand, touch your left ear",
                    "Then touch your nose",
                    "Then touch your right shoulder"
                ],
                "scoring": "1 point for each step completed correctly"
            }
        },
        "interpretation": {
            "35-41": "Normal cognitive function",
            "31-34": "Mild cognitive impairment",
            "21-30": "Moderate cognitive impairment",
            "0-20": "Severe cognitive impairment"
        }
    }

@tool("Convert TICS to MMSE")
def convert_tics_to_mmse(tics_score: int) -> int:
    """
    Convert TICS score to MMSE equivalent.
    
    TICS total: 41 points
    MMSE total: 30 points
    
    Approximate conversion: MMSE ≈ TICS - 2
    
    Args:
        tics_score: TICS test score (0-41)
        
    Returns:
        MMSE equivalent score (0-30)
    """
    # Simple conversion formula
    mmse_score = tics_score - 2
    
    # Ensure within valid range
    return max(0, min(30, mmse_score))

@tool("Calculate Cognitive Quality Score")
def calculate_cognitive_quality_score(tics_score: int) -> int:
    """
    Calculate cognitive quality score normalized to 0-100.
    
    Args:
        tics_score: TICS test score (0-41)
        
    Returns:
        Normalized score (0-100)
    """
    # Normalize to 0-100 scale
    normalized = (tics_score / 41) * 100
    
    return round(normalized)

@tool("Determine Cognitive Risk Level")
def determine_cognitive_risk_level(tics_score: int) -> str:
    """
    Determine cognitive risk level based on TICS score.
    
    Args:
        tics_score: TICS test score (0-41)
        
    Returns:
        Risk level string
    """
    if tics_score >= 35:
        return "normal"
    elif tics_score >= 31:
        return "mild_impairment"
    elif tics_score >= 21:
        return "moderate_impairment"
    else:
        return "severe_impairment"

@tool("Generate Cognitive Recommendations")
def generate_cognitive_recommendations(
    tics_score: int,
    risk_level: str,
    baseline_score: int = None
) -> List[str]:
    """
    Generate recommendations based on cognitive test results.
    
    Args:
        tics_score: Current TICS score
        risk_level: Risk level classification
        baseline_score: Previous baseline score for comparison
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    if risk_level == "normal":
        recommendations.append(
            "Cognitive function is within normal range. Continue with regular activities."
        )
        recommendations.append(
            "Keep your mind active with reading, puzzles, or social activities."
        )
    
    elif risk_level == "mild_impairment":
        recommendations.append(
            "Mild cognitive changes detected. Consider discussing with your doctor."
        )
        recommendations.append(
            "Engage in cognitively stimulating activities like puzzles or learning new skills."
        )
        recommendations.append(
            "Ensure adequate sleep, exercise, and social engagement."
        )
    
    elif risk_level in ["moderate_impairment", "severe_impairment"]:
        recommendations.append(
            "Significant cognitive concerns detected. Please consult with your healthcare provider."
        )
        recommendations.append(
            "A comprehensive neurological evaluation is recommended."
        )
        recommendations.append(
            "Consider memory support strategies and caregiver assistance."
        )
    
    # Trend analysis
    if baseline_score:
        decline = baseline_score - tics_score
        if decline >= 3:
            recommendations.append(
                f"Score has declined by {decline} points since baseline. Medical evaluation recommended."
            )
        elif decline >= 1:
            recommendations.append(
                "Slight decline noted. Continue monitoring and maintain healthy lifestyle."
            )
    
    return recommendations

@tool("Score TICS Section")
def score_tics_section(section_name: str, responses: dict) -> int:
    """
    Score a specific section of the TICS test.
    
    Args:
        section_name: Name of section (e.g., "orientation", "recall")
        responses: Dictionary of responses
        
    Returns:
        Points earned for this section
    """
    scoring_rules = {
        "orientation": lambda r: sum([
            1 if r.get("date_correct") else 0,
            1 if r.get("day_correct") else 0,
            1 if r.get("season_correct") else 0
        ]),
        "registration": lambda r: len([w for w in r.get("words_repeated", []) if w]),
        "attention_calculation": lambda r: len([a for a in r.get("subtractions", []) if a]),
        "recall": lambda r: len([w for w in r.get("words_recalled", []) if w]),
        "naming": lambda r: sum([
            1 if r.get("time_device") in ["watch", "clock"] else 0,
            1 if r.get("writing_device") in ["pen", "pencil"] else 0
        ]),
        "repetition": lambda r: 1 if r.get("phrase_repeated") else 0,
        "comprehension": lambda r: len([c for c in r.get("commands_completed", []) if c])
    }
    
    scorer = scoring_rules.get(section_name)
    if scorer:
        return scorer(responses)
    return 0
