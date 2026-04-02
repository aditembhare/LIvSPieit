// ─── Meditation Timer ─────────────────────────────────────
let timerSeconds = 15 * 60;
let timerRunning = false;
let timerInterval = null;
const totalSeconds = 15 * 60;

function updateTimerDisplay() {
  const m = Math.floor(timerSeconds / 60);
  const s = timerSeconds % 60;
  const display = document.getElementById('timer-display');
  if (display) display.textContent = String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
  
  const pct = timerSeconds / totalSeconds;
  const circumference = 2 * Math.PI * 130;
  const timerCircle = document.getElementById('timer-circle');
  if (timerCircle) timerCircle.style.strokeDashoffset = circumference * pct;
}

function toggleTimer() {
  if (timerRunning) {
    clearInterval(timerInterval);
    document.getElementById('play-icon').textContent = 'play_arrow';
  } else {
    timerInterval = setInterval(() => {
      if (timerSeconds > 0) { timerSeconds--; updateTimerDisplay(); }
      else { clearInterval(timerInterval); timerRunning = false; document.getElementById('play-icon').textContent = 'play_arrow'; }
    }, 1000);
    document.getElementById('play-icon').textContent = 'pause';
  }
  timerRunning = !timerRunning;
}

function adjustTimer(mins) {
  timerSeconds = Math.max(60, timerSeconds + mins * 60);
  updateTimerDisplay();
}

function setTimer(label, secs) {
  clearInterval(timerInterval);
  timerRunning = false;
  timerSeconds = secs;
  const title = document.getElementById('timer-title');
  if (title) title.textContent = label + ' Session';
  const icon = document.getElementById('play-icon');
  if (icon) icon.textContent = 'play_arrow';
  updateTimerDisplay();
}

document.addEventListener('DOMContentLoaded', () => {
    if(document.getElementById('timer-display')) {
        updateTimerDisplay();
    }
});

// ─── Pomodoro ────────────────────────────────────────────
let pomodoroInterval = null;
let pomodoroSeconds = 25 * 60; // 25 mins work
let isWorkPhase = true;
let pomodoroRound = 1;

function updatePomodoroDisplay() {
  const m = Math.floor(pomodoroSeconds / 60);
  const s = pomodoroSeconds % 60;
  document.getElementById('pomodoro-timer').textContent = 
    String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
  
  const total = isWorkPhase ? 25 * 60 : 5 * 60;
  const elapsed = total - pomodoroSeconds;
  const pct = Math.min((elapsed / total) * 100, 100);
  document.getElementById('pomodoro-bar').style.width = pct + '%';
  document.getElementById('pomodoro-pct').textContent = Math.round(pct) + '%';
  
  const phaseDisplay = document.getElementById('pomodoro-phase');
  phaseDisplay.textContent = isWorkPhase ? 'Work Phase (Round ' + pomodoroRound + ')' : 'Break Phase';
  phaseDisplay.className = isWorkPhase ? 'bg-primary/20 text-primary px-3 py-1 rounded-full text-[10px] font-bold tracking-widest uppercase' : 'bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-[10px] font-bold tracking-widest uppercase';
}

function startPomodoro() {
  if (pomodoroInterval) {
    clearInterval(pomodoroInterval);
    pomodoroInterval = null;
    document.getElementById('pomodoro-play-icon').textContent = 'play_arrow';
    return;
  }
  document.getElementById('pomodoro-play-icon').textContent = 'pause';
  pomodoroInterval = setInterval(() => {
    if (pomodoroSeconds > 0) {
      pomodoroSeconds--;
      updatePomodoroDisplay();
    } else {
       isWorkPhase = !isWorkPhase;
       if (isWorkPhase) pomodoroRound++;
       pomodoroSeconds = isWorkPhase ? 25 * 60 : 5 * 60;
       updatePomodoroDisplay();
    }
  }, 1000);
}

function resetPomodoro() {
  if (pomodoroInterval) clearInterval(pomodoroInterval);
  pomodoroInterval = null;
  document.getElementById('pomodoro-play-icon').textContent = 'play_arrow';
  isWorkPhase = true;
  pomodoroRound = 1;
  pomodoroSeconds = 25 * 60;
  updatePomodoroDisplay();
}

// ─── Breathing Exercise ──────────────────────────────────
const breathPhases = [
  { label: 'Inhale', duration: 4, step: '1 of 3' },
  { label: 'Hold', duration: 7, step: '2 of 3' },
  { label: 'Exhale', duration: 8, step: '3 of 3' }
];
let breathIndex = 0;
let breathTimeout = null;
let breathInterval = null; // for countdown
let breathRunning = false;
let currentBreathSeconds = 0;

function applyBreathPhase(i) {
  const phase = breathPhases[i];
  document.getElementById('breath-label').textContent = phase.label;
  document.getElementById('breath-count').textContent = 'Step ' + phase.step;
  
  currentBreathSeconds = phase.duration;
  document.getElementById('breath-timer').textContent = currentBreathSeconds;
  
  if (breathInterval) clearInterval(breathInterval);
  breathInterval = setInterval(() => {
    currentBreathSeconds--;
    if (currentBreathSeconds >= 0) {
      document.getElementById('breath-timer').textContent = currentBreathSeconds;
    }
  }, 1000);

  const core = document.getElementById('breath-core');
  const inner = document.getElementById('breath-inner');
  if (phase.label === 'Inhale') {
    core.style.transform = 'scale(1.2)'; inner.style.transform = 'scale(1.1)';
  } else if (phase.label === 'Exhale') {
    core.style.transform = 'scale(0.9)'; inner.style.transform = 'scale(0.95)';
  } else {
    core.style.transform = 'scale(1.2)'; inner.style.transform = 'scale(1.1)';
  }
  document.querySelectorAll('#breath-dots div').forEach((d,di) => {
    d.classList.toggle('bg-primary', di === i);
    d.classList.toggle('bg-secondary/30', di !== i);
  });
}

function breathCycle() {
  applyBreathPhase(breathIndex);
  breathTimeout = setTimeout(() => {
    breathIndex = (breathIndex + 1) % breathPhases.length;
    if (breathRunning) breathCycle();
  }, breathPhases[breathIndex].duration * 1000);
}

function startBreathing() {
  if (breathRunning) { resetBreathing(); return; }
  breathRunning = true;
  breathCycle();
}

function resetBreathing() {
  breathRunning = false;
  clearTimeout(breathTimeout);
  clearInterval(breathInterval);
  breathIndex = 0;
  document.getElementById('breath-label').textContent = 'Ready';
  document.getElementById('breath-timer').textContent = '';
  document.getElementById('breath-count').textContent = 'Step 1 of 3';
  document.getElementById('breath-core').style.transform = 'scale(1)';
  document.getElementById('breath-inner').style.transform = 'scale(1)';
}

// ─── Nature Audio ────────────────────────────────────────
let natureAudioCtx;
let natureNoiseSource;
let natureGain;
let isNaturePlaying = false;

function toggleNatureAudio() {
  const icon = document.getElementById('nature-play-indicator');
  const natureIcon = document.getElementById('nature-icon');
  
  if (isNaturePlaying) {
    if (natureGain) {
      natureGain.gain.linearRampToValueAtTime(0, natureAudioCtx.currentTime + 1);
      setTimeout(() => { 
        if (natureNoiseSource) { natureNoiseSource.stop(); natureNoiseSource.disconnect(); } 
        isNaturePlaying = false; 
      }, 1000);
    } else {
      isNaturePlaying = false;
    }
    icon.textContent = 'play_circle';
    natureIcon.classList.remove('animate-pulse', 'text-primary');
  } else {
    if (!natureAudioCtx) natureAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    
    const bufferSize = natureAudioCtx.sampleRate * 2;
    const buffer = natureAudioCtx.createBuffer(1, bufferSize, natureAudioCtx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
        data[i] = Math.random() * 2 - 1;
    }
    
    natureNoiseSource = natureAudioCtx.createBufferSource();
    natureNoiseSource.buffer = buffer;
    natureNoiseSource.loop = true;
    
    const filter = natureAudioCtx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 400; 
    
    const lfo = natureAudioCtx.createOscillator();
    lfo.type = 'sine';
    lfo.frequency.value = 0.1;
    const lfoGain = natureAudioCtx.createGain();
    lfoGain.gain.value = 300;
    lfo.connect(lfoGain);
    lfoGain.connect(filter.frequency);
    lfo.start();

    natureGain = natureAudioCtx.createGain();
    natureGain.gain.setValueAtTime(0, natureAudioCtx.currentTime);
    natureGain.gain.linearRampToValueAtTime(0.5, natureAudioCtx.currentTime + 2);
    
    natureNoiseSource.connect(filter);
    filter.connect(natureGain);
    natureGain.connect(natureAudioCtx.destination);
    natureNoiseSource.start();
    
    isNaturePlaying = true;
    icon.textContent = 'pause_circle';
    natureIcon.classList.add('animate-pulse', 'text-primary');
  }
}
function openStretchModal() {
  document.getElementById('stretch-modal').classList.remove('hidden');
}

// Make accessible globally
window.updateTimerDisplay = updateTimerDisplay;
window.toggleTimer = toggleTimer;
window.adjustTimer = adjustTimer;
window.setTimer = setTimer;
window.updatePomodoroDisplay = updatePomodoroDisplay;
window.startPomodoro = startPomodoro;
window.resetPomodoro = resetPomodoro;
window.applyBreathPhase = applyBreathPhase;
window.breathCycle = breathCycle;
window.startBreathing = startBreathing;
window.resetBreathing = resetBreathing;
window.toggleNatureAudio = toggleNatureAudio;
window.openStretchModal = openStretchModal;
