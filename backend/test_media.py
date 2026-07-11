import media
import os

print("Iniciando teste do Modulo 2 (FFmpeg/FFprobe)")

original = "test.mp4"
convertido = "test_wan.mp4"

if not os.path.exists(original):
    print(f"Erro: O arquivo {original} não existe. Crie um vídeo de teste primeiro.")
    exit(1)

print("\n--- 1. Lendo metadados do vídeo ORIGINAL ---")
metadados = media.get_video_metadata(original)
print(metadados)

print("\n--- 2. Convertendo vídeo para a qualidade WAN (80kbps, 10fps, 320x240) ---")
print("Isso pode demorar alguns segundos, o Python está aguardando o FFmpeg...")
sucesso = media.convert_to_wan_quality(original, convertido)

if sucesso:
    print("\nConversao concluida com sucesso! Novo arquivo 'test_wan.mp4' gerado.")
    print("\n--- 3. Lendo metadados do vídeo CONVERTIDO ---")
    metadados_wan = media.get_video_metadata(convertido)
    print(metadados_wan)
else:
    print("\nFalha na conversao.")
