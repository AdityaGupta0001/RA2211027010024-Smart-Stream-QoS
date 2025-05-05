# Real-Time Speech Sentiment Analysis for Streaming Feedback

## Overview

This Python script demonstrates a component of a data-driven solution aimed at enhancing Quality of Service (QoS) for live video game streaming platforms. It focuses specifically on capturing user feedback through speech, converting it to text, and analyzing the sentiment expressed in near real-time.

This serves as a practical implementation of the sentiment analysis aspect discussed in the initial problem description, using live audio input as a proxy for user comments or voice chat interactions that might occur during a stream.

## Problem Context

Live streaming platforms (e.g., Twitch, YouTube Gaming) face challenges in maintaining consistent QoS due to network volatility, variable stream quality, and fluctuating viewer engagement. Traditional methods struggle to adapt dynamically. The initial request highlighted the need for a data-driven approach using:

1.  Big data analytics for network/stream metrics.
2.  Deep Neural Networks (DNNs) for satisfaction classification (QoE prediction).
3.  **BERT-based sentiment analysis** to interpret user sentiment and engagement from text (like chat messages).

## How This Script Contributes

This script directly addresses the **sentiment analysis component** mentioned above. While the original context might imply analyzing text chat, this script uses live speech input to:

1.  **Capture User Feedback:** Simulates capturing user input via the microphone.
2.  **Convert to Text:** Uses Speech-to-Text (STT) technology, analogous to processing text comments.
3.  **Analyze Sentiment:** Employs a pre-trained BERT model (via Hugging Face `transformers`) to determine if the spoken text expresses positive, negative, or neutral sentiment.

The output (sentiment label and score) could conceptually be fed into a larger QoS management system to help gauge viewer satisfaction in real-time, alongside other metrics like network conditions or viewer counts.

## Features

*   **Real-time Audio Capture:** Listens to the default system microphone.
*   **Speech-to-Text (STT):** Uses the `SpeechRecognition` library (leveraging the Google Web Speech API by default) to transcribe spoken words.
*   **Sentiment Analysis:** Utilizes the Hugging Face `transformers` library with a pre-trained BERT model for sentiment classification (Positive/Negative).
*   **Console Output:** Prints the transcribed text and the corresponding sentiment analysis results.
*   **Threading:** Runs audio capture and processing in a separate thread to keep the main program responsive.

## Requirements

*   Python 3.x
*   A working microphone connected to the system.
*   Internet connection (for the default Google Web Speech STT API).
*   Python Libraries:
    *   `SpeechRecognition`
    *   `PyAudio` (May require specific installation steps depending on your OS - consult its documentation if you encounter issues)
    *   `transformers` (Hugging Face)
    *   `torch` (PyTorch) or `tensorflow` (TensorFlow) - required by `transformers`.

## Installation

Install the required libraries using pip:

```
pip install SpeechRecognition PyAudio transformers torch

# or if you prefer TensorFlow:

pip install SpeechRecognition PyAudio transformers tensorflow
```


*(Note: Installing PyAudio can sometimes be tricky. Refer to the official [PyAudio documentation](https://people.csail.mit.edu/hubert/pyaudio/) or search for OS-specific installation guides if needed.)*

## Usage

1.  Save the Python code to a file (e.g., `audio_sentiment.py`).
2.  Run the script from your terminal:
    ```
    python audio_sentiment_analyzer.py
    ```
3.  The script will first try to adjust for ambient noise (remain quiet for a second).
4.  It will then print "Listening for speech...".
5.  Speak clearly into your microphone. The script listens in chunks (up to ~10 seconds per phrase, with silence detection).
6.  After you stop speaking (or the time limit is reached), it will process the audio:
    *   Print the transcribed text ("Speech-to-Text: ...").
    *   Print the detected sentiment and confidence score ("----> Sentiment: ...").
7.  The script will continue listening in a loop.
8.  Press `Ctrl+C` to stop the script.

## How It Works

1.  **Initialization:** Sets up the `SpeechRecognizer`, `Microphone`, and loads the `sentiment-analysis` pipeline from Hugging Face `transformers`.
2.  **Audio Thread:** A separate thread (`audio_processing_thread`) is started to handle audio input without blocking the main program.
3.  **Listening:** The thread uses `recognizer.listen()` to capture audio from the microphone source. It adjusts for ambient noise initially.
4.  **Speech-to-Text:** The captured audio data is sent to `recognizer.recognize_google()` which uses Google's online service to return the transcribed text.
5.  **Sentiment Analysis:** If text is successfully transcribed, it's passed to the `text_sentiment_analyzer` pipeline. This pipeline runs the text through a pre-trained BERT model fine-tuned for sentiment classification.
6.  **Queueing Results:** The transcribed text, sentiment label (POSITIVE/NEGATIVE), and score are put into a `queue`.
7.  **Main Thread:** The main part of the script waits for results to appear in the queue and prints them to the console.

## Limitations

*   **Audio Input Only:** This script *only* processes audio sentiment. It does not include the video analysis component from earlier iterations.
*   **Proxy for Chat:** Uses speech as a proxy for user feedback. Integrating with actual chat APIs (Twitch/YouTube) would be needed for a real-world application analyzing viewer comments.
*   **STT Dependency:** Relies on the Google Web Speech API by default, requiring an internet connection and subject to potential rate limits or API changes. Offline STT engines could be integrated with `SpeechRecognition` but require separate setup.
*   **Generic Sentiment Model:** Uses a general-purpose sentiment model. For specific domains like gaming, fine-tuning a model on relevant slang and context might improve accuracy.
*   **No QoS Integration:** This script only performs sentiment analysis. It does not connect to any network monitoring tools or implement any QoS adjustment logic. It's a standalone demonstration of the sentiment analysis part.
