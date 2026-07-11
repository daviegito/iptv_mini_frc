import subprocess
from datetime import datetime, timedelta

# Dicionário em memória para rastrear streams ativos
# Formato: { "caminho_do_video_perfil": {"process": <Popen>, "expires_at": datetime} }
active_streams = {}

# Trava global da WAN115K para garantir apenas 1 vídeo por vez
wan_locked_until = datetime.min

def start_multicast_stream(video_path: str, multicast_ip: str, port: int, duration_sec: float, profile: str) -> bool:
    global wan_locked_until
    
    stream_key = f"{video_path}_{profile}"
    
    # 1. Limpa transmissões velhas que já terminaram
    clean_expired_streams()

    # 2. Regra de Negócio Crucial: Bloqueio da WAN115K
    if profile == "wan":
        if datetime.now() < wan_locked_until:
            return False # WAN está ocupada, o fluxo é rejeitado!
    
    # 3. Se o vídeo já está tocando para esse perfil (ex: um 2º usuário LAN entra no mesmo canal)
    # nós não precisamos abrir o ffmpeg de novo. O Multicast cuida de replicar o pacote na rede!
    if stream_key in active_streams:
        return True

    # 4. Inicia a transmissão usando o FFmpeg em modo de streaming (lendo na taxa real -re)
    cmd = [
        "ffmpeg",
        "-re",        # Lê o vídeo em tempo real (evita mandar o arquivo todo em 1 segundo)
        "-i", video_path,
        "-c", "copy", # Copia os codecs direto, sem re-renderizar
        "-f", "mpegts", # Formato de transporte ideal para IPTV/UDP
        f"udp://{multicast_ip}:{port}?pkt_size=1316" # Envia pro IP Multicast
    ]
    
    # Roda em background, o Python não fica esperando (subprocess.Popen em vez de subprocess.run)
    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Marca a hora exata que a transmissão vai acabar
    expiration = datetime.now() + timedelta(seconds=duration_sec)
    active_streams[stream_key] = {
        "process": process,
        "expires_at": expiration
    }

    # Se foi pra WAN, "tranca" a rede até a expiração
    if profile == "wan":
        wan_locked_until = expiration

    return True

def clean_expired_streams():
    now = datetime.now()
    expired_keys = []
    for key, data in active_streams.items():
        if now > data["expires_at"]:
            # O vídeo acabou. Mata o processo do ffmpeg para liberar memória
            try:
                data["process"].terminate()
            except Exception:
                pass
            expired_keys.append(key)
            
    for key in expired_keys:
        del active_streams[key]
