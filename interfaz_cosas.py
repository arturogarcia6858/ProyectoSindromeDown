import customtkinter as ctk
import cv2
import threading
import pyttsx3
from ultralytics import YOLO
import vlc
from PIL import Image, ImageTk

# --- DICCIONARIO EDUCATIVO ---
DICCIONARIO_EDUCATIVO = {
    "Toothbrush": ("Cepillo de dientes", "Es un cepillo de dientes. Sirve para lavarte los dientes y mantener tu boca limpia.", "videos/cepillo.mp4"),
    "Spoon": ("Cuchara", "Es una cuchara. Sirve para comer sopa y alimentos deliciosos.", "videos/cuchara.mp4"),
    "Cup": ("Taza", "Es una taza. Sirve para tomar agua, leche o jugo.", "videos/taza.mp4"),
    "Pencil": ("Lápiz", "Es un lápiz. Sirve para escribir y hacer dibujos bonitos.", "videos/lapiz.mp4"),
    "Book": ("Libro", "Es un libro. Sirve para leer e imaginar historias divertidas.", "videos/libro.mp4"),
    "Mobile phone": ("Teléfono", "Es un teléfono celular. Sirve para llamar a papá o mamá.", "videos/telefono.mp4"),
    "Apple": ("Manzana", "Es una manzana. Es una fruta deliciosa y saludable que puedes comer.", "videos/manzana.mp4"),
    "Bottle": ("Botella", "Es una botella. Sirve para guardar agua y mantenerte hidratado.", "videos/botella.mp4"),
}

def abrir_ventana_cosas(ventana_principal):
    ventana_cosas = ctk.CTkToplevel(ventana_principal)
    ventana_cosas.title("Módulo de Cosas - Reconocimiento Inteligente")
    ventana_cosas.configure(fg_color="#ffffff")
    ventana_cosas.after(0, lambda: ventana_cosas.state('zoomed'))
    ventana_cosas.grab_set()

    # Variables de control para la cámara y VLC para poder cerrarlas de forma segura
    cap_holder = [None]
    reproductor_holder = [None]

    def cerrar_modulo_cosas():
        if cap_holder[0] is not None:
            cap_holder[0].release()
        if reproductor_holder[0] is not None:
            reproductor_holder[0].stop()
        ventana_cosas.destroy()

    # 1. Título superior
    lbl_titulo = ctk.CTkLabel(ventana_cosas, text="Módulo de reconocimiento de cosas", font=("Bowlby One SC", 50, "bold"), text_color="#000000")
    lbl_titulo.pack(pady=(80, 70))

    # 2. Contenedor Principal en Dos Columnas (Izquierda: Cámara | Derecha: Video)
    marco_contenido = ctk.CTkFrame(ventana_cosas, fg_color="transparent")
    marco_contenido.pack(expand=True, fill="both", padx=30, pady=10)

    # --- COLUMNA IZQUIERDA: CÁMARA DE YOLO ---
    marco_camara = ctk.CTkFrame(marco_contenido, fg_color="#f0f0f0", corner_radius=20, border_width=3, border_color="#000000")
    marco_camara.pack(side="left", expand=True, padx=20, pady=10)

    lbl_video_camara = ctk.CTkLabel(marco_camara, text="Iniciando sistema...", font=("Bowlby One SC", 20))
    lbl_video_camara.pack(padx=20, pady=20)

    lbl_info_objeto = ctk.CTkLabel(marco_camara, text="Cargando inteligencia artificial...", font=("Bowlby One SC", 22), text_color="#000000")
    lbl_info_objeto.pack(pady=(0, 20))

    # --- COLUMNA DERECHA: REPRODUCTOR DE VIDEO DEMOSTRATIVO (VLC) ---
    marco_video_demo = ctk.CTkFrame(marco_contenido, width=600, height=400, fg_color="black", corner_radius=20)
    marco_video_demo.pack(side="right", expand=True, padx=20, pady=10)
    marco_video_demo.pack_propagate(False)
    ventana_cosas.update()

    # Inicializar reproductor VLC de inmediato (esto no congela la pantalla)
    instancia_vlc = vlc.Instance()
    reproductor_demo = instancia_vlc.media_player_new()
    reproductor_demo.set_hwnd(marco_video_demo.winfo_id())
    reproductor_demo.video_set_scale(0)
    reproductor_holder[0] = reproductor_demo

    # Botón de regresar colocado ANTES de la carga pesada para que aparezca al instante
    btn_volver = ctk.CTkButton(
        ventana_cosas, 
        text="⬅️ ¡Regresar!", 
        font=("Bowlby One SC", 35, "bold"), 
        text_color="#1A17AD",
        fg_color="transparent",
        hover_color="#f0f0f0",
        command=cerrar_modulo_cosas
    )
    btn_volver.place(x=20, y=20)

    # --- CONFIGURACIÓN EN SEGUNDO PLANO (HILO) ---
    def inicializar_sistema_en_segundo_plano():
        # Configuración de voz
        engine = pyttsx3.init()
        voces = engine.getProperty('voices')
        for voz in voces:
            if any(nombre in voz.name.lower() for nombre in ["spanish", "sabina", "helena", "jorge", "loquendo"]):
                engine.setProperty('voice', voz.id)
                break
        engine.setProperty('rate', 135)

        hablando_flag = [False]
        objeto_actual = [None]
        objeto_explicado = [False]

        def hablar_texto(texto):
            hablando_flag[0] = True
            engine.say(texto)
            engine.runAndWait()
            hablando_flag[0] = False

        # Carga pesada de YOLO y apertura de cámara en hilo independiente
        model = YOLO("yolov8n-oiv7.pt")
        class_ids = [idx for idx, name in model.names.items() if name in DICCIONARIO_EDUCATIVO]

        cap = cv2.VideoCapture(0)
        cap_holder[0] = cap
        video_reproduciendo_actual = [None]

        def actualizar_frame_yolo():
            if not ventana_cosas.winfo_exists() or not cap.isOpened():
                return

            ret, frame = cap.read()
            if not ret:
                ventana_cosas.after(15, actualizar_frame_yolo)
                return

            frame = cv2.flip(frame, 1)
            results = model(frame, classes=class_ids, conf=0.45)
            
            if len(results[0].boxes) > 0:
                primer_box = results[0].boxes[0]
                cls_id = int(primer_box.cls[0])
                nombre_en = model.names[cls_id]

                if nombre_en in DICCIONARIO_EDUCATIVO:
                    nombre_es, explicacion, ruta_video = DICCIONARIO_EDUCATIVO[nombre_en]
                    lbl_info_objeto.configure(text=f"¡Detectado: {nombre_es}!", text_color="#4caf50")

                    x1, y1, x2, y2 = map(int, primer_box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cv2.putText(frame, nombre_es, (x1, max(y1 - 10, 25)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                    if objeto_actual[0] != nombre_en:
                        objeto_actual[0] = nombre_en
                        objeto_explicado[0] = False
                        
                        if video_reproduciendo_actual[0] != ruta_video:
                            video_reproduciendo_actual[0] = ruta_video
                            media = instancia_vlc.media_new(ruta_video)
                            reproductor_demo.set_media(media)
                            reproductor_demo.play()

                    if not objeto_explicado[0] and not hablando_flag[0]:
                        objeto_explicado[0] = True
                        threading.Thread(target=hablar_texto, args=(explicacion,), daemon=True).start()
            else:
                lbl_info_objeto.configure(text="Acerca un objeto a la cámara.", text_color="#000000")
                objeto_actual[0] = None
                objeto_explicado[0] = False

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(frame_rgb)
            img_pil = img_pil.resize((700, 550))
            img_tk = ImageTk.PhotoImage(image=img_pil)

            lbl_video_camara.configure(image=img_tk, text="")
            lbl_video_camara.image = img_tk

            if ventana_cosas.winfo_exists():
                ventana_cosas.after(15, actualizar_frame_yolo)

        # Arrancar el bucle de la cámara una vez cargado todo
        ventana_cosas.after(0, actualizar_frame_yolo)

    # Lanzamos la inicialización en segundo plano para que la ventana aparezca volando
    threading.Thread(target=inicializar_sistema_en_segundo_plano, daemon=True).start()