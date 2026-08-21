import customtkinter as ctk
import threading
import speech_recognition as sr
import difflib
import win32com.client
from PIL import Image
import sys  # <-- Importante para cerrar el programa por completo

# --- 1. CONFIGURACIÓN DE VOZ ---
speaker = win32com.client.Dispatch("SAPI.SpVoice")
voces = speaker.GetVoices()
speaker.Voice = voces.Item(3) 
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


# --- 2. LÓGICA DE EVALUACIÓN ---
def rutina_evaluacion(palabra_objetivo, etiqueta_estado, etiqueta_resultado, boton_accion):
    boton_accion.configure(state="disabled")
    
    etiqueta_estado.configure(text="Ajustando micrófono...", text_color="blue")
    etiqueta_resultado.configure(text="") 
    
    r = sr.Recognizer()
    r.pause_threshold = 0.4  
    r.non_speaking_duration = 0.3  

    hablar("Ajustando ruido ambiente... un momento.")
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        
    etiqueta_estado.configure(text=f"Lee en voz alta:\n{palabra_objetivo.upper()}", text_color="black")
    hablar(f"Por favor lee esta palabra: {palabra_objetivo}")
    
    etiqueta_estado.configure(text="Escuchando...", text_color="red")
    with sr.Microphone() as source:
        try:
            audio = r.listen(source, phrase_time_limit=3.0)
            
            etiqueta_estado.configure(text="Analizando...", text_color="orange")
            hablar("Analizando la pronunciación...")
            
            texto_crudo = r.recognize_whisper(audio, model=MODELO_WHISPER, language=IDIOMA)
            palabra_dicha = limpiar_texto(texto_crudo)
            
            palabra_obj_limpia = palabra_objetivo.lower()
            similitud = difflib.SequenceMatcher(None, palabra_obj_limpia, palabra_dicha).ratio()
            porcentaje = similitud * 100
            
            etiqueta_resultado.configure(text=f"Se escuchó: '{palabra_dicha}'\nPrecisión: {porcentaje:.0f}%")
            
            if porcentaje >= 75:
                etiqueta_estado.configure(text="¡Excelente!", text_color="green")
                hablar("¡Excelente esfuerzo! Muy bien dicho, Arturo García López.")
            else:
                etiqueta_estado.configure(text="¡Casi lo logras!", text_color="orange")
                hablar("Vamos a intentarlo de nuevo.")
                
        except sr.UnknownValueError:
            etiqueta_estado.configure(text="No escuché nada.", text_color="red")
            hablar("No pude escuchar bien, intentémoslo de nuevo.")
        except Exception as e:
            etiqueta_estado.configure(text="Ocurrió un error.", text_color="red")
            print(e)
            
    boton_accion.configure(state="normal")


# --- 3. CREACIÓN DE LA NUEVA VENTANA (MÓDULO DE HABLA) ---
def abrir_ventana_hablar():
    ventana_hablar = ctk.CTkToplevel(ventana)
    ventana_hablar.title("Práctica de Lectura")
    ventana_hablar.configure(fg_color="#eeda95")
    
    ventana_hablar.after(0, lambda: ventana_hablar.state('zoomed'))
    ventana_hablar.grab_set() 
    
    lbl_titulo_hablar = ctk.CTkLabel(ventana_hablar, text="🗣️ Módulo de Habla", font=("Bowlby One SC", 40, "bold"), text_color="#333333")
    lbl_titulo_hablar.pack(pady=(40, 20))
    
    lbl_estado_hablar = ctk.CTkLabel(ventana_hablar, text="Presiona el botón para empezar.", font=("Bowlby One SC", 25), text_color="#555555")
    lbl_estado_hablar.pack(pady=20)
    
    lbl_resultado_hablar = ctk.CTkLabel(ventana_hablar, text="", font=("Bowlby One SC", 20, "italic"), text_color="#333333")
    lbl_resultado_hablar.pack(pady=20)
    
    def arrancar_hilo():
        palabra_a_practicar = "guitarra"
        hilo = threading.Thread(target=rutina_evaluacion, args=(palabra_a_practicar, lbl_estado_hablar, lbl_resultado_hablar, btn_empezar))
        hilo.start()

    btn_empezar = ctk.CTkButton(
        ventana_hablar, 
        text="Empezar Práctica", 
        font=("Bowlby One SC", 20, "bold"), 
        height=60, 
        corner_radius=20, 
        command=arrancar_hilo,
        fg_color="#4caf50",
        hover_color="#388e3c"
    )
    btn_empezar.pack(pady=40)
    
    btn_volver = ctk.CTkButton(
        ventana_hablar, 
        text="Regresar al Menú Principal", 
        font=("Bowlby One SC", 16),
        height=40,
        fg_color="#d32f2f", 
        hover_color="#b71c1c", 
        command=ventana_hablar.destroy
    )
    btn_volver.pack(pady=10)

# Función para cerrar todo el sistema por completo
def cerrar_programa():
    ventana.destroy()
    sys.exit()


# --- 4. DISEÑO DEL MENÚ PRINCIPAL ---
ventana = ctk.CTk()
ventana.title("Asistente de Lectura - Menú Principal")
ventana.configure(fg_color="#ffffff")
ventana.after(0, lambda: ventana.state('zoomed'))

# Manejo de error por si el archivo de cursor no está en la ruta exacta
try:
    ventana.configure(cursor="@cursor/xxl/xxlblue.cur")
except:
    pass

lbl_titulo = ctk.CTkLabel(
    ventana, 
    text="¡Bienvenido a \nAprender!", 
    font=("Bowlby One SC", 80, "bold"), 
    text_color="#000000",
    fg_color="transparent"
)
lbl_titulo.pack(pady=(100, 60))

# CAMBIO: Reemplazamos el Label por un CTkButton posicionado en la esquina superior izquierda
btn_salir = ctk.CTkButton(
    ventana, 
    text="⬅️ ¡Salir!", 
    font=("Bowlby One SC", 50, "bold"), 
    text_color="#1A17AD",
    fg_color="transparent",
    hover_color="#f0f0f0",
    command=cerrar_programa # Cierra la app por completo
)
btn_salir.place(x=20, y=20)

marco_botones = ctk.CTkFrame(ventana, fg_color="transparent")
marco_botones.pack(pady=20)

imagen_hablar = ctk.CTkImage(
    light_image=Image.open("imagenes/hablar2.png"), 
    dark_image=Image.open("imagenes/hablar2.png"), 
    size=(200, 250) 
)

imagen_cosas = ctk.CTkImage(
    light_image=Image.open("imagenes/cosas.png"), 
    dark_image=Image.open("imagenes/cosas.png"), 
    size=(200, 250) 
)

imagen_procesos = ctk.CTkImage(
    light_image=Image.open("imagenes/procesos2.png"), 
    dark_image=Image.open("imagenes/procesos2.png"), 
    size=(200, 250) 
)

btn_iniciar = ctk.CTkButton(
    marco_botones, 
    text="", 
    image=imagen_hablar, 
    width=200, 
    height=250,  
    border_width=5, 
    border_color="#000000",     
    hover_color="#947612",
    fg_color="#f0d71e",
    corner_radius=20, 
    command=abrir_ventana_hablar
)
btn_iniciar.pack(side="left", padx=40) 

btn_cosas = ctk.CTkButton(
    marco_botones, 
    text="", 
    image=imagen_cosas, 
    width=200, 
    height=250,  
    border_width=5, 
    border_color="#000000",     
    hover_color="#9d2323",
    fg_color="#e10d0d",
    corner_radius=20 
)
btn_cosas.pack(side="left", padx=40)

btn_proceso = ctk.CTkButton(
    marco_botones, 
    text="", 
    image=imagen_procesos, 
    width=200, 
    height=250,  
    border_width=5, 
    border_color="#000000",     
    hover_color="#24a12f",
    fg_color="#19d529",
    corner_radius=20 
)
btn_proceso.pack(side="left", padx=40)

# Asegurar que si cierran con la "X" de la ventana principal, también se ejecute sys.exit()
ventana.protocol("WM_DELETE_WINDOW", cerrar_programa)

ventana.mainloop()