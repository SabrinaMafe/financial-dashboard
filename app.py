import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# Configuração da página
st.set_page_config(page_title="Dashboard Financeiro", page_icon="💰", layout="wide")
st.title("💰 Dashboard Financeiro Inteligente")

# Campo para inserir a API Key manualmente
api_key = st.text_input("🔑 Digite sua OpenAI API Key:", type="password")

client = None
if api_key:
    client = OpenAI(api_key=api_key)
    st.success("✅ Chave configurada com sucesso!")
else:
    st.warning("Por favor, insira sua chave da OpenAI para gerar recomendações.")

# Upload do extrato
uploaded_file = st.file_uploader("📂 Faça upload do extrato (CSV ou Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("📊 Dados do Extrato")
        st.dataframe(df.head())

        # Verificar se colunas necessárias existem
        if {"Data", "Descrição", "Categoria", "Valor"}.issubset(df.columns):
            # Converter data
            df["Data"] = pd.to_datetime(df["Data"])

            # Total gasto
            total = df["Valor"].sum()
            st.metric("💸 Total Gasto", f"R$ {total:,.2f}")

            # Top 3 categorias
            top_cats = df.groupby("Categoria")["Valor"].sum().nlargest(3)
            st.subheader("🏆 Top 3 Categorias")
            st.table(top_cats)

            # Gráfico pizza
            fig_pie = px.pie(df, values="Valor", names="Categoria", title="Distribuição de Gastos por Categoria")
            st.plotly_chart(fig_pie, use_container_width=True)

            # Gráfico linha (evolução dos gastos)
            df_daily = df.groupby("Data")["Valor"].sum().reset_index()
            fig_line = px.line(df_daily, x="Data", y="Valor", title="Evolução dos Gastos")
            st.plotly_chart(fig_line, use_container_width=True)

            # Recomendações com IA
            if client:
                if st.button("✨ Gerar Recomendações com IA"):
                    resumo = df.groupby("Categoria")["Valor"].sum().to_dict()
                    prompt = f"""
                    Analise os seguintes gastos em reais por categoria e dê recomendações financeiras simples:

                    {resumo}

                    Responda em português, de forma objetiva, em no máximo 5 tópicos.
                    """

                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        recomendacoes = response.choices[0].message.content
                        st.subheader("💡 Recomendações da IA")
                        st.write(recomendacoes)
                    except Exception as e:
                        st.error(f"Erro ao gerar recomendações: {e}")
            else:
                st.info("Digite sua chave de API acima para habilitar as recomendações.")
        else:
            st.error("O arquivo precisa ter as colunas: Data, Descrição, Categoria, Valor.")
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
