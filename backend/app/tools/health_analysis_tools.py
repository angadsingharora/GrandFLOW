# backend/app/tools/health_analysis_tools.py

from crewai_tools import tool
from typing import Dict, List

@tool("Calculate Diet Quality Score")
def calculate_diet_quality_score(
    calories: int,
    macros: dict,
    meals_count: int,
    vitamins: list,
    medical_conditions: list
) -> int:
    """
    Calculate diet quality score (0-100) based on nutritional intake.
    
    Args:
        calories: Total calories consumed
        macros: Dictionary with protein, carbs, fats (in grams)
        meals_count: Number of meals eaten
        vitamins: List of vitamins/supplements taken
        medical_conditions: Patient's medical conditions
        
    Returns:
        Score from 0-100
    """
    score = 50  # Base score
    
    # Calorie assessment (for seniors, 1600-2200 is typical)
    if 1600 <= calories <= 2200:
        score += 20
    elif 1400 <= calories < 1600 or 2200 < calories <= 2400:
        score += 10
    elif calories < 1200:
        score -= 20  # Concerning low intake
    
    # Protein assessment (seniors need 1.0-1.2g per kg body weight, assume 70kg = 70-84g)
    protein = macros.get('protein', 0)
    if 60 <= protein <= 100:
        score += 15
    elif 40 <= protein < 60:
        score += 5
    else:
        score -= 10
    
    # Meal frequency
    if meals_count >= 3:
        score += 10
    elif meals_count == 2:
        score += 5
    
    # Vitamins/supplements
    if len(vitamins) > 0:
        score += 5
    
    # Medical condition considerations
    if "diabetes_type_2" in medical_conditions:
        carbs = macros.get('carbs', 0)
        if carbs < 150:  # Lower carb is better for diabetics
            score += 10
        elif carbs > 250:
            score -= 10
    
    if "hypertension" in medical_conditions:
        # Would check sodium, but not available in macros
        # Assume sodium is controlled if score is already high
        pass
    
    # Cap score between 0-100
    return max(0, min(100, score))

@tool("Calculate Exercise Quality Score")
def calculate_exercise_quality_score(
    steps: int,
    exercise_completed: bool,
    age: int
) -> int:
    """
    Calculate exercise quality score based on activity level.
    
    Args:
        steps: Number of steps taken
        exercise_completed: Whether dedicated exercise was done
        age: Patient age
        
    Returns:
        Score from 0-100
    """
    score = 0
    
    # Step-based scoring (adjusted for seniors)
    if steps >= 7000:
        score += 50
    elif steps >= 5000:
        score += 40
    elif steps >= 3000:
        score += 30
    elif steps >= 1000:
        score += 20
    else:
        score += 10
    
    # Dedicated exercise bonus
    if exercise_completed:
        score += 30
    
    # Age adjustment (lower expectations for older adults)
    if age >= 80:
        score += 10  # Bonus for any activity at advanced age
    elif age >= 75:
        score += 5
    
    return min(100, score)

@tool("Calculate Medication Adherence Rate")
def calculate_medication_adherence_rate(
    medicines_prescribed: list,
    medicines_taken: list
) -> float:
    """
    Calculate medication adherence percentage.
    
    Args:
        medicines_prescribed: List of prescribed medications
        medicines_taken: List of medications actually taken
        
    Returns:
        Adherence rate as percentage (0-100)
    """
    if len(medicines_prescribed) == 0:
        return 100.0
    
    # Match medications taken to prescribed
    prescribed_names = [med['name'].lower() for med in medicines_prescribed]
    taken_names = [med['name'].lower() for med in medicines_taken]
    
    matches = sum(1 for name in prescribed_names if name in taken_names)
    
    adherence_rate = (matches / len(medicines_prescribed)) * 100
    
    return round(adherence_rate, 2)

@tool("Generate Health Recommendations")
def generate_health_recommendations(
    diet_score: int,
    exercise_score: int,
    medication_adherence: float,
    medical_conditions: list
) -> List[str]:
    """
    Generate personalized health recommendations based on scores.
    
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # Diet recommendations
    if diet_score < 60:
        recommendations.append(
            "Consider eating more balanced meals with lean protein and vegetables."
        )
    if diet_score < 40:
        recommendations.append(
            "Your calorie intake seems low. Try adding healthy snacks between meals."
        )
    
    # Exercise recommendations
    if exercise_score < 50:
        recommendations.append(
            "Try to walk for 10-15 minutes after breakfast or lunch."
        )
    if exercise_score < 30:
        recommendations.append(
            "Even light stretching or chair exercises can help. Start small!"
        )
    
    # Medication reminders
    if medication_adherence < 80:
        recommendations.append(
            "Remember to take all prescribed medications. Set phone reminders if needed."
        )
    
    # Condition-specific
    if "diabetes_type_2" in medical_conditions and diet_score < 70:
        recommendations.append(
            "Focus on low-glycemic foods to help manage blood sugar levels."
        )
    
    if "hypertension" in medical_conditions:
        recommendations.append(
            "Continue monitoring blood pressure and limit sodium intake."
        )
    
    # Default positive message if doing well
    if diet_score >= 80 and exercise_score >= 70 and medication_adherence >= 90:
        recommendations.append(
            "Excellent work! You're taking great care of your health. Keep it up!"
        )
    
    return recommendations

@tool("Calculate Symptom Quality Score")
def calculate_symptom_quality_score(symptoms_reported: list, severity_scores: dict) -> int:
    """
    Calculate symptom quality score (higher = fewer/milder symptoms).
    
    Args:
        symptoms_reported: List of symptoms
        severity_scores: Dictionary of symptom: severity (1-10)
        
    Returns:
        Score from 0-100 (100 = no symptoms)
    """
    if len(symptoms_reported) == 0:
        return 100
    
    # Start at 100, subtract based on symptoms
    score = 100
    
    for symptom in symptoms_reported:
        severity = severity_scores.get(symptom, 5)
        
        # Deduct points based on severity
        score -= severity * 5  # Max 50 points per severe symptom
    
    return max(0, score)
