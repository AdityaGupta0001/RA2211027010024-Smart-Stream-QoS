import numpy as np
import pandas as pd
from transformers import pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import speech_recognition as sr
import threading
import queue

def load_qoe_dataset():
    """Load 5G video streaming QoE dataset from SIGCOMM24 repository"""
    try:
        # Use dataset from SIGCOMM24-5GinMidBands artifacts [3]
        # Note: Replace with actual dataset path from the repository
        # Temporary sample dataset based on paper description
        data = {
            'RSRP': np.random.uniform(-120, -80, 100),
            'RSRQ': np.random.uniform(-20, -5, 100),
            'SNR': np.random.uniform(1, 20, 100),
            'quality': np.random.randint(0, 2, 100)
        }
        return pd.DataFrame(data)
    
    except Exception as e:
        print(f"Dataset loading error: {e}")
        print("Please download the dataset from:")
        print("https://github.com/SIGCOMM24-5GinMidBands/artifacts")
        exit()

# --------------------------
# 2. Hybrid Sentiment-QoS Model
# --------------------------
class QoSManager:
    def __init__(self):
        self.sentiment_analyzer = pipeline(
            'sentiment-analysis',
            model='distilbert/distilbert-base-uncased-finetuned-sst-2-english'
        )
        self.qoe_model = self.train_qoe_model()
        self.quality_threshold = 0.77

    def train_qoe_model(self):
        """Train Random Forest classifier using 5G dataset"""
        try:
            df = load_qoe_dataset()
            X = df[['RSRP', 'RSRQ', 'SNR']]
            y = df['quality']
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            model = RandomForestClassifier(n_estimators=100)
            model.fit(X_train, y_train)
            return model
            
        except Exception as e:
            print(f"Model training error: {e}")
            exit()

    # ADD THIS MISSING METHOD
    def predict_quality(self, rsrp, rsrq, snr):
        """Predict video quality (0=Low, 1=High) using channel metrics"""
        return self.qoe_model.predict([[rsrp, rsrq, snr]])[0]

    def analyze_feedback(self, text):
        """BERT-based sentiment analysis"""
        result = self.sentiment_analyzer(text[:512])[0]
        return result['label'], result['score']
# --------------------------
# 3. Real-time Processing (From [4])
# --------------------------
class StreamProcessor:
    def __init__(self):
        self.qos_manager = QoSManager()
        self.input_queue = queue.Queue()
        
    def voice_listener(self):
        """Speech-to-text conversion thread"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            while True:
                audio = r.listen(source)
                try:
                    text = r.recognize_google(audio)
                    self.input_queue.put(('voice', text))
                except Exception as e:
                    print(f"Audio error: {e}")

    def text_listener(self):
        """Console text input thread"""
        while True:
            text = input("Enter feedback: ")
            self.input_queue.put(('text', text))

    def qos_adjustment(self, prediction, sentiment):
        """Adaptive QoS logic (From [4] and [5])"""
        if prediction == 0 or sentiment == 'NEGATIVE':
            return "Lower bitrate (720p)"
        return "Maintain HD (1080p+)"

    def start_processing(self):
        """Main processing loop"""
        # Start input threads
        threading.Thread(target=self.voice_listener, daemon=True).start()
        threading.Thread(target=self.text_listener, daemon=True).start()

        print("Real-time QoS Management System")
        print("--------------------------------")
        print("Modulation options based on:")
        print("- Network metrics (RSRP/RSRQ/SNR)")
        print("- User sentiment analysis")
        
        while True:
            input_type, content = self.input_queue.get()
            
            # Simulated network metrics (replace with real data feed)
            current_metrics = {
                'RSRP': np.random.uniform(-120, -80),
                'RSRQ': np.random.uniform(-20, -5),
                'SNR': np.random.uniform(1, 20)
            }
            
            # Get predictions
            quality_pred = self.qos_manager.predict_quality(
                current_metrics['RSRP'],
                current_metrics['RSRQ'],
                current_metrics['SNR']
            )
            sentiment, confidence = self.qos_manager.analyze_feedback(content)
            
            # Make adjustment decision
            action = self.qos_adjustment(quality_pred, sentiment)
            
            print(f"\nNetwork: {current_metrics}")
            print(f"Feedback ({input_type}): {content}")
            print(f"QoE Prediction: {'High Quality' if quality_pred else 'Needs Adjustment'}")
            print(f"Sentiment: {sentiment} ({confidence:.2%})")
            print(f"Action: {action}")

# --------------------------
# Execution
# --------------------------
if __name__ == "__main__":
    processor = StreamProcessor()
    processor.start_processing()
