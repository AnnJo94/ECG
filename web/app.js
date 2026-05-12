const canvas = document.querySelector("#ecgCanvas");
const ctx = canvas.getContext("2d");
const heartRate = document.querySelector("#heartRate");
const spo2 = document.querySelector("#spo2");
const quality = document.querySelector("#quality");
const rhythm = document.querySelector("#rhythm");
const rhythmNote = document.querySelector("#rhythmNote");
const clock = document.querySelector("#clock");
const leadTitle = document.querySelector("#leadTitle");
const leadSelect = document.querySelector("#leadSelect");
const gain = document.querySelector("#gain");
const speed = document.querySelector("#speed");
const gainValue = document.querySelector("#gainValue");
const speedValue = document.querySelector("#speedValue");
const pauseButton = document.querySelector("#pauseButton");
const resetButton = document.querySelector("#resetButton");
const patientFile = document.querySelector("#patientFile");
const loadDemo = document.querySelector("#loadDemo");
const clearPatient = document.querySelector("#clearPatient");
const patientEmpty = document.querySelector("#patientEmpty");
const patientDetails = document.querySelector("#patientDetails");

let running = true;
let sampleIndex = 0;
let importedSamples = [];
let samples = Array.from({ length: 760 }, () => 0);
let vitals = { heartRate: 74, spo2: 98, quality: 94 };

const demoPatient = {
  name: "Maya Joseph",
  id: "ECG-2026-014",
  age: 42,
  sex: "Female",
  diagnosis: "Post-exercise monitoring",
  heartRate: 82,
  spo2: 99,
  signalQuality: 96,
  lead: "Lead II",
  notes: "Demo patient loaded from the browser interface.",
  samples: Array.from({ length: 900 }, (_, index) => syntheticEcg(index / 92)),
};

function syntheticEcg(t) {
  const beat = t % 1;
  const baseline = 0.035 * Math.sin(2 * Math.PI * t * 0.33);
  const pWave = 0.13 * Math.exp(-((beat - 0.18) / 0.035) ** 2);
  const qWave = -0.22 * Math.exp(-((beat - 0.36) / 0.012) ** 2);
  const rWave = 1.18 * Math.exp(-((beat - 0.39) / 0.01) ** 2);
  const sWave = -0.38 * Math.exp(-((beat - 0.425) / 0.015) ** 2);
  const tWave = 0.34 * Math.exp(-((beat - 0.66) / 0.075) ** 2);
  return baseline + pWave + qWave + rWave + sWave + tWave + (Math.random() - 0.5) * 0.035;
}

function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  const scale = window.devicePixelRatio || 1;
  canvas.width = Math.floor(rect.width * scale);
  canvas.height = Math.floor(rect.height * scale);
  ctx.setTransform(scale, 0, 0, scale, 0, 0);
}

function drawGrid(width, height) {
  ctx.fillStyle = "#06101c";
  ctx.fillRect(0, 0, width, height);

  for (let x = 0; x < width; x += 18) {
    ctx.strokeStyle = x % 90 === 0 ? "#1f3f5f" : "#10233a";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
  }

  for (let y = 0; y < height; y += 18) {
    ctx.strokeStyle = y % 90 === 0 ? "#1f3f5f" : "#10233a";
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();
  }
}

function drawWaveform() {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  drawGrid(width, height);

  const center = height * 0.52;
  const amplitude = height * 0.24 * Number(gain.value);
  const step = width / Math.max(1, samples.length - 1);

  ctx.lineJoin = "round";
  ctx.lineCap = "round";
  ctx.beginPath();
  samples.forEach((value, index) => {
    const x = index * step;
    const y = center - value * amplitude;
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = "rgba(41, 255, 135, 0.24)";
  ctx.lineWidth = 9;
  ctx.stroke();

  ctx.beginPath();
  samples.forEach((value, index) => {
    const x = index * step;
    const y = center - value * amplitude;
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = "#29ff87";
  ctx.lineWidth = 3;
  ctx.stroke();

  const scanX = (sampleIndex * 5) % Math.max(width, 1);
  ctx.strokeStyle = "#d9fff0";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(scanX, 0);
  ctx.lineTo(scanX, height);
  ctx.stroke();

  ctx.fillStyle = "#29ff87";
  ctx.font = "800 12px Segoe UI";
  ctx.fillText(importedSamples.length ? "IMPORTED" : "LIVE", 16, 24);
}

function updateVitals() {
  if (!importedSamples.length) {
    const now = Date.now() / 1000;
    vitals.heartRate = Math.round(74 + Math.sin(now * 0.9) * 5 + (Math.random() - 0.5) * 3);
    vitals.spo2 = Math.max(95, Math.min(100, Math.round(98 + Math.sin(now * 0.35))));
    vitals.quality = Math.max(88, Math.min(99, Math.round(94 + Math.sin(now * 0.55) * 4)));
  }

  heartRate.textContent = vitals.heartRate;
  spo2.textContent = vitals.spo2;
  quality.textContent = vitals.quality;

  if (vitals.heartRate > 100) rhythm.textContent = "Sinus Tachycardia Watch";
  else if (vitals.heartRate < 60) rhythm.textContent = "Sinus Bradycardia Watch";
  else if (vitals.quality < 90) rhythm.textContent = "Signal Noise Detected";
  else rhythm.textContent = "Normal Sinus Rhythm";
}

function updateLabels() {
  gainValue.textContent = `${Number(gain.value).toFixed(2)}x`;
  speedValue.textContent = `${Number(speed.value).toFixed(2)}x`;
  leadTitle.textContent = `${leadSelect.value} - 25 mm/s - ${Number(gain.value).toFixed(2)}x gain`;
  clock.textContent = new Date().toLocaleTimeString();
}

function tick() {
  if (running) {
    const count = Math.max(2, Math.round(5 * Number(speed.value)));
    for (let i = 0; i < count; i += 1) {
      let value;
      if (importedSamples.length) {
        value = importedSamples[sampleIndex % importedSamples.length];
      } else {
        value = syntheticEcg(sampleIndex / 92);
      }
      samples.push(value);
      samples.shift();
      sampleIndex += 1;
    }
    updateVitals();
  }

  updateLabels();
  drawWaveform();
  requestAnimationFrame(tick);
}

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/).filter(Boolean);
  if (!lines.length) return {};
  const headers = splitCsvLine(lines[0]).map((item) => item.trim());
  const values = splitCsvLine(lines[1] || "").map((item) => item.trim());
  return headers.reduce((patient, header, index) => {
    patient[header] = values[index] || "";
    return patient;
  }, {});
}

function splitCsvLine(line) {
  const values = [];
  let current = "";
  let inQuotes = false;

  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    const next = line[index + 1];
    if (char === '"' && next === '"') {
      current += '"';
      index += 1;
    } else if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === "," && !inQuotes) {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }

  values.push(current);
  return values;
}

function normalizeSamples(value) {
  if (Array.isArray(value)) return value.map(Number).filter(Number.isFinite);
  if (typeof value === "string") return value.split(/[\s,;|]+/).map(Number).filter(Number.isFinite);
  return [];
}

function showPatient(patient) {
  const details = {
    Name: patient.name || patient.patientName || "Unknown",
    ID: patient.id || patient.patientId || "Not provided",
    Age: patient.age || "Not provided",
    Sex: patient.sex || patient.gender || "Not provided",
    Diagnosis: patient.diagnosis || patient.condition || "Not provided",
    Notes: patient.notes || "None",
  };

  patientDetails.innerHTML = Object.entries(details)
    .map(([key, value]) => `<dt>${key}</dt><dd>${value}</dd>`)
    .join("");
  patientEmpty.classList.add("hidden");
  patientDetails.classList.remove("hidden");

  vitals = {
    heartRate: Number(patient.heartRate || patient.bpm || vitals.heartRate),
    spo2: Number(patient.spo2 || patient.oxygen || vitals.spo2),
    quality: Number(patient.signalQuality || patient.quality || vitals.quality),
  };

  if (patient.lead) leadSelect.value = patient.lead;
  importedSamples = normalizeSamples(patient.samples || patient.ecg || patient.waveform);
  if (importedSamples.length) {
    samples = Array.from({ length: 760 }, (_, index) => importedSamples[index % importedSamples.length]);
    rhythmNote.textContent = "Imported ECG samples are being replayed in the waveform viewer.";
  } else {
    rhythmNote.textContent = "Patient metadata imported. Synthetic waveform remains active because no samples were provided.";
  }
}

async function importPatient(file) {
  const text = await file.text();
  const parsed = file.name.toLowerCase().endsWith(".json") ? JSON.parse(text) : parseCsv(text);
  const patient = Array.isArray(parsed) ? parsed[0] : parsed;
  showPatient(patient);
}

patientFile.addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (!file) return;
  importPatient(file).catch((error) => {
    alert(`Could not import patient file: ${error.message}`);
  });
});

loadDemo.addEventListener("click", () => showPatient(demoPatient));

clearPatient.addEventListener("click", () => {
  importedSamples = [];
  patientDetails.classList.add("hidden");
  patientEmpty.classList.remove("hidden");
  rhythmNote.textContent = "Synthetic demo signal. Imported samples replace the generated waveform.";
});

pauseButton.addEventListener("click", () => {
  running = !running;
  pauseButton.textContent = running ? "Pause" : "Resume";
});

resetButton.addEventListener("click", () => {
  sampleIndex = 0;
  samples = Array.from({ length: 760 }, () => 0);
});

[leadSelect, gain, speed].forEach((control) => control.addEventListener("input", updateLabels));
window.addEventListener("resize", () => {
  resizeCanvas();
  drawWaveform();
});

resizeCanvas();
tick();
