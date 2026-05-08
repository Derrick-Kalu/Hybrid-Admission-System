document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const showRegister = document.getElementById('showRegister');
    const showLogin = document.getElementById('showLogin');
    
    // Toggle Forms
    showRegister.addEventListener('click', (e) => {
        e.preventDefault();
        loginForm.classList.remove('active');
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
        registerForm.classList.add('active');
    });

    showLogin.addEventListener('click', (e) => {
        e.preventDefault();
        registerForm.classList.remove('active');
        registerForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
        loginForm.classList.add('active');
    });

    // Handle Login
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        const errorDiv = document.getElementById('loginError');
        
        try {
            const response = await fetch('http://127.0.0.1:5000/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                localStorage.setItem('auth_token', data.token); // Store JWT
                localStorage.setItem('applicant_id', data.applicant_id);
                localStorage.setItem('applicant_name', data.full_name);
                
                // Decode token to check if admin (basic client side routing, real protection is on backend)
                try {
                    const payload = JSON.parse(atob(data.token.split('.')[1]));
                    if (payload.is_admin) {
                        window.location.href = 'admin.html';
                        return;
                    }
                } catch(e) {}
                
                window.location.href = 'dashboard.html';
            } else {
                errorDiv.textContent = data.error || 'Login failed';
                errorDiv.classList.remove('hidden');
            }
        } catch (error) {
            errorDiv.textContent = 'Network error. Please ensure the backend is running.';
            errorDiv.classList.remove('hidden');
        }
    });

    // Handle Registration
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const errorDiv = document.getElementById('regError');
        
        const payload = {
            full_name: document.getElementById('regName').value,
            jamb_reg_number: document.getElementById('regJamb').value,
            email: document.getElementById('regEmail').value,
            phone: document.getElementById('regPhone').value,
            password: document.getElementById('regPassword').value
        };
        
        try {
            const response = await fetch('http://127.0.0.1:5000/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                localStorage.setItem('auth_token', data.token); // Store JWT
                localStorage.setItem('applicant_id', data.applicant_id);
                localStorage.setItem('applicant_name', payload.full_name);
                window.location.href = 'dashboard.html';
            } else {
                errorDiv.textContent = data.error || 'Registration failed';
                errorDiv.classList.remove('hidden');
            }
        } catch (error) {
            errorDiv.textContent = 'Network error. Please ensure the backend is running.';
            errorDiv.classList.remove('hidden');
        }
    });
});
