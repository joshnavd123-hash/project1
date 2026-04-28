from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum

def calculate_sustainability_score(description):
    description = description.lower()
    score = 0
    
    # Positive impacts
    if 'walking' in description:
        score += 15
    elif any(word in description for word in ['bus', 'train']):
        score += 10
    elif any(word in description for word in ['eco', 'reusable']):
        score += 8
        
    # Negative impacts
    if any(word in description for word in ['fuel', 'petrol']):
        score -= 8
    if any(word in description for word in ['pizza', 'fast food']):
        score -= 5
    if any(word in description for word in ['shopping', 'clothes']):
        score -= 5
        
    return score

def detect_category(description, default_category):
    description = description.lower()
    
    if any(word in description for word in ['bus', 'train']):
        return 'Transport'
    if any(word in description for word in ['pizza', 'food']):
        return 'Food'
    if any(word in description for word in ['shopping', 'clothes']):
        return 'Shopping'
    if any(word in description for word in ['eco', 'bamboo']):
        return 'Eco Product'
    if any(word in description for word in ['electricity', 'water', 'bill']):
        return 'Bills'
        
    return default_category

def get_weekly_insights(current_expenses, previous_expenses):
    if previous_expenses == 0:
        if current_expenses > 0:
            return "Initial spending started this week.", "No previous data to compare."
        else:
            return "No spending recorded.", "Start tracking to see insights."
            
    diff = current_expenses - previous_expenses
    percentage = (abs(diff) / previous_expenses) * 100
    
    if diff > 0:
        msg = f"Spending increased by {percentage:.1f}% compared to last week."
        insight = "Try to cut down on non-essential categories."
    elif diff < 0:
        msg = f"Spending decreased by {percentage:.1f}% compared to last week!"
        insight = "Great job! You are managing your budget effectively."
    else:
        msg = "Spending is the same as last week."
        insight = "Consistency is key, but look for more ways to save."
        
    return msg, insight

def get_suggestions(category_totals):
    suggestions = []
    
    transport_total = category_totals.get('Transport', 0)
    shopping_total = category_totals.get('Shopping', 0)
    
    if transport_total > 50: # Arbitrary threshold for suggestion
        suggestions.append("High transport spending detected. Consider using public transport or carpooling more often.")
    
    if shopping_total > 100:
        suggestions.append("High shopping expenses. Consider buying second-hand or focusing on sustainable alternatives.")
        
    if not suggestions:
        suggestions.append("Your spending looks balanced. Keep it up!")
        
    return suggestions
