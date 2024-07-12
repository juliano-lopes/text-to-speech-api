# API para aplicação DubVideos
* [Front-end Dub Videos](https://github.com/juliano-lopes/dub-videos-front-end)
## Como utilizar
Essa API tem como objetivo converter um texto em áudio. Para isso são utilizadas algumas API da Google:
* google-auth para autenticação no Google Cloud;
* google-cloud-storage para armazenamento de arquivos;
* google-cloud-texttospeech para gerar áudio por meio de texto.
### Passos para utilização:
* Faça o clone ou baixe o projeto:  
**git clone https://github.com/juliano-lopes/text-to-speech-api.git**  
* Entre na pasta do projeto:  
**cd text-to-speech-api**
* Insira o arquivo com a chave de serviço no caminho:  
**api/config/**
* Será necessário instalar o docker para executar a aplicação em um container.
* Na raiz do projeto, Crie a imagem por meio do Dockerfile:  
**docker build -t dub_videos_speech .**  
* Após criar a imagem, execute o comando:  
**docker run -it -p 5002:5002 dub_videos_speech**  
* A aplicação estará disponível pela porta local 5002
* Abra o endereço:  
http://localhost:5002   
no navegador.  

 ## Como testar
* Acesse a URL http://localhost:5002 e escolha a documentação (Swagger). Após isso execute as rotas com os valores padrão de exemplo.

## Apresentação da Aplicação
* [Assista a o vídeo de aprensentação da aplicação Dub Videos](https://youtu.be/tfAVGTcRtCA)