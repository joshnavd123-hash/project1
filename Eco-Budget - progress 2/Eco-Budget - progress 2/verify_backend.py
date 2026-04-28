import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api/'

def test_backend():
    print("Testing EcoBudget Backend...")
    
    # 1. Add Income
    income_data = {
        "amount": 5000,
        "source": "Salary",
        "date": "2026-04-28"
    }
    r = requests.post(f"{BASE_URL}add-income/", json=income_data)
    print(f"Add Income: {r.status_code}, {r.json()}")

    # 2. Add Expense (Transport - Positive)
    expense_data = {
        "amount": 20.5,
        "description": "Bus ticket to office",
        "category": "Travel",
        "date": "2026-04-28"
    }
    r = requests.post(f"{BASE_URL}add-expense/", json=expense_data)
    print(f"Add Expense (Bus): {r.status_code}, {r.json()}")

    # 3. Add Expense (Food - Negative)
    expense_data = {
        "amount": 15.0,
        "description": "Pizza dinner",
        "category": "Eating Out",
        "date": "2026-04-28"
    }
    r = requests.post(f"{BASE_URL}add-expense/", json=expense_data)
    print(f"Add Expense (Pizza): {r.status_code}, {r.json()}")

    # 4. Get Summary
    r = requests.get(f"{BASE_URL}get-summary/")
    print(f"Get Summary: {r.status_code}, {r.json()}")

    # 5. Get Expenses
    r = requests.get(f"{BASE_URL}get-expenses/")
    print(f"Get Expenses: {len(r.json())} items found")

if __name__ == "__main__":
    test_backend()
