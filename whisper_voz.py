import speech_recognition as sr
import difflib

MODELO_WHISPER = "small" 
#tiny, base, small, medium, y large
IDIOMA = "spanish"

def limpiar_texto(texto):
    texto = texto.lower().strip()
    signos_a_quitar = [".", ",", "!", "?", "¿", "¡", " "]
    for signo in signos_a_quitar:
        texto = texto.replace(signo, "")
    return texto

def evaluar_lectura(palabra_objetivo):
    r = sr.Recognizer()
    
    r.pause_threshold = 0.4  
    r.non_speaking_duration = 0.3  

    with sr.Microphone() as source:
        print("\nAjustando ruido ambiente... un momento.")
        r.adjust_for_ambient_noise(source, duration=1)
        
        print("\n" + "="*40)
        print(f"   Por favor lee esta palabra: {palabra_objetivo.upper()}")
        print("="*40)
        print("Escuchando...")
        
        audio = r.listen(source, phrase_time_limit=2.0)

    try:
        print("Analizando la pronunciación...")
        
        texto_crudo = r.recognize_whisper(audio, model=MODELO_WHISPER, language=IDIOMA)
        
        palabra_dicha_por_el_nino = limpiar_texto(texto_crudo)
        
        palabra_objetivo = palabra_objetivo.lower()
        similitud = difflib.SequenceMatcher(None, palabra_objetivo, palabra_dicha_por_el_nino).ratio()
        porcentaje = similitud * 100

        print("\n--- RESULTADOS ---")
        print(f"Se esperaba: '{palabra_objetivo}'")
        print(f"Se escuchó:  '{palabra_dicha_por_el_nino}'")
        print(f"Precisión:   {porcentaje:.0f}%")
        print("------------------")

        if porcentaje >= 75:
            print("¡Excelente esfuerzo! ¡Muy bien dicho!\n")
            return True 
        else:
            print("Vamos a intentarlo de nuevo.\n")
            return False 

    except sr.UnknownValueError:
        print("No pude escuchar nada con claridad. ¿Intentamos de nuevo?")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    palabra_a_practicar = "guitarra"
    
    lo_logro = False
    while not lo_logro:
        lo_logro = evaluar_lectura(palabra_a_practicar)