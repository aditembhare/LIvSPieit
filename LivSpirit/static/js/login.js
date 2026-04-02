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
