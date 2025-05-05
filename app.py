from flask import Flask, render_template, url_for, request, session
import sqlite3
import secrets
from pypdf import PdfReader 
import google.generativeai as genai
import pytube
import moviepy.editor
import os
import speech_recognition as sr
from pydub import AudioSegment
import shutil
import re
import yt_dlp
from googletrans import Translator
translator = Translator()

def language_translate(text, to_lang):
    text_to_translate = translator.translate(text,src= "en",dest= to_lang)
    text = text_to_translate.text
    return text


genai.configure(api_key='AIzaSyDQjn7bRYXaNCsea_qyZs8dyL-MJ9dj-J4')
gemini_model = genai.GenerativeModel('gemini-1.5-pro')
chat = gemini_model.start_chat(history=[])

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

command = """CREATE TABLE IF NOT EXISTS user (Id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT, mobile TEXT, email TEXT)"""
cursor.execute(command)

command = """CREATE TABLE IF NOT EXISTS Youtube (Id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, sumary TEXT)"""
cursor.execute(command)

command = """CREATE TABLE IF NOT EXISTS Pdf (Id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, sumary TEXT)"""
cursor.execute(command)

command = """CREATE TABLE IF NOT EXISTS Video (Id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, sumary TEXT)"""
cursor.execute(command)

command = """CREATE TABLE IF NOT EXISTS Audio (Id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, sumary TEXT)"""
cursor.execute(command)

command = """CREATE TABLE IF NOT EXISTS Text (Id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, sumary TEXT)"""
cursor.execute(command)

command = """CREATE TABLE IF NOT EXISTS sessions (Id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, timestamp TEXT)"""
cursor.execute(command)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
chat_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/home')
def home():
    return render_template('text.html')

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_input = request.form['query']
        gemini_response = chat.send_message(user_input)
        sumary = gemini_response.text
        chat_history.append([user_input, sumary])

        greet = "Hello, how can i help you"
        return render_template('chatbot.html', greet = greet, chat_history=chat_history)

    greet = "Hello, how can i help you"
    return render_template('chatbot.html', greet = greet)

@app.route('/userlog', methods=['GET', 'POST'])
def userlog():
    if request.method == 'POST':

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        email = request.form['name']
        password = request.form['password']

        query = "SELECT * FROM user WHERE email = '"+email+"' AND password= '"+password+"'"
        cursor.execute(query)
        result = cursor.fetchall()

        if result:
            return render_template('text.html')
        else:
            return render_template('index.html', msg='Sorry, Incorrect Credentials Provided,  Try Again')

    return render_template('index.html')

@app.route('/userreg', methods=['GET', 'POST'])
def userreg():
    if request.method == 'POST':

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']
        
        print(name, mobile, email, password)

        cursor.execute("INSERT INTO user VALUES (NULL, '"+name+"', '"+password+"', '"+mobile+"', '"+email+"')")
        connection.commit()

        from datetime import datetime
        now = datetime.now()
        timestamp = now.strftime("%m/%d/%Y, %H:%M:%S")

        cursor.execute("insert into sessions values(NULL, '"+email+"', '"+timestamp+"')")
        connection.commit()

        return render_template('index.html', msg='Successfully Registered')
    
    return render_template('index.html')

@app.route('/youtube', methods=['GET', 'POST'])
def youtube():
    if request.method == 'POST':
        link = request.form['link']
        print(link)
        
        directory = 'static/temp'
        for file in os.listdir(directory):
            os.remove(directory+'/'+file)

        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': f'{directory}/%(title)s.%(ext)s',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
        except pytube.exceptions.PytubeError as e:
            print('Error:', e)
            return render_template('youtube.html', msg='data not found from entered source')

        ffmpeg_path = "C:/ffmpeg/bin/ffmpeg.exe"
        
        text = ''

        for file in os.listdir(directory):
            if file.endswith(".mp4"):
                video = moviepy.editor.VideoFileClip(os.path.join(directory, file))
                audio = video.audio
                file1 = file.replace('.mp4', '.mp3')
                mp3_file = os.path.join(directory, file1)
                shutil.copy('static/temp/'+file, 'static/video')
                audio.write_audiofile(mp3_file)
                shutil.copy(mp3_file, 'static/audio')
                audio = AudioSegment.from_file(mp3_file, format="mp3", ffmpeg=ffmpeg_path)
                segment_length = 60 * 1000
                segments = [audio[start:start + segment_length] for start in range(0, len(audio), segment_length)]

                recognizer = sr.Recognizer()
                for i, segment in enumerate(segments):
                    print(i, segment)
                    segment.export("temp.wav", format="wav")
                    with sr.AudioFile("temp.wav") as source:
                        audio_data = recognizer.record(source)
                        try:
                            Text = recognizer.recognize_google(audio_data)
                            text += Text
                            print(f"Segment {i+1}: Recognized text:", text)
                        except sr.UnknownValueError:
                            print(f"Segment {i+1}: Speech recognition could not understand the audio")
                        except sr.RequestError as e:
                            print(f"Segment {i+1}: Could not request results; {e}")
        
        print('recognised text')
        print(text)
        print('\n')
        if text.strip():
            gemini_response = chat.send_message('summerization for '+text+' in a paragraph')
            sumary = gemini_response.text
            print('sumerization')
            print(sumary)
            print('\n')

            connection = sqlite3.connect('database.db')
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Youtube VALUES (NULL, ?, ?)", (text, sumary))
            connection.commit()

            text_kn = language_translate(text, 'kn')
            sumary_kn = language_translate(sumary, 'kn')

            text_hi = language_translate(text, 'hi')
            sumary_hi = language_translate(sumary, 'hi')

            return render_template('youtube.html', text=text, sumary=sumary, text_kn=text_kn, sumary_kn=sumary_kn, text_hi=text_hi, sumary_hi=sumary_hi, in_wordcount = len(text.split(' ')), out_wordcount = len(sumary.split(' ')))
        else:
            return render_template('youtube.html', msg='text not recognised in audio')
    return render_template('youtube.html')

@app.route('/audio', methods=['GET', 'POST'])
def audio():
    if request.method == 'POST':
        file = request.form['file']
        print(file)
        text = ''
        ffmpeg_path = "C:/ffmpeg/bin/ffmpeg.exe"
        audio = AudioSegment.from_file('static/audio/'+file, format="mp3", ffmpeg=ffmpeg_path)
        segment_length = 60 * 1000
        segments = [audio[start:start + segment_length] for start in range(0, len(audio), segment_length)]

        recognizer = sr.Recognizer()
        for i, segment in enumerate(segments):
            print(i, segment)
            segment.export("temp.wav", format="wav")
            with sr.AudioFile("temp.wav") as source:
                audio_data = recognizer.record(source)
                try:
                    Text = recognizer.recognize_google(audio_data)
                    text += Text
                    print(f"Segment {i+1}: Recognized text:", text)
                except sr.UnknownValueError:
                    print(f"Segment {i+1}: Speech recognition could not understand the audio")
                except sr.RequestError as e:
                    print(f"Segment {i+1}: Could not request results; {e}")

        print('recognised text')
        print(text)
        print('\n')
        if text.strip():
            gemini_response = chat.send_message('summerization for '+text+' in a paragraph')
            sumary = gemini_response.text
            print('sumerization')
            print(sumary)
            print('\n')

            connection = sqlite3.connect('database.db')
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Audio VALUES (NULL, ?, ?)", (text, sumary))
            connection.commit()

            text_kn = language_translate(text, 'kn')
            sumary_kn = language_translate(sumary, 'kn')

            text_hi = language_translate(text, 'hi')
            sumary_hi = language_translate(sumary, 'hi')

            return render_template('audio.html', audio_url="http://127.0.0.1:5000/static/audio/"+file, text=text, sumary=sumary, text_kn=text_kn, sumary_kn=sumary_kn, text_hi=text_hi, sumary_hi=sumary_hi, in_wordcount = len(text.split(' ')), out_wordcount = len(sumary.split(' ')))
        else:
            return render_template('audio.html', msg='text not recognised in audio')

    return render_template('audio.html')

@app.route('/video', methods=['GET', 'POST'])
def video():
    if request.method == 'POST':
        file = request.form['file']
        print(file)
        directory = 'static/video'
        video = moviepy.editor.VideoFileClip(os.path.join(directory, file))
        audio = video.audio
        file1 = file.replace('.mp4', '.mp3')
        mp3_file = os.path.join(directory, file1)
        audio.write_audiofile(mp3_file)
        shutil.copy(mp3_file, 'static/audio')

        text = ''
        ffmpeg_path = "C:/ffmpeg/bin/ffmpeg.exe"
        audio = AudioSegment.from_file(mp3_file, format="mp3", ffmpeg=ffmpeg_path)
        segment_length = 60 * 1000
        segments = [audio[start:start + segment_length] for start in range(0, len(audio), segment_length)]

        recognizer = sr.Recognizer()
        for i, segment in enumerate(segments):
            print(i, segment)
            segment.export("temp.wav", format="wav")
            with sr.AudioFile("temp.wav") as source:
                audio_data = recognizer.record(source)
                try:
                    Text = recognizer.recognize_google(audio_data)
                    text += Text
                    print(f"Segment {i+1}: Recognized text:", text)
                except sr.UnknownValueError:
                    print(f"Segment {i+1}: Speech recognition could not understand the audio")
                except sr.RequestError as e:
                    print(f"Segment {i+1}: Could not request results; {e}")

        print('recognised text')
        print(text)
        print('\n')
        if text.strip():
            gemini_response = chat.send_message('summerization for '+text+' in a paragraph')
            sumary = gemini_response.text
            print('sumerization')
            print(sumary)
            print('\n')

            connection = sqlite3.connect('database.db')
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Video VALUES (NULL, ?, ?)", (text, sumary))
            connection.commit()

            text_kn = language_translate(text, 'kn')
            sumary_kn = language_translate(sumary, 'kn')

            text_hi = language_translate(text, 'hi')
            sumary_hi = language_translate(sumary, 'hi')

            return render_template('video.html', video_url="http://127.0.0.1:5000/static/video/"+file,  text=text, sumary=sumary, text_kn=text_kn, sumary_kn=sumary_kn, text_hi=text_hi, sumary_hi=sumary_hi, in_wordcount = len(text.split(' ')), out_wordcount = len(sumary.split(' ')))
        else:
            return render_template('video.html', msg='text not recognised in audio')

    return render_template('video.html')

@app.route('/pdf', methods=['GET', 'POST'])
def pdf():
    if request.method == 'POST':
        file = request.form['file']
        print(file)
        
        reader = PdfReader('static/pdf/'+file) 
        page = reader.pages[0]
        text = page.extract_text()
        print('recognised text')
        print(text)
        print('\n')
        
        if text.strip():
            gemini_response = chat.send_message('summerization for '+text+' in a paragraph')
            sumary = gemini_response.text
            print('sumerization')
            print(sumary)
            print('\n')

            connection = sqlite3.connect('database.db')
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Pdf VALUES (NULL, ?, ?)", (text, sumary))
            connection.commit()

            text_kn = language_translate(text, 'kn')
            sumary_kn = language_translate(sumary, 'kn')

            text_hi = language_translate(text, 'hi')
            sumary_hi = language_translate(sumary, 'hi')

            return render_template('pdf.html', pdf_url="http://127.0.0.1:5000/static/pdf/"+file, text=text, sumary=sumary, text_kn=text_kn, sumary_kn=sumary_kn, text_hi=text_hi, sumary_hi=sumary_hi,  in_wordcount = len(text.split(' ')), out_wordcount = len(sumary.split(' ')))
        else:
            return render_template('pdf.html', msg='text not recognised in pdf')
    return render_template('pdf.html')

@app.route('/textsummary', methods=['GET', 'POST'])
def textsummary():
    if request.method == 'POST':
        text = request.form['Text']
        print('recognised text')
        print(text)
        print('\n')

        gemini_response = chat.send_message('summerization for '+text+' in a paragraph')
        sumary = gemini_response.text
        print('sumerization')
        print(sumary)
        print('\n')

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Text VALUES (NULL, ?, ?)", (text, sumary))
        connection.commit()

        text_kn = language_translate(text, 'kn')
        sumary_kn = language_translate(sumary, 'kn')

        text_hi = language_translate(text, 'hi')
        sumary_hi = language_translate(sumary, 'hi')

        return render_template('text.html', text=text, sumary=sumary, text_kn=text_kn, sumary_kn=sumary_kn, text_hi=text_hi, sumary_hi=sumary_hi,  in_wordcount = len(text.split(' ')), out_wordcount = len(sumary.split(' ')))
    return render_template('text.html')

@app.route('/logout')
def logout():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
