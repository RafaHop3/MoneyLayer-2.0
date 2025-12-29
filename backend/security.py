from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

# Carrega o arquivo .env
load_dotenv()

# Tenta ler a chave do arquivo
chave = os.getenv("MASTER_KEY")

# --- TRUQUE PARA GERAR CHAVE NO INÍCIO ---
if not chave:
    print("\n--- ATENÇÃO: MASTER_KEY NÃO ENCONTRADA ---")
    nova_chave = Fernet.generate_key().decode()
    print(f"Copie esta chave e cole no seu arquivo .env após 'MASTER_KEY=':")
    print(f"{nova_chave}")
    print("-------------------------------------------\n")
    # Para não travar o teste agora, usamos a chave gerada na memória
    chave = nova_chave

cipher = Fernet(chave)

def encriptar(texto: str) -> str:
    """Recebe texto normal, devolve embaralhado"""
    if not texto: return ""
    return cipher.encrypt(texto.encode()).decode()

def decriptar(token: str) -> str:
    """Recebe embaralhado, devolve texto normal"""
    if not token: return ""
    try:
        return cipher.decrypt(token.encode()).decode()
    except:
        return "[ERRO: DADO ILEGÍVEL]"

# Teste rápido se rodar este arquivo direto
if __name__ == "__main__":
    segredo = encriptar("SenhaDoBanco123")
    print(f"Encriptado: {segredo}")
    print(f"Decriptado: {decriptar(segredo)}")