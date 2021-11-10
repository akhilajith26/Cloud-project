from flask import Flask, redirect, url_for, request, render_template
import six
from google.cloud import translate_v2 as translate
import google.cloud.texttospeech as tts

import os

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = r"C:\Users\hp\Downloads\qwiklabs-gcp-01-be1eece9e9b1-b49682b3e8de.json"
app = Flask(__name__)


def ttranslate(target, text):
    translate_client = translate.Client()
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    result = translate_client.translate(text, target_language=target)
    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))
    print("Detected Source language: {}".format(result["detectedSourceLanguage"]))
    return result["translatedText"]


def text_to_wav(voice_name: str, text: str):
    language_code = "_".join(voice_name.split("_")[:2])
    text_input = tts.SynthesisInput(text=text)
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)
    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input, voice=voice_params, audio_config=audio_config
    )

    filename = f"{language_code}.wav"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
        print(f'Generated speech saved to "{filename}"')


@app.route("/success/<name>")
def success(name):
    return "welcome %s" % name


@app.route("/")
@app.route("/translated_text", methods=["GET", "POST"])
def translate_text():
    if request.method == "POST" and "to_translate" in request.form:
        to_translate = request.form["to_translate"]
        result = ttranslate("hi", to_translate)
        return render_template("home.html", translated_op=result)
    return render_template("home.html")


@app.route("/texttospeech", methods=["GET", "POST"])
def text_to_speech():
    if request.method == "POST" and "to_speech" in request.form:
        to_speech = request.form["to_speech"]
        text_to_wav("en-AU-Wavenet-A", to_speech)
    return render_template("home.html")


def dummy_translate(text):
    return text


if __name__ == "__main__":
    app.run(debug=True)
