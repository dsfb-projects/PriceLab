# PriceLab — Contexto do Projeto

## O que é

Projeto acadêmico (FAE) chamado **PriceLab** — laboratório de precificação para consultoria de franquias.
Analisa três tipos de serviço: **Expansão**, **Formatação** e **Validação**.
Metodologia: regressão OLS com `statsmodels` (não sklearn) — um modelo por serviço.

O arquivo de referência estatística é `bases/regressão - código final (Leo).py` — código do Léo, intocável em lógica. O backend é um wrapper em torno dele.

## Arquitetura

```
Expandir_Framework/
├── backend/          ← Django REST API
│   ├── app/
│   │   ├── models.py       ← UploadedBase + ResultadoRegressao
│   │   ├── views.py        ← upload_base, resultados_latest
│   │   ├── regression.py   ← OLS por serviço (wrapper do código do Léo)
│   │   └── migrations/
│   └── projeto/
│       ├── settings.py     ← rest_framework, corsheaders, MEDIA_ROOT
│       └── urls.py         ← /api/upload/ e /api/resultados/
├── frontend/
│   └── index.html    ← SPA vanilla JS/CSS, chama API via fetch
├── bases/            ← arquivos Excel de referência + código do Léo
└── requirements.txt
```

## APIs implementadas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/upload/` | Recebe `.xlsx`, roda regressão, salva SQLite, retorna coeficientes |
| GET | `/api/resultados/` | Retorna resultado da última base enviada + preview do df |

Frontend usa `const API_BASE = 'http://localhost:8000'` no topo do JS.

## Como rodar

```bash
cd backend
python manage.py runserver
```

Depois abrir `frontend/index.html` direto no browser (ou `python -m http.server` na pasta frontend).

## Estado atual do desenvolvimento

**Implementado e funcionando:**
- Backend completo: upload, regressão OLS, persistência SQLite
- Frontend: SPA com Visão Geral, páginas por serviço, Calculadora, Upload
- Toggle Gerencial/Técnico (CSS class `mgmt-mode` no body — gerencial é o padrão)
- Preview do dataframe carregado aparece na aba Visão Geral
- Preço ideal com margem 6% (conforme código final do Léo)

**Pendente / com problema conhecido:**
- Importação do Excel ainda falha em alguns casos (bases com formato/aba diferente) — o `carregar_df()` em `regression.py` tem fallback de múltiplas abas mas pode não cobrir todos os casos
- Frontend ainda mostra valores hardcoded nas páginas de serviço (Expansão, Formatação, Validação) — precisam ser substituídos por valores dinâmicos da API após upload
- Rebranding para PriceLab ainda não foi aplicado (logo, títulos, textos)

## Regras importantes

- **Não alterar a lógica estatística** de `regression.py` — apenas o wrapper. A lógica OLS vem do Léo.
- Margem alvo é **6%** (não 30% — era um valor antigo do mock).
- Backend e frontend são **separados** — frontend não é servido pelo Django.
- CORS está habilitado para todas as origens (`CORS_ALLOW_ALL_ORIGINS = True`) — dev only, ok para contexto acadêmico.
- É projeto acadêmico: **simplicidade > perfeição**. Não overengineer.

## Stack

- Backend: Python 3.x, Django 4.2+, Django REST Framework, statsmodels, pandas, openpyxl
- Frontend: HTML/CSS/JS vanilla, Chart.js, fontes Google (DM Serif Display, DM Mono, Sora)
- DB: SQLite (dev/academic — não mudar para Postgres)
- Tema: dark mode (`--bg: #0d0f14`), cores por serviço: azul (Expansão), verde (Formatação), amarelo (Validação)

## Próximos passos sugeridos

1. Fixar o erro de importação do Excel (`carregar_df` em `regression.py`)
2. Aplicar rebranding PriceLab no frontend (logo, título da aba, subtítulo)
3. Traduzir termos técnicos no modo Gerencial ("Curvas de Elasticidade" → "Análise de Sensibilidade")
4. Conectar valores dinâmicos da API nas páginas de cada serviço (hoje estão hardcoded)
5. Reskin visual com tema "laboratório de precificação" — usuário tem plugins Figma/front instalados no Claude Code desktop para ajudar nisso
