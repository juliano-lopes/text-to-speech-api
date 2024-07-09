import json
import math
import os
import shutil
from google.cloud import texttospeech

from model.audio_converter import AudioConverter

from service.authentication import Authentication
from util import Util

class SpeechService:
    def __init__(self, auth: Authentication, transcription, transcript_language: str, translate_language: str):
        self.auth = auth
        self.transcription= transcription
        self.transcript_language = transcript_language
        self.translate_language = translate_language
        

    def upload_blob(self, file):
        file_name = file
        file_name = file.split("/").pop()
        blob = self.auth.get_bucket().blob(file_name)
        blob.upload_from_filename(file)
        #gcs_uri = f"gs://{self.auth.get_bucket_name()}/{file_name}"
        return file_name

    def delete_blob(self, nome_blob):
        blob = self.auth.get_bucket().blob(nome_blob)
        blob.delete()

    def synthesize_ssml(self, ssml, file_output, voice_timbre):
        languages = {
            "pt-BR":{"language_code":"pt-BR", "name":{"m":"pt-BR-Wavenet-B", "f":"pt-BR-Wavenet-C"}, "ssml_gender":{"m":texttospeech.SsmlVoiceGender.MALE, "f":texttospeech.SsmlVoiceGender.FEMALE}},
            "en-US":{"language_code":"en-US", "name":{"m":"en-US-Studio-Q", "f":"en-US-Wavenet-H"}, "ssml_gender":{"m":texttospeech.SsmlVoiceGender.MALE, "f":texttospeech.SsmlVoiceGender.MALE}},
        }

        """Synthesizes speech from the input string of ssml.

        Note: ssml must be well-formed according to:
            https://www.w3.org/TR/speech-synthesis/

        Example: <speak>Hello there.</speak>
        """

        input_text = texttospeech.SynthesisInput(ssml=ssml)

        # Note: the voice can also be specified by name.
        # Names of voices can be retrieved with client.list_voices().
        language = languages[self.translate_language]
        voice = texttospeech.VoiceSelectionParams(
            language_code=language["language_code"],
            name=language["name"][voice_timbre],
            ssml_gender=language["ssml_gender"][voice_timbre],
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = self.auth.tts_client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        with open(file_output, "wb") as out:
            out.write(response.audio_content)
            print(f"Audio content written to file {file_output}")
            return file_output

    def make_dubbing(self):
        path = Util.get_paths()["random_name"]
        Util.make_dirs(path)
        destination = Util.get_paths(path)['destination']
        final_destination = Util.get_paths(path)['final_destination']
        print(f"destination: {destination}\nfinal_destination: {final_destination}")
        translation = self.transcription["transcripted_phrases"]
        print("pós translation")
        with open(f"{final_destination}/transcript-translation.txt", "+w", encoding="utf-8") as f:
            f .write(json.dumps(translation))

        total_time = 0
        final_audio = None
        default_speed = 126
        max_speed = 136
        speed = default_speed

        for line in translation:
            time = 0
            if line == "":
                continue
            else:
                frase = line["translated_phrase"]
                voice_timbre = line["voice_timbre"]
                if voice_timbre == "i": # i is iqual undefined
                    voice_timbre = "m" # it is set to male timbre
                print("voice_timbre foi ", voice_timbre)
                time = int(Util.timestamp_to_seconds(line["time"]))

            if total_time == 0:
                # início
                if time > 0:
                    # criar silencio inicial:
                    #silence = f"<break time='{time + 1}s'/>"
                    silence = f"<break time='{time}s'/>"

                    audio = self.synthesize_ssml(f"<speak>{silence}<prosody rate='{speed}%'>{frase}</prosody></speak>",f"{destination}/{time}-audio_speed_{speed}.wav", voice_timbre)
                    audio = AudioConverter(audio,f"{destination}/{time}-audio_mono", "wav")
                    audio = audio.convert()
                    final_audio = audio
                else:
                    audio = self.synthesize_ssml(f"<speak><prosody rate='{speed}%'>{frase}</prosody></speak>",f"{destination}/{time}-audio_speed_{speed}.wav", voice_timbre)
                    audio = AudioConverter(audio,f"{destination}/{time}-audio_mono", "wav")
                    audio = audio.convert()
                    final_audio = audio

            else:
                #da segunda vez para frente:
                if (time - total_time) > 0:
                    speed = default_speed
                    #silence = f"<break time='{(time - total_time) + 1}s'/>"
                    silence = f"<break time='{(time - total_time)}s'/>"
                    audio = self.synthesize_ssml(f"<speak>{silence}<prosody rate='{speed}%'>{frase}</prosody></speak>",f"{destination}/{time}-audio_speed_{speed}.wav", voice_timbre)
                    audio = AudioConverter(audio, f"{destination}/{time}-audio_mono", "wav")
                    audio = audio.convert()
                    final_audio = AudioConverter.join_audios(final_audio, audio, f"{destination}/joined-final-{time}.wav")
                elif (total_time - time) > 0:
                    diff = total_time - time
                    diff_percent = math.floor((diff * 100) / time)
                    new_speed = math.floor(speed * (1 + diff_percent / 100))
                    if new_speed <= max_speed:
                        speed = new_speed
                    else:
                        speed = max_speed
                    audio = self.synthesize_ssml(f"<speak><prosody rate='{speed}%'>{frase}</prosody></speak>",f"{destination}/{time}-audio_speed_{new_speed}.wav", voice_timbre)
                    audio = AudioConverter(audio, f"{destination}/{time}-audio_mono", "wav")
                    audio = audio.convert()
                    final_audio = AudioConverter.join_audios(final_audio, audio, f"{destination}/joined-final-{time}.wav")

                else:
                    audio = self.synthesize_ssml(f"<speak><prosody rate='{speed}%'>{frase}</prosody></speak>",f"{destination}/{time}-audio_speed_{speed}.wav", voice_timbre)
                    audio = AudioConverter(audio, f"{destination}/{time}-audio_mono", "wav")
                    audio = audio.convert()
                    final_audio = AudioConverter.join_audios(final_audio, audio, f"{destination}/joined-final-{time}.wav")

            audio = AudioConverter(final_audio,f"{destination}", "wav")
            total_time = audio.get_duration()

        file_final_destination = f"{final_destination}/speech_audio_final_{Util.get_paths(path)['name']}.wav"

        shutil.copyfile(final_audio, file_final_destination)
        shutil.rmtree(destination)
        blob_name = self.upload_blob(file_final_destination)
        return blob_name
