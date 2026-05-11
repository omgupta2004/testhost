import speech_recognition as sr
print("SpeechRecognition imported.")
r = sr.Recognizer()
print("Recognizer created.")
try:
    # Just check if we can access the attribute
    print(f"Energy threshold: {r.energy_threshold}")
except Exception as e:
    print(f"Error: {e}")
