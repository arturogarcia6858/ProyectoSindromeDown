import win32com.client

speaker = win32com.client.Dispatch("SAPI.SpVoice")
voices = speaker.GetVoices()

print("Voces instaladas en tu computadora:")
print("-" * 40)

for i in range(voices.Count):
    print(f"Número {i}: {voices.Item(i).GetDescription()}")