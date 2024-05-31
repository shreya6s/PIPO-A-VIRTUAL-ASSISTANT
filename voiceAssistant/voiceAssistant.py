import sys
import threading
import tkinter as tk
import speech_recognition as sr
import pyttsx3 as tts
import requests

r = sr.Recognizer()
r.dynamic_energy_threshold = False

# API keys and base URL for Gemini API
api_key = 'YOUR-API-KEY'
base_url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}'

# Function to make a request to the Gemini API
def make_gemini_request(prompt, method='POST'):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    try:
        response = requests.post(base_url, json=data, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

# Function to ask a question and evaluate the response using the Gemini API
def ask_question_and_evaluate(sentence):
    try:
        reply = make_gemini_request(f"{sentence}. (Reply casually)")
        if not reply or 'candidates' not in reply:
            print("Error: Unable to generate response.")
            return "Sorry, I couldn't think of a response."
        try:
            gemini_reply = reply['candidates'][0]['content']['parts'][0]['text']
            gemini_reply = gemini_reply.replace('*', '')
            gemini_reply = gemini_reply.replace('Gemini', 'Pipo')
            return gemini_reply
        except IndexError:
            print("Error: Unable to access response text. Response structure might have changed.")
            return "Sorry, I couldn't understand that."
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting...")

# Assistant class
class Assistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.speaker = tts.init()
        self.speaker.setProperty("rate", 150)

        self.root = tk.Tk()
        self.root.title("Pipo Assistant")
        self.root.geometry("400x400")
        self.label = tk.Label(text="🐼", font=("Arial", 300, "bold"))
        self.label.pack()

        threading.Thread(target=self.run_assistant).start()
        self.root.mainloop()

    def run_assistant(self):
        while True:
            try:
                with sr.Microphone() as mic:
                    self.recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                    print("👀 Listening...")
                    self.label.config(fg="green")
                    audio = self.recognizer.listen(mic)

                text = self.recognizer.recognize_google(audio)
                text = text.lower()
                print("User:", text)
                self.speaker.runAndWait()  # Ensure the text is spoken before proceeding

                if text == "bye":
                    self.label.config(fg="pink")
                    print("Pipo: Bye!")
                    self.speaker.say("Bye")
                    self.speaker.runAndWait()
                    self.label.config(fg="black")
                    self.speaker.stop()
                    self.root.destroy()
                    sys.exit()
                else:
                    response = ask_question_and_evaluate(text)
                    self.label.config(fg="pink")
                    print("Pipo:", response)
                    self.speaker.say(response)

                    self.speaker.runAndWait()
                    self.label.config(fg="black")

            except Exception as e:
                print("Pipo: Couldn't hear you :(", str(e))
                self.label.config(fg="black")
                continue

Assistant()
