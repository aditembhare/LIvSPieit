// Auto-dismiss flash messages after 4 seconds
setTimeout(() => {
  document.querySelectorAll('.fixed.top-24 > div').forEach(el => {
    el.style.transition = 'opacity 0.5s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  });
}, 4000);
