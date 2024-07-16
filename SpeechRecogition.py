import speech_recognition as sr
from pyfirmata import Arduino, SERVO, util, PWM
from time import sleep
from word2number import w2n
import time as t
import threading
import datetime as dt

running = True
cancel_countdown = False
countdown_time = 60
notification = True

r = sr.Recognizer()
mic = sr.Microphone(device_index=1)
buzzwordsList = ["dispense", "drop", "release"]

port = 'COM4'
pin = 10
board = Arduino(port)

board.digital[pin].mode = SERVO

def rotate(pin, angle):
    board.digital[pin].write(angle)
    sleep(0.5)

board.digital[7].write(0)
board.digital[12].write(0)

def countdown():
    global running
    global cancel_countdown
    time_count = countdown_time
    while time_count:
        t.sleep(1)
        time_count -=1
        if cancel_countdown == True:
            break
        if time_count == 0:
            print("Robot powering off")
            t.sleep(1)
            running = False

def dispense():
    global cancel_countdown
    global running
    global notification
    with mic as source:
        print("Ready For Dispensing, or say 'Off' to turn me off")
        r.adjust_for_ambient_noise(source)
        while running:
            audio = r.listen(source)
            try:
                if r.recognize_google(audio) in buzzwordsList:
                    cancel_countdown = True
                    notification = False
                    print("How many pills do you need dispensed?")
                    try:
                        num_audio = r.listen(source)
                        num_txt = r.recognize_google(num_audio)
                        num_medication = int(w2n.word_to_num(num_txt))

                        if(num_medication <= 5 and num_medication > 0):
                            print("Dispensing Medication")
                            for i in range(num_medication):     
                                rotate(pin, 60)
                                t.sleep(1.5)
                                rotate(pin, 0)
                                t.sleep(1.5)
                        else:
                            print("Exceeded max/min number of medication")
                        print("Ready for dispensing, or say 'Off' to turn me off")
                    except sr.RequestError as e:
                        print(f"no audio : {e}")
                    except sr.UnknownValueError:
                        print("Could not read in your voice command, repeat again")
                    except ValueError:
                        print("Cant covert text to number")     
                elif r.recognize_google(audio) == "off":
                    print("Turning off")
                    t.sleep(1)
                    board.digital[7].write(0)
                    board.digital[12].write(0)
                    running = False
                    cancel_countdown = True
                    notification = False
            except sr.RequestError as e:
                print(f"No audio : {e}")
            except sr.UnknownValueError:
                print("Could not read in your voice command, repeat again")

def notify():
    blink_time = dt.time(16, 52)

    board.digital[7].write(0)
    board.digital[12].write(0)

    def blink_leds():
        global notification
        while notification:
            board.digital[7].write(0)
            t.sleep(1)
            board.digital[12].write(0)
            t.sleep(1)
            board.digital[7].write(1)
            t.sleep(1)
            board.digital[12].write(1)
            t.sleep(1)
        
    
    def check_time():
        global notification
        while notification:
            current_time = dt.datetime.now().time()
            time_difference = dt.datetime.combine(dt.date.today(), blink_time) - dt.datetime.combine(dt.date.today(), current_time)
            if time_difference.total_seconds() <= 0 and abs(time_difference) <= dt.timedelta(minutes=1):
                blink_leds()
            t.sleep(5)
    
    time_thread = threading.Thread(target=check_time)
    time_thread.start()
    time_thread.join()


t1 = threading.Thread(target=dispense)
t2 = threading.Thread(target=countdown)
t3 = threading.Thread(target=notify)

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()