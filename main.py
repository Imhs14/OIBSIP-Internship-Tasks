import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
import os
import subprocess
import smtplib
import psutil
import pyjokes
import pyautogui
import random
import requests

MASTER = "Tony"

print("Initializing The AI Bot...")
print("Now the bot will work, please start talking")

engine = pyttsx3.init('nsss')
voices = engine.getProperty('voices')

# 🎙️ Find and set Allison (Enhanced) voice by name
allison_voice = None
for voice in voices:
    if 'allison' in voice.name.lower():
        allison_voice = voice
        break

if allison_voice:
    engine.setProperty('voice', allison_voice.id)
    print(f"✅ Using voice: {allison_voice.name}")
else:
    engine.setProperty('voice', voices[0].id)
    print("⚠️ Allison not found, using default voice")

# 🔊 Tuned for natural, clear sound
engine.setProperty('rate', 165)
engine.setProperty('volume', 0.9)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()
    print("The bot is talking")

def time():
    Time = datetime.datetime.now().strftime("%H:%M:%S")
    speak('The current time is')
    speak(Time)

def date():
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    speak('The Current date is')
    speak(day)
    speak(month)
    speak(year)

def wishme():
    speak("Welcome back!")
    hour = datetime.datetime.now().hour
    if hour >= 0 and hour < 12:
        speak("Good Morning " + MASTER)
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon " + MASTER)
    elif hour >= 18 and hour < 24:
        speak("Good Evening " + MASTER)
    else:
        speak("Good Night " + MASTER)
    speak("JARVIS at your service. Please tell me how can I help you?")

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-US')
        print(f"User said: {query}\n")
    except Exception as e:
        print(e)
        speak("Say that again please...")
        return "None"
    return query

def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('personal144022@gmail.com', 'none')
    server.sendmail("personal144022@gmail.com", to, content)
    server.close()

def cpu():
    usage = str(psutil.cpu_percent())
    speak('CPU is at ' + usage + ' percent')

def joke():
    speak(pyjokes.get_joke())

def screenshot():
    img = pyautogui.screenshot()
    save_path = os.path.expanduser('~/Desktop/screenshot.png')
    img.save(save_path)
    speak('Screenshot saved to your Desktop')

def who_am_i():
    speak('You are ' + MASTER + ', a brilliant person. I love you!')

def where_born():
    speak('I was created by Vishal, in Nepal')

def how_are_you():
    speak('I am fine, thank you. How can I help you?')

def open_app(app_name):
    subprocess.call(['open', '-a', app_name])

if __name__ == "__main__":
    wishme()

    while True:
        query = takeCommand().lower()

        if 'time' in query:
            time()

        elif 'date' in query:
            date()

        elif 'who am i' in query:
            who_am_i()

        elif 'where were you born' in query:
            where_born()

        elif 'how are you' in query:
            how_are_you()

        elif 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=3)
            speak('According to Wikipedia...')
            print(results)
            speak(results)

        elif 'send email' in query:
            try:
                speak('What should I send?')
                content = takeCommand()
                speak('Who is the receiver?')
                receiver = input("Enter Receiver's Email: ")
                sendEmail(receiver, content)
                speak('Email sent successfully')
            except Exception as e:
                print(e)
                speak('Unable to send Email')

        elif 'search in chrome' in query:
            speak('What should I search?')
            search = takeCommand().lower()
            chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
            webbrowser.get(chrome_path).open_new_tab(search + '.com')

        elif 'search youtube' in query:
            speak('What should I search?')
            search_term = takeCommand().lower()
            speak("Opening YouTube!")
            webbrowser.open('https://www.youtube.com/results?search_query=' + search_term)

        elif 'weather details' in query:
            speak('Which city?')
            weather_up = takeCommand().lower()
            speak('Getting weather update for ' + weather_up)
            url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid=c757f20d5d6b504ff4ba642d4255cf5e&units=metric'.format(weather_up)
            resi = requests.get(url)
            data = resi.json()
            temp = data['main']['temp']
            wind_speed = data['wind']['speed']
            latitude = data['coord']['lat']
            longitude = data['coord']['lon']
            description = data['weather'][0]['description']
            speak('Temperature is {} degree Celsius'.format(temp))
            speak('Wind speed is {} metres per second'.format(wind_speed))
            speak('Latitude is {}'.format(latitude))
            speak('Longitude is {}'.format(longitude))
            speak('Sky conditions are {}'.format(description))

        elif 'open google' in query:
            speak('What should I search?')
            search_term = takeCommand().lower()
            speak('Searching...')
            webbrowser.open('https://www.google.com/search?q=' + search_term)

        elif 'open github' in query:
            speak('Opening GitHub!')
            webbrowser.open('https://www.github.com/imhs14')

        elif 'cpu' in query:
            cpu()

        elif 'joke' in query:
            joke()

        elif 'go offline' in query:
            speak('Going Offline!')
            quit()

        elif 'open word' in query:
            speak('Opening Microsoft Word...')
            open_app('Microsoft Word')

        elif 'open downloads' in query:
            speak('Opening Downloads...')
            downloads = os.path.expanduser('~/Downloads')
            subprocess.call(['open', downloads])

        elif 'open visual code' in query:
            speak('Opening Visual Studio Code...')
            open_app('Visual Studio Code')

        elif 'write a note' in query:
            speak("What should I write?")
            notes = takeCommand()
            notes_path = os.path.expanduser('~/notes.txt')
            file = open(notes_path, 'w')
            speak("Should I include the date and time?")
            ans = takeCommand()
            if 'yes' in ans or 'sure' in ans:
                strTime = datetime.datetime.now().strftime("%H:%M:%S")
                file.write(strTime + ':- ' + notes)
                speak("Done taking notes!")
            else:
                file.write(notes)
            file.close()

        elif 'show notes' in query:
            speak('Showing Notes')
            notes_path = os.path.expanduser('~/notes.txt')
            file = open(notes_path, 'r')
            content = file.read()
            print(content)
            speak(content)
            file.close()

        elif 'screenshot' in query:
            screenshot()

        elif 'play music' in query:
            songs_dir = os.path.expanduser('~/Music')
            music = os.listdir(songs_dir)
            if not music:
                speak('No music files found in your Music folder')
            else:
                speak('Playing a random song')
                no = random.randint(0, len(music) - 1)
                song_path = os.path.join(songs_dir, music[no])
                subprocess.call(['open', song_path])

        elif 'who are you' in query:
            speak("I am JARVIS, Your Smart Assistant!")

        elif 'tell me a fun fact' in query:
            speak("I don't have fun facts yet, but I'm learning!")
