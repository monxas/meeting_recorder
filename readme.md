# Meeting Recorder Tool

A Python-based tool for macOS that captures system audio and microphone input during meetings from applications like Slack, Zoom, and Teams. It then transcribes the recorded audio and generates summarized notes using a Large Language Model (LLM) like OpenAI's GPT-4.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Install Homebrew](#2-install-homebrew)
  - [3. Install Python](#3-install-python)
  - [4. Set Up Virtual Audio Devices](#4-set-up-virtual-audio-devices)
  - [5. Configure Aggregate Device](#5-configure-aggregate-device)
  - [6. Set Up Python Environment](#6-set-up-python-environment)
  - [7. Install Python Dependencies](#7-install-python-dependencies)
  - [8. Configure Environment Variables](#8-configure-environment-variables)
- [Usage](#usage)
  - [1. List Audio Devices](#1-list-audio-devices)
  - [2. Record Audio](#2-record-audio)
  - [3. Transcribe Audio](#3-transcribe-audio)
  - [4. Generate Notes](#4-generate-notes)
  - [5. Automate the Workflow](#5-automate-the-workflow)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Additional Tips](#additional-tips)
- [License](#license)

## Features

- **System Audio Capture**: Records audio from applications like Slack, Zoom, and Teams.
- **Microphone Input**: Simultaneously records your voice through the microphone.
- **Transcription**: Converts recorded audio into text using OpenAI's Whisper.
- **Note Generation**: Summarizes the transcript into concise meeting notes using GPT-4.
- **Automation**: Streamlines the entire process with a master workflow script.

## Prerequisites

- **macOS**: Tested on macOS Catalina and later.
- **Python**: Version 3.7 or higher.
- **Homebrew**: macOS package manager.
- **Virtual Audio Driver**: [BlackHole](https://github.com/ExistentialAudio/BlackHole) (free and open-source) or [Loopback](https://rogueamoeba.com/loopback/) (paid).

## Installation

### 1. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/meeting-recorder.git
cd meeting-recorder
```

> **Note**: Replace `yourusername` with your actual GitHub username if applicable.

### 2. Install Homebrew

If you don't have Homebrew installed, install it using the following command:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

For more details, visit the [Homebrew website](https://brew.sh/).

### 3. Install Python

Ensure you have Python 3.7 or higher installed. You can install Python via Homebrew:

```bash
brew install python
```

Verify the installation:

```bash
python3 --version
```

### 4. Set Up Virtual Audio Devices

macOS doesn't allow direct system audio capture due to privacy and security restrictions. To work around this, set up a virtual audio device using **BlackHole**.

#### a. Install BlackHole

```bash
brew install blackhole-2ch
```

#### b. Create a Multi-Output Device

1. Open **Audio MIDI Setup**:
   - Navigate to **Applications > Utilities > Audio MIDI Setup**.

2. Create a **Multi-Output Device**:
   - Click the **"+"** button at the bottom-left corner and select **"Create Multi-Output Device"**.

3. Configure the Multi-Output Device:
   - Check the boxes for:
     - **Built-in Output** (or your preferred speakers/headphones)
     - **BlackHole 2ch**

4. (Optional) Rename the Multi-Output Device:
   - Double-click the name and rename it to **"Combined Output"** for clarity.

#### c. Create an Aggregate Device

1. In **Audio MIDI Setup**, click the **"+"** button and select **"Create Aggregate Device"**.

2. Configure the Aggregate Device:
   - Check the boxes for:
     - **BlackHole 2ch**
     - **Micrófono de “iPhone 16 Pro”** and/or **Micrófono del MacBook Air**

3. Enable **"Drift Correction"** for the microphone to prevent audio sync issues.

4. (Optional) Rename the Aggregate Device to **"Dispositivo agregado"**.

#### d. Set System Preferences to Use the Created Devices

1. **Set Multi-Output Device as Default Output**:
   - Go to **System Preferences > Sound > Output**.
   - Select **"Combined Output"**.

2. **Configure Applications to Use Combined Input**:
   - In applications like Zoom, Slack, or Teams, set the audio input to **"Dispositivo agregado"**.

### 5. Configure Aggregate Device

Ensure that your Aggregate Device (`Dispositivo agregado`) includes both **BlackHole 2ch** and your **microphone**. All included devices should have the same sample rate (48000 Hz).

### 6. Set Up Python Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
```

### 7. Install Python Dependencies

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

Alternatively, install them manually:

```bash
pip install sounddevice numpy openai python-dotenv git+https://github.com/openai/whisper.git tqdm pyaudio
```

> **Note**: If you encounter issues installing `pyaudio`, install PortAudio via Homebrew first:

```bash
brew install portaudio
pip install pyaudio
```

### 8. Configure Environment Variables

Create a `.env` file in the project root to store your OpenAI API key securely.

```bash
touch .env
```

Add your OpenAI API key to the `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

> **Important**: Replace `your_openai_api_key_here` with your actual OpenAI API key.

Ensure that `.env` is excluded from version control by verifying it's listed in `.gitignore`.

## Usage

### 1. List Audio Devices

Before recording, list all available audio input devices to verify configurations.

```bash
python list_audio_devices.py
```

**Sample Output:**

```
Available audio input devices:
0: Micrófono de “iPhone 16 Pro” - Channels: 1, Sample Rate: 48000.0
1: BlackHole 2ch - Channels: 2, Sample Rate: 48000.0
2: Micrófono del MacBook Air - Channels: 1, Sample Rate: 48000.0
4: Dispositivo agregado - Channels: 3, Sample Rate: 48000.0
```

### 2. Record Audio

Use the `record_audio.py` script to start recording.

```bash
python record_audio.py
```

**Script Behavior:**

- Attempts to record with 3 channels at 48000 Hz using **Dispositivo agregado** (Device ID: 4).
- If it encounters an error, it retries with fewer channels.
- Press `Ctrl+C` to stop recording.

**Successful Output:**

```
Using device 'Dispositivo agregado' (ID: 4)
Device supports up to 3 channel(s) at 48000 Hz
Attempting to record with 3 channel(s) at 48000 Hz
Recording... Press Ctrl+C to stop.
^C
Recording stopped by user.
Successfully recorded with 2 channel(s) at 48000 Hz
Audio recorded and saved to recordings/meeting_audio_20241003_123456.wav
```

### 3. Transcribe Audio

Transcribe the recorded audio using OpenAI's Whisper.

#### Option A: Using Local Whisper

```bash
python transcribe_audio.py
```

#### Option B: Using Whisper API

```bash
python transcribe_audio_api.py
```

> **Note**: Choose either Option A or Option B based on your preference and resources.

### 4. Generate Notes

Generate summarized notes from the transcript using GPT-4.

```bash
python generate_notes.py
```

### 5. Automate the Workflow

Use the `workflow.py` script to automate recording, transcription, and note generation.

```bash
python workflow.py
```

**Workflow Behavior:**

1. Starts recording audio. Speak and engage in your meeting.
2. Press `Ctrl+C` to stop recording.
3. Automatically transcribes the audio.
4. Generates summarized notes.
5. Saves all outputs in respective directories.

## Troubleshooting

### Common Issues

1. **Invalid Number of Channels Error**

   - **Solution**: Ensure that the `CHANNELS` parameter in `record_audio.py` matches a supported configuration (e.g., 2 channels at 48000 Hz).
   
2. **No Audio Captured**

   - **Solution**:
     - Verify that the Aggregate Device is correctly set up in **Audio MIDI Setup**.
     - Ensure that the recording script uses the correct device index.
     - Check microphone and system audio levels.

3. **Permission Issues**

   - **Solution**:
     - Go to **System Preferences > Security & Privacy > Privacy > Microphone**.
     - Ensure that **Terminal** or your Python IDE is checked.

4. **PyAudio Installation Errors**

   - **Solution**:
     - Install PortAudio via Homebrew:
       
       ```bash
       brew install portaudio
       pip install pyaudio
       ```

5. **API Errors During Transcription or Note Generation**

   - **Solution**:
     - Ensure your OpenAI API key is correctly set in the `.env` file.
     - Verify internet connectivity.
     - Check OpenAI service status.

### Additional Tips

- **Test with QuickTime Player**: Before using the Python scripts, test audio capture with QuickTime Player to ensure that both system audio and microphone input are being captured correctly.
  
- **Monitor Audio Levels**: Use **Audio MIDI Setup** to balance audio levels between system audio and microphone input.

## Project Structure

```
meeting-recorder/
├── .env
├── generate_notes.py
├── list_audio_devices.py
├── record_audio.py
├── record_audio_pyaudio.py
├── transcribe_audio.py
├── transcribe_audio_api.py
├── workflow.py
├── requirements.txt
├── README.md
├── .gitignore
├── recordings/
│   └── meeting_audio_YYYYMMDD_HHMMSS.wav
├── transcripts/
│   └── meeting_audio_YYYYMMDD_HHMMSS_transcript.txt
└── notes/
    └── meeting_audio_YYYYMMDD_HHMMSS_notes.txt
```

- **`.env`**: Stores environment variables like API keys.
- **`generate_notes.py`**: Generates summarized notes from transcripts.
- **`list_audio_devices.py`**: Lists available audio input devices.
- **`record_audio.py`**: Records audio using `sounddevice`.
- **`record_audio_pyaudio.py`**: Alternative recording script using `PyAudio`.
- **`transcribe_audio.py` / `transcribe_audio_api.py`**: Transcribes recorded audio.
- **`workflow.py`**: Automates the recording, transcription, and note generation process.
- **`requirements.txt`**: Lists Python dependencies.
- **`README.md`**: This documentation file.
- **`.gitignore`**: Specifies files and directories to be ignored by Git.
- **`recordings/`**: Stores recorded audio files.
- **`transcripts/`**: Stores transcribed text files.
- **`notes/`**: Stores generated meeting notes.

## Additional Tips

1. **Virtual Environment Management**

   - Always activate your virtual environment before running scripts:
     
     ```bash
     source venv/bin/activate
     ```

2. **Updating Dependencies**

   - Keep your dependencies up-to-date:
     
     ```bash
     pip install --upgrade -r requirements.txt
     ```

3. **Securing API Keys**

   - Never commit your `.env` file or API keys to version control.
   - Use tools like GitHub Secrets or environment variables for CI/CD pipelines.

4. **Enhancing the User Interface**

   - Consider developing a simple GUI using frameworks like **Tkinter**, **PyQt**, or **Electron.js** for a more user-friendly experience.

5. **Scheduling Recordings**

   - For automated recordings at specific times, explore using `cron` jobs or macOS's `launchd`.

6. **Monitoring and Logging**

   - Implement logging in your scripts to monitor the application's behavior and troubleshoot issues more effectively.

## License

This project is licensed under the [MIT License](LICENSE).

---

**Disclaimer**: This tool captures system audio and microphone input. Ensure you have the necessary permissions to record meetings and that you comply with all relevant privacy laws and regulations.