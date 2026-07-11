from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
import models, auth
from streamer import start_multicast_stream
import os

router = APIRouter(tags=["Cliente IPTV"])

# Banco de dados temporário de canais em memória (apenas para validar o laboratório rápido)
CHANNELS = {
    1: {
        "id": 1,
        "nome": "Canal 1 - Esportes",
        "video_original": "test.mp4",
        "video_wan": "test_wan.mp4",
        "duration": 5.0, # 5 segundos de duração do nosso vídeo teste
        "ip_lan": "239.10.1.1", # IP Classe D - Range LAN definido pelo prof
        "ip_wan": "239.20.1.1", # IP Classe D - Range WAN definido pelo prof
        "port": 5000
    }
}

@router.get("/channels")
def list_channels(current_user: models.User = Depends(auth.get_current_user)):
    """ Retorna a grade de canais disponíveis no frontend """
    return [{"id": c["id"], "nome": c["nome"]} for c in CHANNELS.values()]

@router.get("/play/{channel_id}")
def play_channel(channel_id: int, current_user: models.User = Depends(auth.get_current_user)):
    """ 
    A Rota Mais Importante. 
    1. Verifica perfil do usuário
    2. Autoriza ou nega o uso da WAN
    3. Aciona o ffmpeg (streamer.py)
    4. Devolve um arquivo playlist.m3u para o VLC 
    """
    if channel_id not in CHANNELS:
        raise HTTPException(status_code=404, detail="Canal não encontrado na base de dados.")
        
    channel = CHANNELS[channel_id]
    profile = current_user.perfil
    if profile == "admin":
        profile = "lan" # O Admin não sofre com a rede lenta

    # Direciona o vídeo e o IP Multicast baseado na qualidade do perfil
    if profile == "lan":
        video_path = channel["video_original"]
        multicast_ip = channel["ip_lan"]
    else: # wan
        video_path = channel["video_wan"]
        multicast_ip = channel["ip_wan"]

    if not os.path.exists(video_path):
        raise HTTPException(status_code=500, detail="Vídeo não encontrado no servidor.")

    # Tenta iniciar a transmissão multicast
    success = start_multicast_stream(
        video_path=video_path,
        multicast_ip=multicast_ip,
        port=channel["port"],
        duration_sec=channel["duration"],
        profile=profile
    )

    # Bloqueio estrito da WAN (Regra do PDF!)
    if not success and profile == "wan":
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail="A rede WAN115K está congestionada! Outro vídeo já está ocupando todo o link."
        )

    # Formata a playlist no padrão M3U
    m3u_content = f"""#EXTM3U
#EXTINF:-1, {channel["nome"]} ({profile.upper()})
udp://@{multicast_ip}:{channel["port"]}
"""

    # Retorna como um arquivo baixável que o navegador enviará direto pro VLC
    return PlainTextResponse(
        content=m3u_content,
        media_type="audio/x-mpegurl",
        headers={"Content-Disposition": f"attachment; filename=canal_{channel_id}.m3u"}
    )
