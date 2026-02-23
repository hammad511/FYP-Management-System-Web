/* ============================================================
   auth-modern.js  –  Shared logic for Sign In & Sign Up pages
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

    /* ── Floating particles ── */
    const particleBox = document.querySelector('.particles');
    if (particleBox) {
        for (let i = 0; i < 30; i++) {
            const s = document.createElement('span');
            s.style.left  = Math.random() * 100 + '%';
            s.style.width = s.style.height = (Math.random() * 5 + 3) + 'px';
            s.style.animationDuration = (Math.random() * 12 + 8) + 's';
            s.style.animationDelay    = (Math.random() * 8) + 's';
            s.style.opacity = Math.random() * 0.4 + 0.1;
            particleBox.appendChild(s);
        }
    }

    /* ── Password visibility toggle ── */
    document.querySelectorAll('.pw-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.parentElement.querySelector('input');
            const isHidden = input.type === 'password';
            input.type = isHidden ? 'text' : 'password';
            const icon = btn.querySelector('i');
            icon.classList.toggle('bi-eye');
            icon.classList.toggle('bi-eye-slash');
        });
    });

    /* ── Password strength meter (signup page) ── */
    const pwField   = document.getElementById('password');
    const bars      = document.querySelectorAll('.pw-bar');
    const pwLabel   = document.getElementById('pwLabel');

    if (pwField && bars.length) {
        pwField.addEventListener('input', () => {
            const v = pwField.value;
            let score = 0;
            if (v.length >= 6)  score++;
            if (v.length >= 10) score++;
            if (/[A-Z]/.test(v) && /[a-z]/.test(v)) score++;
            if (/\d/.test(v))   score++;
            if (/[^A-Za-z0-9]/.test(v)) score++;

            const level = score <= 1 ? 1 : score <= 2 ? 2 : score <= 3 ? 3 : 4;
            const cls   = ['', 'weak', 'fair', 'good', 'strong'][level];
            const txt   = ['', 'Weak', 'Fair', 'Good', 'Strong'][level];

            bars.forEach((b, i) => {
                b.className = 'pw-bar' + (i < level ? ' ' + cls : '');
            });
            if (pwLabel) pwLabel.textContent = v ? txt : '';
        });
    }

    /* ── Inline field validation ── */
    function showError(field, msg) {
        const wrap = field.closest('.input-wrap');
        const errEl = field.closest('.field')?.querySelector('.field-error');
        if (wrap)  { wrap.classList.add('is-invalid'); wrap.classList.remove('is-valid'); }
        if (errEl) { errEl.textContent = msg; errEl.classList.add('show'); }
    }
    function clearError(field) {
        const wrap = field.closest('.input-wrap');
        const errEl = field.closest('.field')?.querySelector('.field-error');
        if (wrap)  { wrap.classList.remove('is-invalid'); }
        if (errEl) { errEl.classList.remove('show'); }
    }
    function markValid(field) {
        const wrap = field.closest('.input-wrap');
        if (wrap) { wrap.classList.add('is-valid'); wrap.classList.remove('is-invalid'); }
        clearError(field);
    }

    /* Live validation on blur */
    document.querySelectorAll('.auth-form input[required], .auth-form select[required]').forEach(el => {
        el.addEventListener('blur', () => {
            if (!el.value.trim()) {
                showError(el, 'This field is required');
                return;
            }
            /* email regex */
            if (el.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value)) {
                showError(el, 'Enter a valid email address');
                return;
            }
            /* min-length password */
            if (el.name === 'password' && el.value.length < 8) {
                showError(el, 'Must be at least 8 characters');
                return;
            }
            /* confirm password match */
            if (el.name === 'confirmPassword') {
                const pw = document.getElementById('password');
                if (pw && el.value !== pw.value) {
                    showError(el, 'Passwords do not match');
                    return;
                }
            }
            markValid(el);
        });
        /* clear red on typing */
        el.addEventListener('input', () => clearError(el));
    });

    /* ── Form submit: full validate + loading spinner ── */
    const form = document.querySelector('.auth-form');
    const btn  = form?.querySelector('.btn-auth');

    if (form && btn) {
        form.addEventListener('submit', e => {
            let hasErr = false;

            form.querySelectorAll('input[required]:not([type=hidden]), select[required]').forEach(el => {
                /* skip fields inside hidden role sections */
                if (el.closest('[style*="display: none"]') || el.closest('[style*="display:none"]')) return;

                if (!el.value.trim()) { showError(el, 'This field is required'); hasErr = true; return; }
                if (el.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value)) {
                    showError(el, 'Enter a valid email address'); hasErr = true; return;
                }
                if (el.name === 'password' && el.value.length < 8) {
                    showError(el, 'Must be at least 8 characters'); hasErr = true; return;
                }
                if (el.name === 'confirmPassword') {
                    const pw = document.getElementById('password');
                    if (pw && el.value !== pw.value) {
                        showError(el, 'Passwords do not match'); hasErr = true; return;
                    }
                }
            });

            if (hasErr) { e.preventDefault(); return; }

            btn.classList.add('loading');
            setTimeout(() => btn.classList.remove('loading'), 6000);
        });
    }

    /* ── Role-specific field toggling (signup) ── */
    const roleSelect = document.getElementById('role');
    if (roleSelect) {
        const sections = {
            student:    document.getElementById('studentFields'),
            faculty:    document.getElementById('facultyFields'),
            supervisor: document.getElementById('supervisorFields'),
        };
        const reqMap = {
            student:    ['program', 'semester'],
            faculty:    ['username'],
            supervisor: ['highestDegree', 'specialization'],
        };

        roleSelect.addEventListener('change', function () {
            /* hide all, remove required */
            Object.values(sections).forEach(s => { if (s) s.style.display = 'none'; });
            Object.values(reqMap).flat().forEach(id => {
                const el = document.getElementById(id);
                if (el) el.required = false;
            });
            /* show selected, add required */
            const sec = sections[this.value];
            if (sec) sec.style.display = 'block';
            (reqMap[this.value] || []).forEach(id => {
                const el = document.getElementById(id);
                if (el) el.required = true;
            });
        });
    }

    /* ── Affiliation toggle (supervisor) ── */
    const affOther  = document.getElementById('otherUniversity');
    const affNutech = document.getElementById('nutechUniversity');
    const affField  = document.getElementById('otherAffiliationField');
    const affInput  = document.getElementById('otherAffiliation');
    if (affOther && affNutech && affField) {
        affOther.addEventListener('change',  () => { affField.style.display = 'block';  if (affInput) affInput.required = true; });
        affNutech.addEventListener('change', () => { affField.style.display = 'none';   if (affInput) affInput.required = false; });
    }

    /* ── Social login redirect ── */
    window.socialLogin = provider => {
        // Require role selection before social login
        const roleSelect = document.getElementById('role');
        if (roleSelect && !roleSelect.value) {
            // Show error on the role field
            const wrap = roleSelect.closest('.input-wrap');
            const errEl = roleSelect.closest('.field')?.querySelector('.field-error');
            if (wrap) { wrap.classList.add('is-invalid'); }
            if (errEl) { errEl.textContent = 'Please select your role before continuing with ' + provider; errEl.classList.add('show'); }
            roleSelect.focus();
            return;
        }
        const role = roleSelect ? roleSelect.value : '';
        window.location.href = `/login/${provider}?role=${encodeURIComponent(role)}`;
    };

    /* ── Auto-dismiss flash alerts ── */
    setTimeout(() => {
        document.querySelectorAll('.auth-alert').forEach(el => {
            el.style.transition = 'opacity 0.3s';
            el.style.opacity = '0';
            setTimeout(() => el.remove(), 300);
        });
    }, 5000);

    /* ── Focus icon color boost ── */
    document.querySelectorAll('.input-wrap input, .input-wrap select').forEach(el => {
        el.addEventListener('focus', () => {
            const ic = el.closest('.input-wrap').querySelector('.icon');
            if (ic) ic.style.color = 'var(--primary)';
        });
        el.addEventListener('blur', () => {
            const ic = el.closest('.input-wrap').querySelector('.icon');
            if (ic && !el.value) ic.style.color = '';
        });
    });

});
