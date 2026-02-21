import os
import random
import sys

try:
    from PIL import Image
    PILLOW_INSTALLED = True
except ImportError:
    print("Pillow não está instalado. Tentando instalar...")
    os.system(f"{sys.executable} -m pip install Pillow")
    try:
        from PIL import Image
        PILLOW_INSTALLED = True
    except ImportError:
        PILLOW_INSTALLED = False

ASSETS_DIR = 'assets'

def process_image(filepath):
    if not PILLOW_INSTALLED:
        print(f"Pressione pular {filepath} - Pillow não instalado.")
        return
    try:
        img = Image.open(filepath)
        
        # Altera sutilmente o pixel 0,0 para garantir mudança de hash e remover cache em algumas plataformas
        pixels = img.load()
        if img.mode == 'RGB' or img.mode == 'RGBA':
            p = pixels[0,0]
            if type(p) == int: pass
            elif len(p) >= 3:
                r, g, b = p[:3]
                r = (r + 1) % 256
                if len(p) == 4:
                    pixels[0,0] = (r, g, b, p[3])
                else:
                    pixels[0,0] = (r, g, b)
                    
        # Salvar sem EXIF (o PIL faz isso por padrão caso o exif original não seja repassado)
        # Manter qualidade alta
        if filepath.lower().endswith('.png'):
            img.save(filepath, format='PNG')
        else:
            img.save(filepath, quality=95)
        print(f"Imagem otimizada e unica: {filepath}")
    except Exception as e:
        print(f"Erro na imagem {filepath}: {e}")

def process_video_or_other(filepath):
    try:
        # Adiciona 1 byte aleatório no final do arquivo.
        # Isso não quebra vídeos MP4 mas muda completamente a assinatura de hash (MD5).
        with open(filepath, 'ab') as f:
            f.write(bytes([random.randint(0, 255)]))
        print(f"Video tornado unico via alteracao de bits: {filepath}")
    except Exception as e:
        print(f"Erro no video {filepath}: {e}")

def main():
    if not os.path.exists(ASSETS_DIR):
        print(f"Pasta {ASSETS_DIR} não encontrada no diretório atual.")
        return
        
    print("Iniciando processo de tornar ativos únicos...")
    for filename in os.listdir(ASSETS_DIR):
        filepath = os.path.join(ASSETS_DIR, filename)
        if os.path.isfile(filepath):
            # Analisa o tipo do arquivo
            ext = filename.lower().split('.')[-1]
            if ext in ['jpg', 'jpeg', 'png']:
                process_image(filepath)
            elif ext in ['mp4', 'mov', 'webm', 'avi'] or 'video' in filename.lower():
                process_video_or_other(filepath)
            else:
                # Se não for imagem nem vídeo conhecido, pode pular.
                pass
    print("Processo finalizado!")

if __name__ == '__main__':
    main()
