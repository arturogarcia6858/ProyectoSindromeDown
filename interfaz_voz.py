import customtkinter as ctk
import threading
import speech_recognition as sr
import difflib
import win32com.client
from PIL import Image
import sys 
import cv2
from PIL import Image, ImageTk
import pygame
import time
import pythoncom
import vlc

# --- 1. CONFIGURACIÓN DE VOZ ---
speaker = win32com.client.Dispatch("SAPI.SpVoice")
voces = speaker.GetVoices()
speaker.Voice = voces.Item(3) 
speaker.Rate = -1

MODELO_WHISPER = "small"
IDIOMA = "spanish"


def limpiar_texto(texto):
    texto = texto.lower().strip()
    signos_a_quitar = [".", ",", "!", "?", "¿", "¡", " "]
    for signo in signos_a_quitar:
        texto = texto.replace(signo, "")
    return texto


pygame.mixer.init()

def rutina_evaluacion(palabra_objetivo, etiqueta_estado, etiqueta_resultado, boton_accion, reproductor):
    pythoncom.CoInitialize() # Permiso para usar audio en este hilo
    boton_accion.configure(state="disabled")
    
    try:
        etiqueta_resultado.configure(text="") 
        
        # 1. FASE DE VIDEO
        etiqueta_estado.configure(text="Mira el video y escucha con atención...", text_color="blue")
        
        reproductor.stop() # Reiniciamos el video por si se había reproducido antes
        reproductor.play()
        time.sleep(1) # Le damos 1 segundo al motor de VLC para arrancar
        
        # El programa se queda "esperando" en este bucle mientras el video esté activo
        while reproductor.get_state() in [vlc.State.Playing, vlc.State.Opening, vlc.State.Buffering]:
            time.sleep(0.5) 
            
        # 2. FASE DE MICRÓFONO (Se ejecuta apenas termina el video)
        etiqueta_estado.configure(text="🔴 ¡Ahora te toca a ti! Escuchando...", text_color="red")
        
        r = sr.Recognizer()
        r.pause_threshold = 0.4  
        r.non_speaking_duration = 0.3  
        
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, phrase_time_limit=3.0)
            
            etiqueta_estado.configure(text="⚙️ Analizando...", text_color="orange")
            texto_crudo = r.recognize_whisper(audio, model=MODELO_WHISPER, language=IDIOMA)
            palabra_dicha = limpiar_texto(texto_crudo)
            
            palabra_obj_limpia = palabra_objetivo.lower()
            similitud = difflib.SequenceMatcher(None, palabra_obj_limpia, palabra_dicha).ratio()
            porcentaje = similitud * 100
            
            etiqueta_resultado.configure(text=f"Se escuchó: '{palabra_dicha}'\nPrecisión: {porcentaje:.0f}%")
            
            if porcentaje >= 75:
                etiqueta_estado.configure(text="⭐ ¡Excelente!", text_color="green")
                speaker.Speak("¡Excelente esfuerzo! Muy bien dicho, Arturo García López.", 1)
            else:
                etiqueta_estado.configure(text="💪 ¡Casi lo logras!", text_color="orange")
                speaker.Speak("Vamos a intentarlo de nuevo.", 1)
                
    except sr.UnknownValueError:
        etiqueta_estado.configure(text="🤔 No escuché nada.", text_color="red")
        speaker.Speak("No pude escuchar bien, intentémoslo de nuevo.", 1)
    except Exception as e:
        etiqueta_estado.configure(text="❌ Ocurrió un error.", text_color="red")
        print(f"Error en el hilo: {e}")
    finally:
        boton_accion.configure(state="normal")

# --- VENTANA DE HABLA ---
def abrir_ventana_hablar():
    ventana_hablar = ctk.CTkToplevel(ventana)
    ventana_hablar.title("Práctica de Lectura")
    ventana_hablar.configure(fg_color="#ffffff")
    
    ventana_hablar.after(0, lambda: ventana_hablar.state('zoomed'))
    ventana_hablar.grab_set()
    
    # 1. Título
    lbl_titulo_hablar = ctk.CTkLabel(ventana_hablar, text="MÓDULO DE HABLA", font=("Bowlby One SC", 70, "bold"), text_color="#000000")
    lbl_titulo_hablar.pack(pady=(80, 20))
    
    # 2. Pantalla para el video (VLC) - Definimos tamaño 16:9
    ancho_video = 640
    alto_video = 360
    marco_pantalla = ctk.CTkFrame(ventana_hablar, width=ancho_video, height=alto_video, fg_color="black")
    marco_pantalla.pack(pady=10)
    marco_pantalla.pack_propagate(False) 
    ventana_hablar.update() 
    
    # Inicialización VLC
    instancia_vlc = vlc.Instance("--no-xlib") # --no-xlib evita conflictos en algunas versiones
    reproductor = instancia_vlc.media_player_new()
    
    # Configuración de video para eliminar bordes
    reproductor.set_hwnd(marco_pantalla.winfo_id())
    reproductor.video_set_scale(0) # 0 = Ajustar al tamaño del contenedor (elimina bandas negras)
    
    # Carga del video
    media = instancia_vlc.media_new("videos/guitarra.mp4")
    reproductor.set_media(media)
    
    # 3. Etiquetas de UI
    lbl_estado_hablar = ctk.CTkLabel(ventana_hablar, text="Presiona el botón para empezar.", font=("Bowlby One SC", 25), text_color="#555555")
    lbl_estado_hablar.pack(pady=10)
    
    lbl_resultado_hablar = ctk.CTkLabel(ventana_hablar, text="", font=("Bowlby One SC", 20, "italic"), text_color="#333333")
    lbl_resultado_hablar.pack(pady=10)
    
    # 4. Botón de Iniciar
    def arrancar_hilo():
        palabra_a_practicar = "guitarra"
        hilo = threading.Thread(target=rutina_evaluacion, args=(palabra_a_practicar, lbl_estado_hablar, lbl_resultado_hablar, btn_empezar, reproductor))
        hilo.start()

    btn_empezar = ctk.CTkButton(
        ventana_hablar, 
        text="Empezar Práctica", 
        font=("Bowlby One SC", 20, "bold"), 
        height=50, 
        corner_radius=20, 
        command=arrancar_hilo,
        fg_color="#4caf50",
        hover_color="#388e3c"
    )
    btn_empezar.pack(pady=10)
    
    # 5. Botón de Regresar
    def cerrar_ventana():
        reproductor.stop()
        ventana_hablar.destroy()

    btn_volver = ctk.CTkButton(
        ventana_hablar, 
        text="⬅️ ¡Regresar!", 
        font=("Bowlby One SC", 50, "bold"), 
        text_color="#1A17AD",
        fg_color="transparent",
        hover_color="#f0f0f0",
        command=cerrar_ventana 
    )
    btn_volver.place(x=20, y=20)

    # 6. Audio Hover
    btn_empezar.bind("<Enter>", lambda event: sonido_hover("Empezar"))
    btn_empezar.bind("<Leave>", detener_audio)
    btn_volver.bind("<Enter>", lambda event: sonido_hover("Regresar"))
    btn_volver.bind("<Leave>", detener_audio)


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

audio_reproducido = False

# --- FUNCIÓN DE AUDIO SIN CONGELAR LA INTERFAZ ---
def reproducir_audio_seguro(mensaje):
    try:
        # Creamos una instancia local de SAPI dentro del hilo para evitar bloqueos del sistema
        localspeaker = win32com.client.Dispatch("SAPI.SpVoice")
        voces = localspeaker.GetVoices()
        localspeaker.Voice = voces.Item(3) 
        localspeaker.Rate = -1
        localspeaker.Speak(mensaje)
    except Exception as e:
        print(e)

# Variable para controlar el hilo actual y poder cancelarlo o ignorarlo si cambia rápido
SVSFlagsAsync = 3 

def sonido_hover(mensaje):
    # Habla el nuevo mensaje en segundo plano y corta cualquier otro
    speaker.Speak(mensaje, SVSFlagsAsync)

def detener_audio(event):
    # Le mandamos un texto vacío con la bandera 3 para callarlo de inmediato
    speaker.Speak("", SVSFlagsAsync)

# --- CONFIGURACIÓN DE LOS BOTONES ---
# Asegúrate de enlazar esto DESPUÉS de haber creado tus botones (btn_iniciar, etc.)

btn_iniciar.bind("<Enter>", lambda event: sonido_hover("Hablar"))
btn_iniciar.bind("<Leave>", detener_audio)

btn_cosas.bind("<Enter>", lambda event: sonido_hover("Cosas"))
btn_cosas.bind("<Leave>", detener_audio)

btn_proceso.bind("<Enter>", lambda event: sonido_hover("Procesos"))
btn_proceso.bind("<Leave>", detener_audio)
btn_salir.bind("<Enter>", lambda event: sonido_hover("¡Salir!"))
btn_salir.bind("<Leave>", detener_audio)

# Asegurar que si cierran con la "X" de la ventana principal, también se ejecute sys.exit()
ventana.protocol("WM_DELETE_WINDOW", cerrar_programa)

ventana.mainloop()