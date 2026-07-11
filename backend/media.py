import subprocess
import json
import os

def get_video_metadata(filepath: str) -> dict:
    """
    Utiliza o comando 'ffprobe' para extrair os metadados do vídeo no formato JSON.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")

    # Comando ffprobe para extrair tudo em JSON
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        filepath
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Erro ao ler metadados com ffprobe: {result.stderr}")

    data = json.loads(result.stdout)
    
    # Garimpa os dados dentro do JSON gigantesco que o ffprobe retorna
    video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    format_data = data.get("format", {})

    metadata = {
        "duration_seconds": float(format_data.get("duration", 0)),
        "bitrate_bps": int(format_data.get("bit_rate", 0)),
        "video_codec": video_stream.get("codec_name") if video_stream else "desconhecido",
        "resolution": f"{video_stream.get('width')}x{video_stream.get('height')}" if video_stream else "desconhecido"
    }
    return metadata


def convert_to_wan_quality(input_filepath: str, output_filepath: str) -> bool:
    """
    Converte um vídeo original para a qualidade restrita da rede WAN (115200 bps).
    Parâmetros exatos extraídos do PDF do professor.
    """
    if not os.path.exists(input_filepath):
        raise FileNotFoundError(f"Arquivo de origem não encontrado: {input_filepath}")

    cmd = [
        "ffmpeg",
        "-y",  # Força sobrescrever o arquivo de destino se ele já existir
        "-i", input_filepath,
        "-c:v", "libx264", # Codec de vídeo
        "-b:v", "80k",     # Limita o vídeo em 80kbps
        "-r", "10",        # Baixa para 10 frames por segundo
        "-s", "320x240",   # Resolução pequena
        "-c:a", "aac",     # Codec de áudio
        "-b:a", "16k",     # Limita o áudio em 16kbps
        "-ac", "1",        # Áudio Mono (1 canal)
        "-ar", "22050",    # Taxa de amostragem de áudio
        output_filepath
    ]

    # subprocess vai "travar" a execução do python até a conversão terminar
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return True
    else:
        # Se der erro, imprimimos o log gigante do ffmpeg no terminal para ajudar a debugar
        print(f"Erro no FFmpeg: {result.stderr}")
        return False
