import customtkinter as ctk
import threading
import speech_recognition as sr
import difflib
import win32com.client
from PIL import Image

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
    # Desactivamos el botón de la ventana de práctica
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
            
    # Volvemos a activar el botón al terminar
    boton_accion.configure(state="normal")


# --- 3. CREACIÓN DE LA NUEVA VENTANA (MÓDULO DE HABLA) ---
def abrir_ventana_hablar():
    # Creamos la ventana secundaria
    ventana_hablar = ctk.CTkToplevel(ventana)
    ventana_hablar.title("Práctica de Lectura")
    ventana_hablar.configure(fg_color="#eeda95")
    
    # La maximizamos igual que el menú principal
    ventana_hablar.after(0, lambda: ventana_hablar.state('zoomed'))
    
    # Evita que se pueda clickear el menú de fondo mientras esta ventana esté abierta
    ventana_hablar.grab_set() 
    
    # Textos de la nueva ventana
    lbl_titulo_hablar = ctk.CTkLabel(ventana_hablar, text="🗣️ Módulo de Habla", font=("Arial", 40, "bold"), text_color="#333333")
    lbl_titulo_hablar.pack(pady=(40, 20))
    
    lbl_estado_hablar = ctk.CTkLabel(ventana_hablar, text="Presiona el botón para empezar.", font=("Arial", 25), text_color="#555555")
    lbl_estado_hablar.pack(pady=20)
    
    lbl_resultado_hablar = ctk.CTkLabel(ventana_hablar, text="", font=("Arial", 20, "italic"), text_color="#333333")
    lbl_resultado_hablar.pack(pady=20)
    
    # Función local para arrancar el hilo sin congelar la ventana
    def arrancar_hilo():
        palabra_a_practicar = "guitarra"
        hilo = threading.Thread(target=rutina_evaluacion, args=(palabra_a_practicar, lbl_estado_hablar, lbl_resultado_hablar, btn_empezar))
        hilo.start()

    # Botón principal de la actividad
    btn_empezar = ctk.CTkButton(
        ventana_hablar, 
        text="Empezar Práctica", 
        font=("Arial", 20, "bold"), 
        height=60, 
        corner_radius=20, 
        command=arrancar_hilo,
        fg_color="#4caf50",
        hover_color="#388e3c"
    )
    btn_empezar.pack(pady=40)
    
    # Botón para salir y regresar al menú
    btn_volver = ctk.CTkButton(
        ventana_hablar, 
        text="Regresar al Menú Principal", 
        font=("Arial", 16),
        height=40,
        fg_color="#d32f2f", 
        hover_color="#b71c1c", 
        command=ventana_hablar.destroy
    )
    btn_volver.pack(pady=10)


# --- 4. DISEÑO DEL MENÚ PRINCIPAL ---
ventana = ctk.CTk()
ventana.title("Asistente de Lectura - Menú Principal")
ventana.configure(fg_color="#eeda95")
ventana.after(0, lambda: ventana.state('zoomed'))

lbl_titulo = ctk.CTkLabel(
    ventana, 
    text="¡Bienvenido a Aprender!", 
    font=("Arial", 50, "bold"), 
    text_color="#333333",
    fg_color="transparent"
)
lbl_titulo.pack(pady=(60, 60)) # Más espacio arriba

# --- CREAMOS UN MARCO PARA ACOMODAR LOS BOTONES HORIZONTALMENTE ---
marco_botones = ctk.CTkFrame(ventana, fg_color="transparent")
marco_botones.pack(pady=20)

# Carga de Imágenes (Ajusté un poco el tamaño para que se vean mejor)
imagen_hablar = ctk.CTkImage(
    light_image=Image.open("imagenes/hablar2.png"), 
    dark_image=Image.open("imagenes/hablar2.png"), 
    size=(150, 200) 
)

imagen_cosas = ctk.CTkImage(
    light_image=Image.open("imagenes/cosas.png"), 
    dark_image=Image.open("imagenes/cosas.png"), 
    size=(150, 200) 
)

imagen_procesos = ctk.CTkImage(
    light_image=Image.open("imagenes/procesos2.png"), 
    dark_image=Image.open("imagenes/procesos2.png"), 
    size=(150, 200) 
)

# Botón 1 (Hablar) - Manda a llamar a la función abrir_ventana_hablar
btn_iniciar = ctk.CTkButton(
    marco_botones, 
    text="", 
    image=imagen_hablar, 
    width=180, 
    height=230,  
    border_width=5, 
    border_color="#3e3720",     
    hover_color="#c2b177",
    fg_color="#eeda95",
    corner_radius=20, 
    command=abrir_ventana_hablar
)
# Lo colocamos a la izquierda con un espacio de separación
btn_iniciar.pack(side="left", padx=40) 

# Botón 2 (Cosas)
btn_cosas = ctk.CTkButton(
    marco_botones, 
    text="", 
    image=imagen_cosas, 
    width=180, 
    height=230,  
    border_width=5, 
    border_color="#3e3720",     
    hover_color="#c2b177",
    fg_color="#eeda95",
    corner_radius=20 
)
btn_cosas.pack(side="left", padx=40)

# Botón 3 (Procesos)
btn_proceso = ctk.CTkButton(
    marco_botones, 
    text="", 
    image=imagen_procesos, 
    width=180, 
    height=230,  
    border_width=5, 
    border_color="#3e3720",     
    hover_color="#c2b177",
    fg_color="#eeda95",
    corner_radius=20 
)
btn_proceso.pack(side="left", padx=40)

ventana.mainloop()