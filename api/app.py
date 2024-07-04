from model.audio_converter import AudioConverter
from service.authentication import Authentication
from config.config import Config
from service.speech_service import SpeechService
from schemas.error import ErrorSchema
from schemas.speech import SpeechRequestSchema, SpeechUriSchema
from util import Util
from flask_openapi3 import OpenAPI, Info, Tag
from flask import json, redirect

from logger import logger
from flask_cors import CORS

info = Info(title="Api to generate audio converting text to speech", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app, origins=['*'])

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
speech_tag = Tag(name="Texto para audio", description="Geração de áudio por meio da conversão de texto para fala")

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/speech/', tags=[speech_tag],
          responses={"200": SpeechUriSchema, "400": ErrorSchema})
async def text_to_speech(form: SpeechRequestSchema):
    """
    realiza a converção da transcrição para audio
    Retorna o nome do arquivo do audio armazenado no gcp:
    """
    
    logger.debug(f"convertendo texto para audio : idioma de origem: {form.original_language}, idioma destino: {form.target_language}'")
    try:
        transcription = json.loads(form.transcription)
        print(f"frase: {transcription['transcripted_phrases'][0]['original_phrase']}")
        #print(transcription)
        auth = Authentication(Config.credential_key, Config.bucket_name)
        dubbing_service = SpeechService(auth, transcription, form.original_language, form.target_language)
        blob_name = dubbing_service.make_dubbing()
        print(f"o nome do recurso foi: {blob_name}")
        return {"blob_name":blob_name}
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = f"Não foi possível gerar o audio ():\n{e}"
        logger.warning(f"Erro ao gerar audio do texto . {error_msg}")
        return {"message": error_msg}, 400
