# PROJETO: PLATAFORMA DE VAGAS UX - BRIEFING COMPLETO
**Data:** 04/02/2026
**Desenvolvido por:** William Vieira
**Contexto:** Sistema automatizado de coleta e gerenciamento de vagas de produto (UX/UI/Product Design/Product Manager)

---

## 🎯 OBJETIVO DO PROJETO

Criar uma plataforma web que:
1. Coleta vagas automaticamente de Indeed, LinkedIn Vagas e LinkedIn Publicações
2. Filtra apenas vagas de PRODUTO (não dev/eng/qa)
3. Apresenta em dashboard minimalista
4. Permite filtros e gestão de candidaturas

---

## 👤 PERFIL DO USUÁRIO

**William Vieira**
- Senior Product Designer
- 18 anos de experiência
- Buscando: Vagas remotas (Brasil) ou híbridas (Rio de Janeiro)
- Requisito: Sem inglês fluente/avançado (até intermediário OK)

**Tipos de vaga aceitos:**
- Product Designer
- Product Manager
- UX Designer / UI Designer
- Service Designer
- Head de Produto
- Product Operations
- AI-Driven Product roles

**Tipos de vaga EXCLUÍDOS:**
- Desenvolvedor/Developer/Engineer
- QA/Tester
- Analista de Dados (puro)
- Designer Gráfico
- Marketing/Growth (sem "product")

---

## 📊 FONTES DE DADOS (3 FONTES)

### 1. INDEED BRASIL
**URL Base:** https://br.indeed.com/empregos?q=UX&l=Brasil&sc=0kf%3Aattr%28DSQF7%29%3B&fromage=last&lang=pt&remotejob=032b3046-06a3-4876-8dfd-474eb5e7ed11

**Filtros aplicados:**
- Termo: UX
- Local: Brasil
- Modalidade: Home Office (Remoto)
- Idioma: Português
- Últimas 24-48h
- Vagas não visualizadas (opcional)

**Dados coletados:**
- Título da vaga
- Empresa
- Link direto (vjk=XXXXX)
- Localização
- Requisitos de inglês (extrair do texto)

**Script atual:** Funcional via JavaScript no navegador

---

### 2. LINKEDIN - BUSCA DE VAGAS
**URL Base:** https://www.linkedin.com/jobs/search/?f_TPR=r86400&f_WT=2&keywords=ux

**Filtros aplicados:**
- Termo: UX
- Remoto: Sim (f_WT=2)
- Últimas 24h (f_TPR=r86400)
- Ordenação: Mais relevantes

**Desafio:** 
- Carrega apenas 7 vagas por página inicialmente
- Precisa scroll para carregar todas as 25 por página
- Tem TAG "Visualizado" para vagas já vistas

**Dados coletados:**
- Título da vaga
- Empresa
- Link direto (jobs/view/XXXXX)
- Localização
- Competências/Skills

**Status atual:** Script coleta apenas primeiras 7 vagas, precisa melhorar scroll

---

### 3. LINKEDIN - PUBLICAÇÕES
**URL Base:** https://www.linkedin.com/search/results/content/?keywords=ux%20vaga&datePosted=%5B%22past-24h%22%5D&sortBy=%5B%22date_posted%22%5D

**Características:**
- Posts de recrutadores com vagas
- Múltiplas vagas por post
- Formatos variados: Email | Link | "Fale comigo"

**Dados coletados:**
- Nome da vaga (extrair do texto)
- Empresa (quando mencionada)
- Localização (Remoto/Híbrido/Presencial/Não especificado)
- Email de contato (regex)
- Links externos (Gupy, Nerdin, etc)
- Perfil do autor (recrutador)
- Forma de contato: Email | Link | Mensagem LinkedIn

**Script atual:** Funcional! Coleta 28-44 vagas por execução

---

## 🗄️ ESTRUTURA DE DADOS

### Tabela: vagas

```sql
CREATE TABLE vagas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo VARCHAR(200) NOT NULL,
    empresa VARCHAR(100),
    tipo_vaga VARCHAR(50), -- Product Designer, Product Manager, UX Designer, etc
    fonte VARCHAR(20), -- 'indeed', 'linkedin_jobs', 'linkedin_posts'
    link_vaga TEXT,
    localizacao VARCHAR(100),
    modalidade VARCHAR(20), -- 'remoto', 'hibrido', 'presencial', 'nao_especificado'
    requisito_ingles VARCHAR(50), -- 'nenhum', 'basico', 'intermediario', 'fluente', 'nao_especificado'
    forma_contato VARCHAR(20), -- 'email', 'link', 'mensagem', 'indeed'
    email_contato VARCHAR(100),
    perfil_autor VARCHAR(200), -- Para LinkedIn posts
    nome_autor VARCHAR(100), -- Para LinkedIn posts
    data_coleta DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pendente', -- 'pendente', 'aplicada', 'descartada'
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fonte ON vagas(fonte);
CREATE INDEX idx_status ON vagas(status);
CREATE INDEX idx_data_coleta ON vagas(data_coleta);
CREATE INDEX idx_modalidade ON vagas(modalidade);
```

---

## 🤖 SCRIPTS DE COLETA

### Script 1: Indeed (JavaScript)
**Status:** ✅ Funcional
**Localização:** Executar no console do navegador

```javascript
// Coletar todas vagas Indeed
const vagas = [];
const jobCards = document.querySelectorAll('td.resultContent');

jobCards.forEach(card => {
  const titleLink = card.querySelector('h2 a, .jobTitle a');
  const companyElement = card.querySelector('.companyName');
  
  if (titleLink) {
    const titulo = titleLink.innerText.trim();
    const empresa = companyElement ? companyElement.innerText.trim() : '';
    const href = titleLink.href;
    const vjk = href.match(/vjk=([^&]+)/)?.[1] || '';
    
    vagas.push({
      titulo,
      empresa,
      link: `https://br.indeed.com/empregos?vjk=${vjk}`,
      fonte: 'indeed'
    });
  }
});

console.log(vagas);
```

---

### Script 2: LinkedIn Vagas (JavaScript)
**Status:** ⚠️ Parcial (precisa melhorar scroll)
**Localização:** Executar no console do navegador

```javascript
// Scroll e coleta
for (let i = 0; i < 20; i++) {
  window.scrollBy(0, 1000);
}

const vagas = [];
const links = document.querySelectorAll('a[href*="/jobs/view/"]');

links.forEach(link => {
  const jobId = link.href.match(/\/jobs\/view\/(\d+)/)?.[1];
  const titulo = link.getAttribute('aria-label') || link.innerText.trim();
  
  if (jobId && titulo) {
    vagas.push({
      titulo,
      link: `https://www.linkedin.com/jobs/view/${jobId}`,
      fonte: 'linkedin_jobs'
    });
  }
});
```

---

### Script 3: LinkedIn Publicações (JavaScript)
**Status:** ✅ Funcional completo
**Localização:** Ver arquivo `script_publicacoes_linkedin.js` nos outputs

**Resultado:** 28-44 vagas de produto por execução

---

## 🎨 REQUISITOS DE UI/UX

### Estilo Visual
- **Minimalista:** Sem frescura, direto ao ponto
- **Cores:** Neutro (preto/branco/cinza) + 1 cor destaque
- **Tipografia:** Sans-serif moderna (Inter, Roboto)
- **Layout:** Cards simples, grid responsivo
- **Mobile-first:** Funcionar bem em mobile

### Componentes Principais

1. **Dashboard Principal**
   - Cards de vagas (título, empresa, local, status)
   - Filtros laterais (sempre visíveis em desktop)
   - Contador de vagas

2. **Filtros**
   - Por fonte (Indeed/LinkedIn Vagas/LinkedIn Posts)
   - Por modalidade (Remoto/Híbrido/Presencial)
   - Por tipo de vaga (dropdown)
   - Por requisito de inglês
   - Por status (Pendente/Aplicada/Descartada)

3. **Card de Vaga**
   ```
   [Tipo da Vaga Badge]
   
   Título da Vaga
   Empresa • Localização
   
   [Remoto] [Inglês: Intermediário]
   
   [Link] [Email] [Status]
   ```

4. **Modal de Detalhes**
   - Todas informações da vaga
   - Campo para observações
   - Botões de ação: Aplicar | Descartar | Link externo

---

## 💻 STACK TECNOLÓGICA RECOMENDADA

### Backend
**Linguagem:** Python 3.11+

**Framework:** FastAPI
- Rápido
- Async nativo
- Documentação automática (Swagger)
- Fácil de testar

**Banco de Dados:**
- **Inicial:** SQLite (desenvolvimento/MVP)
- **Produção:** PostgreSQL (escala)

**ORM:** SQLAlchemy

**Scheduler:** APScheduler (para coletas automáticas diárias)

**Scraping:** 
- Selenium (para LinkedIn - precisa JavaScript)
- Requests + BeautifulSoup (para Indeed - pode ser mais leve)

### Frontend
**Framework:** React 18+
- Componentização
- Estado gerenciado (Context API ou Zustand)
- React Router para navegação

**Styling:** Tailwind CSS
- Rápido para prototipar
- Utility-first
- Responsivo fácil

**Build:** Vite
- Mais rápido que CRA
- Dev server instantâneo

### DevOps
**Containerização:** Docker
**Deploy Backend:** Render ou Railway
**Deploy Frontend:** Vercel ou Netlify
**CI/CD:** GitHub Actions

---

## 📁 ESTRUTURA DE PASTAS

```
vagas-ux-platform/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── database.py          # DB connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── crud.py              # CRUD operations
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── vagas.py         # Endpoints de vagas
│   │   │   └── stats.py         # Estatísticas
│   │   └── scrapers/
│   │       ├── __init__.py
│   │       ├── indeed.py        # Scraper Indeed
│   │       ├── linkedin_jobs.py # Scraper LinkedIn vagas
│   │       ├── linkedin_posts.py# Scraper LinkedIn posts
│   │       └── scheduler.py     # Agendamento automático
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VagaCard.jsx
│   │   │   ├── Filtros.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   └── Modal.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   └── Config.jsx
│   │   ├── services/
│   │   │   └── api.js           # Axios config
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── scripts/
│   ├── migrate_initial_data.py  # Migrar vagas atuais
│   └── test_scrapers.py         # Testar scrapers
│
├── data/
│   └── vagas.db                 # SQLite (dev)
│
├── docs/
│   └── BRIEFING.md              # Este arquivo
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🚀 FLUXO DE DESENVOLVIMENTO (FASES)

### FASE 1: MVP Backend (3-5 dias)
1. Setup FastAPI + SQLite
2. Models e schemas
3. Endpoints básicos (CRUD vagas)
4. Migrar dados atuais (3 Indeed + 11 LinkedIn + 28 Posts)
5. Testar API com Postman/Thunder

### FASE 2: Scrapers Python (5-7 dias)
1. Converter script Indeed para Python
2. Converter script LinkedIn Vagas (Selenium)
3. Converter script LinkedIn Posts (Selenium)
4. Testar scrapers individualmente
5. Implementar scheduler (rodar 1x/dia)

### FASE 3: Frontend MVP (5-7 dias)
1. Setup React + Vite + Tailwind
2. Dashboard com lista de vagas
3. Componente VagaCard
4. Filtros básicos
5. Conectar com API

### FASE 4: Features Avançadas (7-10 dias)
1. Modal de detalhes
2. Sistema de status (aplicada/descartada)
3. Observações por vaga
4. Estatísticas (quantas aplicadas, por fonte, etc)
5. Exportar relatório

### FASE 5: Deploy (2-3 dias)
1. Dockerizar aplicação
2. Deploy backend (Render/Railway)
3. Deploy frontend (Vercel)
4. Configurar domínio (opcional)
5. Setup automação diária

**TOTAL ESTIMADO: 22-32 dias** (trabalho part-time)

---

## 🔧 COMO INICIAR NO CLAUDE CODE

### 1. Abrir Claude Code
- Abrir terminal
- Navegar para pasta de projetos: `cd ~/Projects`

### 2. Criar estrutura inicial
```bash
mkdir vagas-ux-platform
cd vagas-ux-platform
mkdir -p backend/app/api backend/app/scrapers frontend data docs scripts
```

### 3. Setup Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
pip install fastapi uvicorn sqlalchemy pydantic selenium beautifulsoup4 requests
pip freeze > requirements.txt
```

### 4. Setup Frontend
```bash
cd ../frontend
npm create vite@latest . -- --template react
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 5. Criar arquivo base API
```bash
cd ../backend/app
touch main.py database.py models.py schemas.py crud.py
```

### 6. Rodar backend
```bash
cd ../backend
uvicorn app.main:app --reload
```

### 7. Rodar frontend (outro terminal)
```bash
cd frontend
npm run dev
```

---

## 📝 DADOS INICIAIS PARA MIGRAÇÃO

### Indeed (3 vagas - JÁ APLICADAS)
1. Pessoa Design UX UI Sr - Avivatec
2. Product Owner Senior (Open Finance) - CI&T
3. Product Owner IA & Inovação - Grôwnt

### LinkedIn Vagas (11 vagas)
Ver arquivo: `Vagas_LinkedIn_Produto_04_02.txt`

### LinkedIn Publicações (28 vagas)
Ver arquivo: `Vagas_LinkedIn_Publicacoes_FINAL_04_02.txt`

**Total para migrar:** 42 vagas

---

## ⚠️ DESAFIOS TÉCNICOS CONHECIDOS

1. **LinkedIn precisa autenticação**
   - Selenium precisa fazer login
   - Usar cookies salvos ou credenciais
   - Rate limiting: não fazer mais de 1 coleta/hora

2. **Indeed bloqueia bots**
   - Usar headers realistas
   - Delay entre requests
   - Selenium pode ser necessário

3. **Scroll infinito LinkedIn**
   - Implementar scroll automático confiável
   - Aguardar carregamento de conteúdo dinâmico

4. **Filtro de vagas de produto**
   - Lógica complexa (incluir/excluir termos)
   - Pode haver falsos positivos
   - Permitir ajuste manual

5. **Duplicatas**
   - Mesma vaga em múltiplas fontes
   - Usar hash do título+empresa+link
   - Marcar como "duplicata" em vez de criar novo registro

---

## 🎯 CRITÉRIOS DE SUCESSO

### MVP (Mínimo Viável)
- ✅ 3 fontes funcionando
- ✅ Banco de dados com 40+ vagas
- ✅ Dashboard mostrando vagas
- ✅ Filtros funcionando
- ✅ Marcar status (pendente/aplicada/descartada)

### V1.0 (Versão Completa)
- ✅ Coleta automática diária
- ✅ Notificações de novas vagas
- ✅ Exportar relatório
- ✅ Estatísticas
- ✅ Deploy em produção

---

## 📞 CONTATO E INFORMAÇÕES

**Email (para testes):** williamvieira.vagas@gmail.com
**Phone:** +55 24 98121-9442
**Localização:** Rio de Janeiro, RJ, Brasil

---

## 🔗 ARQUIVOS DE REFERÊNCIA

**Localizados em:** `/mnt/user-data/outputs/`

1. `Vagas_Indeed_04_02.txt` - 3 vagas Indeed
2. `Vagas_LinkedIn_Produto_04_02.txt` - 11 vagas LinkedIn
3. `Vagas_LinkedIn_Publicacoes_FINAL_04_02.txt` - 28 vagas publicações
4. `script_publicacoes_linkedin.js` - Script completo de coleta

---

**ESTE DOCUMENTO É A BASE COMPLETA PARA INICIAR O DESENVOLVIMENTO NO CLAUDE CODE.**

**Última atualização:** 04/02/2026
**Status:** Pronto para desenvolvimento
