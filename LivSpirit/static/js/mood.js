function selectMood(mood, btn) {
  document.getElementById('mood-level-input').value = mood;
  document.querySelectorAll('.mood-btn').forEach(b => {
    b.querySelector('div').classList.remove('bg-primary-container', 'ring-4', 'ring-primary-fixed/30');
    b.querySelector('div').classList.add('bg-surface-container-low');
    b.querySelector('span.material-symbols-outlined').classList.remove('text-on-primary');
    b.querySelector('span.material-symbols-outlined').classList.add('text-primary');
    b.querySelector('span.text-xs').classList.remove('font-bold', 'text-primary');
    b.querySelector('span.text-xs').classList.add('text-on-surface-variant');
  });
  btn.querySelector('div').classList.add('bg-primary-container', 'ring-4', 'ring-primary-fixed/30');
  btn.querySelector('div').classList.remove('bg-surface-container-low');
  btn.querySelector('span.material-symbols-outlined').classList.add('text-on-primary');
  btn.querySelector('span.material-symbols-outlined').classList.remove('text-primary');
  btn.querySelector('span.text-xs').classList.add('font-bold', 'text-primary');
  btn.querySelector('span.text-xs').classList.remove('text-on-surface-variant');
}

window.selectMood = selectMood;
