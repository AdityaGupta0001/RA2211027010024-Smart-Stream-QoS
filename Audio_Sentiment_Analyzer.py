import speech_recognition as sr
from transformers import pipeline
import threading
import queue
import time

MICROPHONE_INDEX = None 

recognizer = sr.Recognizer()
try:
    microphone = sr.Microphone(device_index=MICROPHONE_INDEX)
    print(f"Using microphone: {microphone.list_microphone_names()[MICROPHONE_INDEX if MICROPHONE_INDEX is not None else 0]}" )
except (OSError, IndexError, Exception) as e:
    print(f"Error initializing microphone: {e}")
    print("Please ensure a microphone is connected and the index (if specified) is correct.")
    print("Available microphones:", sr.Microphone.list_microphone_names())
    exit()

try:
    text_sentiment_analyzer = pipeline('sentiment-analysis')
    print("Text sentiment analyzer loaded successfully.")
except Exception as e:
    print(f"Error loading text sentiment analyzer: {e}")
    print("Please ensure 'transformers' and 'torch' or 'tensorflow' are installed.")
    text_sentiment_analyzer = None

results_queue = queue.Queue()

def audio_processing_thread(q):
    """Captures audio, performs STT, and text sentiment analysis."""
    global recognizer, microphone, text_sentiment_analyzer
    
    with microphone as source:
        print("Adjusting for ambient noise... please wait.")
        try:
           recognizer.adjust_for_ambient_noise(source, duration=1)
           print("Ambient noise adjustment complete.")
        except Exception as e:
           print(f"Could not adjust for ambient noise: {e}. Proceeding anyway.")
           
    while True:
        print("\nListening for speech...")
        audio = None
        try:
            with microphone as source:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10) 
            
            if audio:
                print("Audio captured, processing text...")
                try:
                    text = recognizer.recognize_google(audio)
                    print(f"Speech-to-Text: \"{text}\"")
                    
                    if text_sentiment_analyzer:
                        sentiment_result = text_sentiment_analyzer(text)[0]
                        text_sentiment = sentiment_result['label']
                        text_score = sentiment_result['score']
                        q.put({"type": "audio", "text": text, "sentiment": text_sentiment, "score": text_score})
                    else:
                         print("Sentiment analyzer not available.")
                         q.put({"type": "audio", "text": text, "sentiment": "N/A", "score": 0.0})

                except sr.UnknownValueError:
                    print("STT Error: Google Speech Recognition could not understand audio")
                    q.put({"type": "audio", "text": None, "sentiment": "UNKNOWN_AUDIO", "score": 0.0})
                except sr.RequestError as e:
                    print(f"STT Error: Could not request results from Google Speech Recognition service; {e}")
                    q.put({"type": "audio", "text": None, "sentiment": "STT_API_ERROR", "score": 0.0})
            else:
                 print("No audio data received from listen().")
                 q.put({"type": "audio", "text": None, "sentiment": "NO_AUDIO_DATA", "score": 0.0})


        except sr.WaitTimeoutError:
            pass 
        except Exception as e:
            print(f"An unexpected error occurred in audio thread: {e}")
            q.put({"type": "audio", "text": None, "sentiment": "AUDIO_THREAD_ERROR", "score": 0.0})
            time.sleep(1)

if __name__ == "__main__":
    if not text_sentiment_analyzer:
        print("Cannot proceed without a functional sentiment analyzer.")
        exit()
        
    print("Starting audio processing thread...")

    audio_thread = threading.Thread(target=audio_processing_thread, args=(results_queue,), daemon=True)
    audio_thread.start()
    
    print("\n--- Real-time Speech Sentiment Analysis ---")
    print("(Press Ctrl+C to stop)")

    try:
        while True:
            try:
                result = results_queue.get(timeout=60)
                
                if result['type'] == 'audio':
                    if result['text']:
                        print(f"----> Sentiment: {result['sentiment']} (Score: {result['score']:.3f}) | Text: '{result['text']}'")
                    else:
                        print(f"----> Status: {result['sentiment']}") 
            except queue.Empty:
                pass
            except KeyboardInterrupt:
                 print("\nStopping...")
                 break
            except Exception as e:
                 print(f"Error processing queue item in main loop: {e}")


    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        print("Program terminated.")
