import cv2
import threading
import pyttsx3
from ultralytics import YOLO

# --- CONFIGURACIÓN DE VOZ (SAPI5 / Windows) ---
engine = pyttsx3.init()

# Buscar voz en español
voces = engine.getProperty('voices')
for voz in voces:
    if any(nombre in voz.name.lower() for nombre in ["spanish", "sabina", "helena", "jorge", "loquendo"]):
        engine.setProperty('voice', voz.id)
        break

engine.setProperty('rate', 135)

# --- DICCIONARIO EDUCATIVO ---
DICCIONARIO_EDUCATIVO = {
    "Toothbrush": ("Cepillo de dientes", "Es un cepillo de dientes. Sirve para lavarte los dientes y mantener tu boca limpia."),
    "Spoon": ("Cuchara", "Es una cuchara. Sirve para comer sopa y alimentos deliciosos."),
    "Cup": ("Taza", "Es una taza. Sirve para tomar agua, leche o jugo."),
    "Pencil": ("Lápiz", "Es un lápiz. Sirve para escribir y hacer dibujos bonitos."),
    "Book": ("Libro", "Es un libro. Sirve para leer e imaginar historias divertidas."),
    "Mobile phone": ("Teléfono", "Es un teléfono celular. Sirve para llamar a papá o mamá."),
    "Apple": ("Manzana", "Es una manzana. Es una fruta deliciosa y saludable que puedes comer."),
    "Bottle": ("Botella", "Es una botella. Sirve para guardar agua y mantenerte hidratado."),
}

hablando = False
objeto_actual = None
objeto_explicado = False

def hablar(texto):
    global hablando
    hablando = True
    engine.say(texto)
    engine.runAndWait()
    hablando = False

# --- DETECCIÓN CON YOLO ---
model = YOLO("yolov8n-oiv7.pt")
class_ids = [idx for idx, name in model.names.items() if name in DICCIONARIO_EDUCATIVO]

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, classes=class_ids, conf=0.45)

    # Verificar si hay al menos una detección en el fotograma
    if len(results[0].boxes) > 0:
        # 1. Tomar ÚNICAMENTE el primer objeto detectado
        primer_box = results[0].boxes[0]
        cls_id = int(primer_box.cls[0])
        nombre_en = model.names[cls_id]

        if nombre_en in DICCIONARIO_EDUCATIVO:
            nombre_es, explicacion = DICCIONARIO_EDUCATIVO[nombre_en]

            # Dibujar recuadro solo para el primer objeto
            x1, y1, x2, y2 = map(int, primer_box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(frame, nombre_es, (x1, max(y1 - 10, 25)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # 2. Si es un objeto nuevo, reiniciar el estado de explicación
            if objeto_actual != nombre_en:
                objeto_actual = nombre_en
                objeto_explicado = False

            # 3. Hablar SOLO si no se ha explicado este objeto aún y no se está hablando
            if not objeto_explicado and not hablando:
                objeto_explicado = True
                threading.Thread(target=hablar, args=(explicacion,), daemon=True).start()
    else:
        # Si ya no hay ningún objeto frente a la cámara, reiniciar para el siguiente
        objeto_actual = None
        objeto_explicado = False

    cv2.imshow("Asistente Educativo - Solo Primer Objeto", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()