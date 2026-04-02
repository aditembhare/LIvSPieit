// Auto-hide flash messages
setTimeout(() => {
  document.querySelectorAll('[class*="animate-pulse"]').forEach(el => el.remove());
}, 3000);

// Tibetan Sound Bath Logic
let tibetanTimer;
let tibetanSeconds = 600; // 10 mins
let tibetanPlaying = false;
let audioCtx;
let oscillator;
let gainNode;

function updateTibetanDisplay() {
  const m = Math.floor(tibetanSeconds / 60);
  const s = tibetanSeconds % 60;
  document.getElementById('tibetan-timer').textContent = 
    String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
}

function openTibetanModal() {
  document.getElementById('tibetan-modal').classList.remove('hidden');
  tibetanSeconds = 600;
  updateTibetanDisplay();
}

function closeTibetanModal() {
  document.getElementById('tibetan-modal').classList.add('hidden');
  stopTibetanAudio();
  clearInterval(tibetanTimer);
  tibetanPlaying = false;
  document.getElementById('tibetan-play-icon').textContent = 'play_arrow';
}

function toggleTibetanPlay() {
  if (tibetanPlaying) {
    clearInterval(tibetanTimer);
    stopTibetanAudio();
    document.getElementById('tibetan-play-icon').textContent = 'play_arrow';
    document.getElementById('bowl-icon').classList.remove('animate-pulse');
  } else {
    playTibetanAudio();
    document.getElementById('tibetan-play-icon').textContent = 'pause';
    document.getElementById('bowl-icon').classList.add('animate-pulse');
    tibetanTimer = setInterval(() => {
      if (tibetanSeconds > 0) {
        tibetanSeconds--;
        updateTibetanDisplay();
      } else {
        closeTibetanModal();
      }
    }, 1000);
  }
  tibetanPlaying = !tibetanPlaying;
}

function playTibetanAudio() {
  if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  oscillator = audioCtx.createOscillator();
  gainNode = audioCtx.createGain();
  
  // Tibetan bowl base freq
  oscillator.type = 'sine';
  oscillator.frequency.setValueAtTime(174.61, audioCtx.currentTime); // F3
  
  // Add some harmonics for bowl sound
  const osc2 = audioCtx.createOscillator();
  osc2.type = 'sine';
  osc2.frequency.setValueAtTime(174.61 * 2, audioCtx.currentTime);
  const gain2 = audioCtx.createGain();
  gain2.gain.value = 0.2;
  osc2.connect(gain2);
  gain2.connect(gainNode);
  osc2.start();
  
  // Modulate volume slightly
  const lfo = audioCtx.createOscillator();
  lfo.type = 'sine';
  lfo.frequency.value = 0.2;
  const lfoGain = audioCtx.createGain();
  lfoGain.gain.value = 0.3;
  lfo.connect(lfoGain);
  lfoGain.connect(gainNode.gain);
  lfo.start();
  
  gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
  gainNode.gain.linearRampToValueAtTime(0.5, audioCtx.currentTime + 2); // Fade in
  
  oscillator.connect(gainNode);
  gainNode.connect(audioCtx.destination);
  oscillator.start();
  
  // Store extra nodes to stop them later
  oscillator.osc2 = osc2;
  oscillator.lfo = lfo;
}

function stopTibetanAudio() {
  if (gainNode) {
    gainNode.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 1); // Fade out
    setTimeout(() => {
      if(oscillator) {
        oscillator.stop();
        if(oscillator.osc2) oscillator.osc2.stop();
        if(oscillator.lfo) oscillator.lfo.stop();
      }
    }, 1000);
  }
}
window.openTibetanModal = openTibetanModal;
window.closeTibetanModal = closeTibetanModal;
window.toggleTibetanPlay = toggleTibetanPlay;
