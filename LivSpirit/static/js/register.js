function togglePassword(fieldId, btn) {
  const input = document.getElementById(fieldId);
  const icon  = btn.querySelector('.material-symbols-outlined');
  if (input.type === 'password') {
    input.type = 'text';
    icon.textContent = 'visibility_off';
  } else {
    input.type = 'password';
    icon.textContent = 'visibility';
  }
}

window.togglePassword = togglePassword;

document.addEventListener('DOMContentLoaded', () => {
  // Password Strength Meter
  const pwInput = document.getElementById('password');
  const meter   = document.getElementById('strength-meter');
  const label   = document.getElementById('strength-label');
  const bars    = ['s1','s2','s3','s4'].map(id => document.getElementById(id));

  if (pwInput) {
    pwInput.addEventListener('input', () => {
      const val = pwInput.value;
      if (!val) { meter.classList.add('hidden'); return; }
      meter.classList.remove('hidden');

      let score = 0;
      if (val.length >= 6) score++;
      if (val.length >= 10) score++;
      if (/[A-Z]/.test(val) && /[0-9]/.test(val)) score++;
      if (/[^A-Za-z0-9]/.test(val)) score++;

      const colors = ['bg-red-400', 'bg-amber-400', 'bg-yellow-400', 'bg-green-500'];
      const labels = ['Too weak', 'Fair', 'Good', 'Strong'];
      bars.forEach((bar, i) => {
        bar.className = `h-1 flex-1 rounded-full transition-colors duration-300 ${i < score ? colors[score-1] : 'bg-surface-container-high'}`;
      });
      label.textContent = labels[score - 1] || '';
    });
  }
});
