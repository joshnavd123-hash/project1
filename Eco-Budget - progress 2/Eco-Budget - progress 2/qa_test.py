import requests
import json

BASE_URL = 'http://127.0.0.1:8000/'
API_URL = f'{BASE_URL}api/'

def run_tests():
    print("Starting QA Test Suite for EcoBudget...")
    session = requests.Session()
    
    # 1. Test Registration
    print("\n[1] Testing Registration...")
    reg_data = {"email": "qa_user_final@example.com", "password": "password123"}
    r = requests.post(f"{API_URL}register/", json=reg_data)
    print(f"Register (New): {r.status_code}, {r.json()}")
    
    r = requests.post(f"{API_URL}register/", json=reg_data)
    print(f"Register (Duplicate): {r.status_code}, {r.json()}")

    # 2. Test Security (Unauthorized Access)
    print("\n[2] Testing Security (Unauthorized Access)...")
    r = requests.get(f"{API_URL}get-summary/")
    print(f"Get Summary (Unauth): {r.status_code} (Expected 302 Redirect to Login)")

    # 3. Test Login
    print("\n[3] Testing Login...")
    login_data = {"email": "qa_user_final@example.com", "password": "password123"}
    r = session.post(f"{API_URL}login/", json=login_data)
    print(f"Login (Correct): {r.status_code}, {r.json()}")

    r = requests.post(f"{API_URL}login/", json={"email": "wrong", "password": "wrong"})
    print(f"Login (Incorrect): {r.status_code}, {r.json()}")

    # 4. Test Functional - Add Income
    print("\n[4] Testing Add Income...")
    income_data = {"amount": 5000, "source": "Salary", "date": "2026-04-28"}
    r = session.post(f"{API_URL}add-income/", json=income_data)
    print(f"Add Income: {r.status_code}, {r.json()}")

    # 5. Test Functional - Add Expense (Check Sustainability Score)
    print("\n[5] Testing Add Expense & Scoring...")
    expense_data = {"amount": 50, "description": "Bus ticket to park", "category": "Travel", "date": "2026-04-28"}
    r = session.post(f"{API_URL}add-expense/", json=expense_data)
    res_data = r.json()
    print(f"Add Expense (Bus): {r.status_code}, Score: {res_data.get('data', {}).get('sustainability_score')} (Expected +10)")

    expense_data_negative = {"amount": 100, "description": "Fuel for car", "category": "Travel", "date": "2026-04-28"}
    r = session.post(f"{API_URL}add-expense/", json=expense_data_negative)
    res_data_neg = r.json()
    print(f"Add Expense (Fuel): {r.status_code}, Score: {res_data_neg.get('data', {}).get('sustainability_score')} (Expected -8)")

    # 6. Test Summary Calculations
    print("\n[6] Testing Summary Calculations...")
    r = session.get(f"{API_URL}get-summary/")
    summary = r.json()
    print(f"Summary: Income={summary['total_income']}, Expense={summary['total_expense']}, Balance={summary['balance']}, Score={summary['total_sustainability_score']}")
    
    # Verification
    if summary['balance'] == 4850 and summary['total_sustainability_score'] == 2:
        print("PASS: Summary calculation verified!")
    else:
        print("FAIL: Summary calculation discrepancy!")

    # 7. Test User Isolation
    print("\n[7] Testing User Isolation...")
    # Create second user
    requests.post(f"{API_URL}register/", json={"email": "user isolation@example.com", "password": "password"})
    session2 = requests.Session()
    session2.post(f"{API_URL}login/", json={"email": "user isolation@example.com", "password": "password"})
    
    r2 = session2.get(f"{API_URL}get-summary/")
    summary2 = r2.json()
    print(f"User 2 Summary (Empty): {summary2['total_income']} (Expected 0)")
    if summary2['total_income'] == 0:
        print("PASS: User isolation verified!")
    else:
        print("FAIL: User isolation failed!")

    print("\nDONE: QA Test Suite Completed.")

if __name__ == "__main__":
    run_tests()
