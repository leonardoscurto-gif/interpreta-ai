import streamlit as st
import google.generativeai as genai

st.set_page_config(
    page_title="Interpreta-AI - NEIE",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Interpreta-AI — NEIE/DPU")
st.subheader("Análise Processual com Inteligência Artificial — Divisão Criminal e Cível Eleitoral")
st.markdown("---")

# Configuração da API via secrets do Streamlit Cloud
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    modelo = genai.GenerativeModel("gemini-1.5-flash-latest")
except Exception:
    st.error("⚠️ Chave de API não configurada. Configure GEMINI_API_KEY nos Secrets do Streamlit Cloud.")
    st.stop()

# Prompt jurídico estruturado baseado no fluxo real da assessoria do NEIE
PROMPT_SISTEMA = """
Você é um assistente jurídico especializado em direito eleitoral brasileiro, 
atuando como suporte à assessoria do Núcleo Estratégico de Interiorização 
Eleitoral (NEIE) da Defensoria Pública da União (DPU).

Sua função é analisar textos brutos de processos eleitorais e gerar um 
despacho inaugural estruturado, no padrão institucional da DPU, contendo 
obrigatoriamente os seguintes itens:

1. COMPETÊNCIA E ATRIBUIÇÃO DO NEIE
   - Identifique o estado e a zona eleitoral
   - Defina qual Ofício do NEIE é competente:
     * 1º Ofício — Região Sul (PR, RS, SC)
     * 2º Ofício — Região Sudeste (SP, RJ, MG, ES)
     * 3º Ofício — Regiões Norte e Centro-Oeste
     * 4º Ofício — Região Nordeste
     * Obs: casos de Violência Política de Gênero (VPG) são sempre 
       centralizados no 1º Ofício (Região Sul), independentemente do estado

2. IMPUTAÇÃO E PENA EM ABSTRATO
   - Identifique o crime imputado e o artigo legal
   - Informe a pena mínima e máxima prevista

3. MARCOS PRESCRICIONAIS
   - Calcule o prazo prescricional com base no Art. 109 do Código Penal
   - Identifique o ano do fato
   - Projete o ano limite para a punibilidade estatal
   - Adote sempre a perspectiva da Defesa (a prescrição favorece o assistido)

4. CABIMENTO DE ANPP OU SUSPENSÃO CONDICIONAL DO PROCESSO
   - Avalie se há possibilidade de Acordo de Não Persecução Penal (ANPP)
   - Avalie se há possibilidade de Suspensão Condicional do Processo (Art. 89 da Lei 9.099/95)

5. FASE PROCESSUAL
   - Identifique em que fase se encontra o processo (inquérito, denúncia, 
     resposta à acusação, instrução, julgamento etc.)

6. AUDIÊNCIAS DESIGNADAS
   - Verifique se há audiência marcada no texto
   - Se houver, destaque com ALERTA DE URGÊNCIA

7. SITUAÇÃO DA CITAÇÃO
   - Identifique se a citação foi pessoal, por edital, se há revelia 
     ou necessidade de curadoria especial

8. DILIGÊNCIAS NECESSÁRIAS
   - Liste as diligências a serem realizadas pelo Cartório
   - Liste as diligências a serem realizadas pela Assessoria

9. TESES DEFENSIVAS INICIAIS
   - Sugira teses de defesa aplicáveis ao caso concreto

10. PROVIDÊNCIAS
    - Indique as providências imediatas da Assessoria
    - Indique as providências imediatas do Cartório

Ao final, gere o DESPACHO INAUGURAL completo, formatado no padrão 
institucional da DPU, numerado por itens, pronto para ser inserido no PAJ.

IMPORTANTE:
- Seja objetivo e técnico
- Use linguagem jurídica formal
- Se alguma informação não estiver disponível no texto, indique expressamente
- Nunca invente dados que não constem no texto fornecido
- Adote sempre a perspectiva da Defensoria Pública (defesa do assistido)
"""

col_esquerda, col_direita = st.columns([1, 1])

with col_esquerda:
    st.markdown("### 📥 Entrada de Dados")

    with st.form(key="formulario_neie"):
        paj_numero = st.text_input(
            "Número do PAJ (SIS-DPU):",
            placeholder="Ex: 2026/123-01955"
        )
        num_processo = st.text_input(
            "Número do Processo Judicial (se disponível):",
            placeholder="Ex: 0600650-87.2024.6.26.0304"
        )

        st.markdown("#### 📄 Texto Bruto do Processo")
        texto_processo = st.text_area(
            "Cole aqui o texto extraído do PJe, e-mail do cartório ou PDF:",
            placeholder="Cole o conteúdo integral ou parcial do processo, denúncia, despacho ou intimação...",
            height=350
        )

        tipo_demanda = st.radio(
            "Natureza da demanda:",
            ["Criminal Eleitoral", "Cível Eleitoral", "Violência Política de Gênero (VPG)"]
        )

        botao_analisar = st.form_submit_button(
            label="🔍 Analisar com IA e Gerar Despacho Inaugural"
        )

with col_direita:
    st.markdown("### 📊 Análise e Despacho Inaugural")

    if botao_analisar:
        if not texto_processo.strip():
            st.warning("⚠️ Insira o texto do processo para análise.")
        else:
            with st.spinner("🤖 Analisando o processo com IA... Aguarde."):
                try:
                    # Monta o prompt completo com os dados do caso
                    prompt_completo = f"""
{PROMPT_SISTEMA}

---
DADOS DO CASO:
PAJ: {paj_numero if paj_numero else "Não informado"}
Número do Processo: {num_processo if num_processo else "A identificar no texto"}
Natureza: {tipo_demanda}

TEXTO BRUTO DO PROCESSO:
{texto_processo}
---

Gere a análise completa e o despacho inaugural conforme as instruções acima.
"""
                    resposta = modelo.generate_content(prompt_completo)
                    resultado = resposta.text

                    st.success("✅ Análise concluída com sucesso!")
                    st.markdown("---")

                    # Exibe o resultado em área copiável
                    st.text_area(
                        "📋 Despacho Inaugural — Pronto para copiar ao PAJ:",
                        value=resultado,
                        height=600
                    )

                    # Botão de download do despacho
                    st.download_button(
                        label="⬇️ Baixar Despacho em .txt",
                        data=resultado,
                        file_name=f"despacho_{paj_numero.replace('/', '-') if paj_numero else 'neie'}.txt",
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"Erro na análise: {str(e)}")

    else:
        st.info("📥 Preencha os dados e cole o texto do processo na coluna esquerda para iniciar a análise.")
        st.markdown("---")
        st.markdown("#### Como usar:")
        st.markdown("1. Informe o número do PAJ")
        st.markdown("2. Informe o número do processo (se disponível)")
        st.markdown("3. Cole o texto bruto do processo")
        st.markdown("4. Selecione a natureza da demanda")
        st.markdown("5. Clique em **Analisar com IA**")
        st.markdown("---")
        st.markdown("#### O sistema analisará automaticamente:")
        st.markdown("- ⚖️ Competência e atribuição do Ofício do NEIE")
        st.markdown("- 📜 Imputação e pena em abstrato")
        st.markdown("- ⏱️ Marcos prescricionais (visão da Defesa)")
        st.markdown("- 🤝 Cabimento de ANPP ou suspensão condicional")
        st.markdown("- 📋 Fase processual e situação da citação")
        st.markdown("- 🚨 Audiências designadas (alerta de urgência)")
        st.markdown("- 📌 Diligências e teses defensivas iniciais")
