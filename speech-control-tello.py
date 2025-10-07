from djitellopy import Tello

import sys
import vosk
import pyaudio
import json
import threading
import queue



#======================= SETUP INICIAL DRONE =======================
tello = Tello()

try:
    tello.connect()
    if tello.get_battery() is None:
        raise Exception("Sem resposta.")
    print("Drone conectado.")
    print(f"Bateria {tello.get_battery()}%")
except Exception as e:
    print("Erro ao conectar drone.")
    sys.exit(1)


#======================= SETUP MODELO VOSK =======================
commands = {
    "decolar": ("takeoff", None),
    "decola": ("takeoff", None),
    "pousar": ("land", None),
    "pousa": ("land", None),
    "frente": ("forward", 40),
    "tras": ("back", 40),
    "trás": ("back", 40),
    "traz": ("back", 40),
    "direita": ("right", 40),
    "esquerda": ("left", 40),
    "cima": ("up", 40),
    "acima": ("up", 40),
    "baixo": ("down", 40),
    "abaixo": ("down", 40),
    "manobra trás": ("flip", "b"),
    "manobra atrás": ("flip", "b"),
    "manobra tras": ("flip", "b"),
    "manobra traz": ("flip", "b"),
    "manobra esquerda": ("flip", "l"),
    "manobra direita": ("flip", "r"),
    "manobra frente": ("flip", "f"),
    "manobra a frente": ("flip", "f"),
    "girar": ("cw", 45)
}

model_path = "vosk-model-small-pt-0.3"

model = vosk.Model(model_path)

rec = vosk.KaldiRecognizer(
    model,
    16000,
    '["decolar", "decola", "pousar", "pousa", "frente", "trás", "tras", "traz", "direita", "esquerda", "cima", "acima", "baixo", "abaixo", "manobra trás", "manobra tras", "manobra atrás", "manobra traz", "manobra esquerda", "manobra frente", "manobra a frente", "manobra direita", "girar"]'
)


#======================= SETUP MICROFONE =======================

p = pyaudio.PyAudio()

stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=1024
)

stream.start_stream()
print("Microfone aberto.")

#======================= FILA DE COMANDOS =======================
cmdq = queue.Queue()


#======================= FUNÇÃO PARA ENVIAR COMANDOS AO DRONE =======================

def send_command():
    while True:
        cmd, val = cmdq.get()
        print (f"Executando {cmd} {val if val else ''}")

        try:
            match cmd:
                case "takeoff":
                    tello.takeoff()
                case "land":
                    tello.land()
                case "forward":
                    tello.move_forward(val)
                case "back":
                    tello.move_back(val)
                case "right":
                    tello.move_right(val)
                case "left":
                    tello.move_left(val)
                case "up":
                    tello.move_up(val)
                case "down":
                    tello.move_down(val)
                case "flip":
                    if val in ["f", "l", "b", "r"]:
                        tello.flip(val)
                case "cw":
                    tello.rotate_clockwise(val)
        except Exception as e:
            print("Erro no comando: ", e)
        finally:
            cmdq.task_done()

command_proc = threading.Thread(target=send_command, daemon=True)
command_proc.start()


#======================= FUNÇÃO DE FINALIZAÇÃO =======================

def finish():
    stream.stop_stream()
    stream.close()
    p.terminate()
    if tello.is_flying():
        tello.land()
    tello.end()


#======================= FUNÇÃO DE RECONHECIMENTO E TRANSCRIÇÃO DE VOZ =======================

def speech_text():
    try:
        while True:
            data=stream.read(
                4000,
                exception_on_overflow=False
            )

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if(text):
                    print(f"\nComando: {text}")
                    if text in commands:
                        cmdq.put(commands[text])
                        print(f"Adicionando comando {commands[text]}")
                    else:
                        partial = json.loads(rec.PartialResult()).get("partial", "").strip()
                        if partial in commands:
                            cmdq.put(commands[text])
                            print(f"Adicionando comando {commands[text]}")
    except KeyboardInterrupt:
        print("Interrompido pelo usuário")
    finally:
        finish()



speech_text()