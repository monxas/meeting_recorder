// frontend/app.js

// API Base URL
const API_BASE_URL = '/api'; // Same origin

// DOM Elements
const audioDeviceSelect = document.getElementById('audioDevice');
const toggleBtn = document.getElementById('toggleBtn');
const statusDisplay = document.getElementById('status');
const summariesList = document.getElementById('summariesList');
const summaryContent = document.getElementById('summaryContent');
const questionInput = document.getElementById('questionInput');
const askBtn = document.getElementById('askBtn');
const answerContent = document.getElementById('answerContent');

// State Variables
let isRecording = false;
let currentNotesFile = ''; // To track the current notes file

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    console.log('Document loaded, initializing application...');
    fetchAudioDevices();
    fetchRecordings();
    setupEventListeners();
    updateStatus(); // Initial status
    // Optionally, set an interval to update status every few seconds
    // setInterval(updateStatus, 5000);
});

// Fetch available audio devices from the backend and populate the dropdown
function fetchAudioDevices() {
    console.log('Fetching audio devices...');
    fetch(`${API_BASE_URL}/audio-devices`)
        .then(response => response.json())
        .then(devices => {
            console.log('Audio devices fetched:', devices);
            populateAudioDevices(devices);
        })
        .catch(error => {
            console.error('Error fetching audio devices:', error);
            alert('Failed to load audio devices. Please try again.');
        });
}

// Populate the audio devices dropdown
function populateAudioDevices(devices) {
    console.log('Populating audio devices...');
    // Clear existing options
    audioDeviceSelect.innerHTML = '';

    if (devices.length === 0) {
        console.warn('No audio devices found.');
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
    console.log('Audio devices populated.');
}

// Set up event listeners for the toggle and ask buttons
function setupEventListeners() {
    console.log('Setting up event listeners...');
    toggleBtn.addEventListener('click', toggleRecording);
    askBtn.addEventListener('click', askQuestion);
    console.log('Event listeners set up.');
}

// Toggle recording state
function toggleRecording() {
    console.log('Toggling recording state. Current state:', isRecording);
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
}

// Start recording
function startRecording() {
    console.log('Starting recording...');
    const selectedDeviceId = audioDeviceSelect.value;

    if (!selectedDeviceId) {
        console.warn('No audio input device selected.');
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
    console.log('Sending request to start recording with device ID:', selectedDeviceId);
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
            console.log('Recording started successfully:', data);
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
    console.log('Stopping recording...');
    // Update UI to reflect idle state
    isRecording = false;
    toggleBtn.textContent = 'Start Recording';
    toggleBtn.classList.remove('recording');
    statusDisplay.textContent = 'Status: Stopping...';

    // Send POST request to stop recording
    console.log('Sending request to stop recording...');
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
            console.log('Recording stopped successfully:', data);
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

// Update the status display by fetching from the backend
function updateStatus() {
    console.log('Updating status...');
    fetch(`${API_BASE_URL}/status`)
        .then(response => response.json())
        .then(data => {
            console.log('Status fetched:', data);
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

// Fetch recordings from the backend and display them
function fetchRecordings() {
    console.log('Fetching recordings...');
    fetch(`${API_BASE_URL}/recordings`)
        .then(response => response.json())
        .then(recordings => {
            console.log('Recordings fetched:', recordings);
            populateRecordings(recordings);
        })
        .catch(error => {
            console.error('Error fetching recordings:', error);
            summariesList.innerHTML = '<li>Failed to load recordings.</li>';
        });
}

// Populate the recordings list with summaries
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
        return getTimestamp(b.audio_file).localeCompare(getTimestamp(a.audio_file));
    });

    recordings.forEach(recording => {
        const li = document.createElement('li');

        // Format the file name to display a readable date
        const timestampMatch = recording.audio_file.match(/meeting_audio_(\d{8}_\d{6})\.wav/);
        const timestamp = timestampMatch ? timestampMatch[1] : '';
        const friendlyDate = formatTimestamp(timestamp);
        console.log('Friendly date:', friendlyDate);

        const nameSpan = document.createElement('span');
        nameSpan.classList.add('recording-name');
        nameSpan.textContent = `Meeting on ${friendlyDate}`;

        if (recording.notes_file) {
            const summaryButton = document.createElement('button');
            summaryButton.textContent = 'View Summary';
            summaryButton.className = 'summary-button';
            summaryButton.dataset.notesFile = recording.notes_file; // Store notes_file in data attribute
            summaryButton.addEventListener('click', () => {
                console.log('Viewing summary for:', recording.notes_file);
                displaySummary(recording.notes_file);
                setActiveSummary(summaryButton, recording.notes_file);
            });
            li.appendChild(nameSpan);
            li.appendChild(summaryButton);
        } else {
            li.appendChild(nameSpan);
            const noSummary = document.createElement('span');
            noSummary.textContent = ' (No summary available)';
            li.appendChild(noSummary);
        }

        summariesList.appendChild(li);
    });
}

// Function to extract and format timestamp from filename
function formatTimestamp(timestamp) {
    if (!timestamp) return 'Unknown Time';
    const year = timestamp.slice(0, 4);
    const month = timestamp.slice(4, 6);
    const day = timestamp.slice(6, 8);
    const hour = timestamp.slice(9, 11);
    const minute = timestamp.slice(11, 13);
    return `${year}-${month}-${day} at ${hour}:${minute}`;
}

function getTimestamp(filename) {
    console.log('Extracting timestamp from filename:', filename);
    const match = filename.match(/meeting_audio_(\d{8}_\d{6})\.wav/);
    const timestamp = match ? match[1] : '';
    console.log('Extracted timestamp:', timestamp);
    return timestamp;
}

// Function to display the summary in the main content area
function displaySummary(notesFile) {
    console.log('Displaying summary for notes file:', notesFile);
    if (!notesFile) {
        console.warn('No notes file provided.');
        summaryContent.innerHTML = '<p>No summary available for this recording.</p>';
        return;
    }

    fetch(`/notes/${notesFile}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch summary.');
            }
            return response.text();
        })
        .then(text => {
            console.log('Summary fetched successfully for notes file:', notesFile);
            const htmlContent = marked.parse(text);
            summaryContent.innerHTML = `<div>${htmlContent}</div>`;
            // Clear previous answers
            answerContent.innerHTML = '';
            // Clear question input
            questionInput.value = '';
        })
        .catch(error => {
            console.error('Error fetching summary:', error);
            summaryContent.innerHTML = '<p>Failed to load summary.</p>';
        });
}

// Function to set the active summary button and update currentNotesFile
function setActiveSummary(activeButton, notesFile) {
    // Remove the 'active' class from all buttons
    const allButtons = summariesList.querySelectorAll('.summary-button');
    allButtons.forEach(button => {
        button.classList.remove('active');
    });
    // Add the 'active' class to the clicked button
    activeButton.classList.add('active');
    // Update the currentNotesFile
    currentNotesFile = notesFile;
    console.log('Current notes file set to:', currentNotesFile);
}

// Function to ask a question based on the summary
function askQuestion() {
    const question = questionInput.value.trim();
    if (!question) {
        alert('Please enter a question before submitting.');
        return;
    }

    if (!currentNotesFile) {
        alert('No summary is currently selected. Please select a summary to ask questions about.');
        return;
    }

    // Create the request body
    const requestBody = {
        notes_file: currentNotesFile,
        question: question
    };

    // Send the question to the backend
    console.log('Sending question to backend:', requestBody);
    askBtn.disabled = true;
    askBtn.textContent = 'Asking...';

    fetch(`${API_BASE_URL}/ask-question`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.detail || 'Failed to get an answer.');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Answer received:', data);
            displayAnswer(data.answer);
        })
        .catch(error => {
            console.error('Error asking question:', error);
            alert(`Error: ${error.message}`);
        })
        .finally(() => {
            askBtn.disabled = false;
            askBtn.textContent = 'Ask';
        });
}

// Function to display the answer in the UI
function displayAnswer(answer) {
    console.log('Displaying answer:', answer);
    answerContent.innerHTML = `
        <h3>Answer</h3>
        <p>${escapeHtml(answer)}</p>
    `;
}

// Utility function to escape HTML to prevent XSS
function escapeHtml(text) {
    console.log('Escaping HTML for text:', text);
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    const escapedText = text.replace(/[&<>"']/g, function(m) { return map[m]; });
    console.log('Escaped text:', escapedText);
    return escapedText;
}
