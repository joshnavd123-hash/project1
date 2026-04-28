// ==========================================
// API Configuration
// ==========================================
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// ==========================================
// State Management
// ==========================================
let transactions = [];
let summaryData = {
    total_income: 0,
    total_expense: 0,
    balance: 0,
    total_sustainability_score: 0,
    weekly_comparison: { message: '', insight: '' },
    suggestions: []
};

// Chart Instances
let barChartInstance = null;
let pieChartInstance = null;

// ==========================================
// DOM Elements
// ==========================================
const transactionForm = document.getElementById('transaction-form');
const typeSelect = document.getElementById('type');
const categoryGroup = document.getElementById('category-group');

// Summary elements
const totalIncomeEl = document.getElementById('total-income');
const totalExpenseEl = document.getElementById('total-expense');
const balanceEl = document.getElementById('balance');
const scoreEl = document.getElementById('sustainability-score');
const scoreBadgeEl = document.getElementById('score-badge');
const scoreProgressEl = document.getElementById('score-progress');

// Lists and Containers
const transactionsListEl = document.getElementById('transactions-list');
const insightsContainerEl = document.getElementById('insights-container');
const suggestionsContainerEl = document.getElementById('suggestions-container');

// ==========================================
// Authentication & Route Protection
// ==========================================
function updateNavigationState() {
    const loggedInUser = localStorage.getItem('loggedInUser');
    const navLogin = document.getElementById('nav-login');
    const navRegister = document.getElementById('nav-register');
    const navDashboard = document.getElementById('nav-dashboard');
    const navLogout = document.getElementById('nav-logout');

    if (loggedInUser) {
        if(navLogin) navLogin.style.display = 'none';
        if(navRegister) navRegister.style.display = 'none';
        if(navDashboard) navDashboard.style.display = 'inline-block';
        if(navLogout) navLogout.style.display = 'inline-flex';
    } else {
        if(navLogin) navLogin.style.display = 'inline-block';
        if(navRegister) navRegister.style.display = 'inline-flex';
        if(navDashboard) navDashboard.style.display = 'none';
        if(navLogout) navLogout.style.display = 'none';
    }
}

function handleLogout(e) {
    e.preventDefault();
    localStorage.removeItem('loggedInUser');
    window.location.href = 'index.html';
}

function checkRouteProtection() {
    const isDashboard = window.location.pathname.includes('dashboard.html');
    const loggedInUser = localStorage.getItem('loggedInUser');
    if (isDashboard && !loggedInUser) {
        window.location.href = 'login.html';
    }
}

// ==========================================
// API Calls
// ==========================================
async function fetchSummary() {
    try {
        const response = await fetch(`${API_BASE_URL}/get-summary/`);
        summaryData = await response.json();
        updateSummaryUI();
    } catch (error) {
        console.error('Error fetching summary:', error);
    }
}

async function fetchTransactions() {
    try {
        const [expensesRes, incomeRes] = await Promise.all([
            fetch(`${API_BASE_URL}/get-expenses/`),
            fetch(`${API_BASE_URL}/get-income/`)
        ]);
        
        const expenses = await expensesRes.json();
        const income = await incomeRes.json();
        
        // Map income to match transaction structure
        const mappedIncome = income.map(i => ({
            ...i,
            type: 'income',
            description: i.source,
            category: 'Income'
        }));
        
        const mappedExpenses = expenses.map(e => ({
            ...e,
            type: 'expense'
        }));
        
        transactions = [...mappedExpenses, ...mappedIncome];
        updateTransactionsUI();
        updateCharts();
    } catch (error) {
        console.error('Error fetching transactions:', error);
    }
}

async function handleAddTransaction(e) {
    e.preventDefault();

    const type = document.getElementById('type').value;
    const amount = parseFloat(document.getElementById('amount').value);
    const date = document.getElementById('date').value;
    const description = document.getElementById('description').value.trim();
    const category = document.getElementById('category').value;

    const endpoint = type === 'expense' ? 'add-expense/' : 'add-income/';
    const payload = type === 'expense' 
        ? { amount, description, category, date }
        : { amount, source: description, date };

    try {
        const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        if (result.status === 'success') {
            transactionForm.reset();
            document.getElementById('date').valueAsDate = new Date();
            // Refresh all data
            await Promise.all([fetchSummary(), fetchTransactions()]);
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error adding transaction:', error);
        alert('Failed to connect to backend.');
    }
}

// ==========================================
// UI Updaters
// ==========================================
function updateSummaryUI() {
    totalIncomeEl.textContent = `$${summaryData.total_income.toFixed(2)}`;
    totalExpenseEl.textContent = `$${summaryData.total_expense.toFixed(2)}`;
    balanceEl.textContent = `$${summaryData.balance.toFixed(2)}`;
    scoreEl.textContent = summaryData.total_sustainability_score;
    
    // Balance color
    if(summaryData.balance < 0) balanceEl.style.color = 'var(--color-red)';
    else if(summaryData.balance > 0) balanceEl.style.color = 'var(--color-green)';
    else balanceEl.style.color = 'var(--text-primary)';

    updateSustainabilityVisuals(summaryData.total_sustainability_score);
    updateInsightsAndSuggestionsUI();
}

function updateSustainabilityVisuals(score) {
    scoreBadgeEl.className = 'badge';
    let progressPercentage = 50;

    if (score < 0) {
        scoreBadgeEl.classList.add('badge-red');
        scoreBadgeEl.textContent = 'Needs Work';
        progressPercentage = Math.max(0, 50 + score);
        scoreProgressEl.style.backgroundColor = 'var(--color-red)';
    } else if (score >= 0 && score <= 40) {
        scoreBadgeEl.classList.add('badge-yellow');
        scoreBadgeEl.textContent = 'Moderate';
        progressPercentage = 50 + (score / 2);
        scoreProgressEl.style.backgroundColor = 'var(--color-yellow)';
    } else if (score > 40 && score <= 80) {
        scoreBadgeEl.classList.add('badge-green');
        scoreBadgeEl.textContent = 'Eco Warrior';
        progressPercentage = 70 + ((score - 40) / 2);
        scoreProgressEl.style.backgroundColor = 'var(--color-green)';
    } else {
        scoreBadgeEl.classList.add('badge-gold');
        scoreBadgeEl.textContent = 'Eco Legend';
        progressPercentage = Math.min(100, 90 + ((score - 80) / 2));
        scoreProgressEl.style.backgroundColor = 'var(--color-gold)';
    }
    scoreProgressEl.style.width = `${progressPercentage}%`;
}

function updateTransactionsUI() {
    if (transactions.length === 0) {
        transactionsListEl.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 2rem 0;">No transactions added yet.</p>';
        return;
    }

    const sorted = [...transactions].sort((a, b) => new Date(b.date) - new Date(a.date));
    
    transactionsListEl.innerHTML = sorted.map(t => {
        const isExpense = t.type === 'expense';
        const sign = isExpense ? '-' : '+';
        const amountColor = isExpense ? 'var(--color-red)' : 'var(--color-green)';
        const scoreBadge = isExpense && t.sustainability_score !== 0 
            ? `<span style="font-size: 0.75rem; color: ${t.sustainability_score > 0 ? 'var(--color-green)' : 'var(--color-red)'}">(${t.sustainability_score > 0 ? '+' : ''}${t.sustainability_score} pts)</span>`
            : '';

        return `
            <div class="expense-item">
                <div class="expense-info">
                    <h4>${t.description} ${scoreBadge}</h4>
                    <p>${t.category} | ${t.date}</p>
                </div>
                <div class="expense-amount" style="color: ${amountColor}">
                    ${sign}$${t.amount.toFixed(2)}
                </div>
            </div>
        `;
    }).join('');
}

function updateInsightsAndSuggestionsUI() {
    // Insights
    let insightHtml = '';
    if (summaryData.weekly_comparison.message) {
        insightHtml += `
            <div class="insight-message">
                <span>📊</span>
                <div>
                    <p style="margin:0; font-weight: 600;">${summaryData.weekly_comparison.message}</p>
                    <p style="margin:0; font-size: 0.9rem;">${summaryData.weekly_comparison.insight}</p>
                </div>
            </div>
        `;
    }
    insightsContainerEl.innerHTML = insightHtml || '<p>Start tracking to see insights.</p>';

    // Suggestions
    let suggestionHtml = '';
    if (summaryData.suggestions.length > 0) {
        suggestionHtml = summaryData.suggestions.map(s => `
            <div class="suggestion-message">
                <span>🌱</span>
                <p style="margin:0;">${s}</p>
            </div>
        `).join('');
    }
    suggestionsContainerEl.innerHTML = suggestionHtml || '<p>Keep up the good work!</p>';
}

// ==========================================
// Chart.js Integration
// ==========================================
function initCharts() {
    const barCtx = document.getElementById('barChart');
    const pieCtx = document.getElementById('pieChart');
    if (!barCtx || !pieCtx) return;

    barChartInstance = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Daily Expenses ($)',
                data: [0, 0, 0, 0, 0, 0, 0],
                backgroundColor: '#66bb6a',
                borderColor: '#2e7d32',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { title: { display: true, text: 'Recent Expenses by Day' } },
            scales: { y: { beginAtZero: true } }
        }
    });

    pieChartInstance = new Chart(pieCtx, {
        type: 'doughnut',
        data: {
            labels: ['Food', 'Transport', 'Shopping', 'Eco Product', 'Bills'],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: ['#ffa726', '#42a5f5', '#ef5350', '#66bb6a', '#90caf9'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'Expense Categories' },
                legend: { position: 'bottom' }
            }
        }
    });
}

function updateCharts() {
    if (!barChartInstance || !pieChartInstance) return;

    const expenses = transactions.filter(t => t.type === 'expense');

    // Pie Chart
    const categoryTotals = { 'Food': 0, 'Transport': 0, 'Shopping': 0, 'Eco Product': 0, 'Bills': 0 };
    expenses.forEach(t => {
        if(categoryTotals[t.category] !== undefined) categoryTotals[t.category] += t.amount;
    });

    pieChartInstance.data.datasets[0].data = [
        categoryTotals['Food'], categoryTotals['Transport'], categoryTotals['Shopping'],
        categoryTotals['Eco Product'], categoryTotals['Bills']
    ];
    pieChartInstance.update();

    // Bar Chart
    const dailyTotals = [0, 0, 0, 0, 0, 0, 0];
    expenses.forEach(t => {
        const dateObj = new Date(t.date);
        let day = dateObj.getDay(); // 0-Sun, 1-Mon
        day = day === 0 ? 6 : day - 1; // Mon-0, Sun-6
        dailyTotals[day] += t.amount;
    });

    barChartInstance.data.datasets[0].data = dailyTotals;
    barChartInstance.update();
}

// ==========================================
// Initialization
// ==========================================
document.addEventListener('DOMContentLoaded', async () => {
    // Auth Initialization
    checkRouteProtection();
    updateNavigationState();

    const navLogout = document.getElementById('nav-logout');
    if(navLogout) {
        navLogout.addEventListener('click', handleLogout);
    }

    // Register Form Handling (Redirects to Login on success)
    const registerForm = document.getElementById('register-form');
    if(registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('reg-email').value;
            const pass = document.getElementById('reg-password').value;
            const conf = document.getElementById('reg-confirm-password').value;
            const errorEl = document.getElementById('register-error');

            if (pass !== conf) {
                errorEl.textContent = "Passwords do not match.";
                errorEl.style.display = 'block';
                return;
            }

            try {
                // Using login API to simulate a "check" for registration
                const response = await fetch(`${API_BASE_URL}/login/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password: pass })
                });
                const result = await response.json();
                if (result.status === 'success') {
                    // Redirect to LOGIN instead of Dashboard
                    alert('Registration successful! Please login.');
                    window.location.href = 'login.html';
                } else {
                    errorEl.textContent = result.message;
                    errorEl.style.display = 'block';
                }
            } catch (err) {
                errorEl.textContent = "Connection error.";
                errorEl.style.display = 'block';
            }
        });
    }

    // Login Form Handling
    const loginForm = document.getElementById('login-form');
    if(loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const pass = document.getElementById('login-password').value;
            const errorEl = document.getElementById('login-error');

            try {
                const response = await fetch(`${API_BASE_URL}/login/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password: pass })
                });
                const result = await response.json();
                if (result.status === 'success') {
                    localStorage.setItem('loggedInUser', JSON.stringify(result.user));
                    window.location.href = 'dashboard.html';
                } else {
                    errorEl.textContent = result.message;
                    errorEl.style.display = 'block';
                }
            } catch (err) {
                errorEl.textContent = "Connection error.";
                errorEl.style.display = 'block';
            }
        });
    }

    if(typeSelect) {
        typeSelect.addEventListener('change', (e) => {
            categoryGroup.style.display = e.target.value === 'income' ? 'none' : 'block';
        });
    }

    if(transactionForm) {
        document.getElementById('date').valueAsDate = new Date();
        transactionForm.addEventListener('submit', handleAddTransaction);
    }

    initCharts();
    
    // Fetch initial data from backend
    if (window.location.pathname.includes('dashboard.html')) {
        await Promise.all([fetchSummary(), fetchTransactions()]);
    }
});
