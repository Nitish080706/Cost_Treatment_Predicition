

const API_BASE_URL = 'http://localhost:5000/api';

const token = localStorage.getItem('token');
const userInfo = JSON.parse(localStorage.getItem('user') || '{}');

const mainModeChatBtn = document.getElementById('main-mode-chat');
const mainModePredictBtn = document.getElementById('main-mode-predict');
const chatSection = document.getElementById('chat-section');
const predictionSection = document.getElementById('prediction-section');

const predictionForm = document.getElementById('prediction-form');
const predictBtn = document.getElementById('predict-btn');
const predictionResult = document.getElementById('prediction-result');
const predictedCost = document.getElementById('predicted-cost');
const modelPredictions = document.getElementById('model-predictions');

const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const modeTextBtn = document.getElementById('mode-text');
const modeOptionsBtn = document.getElementById('mode-options');
const textInputMode = document.getElementById('text-input-mode');
const optionsMode = document.getElementById('options-mode');
const optionBtns = document.querySelectorAll('.option-btn');

let mainMode = 'prediction'; // 'chat' or 'prediction'

mainModeChatBtn.addEventListener('click', () => {
    mainMode = 'chat';
    mainModeChatBtn.classList.add('active');
    mainModePredictBtn.classList.remove('active');
    chatSection.classList.remove('hidden');
    predictionSection.classList.add('hidden');
});

mainModePredictBtn.addEventListener('click', () => {
    mainMode = 'prediction';
    mainModePredictBtn.classList.add('active');
    mainModeChatBtn.classList.remove('active');
    predictionSection.classList.remove('hidden');
    chatSection.classList.add('hidden');
});

let currentMode = 'text';

modeTextBtn.addEventListener('click', () => {
    currentMode = 'text';
    modeTextBtn.classList.add('active');
    modeOptionsBtn.classList.remove('active');
    textInputMode.classList.remove('hidden');
    optionsMode.classList.add('hidden');
});

modeOptionsBtn.addEventListener('click', () => {
    currentMode = 'options';
    modeOptionsBtn.classList.add('active');
    modeTextBtn.classList.remove('active');
    optionsMode.classList.remove('hidden');
    textInputMode.classList.add('hidden');
});

sendBtn.addEventListener('click', () => sendMessage());
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    addMessageToChat(message, 'user');
    chatInput.value = '';

    sendBtn.disabled = true;
    chatInput.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                type: 'text'
            })
        });

        const data = await response.json();

        if (data.success) {
            addMessageToChat(data.response, 'ai');
        } else {
            addMessageToChat('Hmm, something went wrong. ' + (data.error || 'Could you try that again?'), 'ai');
        }
    } catch (error) {
        console.error('Chat error:', error);
        addMessageToChat("I'm having trouble connecting right now. Can you check if the backend server is running?", 'ai');
    } finally {
        sendBtn.disabled = false;
        chatInput.disabled = false;
        chatInput.focus();
    }
}

optionBtns.forEach(btn => {
    btn.addEventListener('click', async () => {
        const option = btn.getAttribute('data-option');
        const optionText = btn.textContent.trim();

        addMessageToChat(optionText, 'user');

        optionBtns.forEach(b => b.disabled = true);

        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: option,
                    type: 'option'
                })
            });

            const data = await response.json();

            if (data.success) {
                addMessageToChat(data.response, 'ai');
            } else {
                addMessageToChat('Oops, something didn\'t work. ' + (data.error || 'Mind trying again?'), 'ai');
            }
        } catch (error) {
            console.error('Chat error:', error);
            addMessageToChat("Having connection issues. Is the server up and running?", 'ai');
        } finally {
            optionBtns.forEach(b => b.disabled = false);
        }
    });
});

function addMessageToChat(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = `message-avatar ${sender}`;
    avatar.textContent = sender === 'ai' ? '🤖' : '👤';

    const content = document.createElement('div');
    content.className = `message-content ${sender}`;
    content.textContent = message;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

predictionForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    predictBtn.classList.add('loading');
    predictBtn.disabled = true;

    try {

        const formData = {
            age: parseInt(document.getElementById('age').value),
            gender: document.getElementById('gender').value,
            bmi: parseFloat(document.getElementById('bmi').value),
            smoker: document.getElementById('smoker').checked ? 'Yes' : 'No',
            diabetes: document.getElementById('diabetes').checked ? 1 : 0,
            hypertension: document.getElementById('hypertension').checked ? 1 : 0,
            heart_disease: document.getElementById('heart_disease').checked ? 1 : 0,
            asthma: document.getElementById('asthma').checked ? 1 : 0,
            physical_activity_level: document.getElementById('physical_activity_level').value,
            daily_steps: parseInt(document.getElementById('daily_steps').value),
            sleep_hours: parseFloat(document.getElementById('sleep_hours').value),
            stress_level: parseInt(document.getElementById('stress_level').value),
            doctor_visits_per_year: parseInt(document.getElementById('doctor_visits_per_year').value),
            hospital_admissions: parseInt(document.getElementById('hospital_admissions').value),
            medication_count: parseInt(document.getElementById('medication_count').value),
            insurance_type: document.getElementById('insurance_type').value,
            insurance_coverage_pct: parseInt(document.getElementById('insurance_coverage_pct').value),
            city_type: document.getElementById('city_type').value,
            previous_year_cost: parseFloat(document.getElementById('previous_year_cost').value)
        };

        if (userInfo.email) {
            formData.user_email = userInfo.email;
        }

        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {

            displayPrediction(data);
        } else {
            showError(data.error || 'Hmm, prediction didn\'t work. Let\'s try again!');
        }

    } catch (error) {
        console.error('Error making prediction:', error);
        showError('Can\'t reach the server right now. Is it running?');
    } finally {

        predictBtn.classList.remove('loading');
        predictBtn.disabled = false;
    }
});

function displayPrediction(data) {

    predictionResult.classList.remove('hidden');

    const costInr = data.prediction_inr;
    predictedCost.textContent = `₹${Math.round(costInr).toLocaleString('en-IN')}`;

    const modelsHTML = Object.entries(data.individual_predictions)
        .map(([model, value]) => `
            <div class="model-prediction">
                <span class="model-name">${model}</span>
                <span class="model-value">₹${Math.round(value).toLocaleString('en-IN')}</span>
            </div>
        `).join('');

    modelPredictions.innerHTML = modelsHTML;

    if (data.cost_explanation) {
        const explanation = data.cost_explanation;
        const explanationHTML = `
            <div class="cost-explanation">
                <h3 class="explanation-title">💡 Why This Cost?</h3>
                <p class="explanation-summary">${explanation.summary}</p>
                
                <div class="impact-factors">
                    <h4>Key Cost Factors:</h4>
                    <table class="factors-table">
                        <thead>
                            <tr>
                                <th>Factor</th>
                                <th>Impact</th>
                                <th>Est. Contribution</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${explanation.detailed_factors.map(([factor, impact, amount]) => `
                                <tr class="impact-${impact.toLowerCase().replace(' ', '-')}">
                                    <td>${factor}</td>
                                    <td><span class="impact-badge impact-${impact.toLowerCase().replace(' ', '-')}">${impact}</span></td>
                                    <td class="amount">${amount}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                
                <div class="insurance-breakdown">
                    <h4>Insurance Coverage Breakdown:</h4>
                    <div class="breakdown-grid">
                        <div class="breakdown-item">
                            <span class="label">Total Cost</span>
                            <span class="value">${explanation.total_cost_inr}</span>
                        </div>
                        <div class="breakdown-item">
                            <span class="label">Insurance Covers</span>
                            <span class="value success">${explanation.insurance_coverage.covered_amount}</span>
                        </div>
                        <div class="breakdown-item highlight">
                            <span class="label">Your Out-of-Pocket</span>
                            <span class="value">${explanation.insurance_coverage.out_of_pocket}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        const existingExplanation = document.querySelector('.cost-explanation');
        if (existingExplanation) {
            existingExplanation.remove();
        }
        modelPredictions.insertAdjacentHTML('afterend', explanationHTML);
    }

    predictionResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;

        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }

        element.textContent = '$' + current.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }, 16);
}

function showError(message) {

    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-notification';
    errorDiv.innerHTML = `
        <div class="error-content">
            <span class="error-icon">⚠️</span>
            <span class="error-message">${message}</span>
        </div>
    `;

    document.body.appendChild(errorDiv);

    if (!document.querySelector('#error-notification-styles')) {
        const style = document.createElement('style');
        style.id = 'error-notification-styles';
        style.textContent = `
            .error-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(239, 68, 68, 0.95);
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(239, 68, 68, 0.3);
                z-index: 1000;
                animation: slideInRight 0.3s ease;
            }
            
            .error-content {
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }
            
            .error-icon {
                font-size: 1.5rem;
            }
            
            .error-message {
                font-weight: 500;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
    }

    setTimeout(() => {
        errorDiv.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => errorDiv.remove(), 300);
    }, 5000);
}

async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/statistics`);
        const stats = await response.json();

        console.log('Dataset statistics:', stats);

    } catch (error) {
        console.log('Could not load statistics:', error.message);
    }
}

function setupFormValidation() {
    const inputs = document.querySelectorAll('input[type="number"]');

    inputs.forEach(input => {
        input.addEventListener('input', () => {
            const value = parseFloat(input.value);
            const min = parseFloat(input.min);
            const max = parseFloat(input.max);

            if (value < min) {
                input.value = min;
            } else if (value > max) {
                input.value = max;
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadStatistics();
    setupFormValidation();
    initializeAuth();

    console.log('All ready! Make sure the Flask backend is running on http://localhost:5000');
});

function initializeAuth() {
    const loginLink = document.getElementById('loginLink');
    const signupLink = document.getElementById('signupLink');
    const userInfoDiv = document.getElementById('userInfo');
    const userWelcome = document.getElementById('userWelcome');
    const logoutBtn = document.getElementById('logoutBtnHeader');

    if (token && userInfo.email) {
        loginLink.style.display = 'none';
        signupLink.style.display = 'none';
        userInfoDiv.style.display = 'flex';
        userWelcome.textContent = `Welcome, ${userInfo.name || userInfo.email}!`;

        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.reload();
        });
    } else {
        loginLink.style.display = 'inline-block';
        signupLink.style.display = 'inline-block';
        userInfoDiv.style.display = 'none';
    }
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
