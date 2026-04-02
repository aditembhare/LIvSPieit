document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.reflection-card').forEach(card => {
    card.addEventListener('click', () => {
      document.getElementById('modal-title').textContent = card.dataset.title;
      document.getElementById('modal-date').textContent = card.dataset.date;
      document.getElementById('modal-content').textContent = card.dataset.content;
      document.getElementById('reflection-modal').classList.remove('hidden');
    });
  });
});
