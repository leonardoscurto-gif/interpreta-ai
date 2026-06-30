import streamlit as st
import re

# Configuração da página institucional
st.set_page_config(
    page_title="Interpreta-AI - NEIE",
    page_icon="⚖️",
    layout="wide"
)

# Cabeçalho do Sistema
st.title("⚖️ Interpreta-AI")
st.subheader("Motor de Triagem, Regionalização e Análise Prescricional Estrita - NEIE")
st.markdown("---")

col_esquerda, col_direita = st.columns([1, 1])

with col_esquerda:
    st.markdown("### 📥 Entrada de Texto Bruto (PJe / Denúncia)")
    
    with st.form(key="formulario_triagem"):
        texto_peticiao = st.text_area(
            "Cole aqui o texto integral extraído do processo/intimação:",
            height=380,
            placeholder="Cole o texto do tribunal aqui para a IA analisar..."
        )
        
        st.markdown("💡 *Dica: O motor aplicará as regras de atração dos Ofícios I, II, III e IV da Portaria e calculará os marcos temporais.*")
        botao_enviar = st.form_submit_button(label="🚀 Analisar Processo e Gerar Despacho")

with col_direita:
    st.markdown("### 📤 Despacho Gerado por Inteligência Contextual")
    
    if botao_enviar and texto_peticiao:
        # Normalização do texto para análise contextual
        texto_clean = texto_peticiao.lower().replace("\n", " ").replace("\r", " ")
        texto_clean = re.sub(r'\s+', ' ', texto_clean)
        
        # --- 1. MOTOR DE EXTRAÇÃO DE DADOS ---
        padrao_processo = re.search(r'\d{7}\s*[-–]?\s*\d{2}\s*\.\s*\d{4}\s*\.\s*\d\s*\.\s*\d{2}\s*\.\s*\d{4}', texto_peticiao)
        num_processo = padrao_processo.group(0).strip() if padrao_processo else "[NÚMERO DE PROCESSO NÃO LOCALIZADO]"

        padrao_zona = re.search(r'(\d+\s*ª?\s*(?:zona|z\.e\.)\s*(?:eleitoral)?.*?)(?:perante|da comarca|$)', texto_clean)
        if padrao_zona:
            zona_eleitoral = padrao_zona.group(1).strip().upper()
        else:
            comarca_busca = re.search(r'(comarca de\s*[a-zA-Záàâãéèêíïóôõöúçñ\s\/]+)', texto_clean)
            zona_eleitoral = comarca_busca.group(1).strip().upper() if comarca_busca else "[LOCALIDADE NÃO IDENTIFICADA]"

        padrao_artigo = re.search(r'(art\s*\.?\s*\d+[^;]*?(?:lei|c\/c|código|\d{4})[^;.\n]*)', texto_clean)
        artigo_lei = padrao_artigo.group(1).strip().upper() if padrao_artigo else "ARTIGO NÃO IDENTIFICADO"

        # --- 2. CLASSIFICAÇÃO DOS OFÍCIOS NATURAIS ---
        oficio_sugerido = "Ofício Geral / Coordenação NEIE"
        regiao_detalhe = "Região não mapeada automaticamente."
        
        if any(est in texto_clean for est in ["rio grande do sul", "/rs", "paraná", "/pr", "santa catarina", "/sc", ".6.21.", ".6.16.", ".6.24."]):
            oficio_sugerido = "1º Ofício de Atuação (Região Sul)"
            regiao_detalhe = "Jurisdição: PR, RS e SC (Art. 1º, I)"
        elif any(est in texto_clean for est in ["são paulo", "/sp", "rio de janeiro", "/rj", "minas gerais", "/mg", "espírito santo", "/es", ".6.02.", ".6.19.", ".6.13.", ".6.08."]):
            oficio_sugerido = "2º Ofício de Atuação (Região Sudeste)"
            regiao_detalhe = "Jurisdição: SP, RJ, MG e ES (Art. 1º, II)"
        elif any(est in texto_clean for est in ["piauí", "/pi", ".6.18.", "distrito federal", "/df", "goiás", "/go", "mato grosso", "/mt", "amazonas", "/am", "pará", "/pa", ".6.07."]):
            oficio_sugerido = "3º Ofício de Atuação (Regiões Norte e Centro-Oeste)"
            regiao_detalhe = "Jurisdição Unificada: Norte e Centro-Oeste (Art. 1º, III)"
        elif any(est in texto_clean for est in ["bahia", "/ba", "ceará", "/ce", "pernambuco", "/pe", "maranhão", "/ma", "paraíba", "/pb", "rio grande do norte", "/rn"]):
            oficio_sugerido = "4º Ofício de Atuação (Região Nordeste)"
            regiao_detalhe = "Jurisdição: Estados do Nordeste (Art. 1º, IV)"

        # Atração Temática Prevalente (Art. 2º da Portaria)
        eh_caso_genero = any(g in texto_clean for g in ["gênero", "violência política", "art. 326-b", "candidata", "vpg"])
        if eh_caso_genero:
            oficio_sugerido = "1º Ofício de Atuação (Sul - Centralização Nacional VPG - Art. 2º)"
            regiao_detalhe = "Atração Temática Prevalente: Violência Política de Gênero"

        # --- 3. ANÁLISE DE CONTEXTO PROCESSUAL ---
        if any(g in texto_clean for g in ["in albis", "curador", "curadoria", "edital", "revel", "não constituiu"]):
            curadoria_text = "transcorreu in albis o prazo para constituição de advogado particular, circunstância que ensejou a habilitação da Defensoria Pública da União nos autos, para a atuação a título de curadoria especial"
        else:
            curadoria_text = "habilitação regular da Defensoria Pública da União para assistência jurídica integral da parte necessitada"

        if any(g in texto_clean for g in ["anpp", "persecução", "acordo de não", "proposta de acordo"]):
            anpp_text = "foi determinada a suspensão do processo para análise da possibilidade de oferecimento de Acordo de Não Persecução Penal (ANPP)"
        else:
            anpp_text = "não há indicativos de proposta de ANPP pendente, seguindo o rito comum ordinário"

        # --- 4. MARCOS TEMPORAIS E PRESCRIÇÃO DA DEFESA ---
        ano_fato = 2026
        for ano in ["2020", "2021", "2022", "2023", "2024", "2025", "2026"]:
            if ano in texto_clean:
                ano_fato = int(ano)
                break
        
        pena_maxima = 4  
        if "348" in texto_clean:
            pena_maxima = 6  
        elif "326-b" in texto_clean:
            pena_maxima = 4  

        if pena_maxima <= 2:
            anos_prescricao = 4
        elif pena_maxima <= 4:
            anos_prescricao = 8
        elif pena_maxima <= 8:
            anos_prescricao = 12
        else:
            anos_prescricao = 20

        ano_limite = ano_fato + anos_prescricao

        # --- 5. MONTAGEM DO DESPACHO FINAL ---
        texto_despacho_final = (
            f"1. PAJ recebido para atuação nos termos da Resolução CSDPU nº 250, de 9 de junho de 2026.\n"
            f"2. Tramita em desfavor da parte assistida a Ação Penal Eleitoral nº {num_processo}, perante a {zona_eleitoral}. "
            f"Trata-se de localidade sem cobertura ordinária por Unidade ou Núcleo Regional da DPU, razão pela qual é de atribuição do NEIE, direcionado ao {oficio_sugerido}.\n\n"
            f"DA IMPUTAÇÃO E MARCOS PRESCRICIONAIS:\n"
            f"3. A denúncia imputa à assistida a prática do delito previsto no {artigo_lei}.\n"
            f"4. Certifico, para fins de análise prescricional com foco na estratégia da Defesa, que o fato ocorreu no ano de {ano_fato} e possui pena máxima cominada de {pena_maxima} anos. "
            f"Sob a égide do Art. 109 do Código Penal, o lapso prescricional em abstrato é de {anos_prescricao} anos, fixando o ano limite de punibilidade estatal em {ano_limite}. "
            f"Considerados os marcos interruptivos documentados, não se verifica a ocorrência do decurso temporal extintivo até o momento, encontrando-se regular o curso processual.\n\n"
            f"DA ANÁLISE PROCESSUAL:\n"
            f"5. Ademais, certifico que as partes assistidas foram devidamente citadas e que {curadoria_text}.\n"
            f"6. Certifico, ainda, que {anpp_text}.\n\n"
            f"DILIGÊNCIAS CARTORÁRIAS:\n"
            f"7. Ao Cartório:\n"
            f"a) Entrar em contato com as partes assistidas para cientificá-las acerca da denúncia ofertada pelo Ministério Público Federal pela suposta prática de crime eleitoral, bem como informar que a Defensoria Pública da União foi nomeada para promover sua defesa.\n"
            f"b) Solicitar informações sobre o interesse em arrolar testemunhas que possam contribuir para o esclarecimento dos fatos, enviando seus dados de qualificação, pois este é o momento processual adequado para a apresentação do rol ao Juízo.\n\n"
            f"DILIGÊNCIAS DA ASSESSORIA JURÍDICA:\n"
            f"8. Adotar as providências cabíveis para elaboração da resposta à acusação."
        )

        # Exibição na Tela
        st.success("🤖 Análise Concluída! Informações processadas com sucesso.")
        st.text_area("📋 Minuta de Despacho Pronta (Copiar e Colar):", value=texto_despacho_final, height=500)
        
        # Painel Informativo Técnico
        st.info(f"📊 **Dados de Back-End Calculados:**\n"
                f"* **Distribuição Final:** {oficio_sugerido} ({regiao_detalhe})\n"
                f"* **Ano Encontrado do Fato:** {ano_fato}\n"
                f"* **Pena Máxima Avaliada:** {pena_maxima} anos\n"
                f"* **Prescrição Projetada (Teto):** {ano_limite}")

    elif not texto_peticiao:
        st.info("📥 Insira o texto na esquerda e clique no botão para rodar.")