import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="MoneyLayer 2.0", page_icon="💸", layout="wide")

# Título
st.title("💸 MoneyLayer 2.0 - Dashboard")
st.markdown("### A Camada de Dinheiro com Interesse Social")

# URL da API
API_URL = "http://127.0.0.1:8000/api/v1"

# --- SIDEBAR: Fazer Pagamento ---
with st.sidebar:
    st.header("📲 Nova Transação")
    valor = st.number_input("Valor (R$)", min_value=1.0, value=2000.0, step=10.0)
    desc = st.text_input("Descrição", value="Pagamento via Dashboard")
    
    if st.button("Processar Pagamento", type="primary"):
        payload = {"valor": valor, "description": desc, "user_id": 1}
        try:
            # Autenticação básica do Admin
            auth = ('admin@moneylayer.com', '123456')
            response = requests.post(f"{API_URL}/social/processar-distribuicao", json=payload, auth=auth)
            
            if response.status_code == 200:
                dados = response.json()
                st.success(f"✅ Sucesso! ID: {dados['db_id']}")
                st.json(dados['auditoria'])
            else:
                st.error(f"Erro: {response.text}")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")

# --- ÁREA PRINCIPAL: Gráficos ---
try:
    # Busca transações (usando auth admin para garantir acesso)
    auth = ('admin@moneylayer.com', '123456')
    res = requests.get(f"{API_URL}/transactions/", auth=auth)
    
    if res.status_code == 200:
        transacoes = res.json()
        if transacoes:
            df = pd.DataFrame(transacoes)
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total Bruto", f"R$ {df['amount'].sum():,.2f}")
            col2.metric("🤝 Fundo Social", f"R$ {df['social_value'].sum():,.2f}")
            col3.metric("💼 Líquido Privado", f"R$ {df['net_value'].sum():,.2f}")
            
            # Gráficos
            st.divider()
            colA, colB = st.columns(2)
            with colA:
                st.subheader("Distribuição")
                fig = px.pie(names=["Privado", "Social"], values=[df['net_value'].sum(), df['social_value'].sum()])
                st.plotly_chart(fig, use_container_width=True)
            with colB:
                st.subheader("Histórico")
                st.dataframe(df[['id', 'description', 'amount', 'social_value']])
        else:
            st.info("Nenhuma transação ainda.")
    else:
        st.warning(f"Não consegui ler as transações. Status: {res.status_code}")

except Exception as e:
    st.error(f"O Backend parece estar desligado. {e}")
