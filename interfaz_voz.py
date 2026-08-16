import tkinter as tk
import threading
import speech_recognition as sr
import difflib
import win32com.client

speaker = win32com.client.Dispatch("SAPI.SpVoice")
voces = speaker.GetVoices()
speaker.Voice = voces.Item(2) 
speaker.Rate = -1

MODELO_WHISPER = "small"
IDIOMA = "spanish"

def hablar(texto):
    print(texto)
    speaker.Speak(texto)

def limpiar_texto(texto):
    texto = texto.lower().strip()
    signos_a_quitar = [".", ",", "!", "?", "¿", "¡", " "]
    for signo in signos_a_quitar:
        texto = texto.replace(signo, "")
    return texto

def rutina_evaluacion(palabra_objetivo):
    btn_iniciar.config(state=tk.DISABLED)
    
    lbl_estado.config(text="Ajustando micrófono...", fg="blue")
    lbl_resultado.config(text="")
    
    r = sr.Recognizer()
    r.pause_threshold = 0.4  
    r.non_speaking_duration = 0.3  

    hablar("Ajustando ruido ambiente... un momento.")
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        
    lbl_estado.config(text=f"Lee en voz alta:\n{palabra_objetivo.upper()}", fg="black")
    hablar(f"Por favor lee esta palabra: {palabra_objetivo}")
    
    lbl_estado.config(text="Escuchando...", fg="red")
    with sr.Microphone() as source:
        try:
            audio = r.listen(source, phrase_time_limit=3.0)
            
            lbl_estado.config(text="⚙️ Analizando...", fg="orange")
            hablar("Analizando la pronunciación...")
            
            texto_crudo = r.recognize_whisper(audio, model=MODELO_WHISPER, language=IDIOMA)
            palabra_dicha = limpiar_texto(texto_crudo)
            
            palabra_obj_limpia = palabra_objetivo.lower()
            similitud = difflib.SequenceMatcher(None, palabra_obj_limpia, palabra_dicha).ratio()
            porcentaje = similitud * 100
            
            lbl_resultado.config(text=f"Se escuchó: '{palabra_dicha}'\nPrecisión: {porcentaje:.0f}%")
            
            if porcentaje >= 75:
                lbl_estado.config(text="¡Excelente!", fg="green")
                hablar("¡Excelente esfuerzo! Muy bien dicho, Arturo García López.")
            else:
                lbl_estado.config(text="¡Casi lo logras!", fg="orange")
                hablar("Vamos a intentarlo de nuevo.")
                
        except sr.UnknownValueError:
            lbl_estado.config(text="No escuché nada.", fg="red")
            hablar("No pude escuchar bien, intentémoslo de nuevo.")
        except Exception as e:
            lbl_estado.config(text="Ocurrió un error.", fg="red")
            print(e)
            
    btn_iniciar.config(state=tk.NORMAL)

def boton_presionado():
    palabra_a_practicar = "guitarra"
    hilo = threading.Thread(target=rutina_evaluacion, args=(palabra_a_practicar,))
    hilo.start()

ventana = tk.Tk()
ventana.title("Asistente de Lectura")
ventana.geometry("400x350")
ventana.configure(bg="#f0f8ff") 

lbl_titulo = tk.Label(ventana, text="¡Vamos a practicar!", font=("Arial", 18, "bold"), bg="#f0f8ff")
lbl_titulo.pack(pady=20)

lbl_estado = tk.Label(ventana, text="Presiona 'Iniciar' cuando estés listo.", font=("Arial", 14), bg="#f0f8ff")
lbl_estado.pack(pady=10)

lbl_resultado = tk.Label(ventana, text="", font=("Arial", 12, "italic"), bg="#f0f8ff")
lbl_resultado.pack(pady=10)

btn_iniciar = tk.Button(ventana, text="Iniciar Práctica", font=("Arial", 14), bg="#4caf50", fg="white", 
                        command=boton_presionado, padx=10, pady=5)
btn_iniciar.pack(pady=20)

ventana.mainloop()