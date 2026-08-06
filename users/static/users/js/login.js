const container = document.querySelector('.container');
const registerBtn = document.querySelector('.register-btn');
const loginBtn = document.querySelector('.login-btn');

registerBtn.addEventListener('click', ()=>{
    container.classList.add('active');
})

loginBtn.addEventListener('click', ()=>{
    container.classList.remove('active');
})

// ============================================================
// Password show/hide toggle
// ============================================================
document.querySelectorAll('.toggle-password').forEach(function(icon) {
    icon.addEventListener('click', function() {
        const targetId = this.getAttribute('data-target');
        const input = document.getElementById(targetId);
if (input.type === 'password') {
            input.type = 'text';
            this.classList.remove('fa-eye');
            this.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            this.classList.remove('fa-eye-slash');
            this.classList.add('fa-eye');
        }
    });
});

// ============================================================
// System Loading Overlay
// ============================================================
window.addEventListener('load', function() {
    const loader = document.getElementById('systemLoader');
    if (loader) {
        setTimeout(function() { loader.classList.add('hide'); }, 400);
    }
});

// ============================================================
// Multi-Step Registration
// ============================================================
let currentStep = 1;
const totalSteps = 3;

const stepPanels = document.querySelectorAll('.step-panel');
const steps = document.querySelectorAll('.steps-indicator .step');
const stepLines = document.querySelectorAll('.steps-indicator .step-line');
const progressFill = document.getElementById('progressFill');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const submitBtn = document.getElementById('submitBtn');

function updateProgress() {
    // Update step indicator states
    steps.forEach(function(step, i) {
        step.classList.toggle('active', i < currentStep);
    });
    stepLines.forEach(function(line, i) {
        line.classList.toggle('active', i < currentStep - 1);
    });

    // Update progress bar
    if (progressFill) {
        const pct = ((currentStep - 1) / (totalSteps - 1)) * 100;
        progressFill.style.width = pct + '%';
    }

    // Show/hide nav buttons
    prevBtn.style.display = currentStep === 1 ? 'none' : 'block';
    nextBtn.style.display = currentStep === totalSteps ? 'none' : 'block';
    submitBtn.style.display = currentStep === totalSteps ? 'block' : 'none';
}

function goToStep(step) {
    // Animate current out
    const currentPanel = document.querySelector('.step-panel.active');
    if (step > currentStep) {
        currentPanel.classList.add('exit-left');
        currentPanel.classList.remove('active');
    } else {
        currentPanel.classList.add('exit-right');
        currentPanel.classList.remove('active');
    }

    setTimeout(function() {
        currentPanel.classList.remove('exit-left', 'exit-right');
        const targetPanel = document.querySelector('.step-panel[data-panel="' + step + '"]');
        if (targetPanel) {
            targetPanel.classList.add('active');
            if (step > currentStep) {
                targetPanel.classList.add('enter-right');
            } else {
                targetPanel.classList.add('enter-left');
            }
            setTimeout(function() {
                targetPanel.classList.remove('enter-right', 'enter-left');
            }, 50);
        }
        currentStep = step;
        updateProgress();
    }, 250);
}

// ============================================================
// Validation helpers
// ============================================================
function setFieldState(input, status, feedbackId, message) {
    const container2 = input.closest('.input-box');
    const statusIcon = input.closest('.input-box').querySelector('.field-status');
    const feedback = document.getElementById(feedbackId);

    if (status === 'valid') {
        container2.classList.add('valid');
        container2.classList.remove('invalid');
        if (statusIcon) {
            statusIcon.className = 'fa-solid fa-circle-check field-status';
            statusIcon.style.color = '#2ecc71';
        }
        if (feedback) {
            feedback.className = 'field-feedback valid';
            feedback.textContent = message || '';
        }
    } else if (status === 'invalid') {
        container2.classList.add('invalid');
        container2.classList.remove('valid');
        if (statusIcon) {
            statusIcon.className = 'fa-solid fa-circle-exclamation field-status';
            statusIcon.style.color = '#e74c3c';
        }
        if (feedback) {
            feedback.className = 'field-feedback invalid';
            feedback.textContent = message || '';
        }
    } else {
        container2.classList.remove('valid', 'invalid');
        if (statusIcon) {
            statusIcon.className = 'fa-solid fa-circle-check field-status';
            statusIcon.style.color = '';
        }
        if (feedback) {
            feedback.className = 'field-feedback';
            feedback.textContent = '';
        }
    }
}

// ============================================================
// Step 1 validation
// ============================================================
function validateStep1() {
    const first = document.getElementById('firstName');
    const last = document.getElementById('lastName');
    let valid = true;

    if (!first.value.trim()) {
        first.closest('.input-box').classList.add('invalid');
        valid = false;
    } else {
        first.closest('.input-box').classList.remove('invalid');
    }
    if (!last.value.trim()) {
        last.closest('.input-box').classList.add('invalid');
        valid = false;
    } else {
        last.closest('.input-box').classList.remove('invalid');
    }
    return valid;
}

// ============================================================
// Step 2 validation + AJAX availability checks
// ============================================================
let usernameValid = false;
let emailValid = false;

const usernameInput = document.getElementById('username');
const emailInput = document.getElementById('email');

let usernameCheckTimer = null;
usernameInput.addEventListener('input', function() {
    clearTimeout(usernameCheckTimer);
    usernameValid = false;
    const value = this.value.trim();
    if (!value) {
        setFieldState(this, '', 'usernameFeedback', '');
        return;
    }
    setFieldState(this, '', 'usernameFeedback', 'Checking...');
    usernameCheckTimer = setTimeout(function() {
        checkUsername(value);
    }, 500);
});

async function checkUsername(username) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    try {
const res = await fetch("/check-username/", {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await res.json();
        if (data.available) {
            usernameValid = true;
            setFieldState(usernameInput, 'valid', 'usernameFeedback', data.message);
        } else {
            usernameValid = false;
            setFieldState(usernameInput, 'invalid', 'usernameFeedback', data.message);
        }
    } catch (e) {
        setFieldState(usernameInput, '', 'usernameFeedback', '');
    }
}

let emailCheckTimer = null;
emailInput.addEventListener('input', function() {
    clearTimeout(emailCheckTimer);
    emailValid = false;
    const value = this.value.trim();
    if (!value) {
        setFieldState(this, '', 'emailFeedback', '');
        return;
    }
    if (!validateEmail(value)) {
        setFieldState(this, 'invalid', 'emailFeedback', 'Please enter a valid email address.');
        return;
    }
    setFieldState(this, '', 'emailFeedback', 'Checking...');
    emailCheckTimer = setTimeout(function() {
        checkEmail(value);
    }, 500);
});

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

async function checkEmail(email) {
    const formData = new FormData();
    formData.append('email', email);
    formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    try {
const res = await fetch("/check-email/", {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await res.json();
        if (data.available) {
            emailValid = true;
            setFieldState(emailInput, 'valid', 'emailFeedback', data.message);
        } else {
            emailValid = false;
            setFieldState(emailInput, 'invalid', 'emailFeedback', data.message);
        }
    } catch (e) {
        setFieldState(emailInput, '', 'emailFeedback', '');
    }
}

function validateStep2() {
    const username = usernameInput.value.trim();
    const email = emailInput.value.trim();
    if (!username) {
        setFieldState(usernameInput, 'invalid', 'usernameFeedback', 'Username is required.');
        return false;
    }
    if (!email) {
        setFieldState(emailInput, 'invalid', 'emailFeedback', 'Email is required.');
        return false;
    }
    if (!validateEmail(email)) {
        setFieldState(emailInput, 'invalid', 'emailFeedback', 'Please enter a valid email address.');
        return false;
    }
    if (!usernameValid) {
        setFieldState(usernameInput, 'invalid', 'usernameFeedback', 'Please wait for username check or enter a valid username.');
        return false;
    }
    if (!emailValid) {
        setFieldState(emailInput, 'invalid', 'emailFeedback', 'Please wait for email check.');
        return false;
    }
    return true;
}

// ============================================================
// Step 3 validation — password strength
// ============================================================
function getPasswordScore(pw) {
    let score = 0;
    if (pw.length >= 8) score++;
    if (pw.length >= 12) score++;
    if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
    if (/\d/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;
    return Math.min(score, 4);
}

const regPassword = document.getElementById('regPassword');
const regConfirmPassword = document.getElementById('regConfirmPassword');
const strengthBar = document.getElementById('strengthBar');
const strengthLabel = document.getElementById('strengthLabel');

regPassword.addEventListener('input', function() {
    const score = getPasswordScore(this.value);
    const strengthText = ['Too weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#27ae60'];
    if (this.value.length === 0) {
        strengthBar.style.width = '0%';
        strengthLabel.textContent = '';
        this.closest('.input-box').classList.remove('invalid', 'valid');
        return;
    }
    strengthBar.style.width = ((score + 1) / 5 * 100) + '%';
    strengthBar.style.background = colors[score];
    strengthLabel.textContent = strengthText[score];
    strengthLabel.style.color = colors[score];
    if (score < 1) {
        this.closest('.input-box').classList.add('invalid');
        this.closest('.input-box').classList.remove('valid');
    } else {
        this.closest('.input-box').classList.remove('invalid');
        this.closest('.input-box').classList.add('valid');
    }
    checkConfirmMatch();
});

regConfirmPassword.addEventListener('input', checkConfirmMatch);

function checkConfirmMatch() {
    const pw = regPassword.value;
    const confirm = regConfirmPassword.value;
    if (confirm.length === 0) {
        setFieldState(regConfirmPassword, '', 'confirmFeedback', '');
        return;
    }
    if (pw === confirm) {
        setFieldState(regConfirmPassword, 'valid', 'confirmFeedback', 'Passwords match.');
    } else {
        setFieldState(regConfirmPassword, 'invalid', 'confirmFeedback', 'Passwords do not match.');
    }
}

function validateStep3() {
    const pw = regPassword.value;
    const confirm = regConfirmPassword.value;
    if (pw.length < 8) {
        regPassword.closest('.input-box').classList.add('invalid');
        return false;
    }
    if (getPasswordScore(pw) < 1) {
        regPassword.closest('.input-box').classList.add('invalid');
        return false;
    }
    if (pw !== confirm) {
        setFieldState(regConfirmPassword, 'invalid', 'confirmFeedback', 'Passwords do not match.');
        return false;
    }
    return true;
}

// ============================================================
// Next / Back / Submit
// ============================================================
nextBtn.addEventListener('click', function() {
    let valid = false;
    if (currentStep === 1) valid = validateStep1();
    else if (currentStep === 2) valid = validateStep2();
    if (valid) goToStep(currentStep + 1);
});

prevBtn.addEventListener('click', function() {
    if (currentStep > 1) goToStep(currentStep - 1);
});

document.getElementById('registerForm').addEventListener('submit', function(e) {
    if (!validateStep3()) {
        e.preventDefault();
        return;
    }
    // Show loading overlay on submit
    const loader = document.getElementById('systemLoader');
    if (loader) loader.classList.remove('hide');
});

// Initialize progress
updateProgress();

// ============================================================
// CSRF cookie helper
// ============================================================
function getCookie(name) {
    const value = '; ' + document.cookie;
    const parts = value.split('; ' + name + '=');
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
}
