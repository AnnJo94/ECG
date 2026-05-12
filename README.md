# ECG Signal Command Center

A standalone Python ECG dashboard with a modern Tkinter GUI, live synthetic waveform rendering, telemetry cards, lead selection, gain controls, sweep speed controls, pause/resume, and rhythm status readouts.

## Features

- Live animated ECG waveform simulation
- Heart rate, SpO2, and signal quality telemetry cards
- Lead selector for standard ECG lead labels
- Adjustable waveform gain and sweep speed
- Pause/resume and reset controls
- Rhythm readout for demo monitoring states
- No third-party dependencies required

## Screenshots

![ECG dashboard](screenshots/dashboard.png)

## Requirements

- Python 3.10 or newer

## Getting Started

Clone the repository:

```bash
git clone git@github.com:AnnJo94/ECG.git
cd ECG
```

Run the dashboard:

```bash
python ECG.py
```

## Project Structure

```text
ECG/
├── ECG.py
├── README.md
└── screenshots/
    └── placeholder.svg
```

## Notes

This app uses a synthetic ECG-like signal for demonstration. It is not intended for clinical diagnosis or medical decision-making.
