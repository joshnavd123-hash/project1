import json
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Transaction, Income
from .logic import calculate_sustainability_score, detect_category, get_weekly_insights, get_suggestions
from django.db.models import Sum

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

def home_page(request):
    return render(request, 'index.html')

def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard_page')
    return render(request, 'login.html')

def register_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard_page')
    return render(request, 'register.html')

@login_required
def dashboard_page(request):
    return render(request, 'dashboard.html')

def root_view(request):
    return JsonResponse({"message": "EcoBudget Backend is running successfully"})

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('email')
            email = data.get('email')
            password = data.get('password')
            name = data.get('name', '')
            
            if not username or not password:
                return JsonResponse({'status': 'error', 'message': 'Email and password are required'}, status=400)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'User already exists'}, status=400)
            
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = name
            user.save()
            return JsonResponse({'status': 'success', 'message': 'Registration successful'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('email')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                display_name = user.first_name if user.first_name else user.username.split('@')[0]
                return JsonResponse({
                    'status': 'success',
                    'message': 'Login successful',
                    'user': {'name': display_name, 'email': user.email}
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

from django.contrib.auth import logout as auth_logout

def logout_view(request):
    print(f"Logging out user: {request.user}")
    auth_logout(request)
    print(f"User after logout: {request.user}")
    return redirect('home')

@login_required
@csrf_exempt
def add_expense(request):
    if request.method == 'POST':
        try:
            if not request.body:
                return JsonResponse({'status': 'error', 'message': 'Empty request body'}, status=400)
            data = json.loads(request.body)
            if 'amount' not in data or 'description' not in data:
                return JsonResponse({'status': 'error', 'message': 'Amount and description are required'}, status=400)
            try:
                amount = float(data.get('amount'))
            except (ValueError, TypeError):
                return JsonResponse({'status': 'error', 'message': 'Invalid amount format'}, status=400)
                
            description = data.get('description', '')
            frontend_category = data.get('category', 'Miscellaneous')
            date = data.get('date', timezone.now().date())
            
            category = detect_category(description, frontend_category)
            score = calculate_sustainability_score(description)
            
            transaction = Transaction.objects.create(
                user=request.user,
                amount=amount,
                category=category,
                date=date,
                description=description,
                sustainability_score=score
            )
            return JsonResponse({
                'status': 'success',
                'message': 'Expense added successfully',
                'data': {
                    'id': transaction.id,
                    'category': transaction.category,
                    'sustainability_score': transaction.sustainability_score
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

@login_required
@csrf_exempt
def add_income(request):
    if request.method == 'POST':
        try:
            if not request.body:
                return JsonResponse({'status': 'error', 'message': 'Empty request body'}, status=400)
            data = json.loads(request.body)
            if 'amount' not in data or 'source' not in data:
                return JsonResponse({'status': 'error', 'message': 'Amount and source are required'}, status=400)
            try:
                amount = float(data.get('amount'))
            except (ValueError, TypeError):
                return JsonResponse({'status': 'error', 'message': 'Invalid amount format'}, status=400)
                
            source = data.get('source', '')
            date = data.get('date', timezone.now().date())
            
            income = Income.objects.create(
                user=request.user,
                amount=amount,
                source=source,
                date=date
            )
            return JsonResponse({'status': 'success', 'message': 'Income added successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

@login_required
def get_expenses(request):
    try:
        expenses = Transaction.objects.filter(user=request.user).order_by('-date')
        data = list(expenses.values())
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def get_income(request):
    try:
        income = Income.objects.filter(user=request.user).order_by('-date')
        data = list(income.values())
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def get_summary(request):
    try:
        total_income = Income.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0
        total_expense = Transaction.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0
        balance = total_income - total_expense
        total_score = Transaction.objects.filter(user=request.user).aggregate(total=Sum('sustainability_score'))['total'] or 0
        
        today = timezone.now().date()
        last_7_days_start = today - timedelta(days=6)
        prev_7_days_start = today - timedelta(days=13)
        
        current_expenses = Transaction.objects.filter(user=request.user, date__range=[last_7_days_start, today]).aggregate(total=Sum('amount'))['total'] or 0
        previous_expenses = Transaction.objects.filter(user=request.user, date__range=[prev_7_days_start, last_7_days_start - timedelta(days=1)]).aggregate(total=Sum('amount'))['total'] or 0
        
        insight_msg, insight_text = get_weekly_insights(current_expenses, previous_expenses)
        category_totals = {
            item['category']: item['total'] 
            for item in Transaction.objects.filter(user=request.user).values('category').annotate(total=Sum('amount'))
        }
        suggestions = get_suggestions(category_totals)
        
        return JsonResponse({
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'total_sustainability_score': total_score,
            'weekly_comparison': {
                'message': insight_msg,
                'insight': insight_text
            },
            'suggestions': suggestions
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
