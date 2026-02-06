from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import date
import re
import time

from .login_helper import criar_driver_com_perfil

TERMOS_PRODUTO = [
    "product designer", "product design", "product manager", "ux designer", "ui designer",
    "ux/ui", "ui/ux", "service designer", "head de produto", "product owner",
    "product operations", "design de produto", "designer de produto", "vaga de ux",
    "vaga ux", "vaga product", "vaga designer", "oportunidade ux", "oportunidade product",
    "ux research", "ux researcher", "design ops", "designops",
]

TERMOS_EXCLUIR = [
    "developer", "desenvolvedor", "engineer", "engenheiro", "qa", "tester",
    "analista de dados", "data analyst", "designer gráfico", "graphic designer",
    "marketing", "growth", "devops", "backend", "frontend", "fullstack",
]

PLATAFORMAS_VAGAS = [
    "gupy.io", "lever.co", "greenhouse.io", "workable.com", "nerdin.com.br",
    "99jobs.com", "vagas.com", "catho.com.br", "trampos.co",
]


def eh_post_produto(texto):
    texto_lower = texto.lower()
    for termo in TERMOS_EXCLUIR:
        if termo in texto_lower:
            if not any(t in texto_lower for t in TERMOS_PRODUTO):
                return False
    for termo in TERMOS_PRODUTO:
        if termo in texto_lower:
            return True
    return False


def extrair_emails(texto):
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, texto)
    return list(set([e for e in emails if 'example' not in e.lower()]))


def extrair_links_externos(texto):
    pattern = r'https?://[^\s<>"{}|\\^`\[\])(\']+'
    links = re.findall(pattern, texto)
    resultado = []
    for link in links:
        link = link.rstrip('.,;:!?')
        if 'linkedin.com' not in link.lower():
            resultado.append(link)
    return list(set(resultado))


def limpar_titulo(titulo):
    """Limpa e valida um título extraído."""
    if not titulo:
        return None
    # Remove caracteres especiais do início e fim
    titulo = re.sub(r'^[:\s\-•→🔹📣🚀💼✨|]+', '', titulo)
    titulo = re.sub(r'[:\s\-•→🔹📣🚀💼✨|]+$', '', titulo)
    # Remove URLs
    if titulo.startswith('http') or 'lnkd.in' in titulo:
        return None
    # Remove se for muito curto ou só emojis/símbolos
    titulo_limpo = re.sub(r'[^\w\s]', '', titulo)
    if len(titulo_limpo.strip()) < 5:
        return None
    # Remove frases genéricas
    frases_ignorar = ['link do instagram', 'vale a pena', 'passando na sua', 'ajudaria muito']
    if any(f in titulo.lower() for f in frases_ignorar):
        return None
    return titulo.strip()[:100]


def extrair_titulo_vaga(texto):
    """Extrai título da vaga do texto do post."""

    # Padrões específicos para cargos
    padroes_cargo = [
        # Vagas explícitas
        r'(?:vaga|oportunidade|contratando|hiring)[:\s\-]+(?:de\s+)?([A-Za-z][A-Za-z\s/\-]+(?:jr|pleno|sênior|senior|remoto)?)',
        # Designer com qualificador
        r'\b((?:product |ux |ui |ux/ui |ui/ux |service )?designer(?:\s+(?:jr|pleno|sênior|senior|remoto))?)\b',
        # Manager/Owner
        r'\b(product (?:manager|owner)(?:\s+(?:jr|pleno|sênior|senior))?)\b',
        # Head de área
        r'\b(head (?:de |of )?(?:produto|product|design|ux))\b',
        # UX Research
        r'\b(ux research(?:er)?)\b',
    ]

    texto_lower = texto.lower()
    for padrao in padroes_cargo:
        match = re.search(padrao, texto_lower)
        if match:
            titulo = match.group(1).strip()
            titulo = limpar_titulo(titulo)
            if titulo and len(titulo) > 5:
                # Capitaliza corretamente
                return titulo.title()

    # Busca em linhas específicas
    linhas = texto.split('\n')
    for linha in linhas[:10]:
        linha = linha.strip()
        linha_lower = linha.lower()

        # Pula linhas que são claramente não-títulos
        if linha.startswith('http') or len(linha) < 8 or len(linha) > 100:
            continue
        if any(x in linha_lower for x in ['instagram', 'curtir', 'comentar', 'seguir']):
            continue

        # Verifica se contém termos de cargo específicos (não só "designer")
        termos_especificos = ['ux', 'ui', 'product', 'manager', 'head de', 'head of', 'sênior', 'senior', 'pleno', 'júnior', 'junior', 'jr']
        if any(t in linha_lower for t in termos_especificos) and 'designer' in linha_lower:
            titulo = limpar_titulo(linha)
            if titulo and len(titulo) > 8:
                return titulo

    # Fallback: usa o tipo de vaga detectado
    tipo = classificar_tipo_vaga(texto)
    modalidade = classificar_modalidade(texto)
    if modalidade != 'nao_especificado':
        return f"{tipo} ({modalidade.title()})"
    return tipo


def extrair_empresa(texto):
    padroes = [r'(?:@|na|at)[:\s]+([A-Z][a-zA-Z0-9\s&\-\.]{2,30})']
    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            return match.group(1).strip()[:50]
    return None


def classificar_modalidade(texto):
    texto_lower = texto.lower()
    if 'remoto' in texto_lower or 'remote' in texto_lower:
        return 'remoto'
    elif 'híbrido' in texto_lower or 'hibrido' in texto_lower:
        return 'hibrido'
    elif 'presencial' in texto_lower:
        return 'presencial'
    return 'nao_especificado'


def classificar_tipo_vaga(texto):
    texto_lower = texto.lower()
    if "product manager" in texto_lower or "product owner" in texto_lower:
        return "Product Manager"
    elif "ux/ui" in texto_lower or "ui/ux" in texto_lower:
        return "UX/UI Designer"
    elif "ux designer" in texto_lower:
        return "UX Designer"
    elif "ui designer" in texto_lower:
        return "UI Designer"
    elif "product designer" in texto_lower:
        return "Product Designer"
    return "Product Designer"


def determinar_forma_contato(emails, links, texto):
    if emails:
        return 'email'
    if links:
        return 'link'
    return 'mensagem'


def scroll_e_extrair_posts(driver, max_scrolls=30):
    """Faz scroll e extrai posts de vagas."""
    posts_coletados = []
    textos_vistos = set()
    ultimo_count = 0
    ultimo_posts_pagina = 0

    print("Fazendo scroll e coletando posts...")

    # Clica no body para focar
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        body.click()
    except:
        pass

    for i in range(max_scrolls):
        # Usa Page Down para scroll (simula usuário)
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            for _ in range(5):
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.2)
        except:
            driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(1.5)

        # Pega texto da página
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
        except:
            continue

        # Divide por separador de posts
        partes = body_text.split("Publicação no feed")

        if i % 5 == 0:
            print(f"  Scroll {i+1}: {len(partes)-1} posts na página, {len(posts_coletados)} vagas coletadas")

        for parte in partes[1:]:
            texto = parte.split("Gostar")[0].strip()
            if len(texto) < 50:
                continue

            texto_hash = hash(texto[:200])
            if texto_hash in textos_vistos:
                continue
            textos_vistos.add(texto_hash)

            if not eh_post_produto(texto):
                continue

            # Extrai dados
            emails = extrair_emails(texto)
            links = extrair_links_externos(texto)
            titulo = extrair_titulo_vaga(texto)
            empresa = extrair_empresa(texto)
            modalidade = classificar_modalidade(texto)
            tipo_vaga = classificar_tipo_vaga(texto)
            forma_contato = determinar_forma_contato(emails, links, texto)

            # Extrai autor
            nome_autor = None
            linhas = texto.split('\n')
            for linha in linhas[:3]:
                if '•' in linha:
                    nome_autor = linha.split('•')[0].strip()
                    break

            posts_coletados.append({
                "titulo": titulo,
                "empresa": empresa,
                "tipo_vaga": tipo_vaga,
                "fonte": "linkedin_posts",
                "link_vaga": links[0] if links else None,
                "localizacao": None,
                "modalidade": modalidade,
                "requisito_ingles": "nao_especificado",
                "forma_contato": forma_contato,
                "email_contato": emails[0] if emails else None,
                "perfil_autor": None,
                "nome_autor": nome_autor,
                "data_coleta": date.today().isoformat(),
            })

            print(f"  + {titulo[:40]}... ({forma_contato})")

        # Para se não encontrou novos posts na página
        posts_pagina = len(partes) - 1
        if posts_pagina == ultimo_posts_pagina and i > 5:
            print("  Fim do conteúdo - sem novos posts carregados")
            break
        ultimo_posts_pagina = posts_pagina

    return posts_coletados


def coletar_vagas_linkedin_posts(max_scrolls=30, headless=False):
    """Coleta vagas de publicações do LinkedIn."""

    url = "https://www.linkedin.com/search/results/content/?keywords=ux%20vaga&datePosted=%22past-24h%22&sortBy=%22date_posted%22"
    driver = None

    try:
        driver = criar_driver_com_perfil(headless=headless)
        driver.get(url)
        time.sleep(5)

        print(f"URL: {driver.current_url}")
        print("Coletando publicações...")

        vagas = scroll_e_extrair_posts(driver, max_scrolls)

        print(f"\nTotal: {len(vagas)} vagas")
        return vagas

    except Exception as e:
        print(f"Erro: {e}")
        return []

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    vagas = coletar_vagas_linkedin_posts()
    print(f"\n{'='*50}")
    print(f"RESULTADO: {len(vagas)} vagas")
    for v in vagas[:10]:
        print(f"\n- {v['titulo']}")
        print(f"  Contato: {v['forma_contato']}")
