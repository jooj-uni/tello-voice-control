# tello-voice-control
Voice control for Tello drones using Vosk for Portuguese speech recognition, PyAudio for audio capture, and djitellopy for drone commands.

# Features
* Real-time voice recognition
* Control basic Tello movements: taleoff, land, move forward/back/left/right/up/down
* Flip in multiples directions
* Threaded execution for responsiveness
* Queue system to void blocking in execution

# Requirements
* Python 3.8+
* Tello drone
* Libraries:
  * djitellopy
  * pyAudio
  * Vosk
