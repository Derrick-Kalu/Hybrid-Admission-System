document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    const showRegister = document.getElementById('showRegister');
    const showLogin = document.getElementById('showLogin');
    const showForgot = document.getElementById('showForgot');
    const forgotShowLogin = document.getElementById('forgotShowLogin');
    
    // Toggle Forms
    showRegister.addEventListener('click', (e) => {
        e.preventDefault();
        loginForm.classList.remove('active');
        loginForm.classList.add('hidden');
        forgotPasswordForm.classList.add('hidden');
        forgotPasswordForm.classList.remove('active');
        registerForm.classList.remove('hidden');
        registerForm.classList.add('active');
    });

    showLogin.addEventListener('click', (e) => {
        e.preventDefault();
        registerForm.classList.remove('active');
        registerForm.classList.add('hidden');
        forgotPasswordForm.classList.add('hidden');
        forgotPasswordForm.classList.remove('active');
        loginForm.classList.remove('hidden');
        loginForm.classList.add('active');
    });

    showForgot.addEventListener('click', (e) => {
        e.preventDefault();
        loginForm.classList.remove('active');
        loginForm.classList.add('hidden');
        registerForm.classList.remove('active');
        registerForm.classList.add('hidden');
        forgotPasswordForm.classList.remove('hidden');
        forgotPasswordForm.classList.add('active');
        document.getElementById('forgotError').classList.add('hidden');
        document.getElementById('forgotSuccess').classList.add('hidden');
    });

    forgotShowLogin.addEventListener('click', (e) => {
        e.preventDefault();
        forgotPasswordForm.classList.remove('active');
        forgotPasswordForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
        loginForm.classList.add('active');
    });

    // Handle Forgot Password Submission
    forgotPasswordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('forgotEmail').value;
        const errorDiv = document.getElementById('forgotError');
        const successDiv = document.getElementById('forgotSuccess');
        errorDiv.classList.add('hidden');
        successDiv.classList.add('hidden');

        try {
            const response = await fetch('http://127.0.0.1:5000/api/forgot-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });

            const data = await response.json();

            if (response.ok) {
                successDiv.innerHTML = `✅ Password reset successful!<br><br>Your temporary password is: <strong id="tempPasswordVal" style="font-size: 1.1rem; color: var(--navy-dark); background: var(--off-white); padding: 0.2rem 0.5rem; border-radius: 4px; border: 1px solid var(--gold); display: inline-block; margin-top: 0.5rem; font-family: monospace;">${data.temp_password}</strong> <button type="button" id="copyPasswordBtn" style="margin-left: 0.5rem; padding: 0.25rem 0.6rem; font-size: 0.8rem; background: var(--navy); color: white; border: none; border-radius: 4px; cursor: pointer; transition: all 0.2s ease; vertical-align: middle;">📋 Copy</button><br><br>Please copy this temporary password and use it to log in now.`;
                successDiv.classList.remove('hidden');
                document.getElementById('forgotEmail').value = '';

                // Set up copy button event listener
                const copyBtn = document.getElementById('copyPasswordBtn');
                if (copyBtn) {
                    copyBtn.addEventListener('click', () => {
                        navigator.clipboard.writeText(data.temp_password).then(() => {
                            copyBtn.textContent = '✅ Copied!';
                            copyBtn.style.background = '#10b981';
                            setTimeout(() => {
                                copyBtn.textContent = '📋 Copy';
                                copyBtn.style.background = '#1e3a8a';
                            }, 2000);
                        }).catch(() => {
                            // Fallback if clipboard API fails
                            const textArea = document.createElement("textarea");
                            textArea.value = data.temp_password;
                            document.body.appendChild(textArea);
                            textArea.select();
                            document.execCommand("copy");
                            document.body.removeChild(textArea);
                            copyBtn.textContent = '✅ Copied!';
                            copyBtn.style.background = '#10b981';
                            setTimeout(() => {
                                copyBtn.textContent = '📋 Copy';
                                copyBtn.style.background = '#1e3a8a';
                            }, 2000);
                        });
                    });
                }
            } else {
                errorDiv.textContent = data.error || 'Reset failed';
                errorDiv.classList.remove('hidden');
            }
        } catch (error) {
            errorDiv.textContent = 'Network error. Please ensure the backend is running.';
            errorDiv.classList.remove('hidden');
        }
    });

    // Theme Toggle Click Listener
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-theme');
            const theme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
            localStorage.setItem('theme', theme);
        });
    }

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
