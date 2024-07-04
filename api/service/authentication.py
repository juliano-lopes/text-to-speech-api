import google.auth
from google.cloud import storage
from google.cloud import texttospeech

class Authentication:
    def __init__(self, credential_key, bucket_name):
        credentials, _ = google.auth.load_credentials_from_file(
        credential_key
        )
        self.storage_client = storage.Client(credentials=credentials)
        bucket = self.storage_client.bucket(bucket_name)
        self.bucket_name = bucket_name
        self.bucket = bucket
        self.tts_client = texttospeech.TextToSpeechClient(credentials=credentials)

    def get_bucket(self):
        return self.bucket

    def get_bucket_name(self):
        return self.bucket_name
