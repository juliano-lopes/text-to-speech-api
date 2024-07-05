from pydantic import BaseModel, Field

class SpeechRequestSchema(BaseModel):
    """ Define como um texto para audio será representado
    """
    original_language: str = Field("pt-BR", description="Idioma da transcrição")
    target_language: str = Field("en-US", description="Idioma da tradução da transcrição, o mesmo que será utilizado para conversão do texto para audio.")
    #transcription: str = Field('{"transcripted_phrases":[{"time":"0:00","original_phrase":" Olá, eu sou o Juliano Lopes e eu vou fazer a apresentação da aplicação Dub Vídeos, que a ideia é dublar um vídeo. ","translated_phrase":" Hello, I am Juliano Lopes and I am going to present the Dub Videos application, which aims to dub a video."},{"time":"0:08","original_phrase":" Então, se o usuário precisa de fazer a dublagem de um vídeo, ele tem um áudio ali que tá em outro idioma, por exemplo, inglês, e esse usuário precisa assistir o vídeo, entender o conteúdo, ou aquele áudio em português. ","translated_phrase":" So, if the user needs to dub a video, he has an audio there that is in another language, for example, English, and this user needs to watch the video, understand the content, or that audio in Portuguese."},{"time":"0:20","original_phrase":" Então, basicamente, a Dub Vídeos pega esse vídeo, faz a dublagem dele de forma automatizada e traz um novo vídeo gerado, porém, no idioma especificado pelo usuário. ","translated_phrase":" So, basically, Dub Videos takes this video, dubs it automatically and brings a new generated video, but in the language specified by the user."}]}', description="Uma transcrição")
    transcription: str = Field('', description="Uma transcrição")


class SpeechUriSchema(BaseModel):
    blob_name: str = Field("", description="Nome do recurso de audio armazenado no GCP")