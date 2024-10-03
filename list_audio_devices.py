# list_audio_devices.py

import sounddevice as sd

def list_devices():
    print("Available audio input devices:")
    for idx, device in enumerate(sd.query_devices()):
        if device['max_input_channels'] > 0:
            print(f"{idx}: {device['name']} - Channels: {device['max_input_channels']}, Sample Rate: {device['default_samplerate']}")

if __name__ == "__main__":
    list_devices()
