import vosk
import pyaudio
import json

model_path = "vosk-model-small-pt-0.3"

model = vosk.Model(model_path)

#cria um objeto de reconhecimento de fala, especificando modelo e freq de amostragem
#é ele que recebe blocos de áudio e gera o texto
rec = vosk.KaldiRecognizer(
    model, 
    16000, 
    '["decolar", "pousar", "frente", "trás", "direita", "esquerda", "pare"]'    #esse parametro define a lista de palavras que ele vai reconhecer; qualquer coisa além disso, não será transcrito para texto
    )

#inicializa o áudio
p = pyaudio.PyAudio()

#abre o microfone com esses parâmetros (16 bits, mono, 16kHz)
stream = p.open(
    format=pyaudio.paInt16, #define formato do áudio, no caso é int de 16 bits com sinal (formato aceito no Vosk)
    channels=1, #define canais de áudio, Vosk espera mono
    rate=16000, #taxa de amostragem, o modelo Vosk em pt é treinado para 16kHz; outra taxa pode comprometer
    input=True, #define se a stream é entrada ou saída
    frames_per_buffer=4000  #tamanho de bloco lido a cada chamada de read(); como cada amostra tem 2 bytes (paInt16), cada bloco tem 4000*2=8000 bytes
)

#esse valor de buffer dá +/- 0.25s de áudio a 16Khz, então cada chamada de read() lê 0.25s de áudio

stream.start_stream()
print("Microfone aberto.")


#o Vosk divide o áudio em frase, baseando-se em pausas e na energia do sinal

try:
    while True:
        data = stream.read(
            4000, #lê 4000 frames do microfone (como cada frame tem 2 bytes, paInt16, data contém 8kb de áudio)
            exception_on_overflow=False #se o áudio demora demais, o pyaudio lança uma exception; aqui, evitamos que isso aconteça
            )
        if rec.AcceptWaveform(data):    #processa o áudio e retorna True se detecta um fim de uma frase; False se a frase ainda está sendo formada
            result = json.loads(rec.Result())   #o .Result() retorna o texto final da frase reconhecida; tem campos como text, result, confidence; essa linha converte a string json em dict 
            text = result.get("text", "").strip()   #pega o texto da transcrição e remove espaços extras
            if text:
                print(f"\n[Final]  {text}")
        else:
            partial = json.loads(rec.PartialResult()).get("partial", "")    #retorna resultados parciais enquanto fala
            if partial:
                print(f"[Parcial] {partial}", end="\r")
except KeyboardInterrupt:
    print("\nInterrompido pelo usuário.")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()