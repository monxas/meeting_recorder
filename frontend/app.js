// frontend/app.js

// API Base URL
const API_BASE_URL = '/api'; // Same origin

// DOM Elements
const audioDeviceSelect = document.getElementById('audioDevice');
const toggleBtn = document.getElementById('toggleBtn');
const statusDisplay = document.getElementById('status');
const summariesList = document.getElementById('summariesList');

// State Variable
let isRecording = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    fetchAudioDevices();
    fetchRecordings();
    setupEventListeners();
    updateStatus(); // Initial status
    // Optionally, set an interval to update status every few seconds
    // setInterval(updateStatus, 5000);
});

// Fetch available audio devices from the back-end and populate the dropdown
function fetchAudioDevices() {
    fetch(`${API_BASE_URL}/audio-devices`)
        .then(response => response.json())
        .then(devices => {
            populateAudioDevices(devices);
        })
        .catch(error => {
            console.error('Error fetching audio devices:', error);
            alert('Failed to load audio devices. Please try again.');
        });
}

// Populate the audio devices dropdown
function populateAudioDevices(devices) {
    // Clear existing options
    audioDeviceSelect.innerHTML = '';

    if (devices.length === 0) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = 'No audio devices found';
        audioDeviceSelect.appendChild(option);
        return;
    }

    // Add a default option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select an audio input device';
    audioDeviceSelect.appendChild(defaultOption);

    // Add device options
    devices.forEach(device => {
        const option = document.createElement('option');
        option.value = device.id;
        option.textContent = `${device.name} (${device.channels} channels)`;
        audioDeviceSelect.appendChild(option);
    });
}

// Set up event listeners for the toggle button
function setupEventListeners() {
    toggleBtn.addEventListener('click', toggleRecording);
}

// Toggle recording state
function toggleRecording() {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
}

// Start recording
function startRecording() {
    const selectedDeviceId = audioDeviceSelect.value;

    if (!selectedDeviceId) {
        alert('Please select an audio input device before starting the recording.');
        return;
    }

    // Disable the dropdown to prevent changing devices mid-recording
    audioDeviceSelect.disabled = true;

    // Update UI to reflect recording state
    isRecording = true;
    toggleBtn.textContent = 'Stop Recording';
    toggleBtn.classList.add('recording');
    statusDisplay.textContent = 'Status: Recording...';

    // Send POST request to start recording
    fetch(`${API_BASE_URL}/start-recording`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ device_id: parseInt(selectedDeviceId) })
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.detail || 'Failed to start recording.');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Recording started:', data);
        })
        .catch(error => {
            console.error('Error starting recording:', error);
            alert(`Error starting recording: ${error.message}`);
            // Revert UI changes
            isRecording = false;
            toggleBtn.textContent = 'Start Recording';
            toggleBtn.classList.remove('recording');
            statusDisplay.textContent = 'Status: Idle';
            audioDeviceSelect.disabled = false;
        });
}

// Stop recording
function stopRecording() {
    // Update UI to reflect idle state
    isRecording = false;
    toggleBtn.textContent = 'Start Recording';
    toggleBtn.classList.remove('recording');
    statusDisplay.textContent = 'Status: Stopping...';

    // Send POST request to stop recording
    fetch(`${API_BASE_URL}/stop-recording`, {
        method: 'POST'
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.detail || 'Failed to stop recording.');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Recording stopped:', data);
            statusDisplay.textContent = 'Status: Idle';
            // Re-enable the dropdown
            audioDeviceSelect.disabled = false;
            // Refresh the recordings list
            fetchRecordings();
        })
        .catch(error => {
            console.error('Error stopping recording:', error);
            alert(`Error stopping recording: ${error.message}`);
            // Revert UI changes
            isRecording = false;
            toggleBtn.textContent = 'Start Recording';
            toggleBtn.classList.remove('recording');
            statusDisplay.textContent = 'Status: Idle';
            audioDeviceSelect.disabled = false;
        });
}

// Update the status display by fetching from the back-end
function updateStatus() {
    fetch(`${API_BASE_URL}/status`)
        .then(response => response.json())
        .then(data => {
            statusDisplay.textContent = `Status: ${data.status}`;
            if (data.status === 'Recording') {
                isRecording = true;
                toggleBtn.textContent = 'Stop Recording';
                toggleBtn.classList.add('recording');
                audioDeviceSelect.disabled = true;
            } else {
                isRecording = false;
                toggleBtn.textContent = 'Start Recording';
                toggleBtn.classList.remove('recording');
                audioDeviceSelect.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error fetching status:', error);
            statusDisplay.textContent = 'Status: Unknown';
        });
}

// Fetch recordings from the back-end and display them
function fetchRecordings() {
    fetch(`${API_BASE_URL}/recordings`)
        .then(response => response.json())
        .then(recordings => {
            populateRecordings(recordings);
        })
        .catch(error => {
            console.error('Error fetching recordings:', error);
            summariesList.innerHTML = '<li>Failed to load recordings.</li>';
        });
}

// Populate the recordings list with audio players
function populateRecordings(recordings) {
    // Clear existing list
    summariesList.innerHTML = '';

    if (recordings.length === 0) {
        const li = document.createElement('li');
        li.textContent = 'No recordings available.';
        summariesList.appendChild(li);
        return;
    }

    // Sort recordings by timestamp descending (newest first)
    recordings.sort((a, b) => {
        const getTimestamp = filename => {
            const match = filename.match(/meeting_audio_(\d{8}_\d{6})\.wav/);
            return match ? match[1] : '';
        };
        return getTimestamp(b).localeCompare(getTimestamp(a));
    });

    recordings.forEach(recording => {
        const li = document.createElement('li');

        const nameSpan = document.createElement('span');
        nameSpan.classList.add('recording-name');
        nameSpan.textContent = recording;

        const audio = document.createElement('audio');
        audio.controls = true;
        audio.src = `/recordings/${recording}`; // Added leading slash for absolute path

        li.appendChild(nameSpan);
        li.appendChild(audio);
        summariesList.appendChild(li);
    });
}
