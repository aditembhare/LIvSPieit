document.addEventListener('DOMContentLoaded', () => {
  // Password match indicator
  const newPw  = document.getElementById('new_password');
  const confPw = document.getElementById('confirm_pw');
  const msg    = document.getElementById('pw-match-msg');

  function checkMatch() {
    if (!confPw.value) { msg.classList.add('hidden'); return; }
    msg.classList.remove('hidden');
    if (newPw.value === confPw.value) {
      msg.textContent = '✓ Passwords match';
      msg.className = 'text-xs text-green-600';
    } else {
      msg.textContent = '✗ Passwords do not match';
      msg.className = 'text-xs text-red-500';
    }
  }

  if (newPw && confPw) {
    newPw.addEventListener('input', checkMatch);
    confPw.addEventListener('input', checkMatch);
  }

  // Close modal on backdrop click
  const deleteModal = document.getElementById('delete-modal');
  if (deleteModal) {
    deleteModal.addEventListener('click', function(e) {
      if (e.target === this) this.classList.add('hidden');
    });
  }
});
