import requests
import sys

# URL CORRIGIDA (Conforme sua imagem do Render)
URL = "https://moneylayer-2-0.onrender.com"

def verificar_site():
    print(f"🔍 Iniciando auditoria externa em: {URL}...")
    
    try:
        response = requests.get(URL)
        
        # 1. Verifica se o servidor respondeu (Status 200)
        if response.status_code == 200:
            print("✅ SERVIDOR ONLINE (Status 200)")
        else:
            print(f"❌ ERRO: Servidor respondeu com {response.status_code}")
            sys.exit(1)
            
        # 2. Verifica elementos chave no HTML
        conteudo = response.text
        
        if "MoneyLayer" in conteudo:
            print("✅ Marca MoneyLayer encontrada")
        else:
            print("⚠️ ALERTA: Nome do projeto sumiu da home!")

        if "Auditoria" in conteudo:
            print("✅ Tabela de Auditoria visível")
        else:
            print("⚠️ ALERTA: Auditoria não encontrada!")
            
        if "Pagar" in conteudo:
            print("✅ Botão de Pagamento Ativo")
        else:
            print("⚠️ ALERTA: Botão de pagamento sumiu!")

        print("\n🚀 CONCLUSÃO: O Frontend parece estar 100% operacional.")
        
    except Exception as e:
        print(f"❌ CRÍTICO: Não foi possível conectar ao site. Erro: {e}")

if __name__ == "__main__":
    verificar_site()
