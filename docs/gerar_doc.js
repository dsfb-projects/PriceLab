const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageNumber, Header, Footer, ExternalHyperlink
} = require('docx');
const fs = require('fs');

// ── Helpers ──────────────────────────────────────────────────────────────────
const ACCENT = "1F3F6B";   // azul escuro
const LIGHT  = "E8EDF5";   // fundo leve p/ cabeçalho de tabela
const GRAY   = "F5F5F5";   // linha alternada
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 100, bottom: 100, left: 160, right: 160 };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 120 },
    children: [new TextRun({ text, bold: true, size: 32, color: ACCENT, font: "Arial" })],
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 80 },
    children: [new TextRun({ text, bold: true, size: 26, color: "2C2C2C", font: "Arial" })],
  });
}

function body(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 120 },
    children: [new TextRun({ text, size: 22, font: "Arial", ...opts })],
  });
}

function code(text) {
  return new Paragraph({
    spacing: { after: 80, before: 80 },
    indent: { left: 720 },
    children: [new TextRun({ text, font: "Courier New", size: 20, color: "3A3A3A" })],
    shading: { fill: "F0F0F0", type: ShadingType.CLEAR },
  });
}

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 80 },
    children: [new TextRun({ text, size: 22, font: "Arial" })],
  });
}

function divider() {
  return new Paragraph({
    spacing: { before: 200, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "DDDDDD", space: 1 } },
    children: [],
  });
}

function tableHeader(cells) {
  return new TableRow({
    tableHeader: true,
    children: cells.map(text =>
      new TableCell({
        borders, margins: cellMargins,
        shading: { fill: ACCENT, type: ShadingType.CLEAR },
        children: [new Paragraph({
          children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 20, font: "Arial" })],
        })],
      })
    ),
  });
}

function tableRow(cells, shade = false) {
  return new TableRow({
    children: cells.map(text =>
      new TableCell({
        borders, margins: cellMargins,
        shading: { fill: shade ? GRAY : "FFFFFF", type: ShadingType.CLEAR },
        children: [new Paragraph({
          children: [new TextRun({ text, size: 20, font: "Arial" })],
        })],
      })
    ),
  });
}

// ── Documento ─────────────────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "•",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } },
      }],
    }],
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: ACCENT },
        paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2C2C2C" },
        paragraph: { spacing: { before: 240, after: 80 }, outlineLevel: 1 } },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "1F3F6B", space: 1 } },
          children: [
            new TextRun({ text: "PriceLab", bold: true, font: "Arial", size: 22, color: ACCENT }),
            new TextRun({ text: "  —  Documentação Técnica", font: "Arial", size: 22, color: "888888" }),
          ],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [
            new TextRun({ text: "Página ", font: "Arial", size: 18, color: "888888" }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 18, color: "888888" }),
          ],
        })],
      }),
    },
    children: [

      // ── CAPA ──
      new Paragraph({ spacing: { before: 1200, after: 80 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "PriceLab", bold: true, size: 64, color: ACCENT, font: "Arial" })] }),
      new Paragraph({ spacing: { after: 80 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Laboratório de Precificação", size: 32, color: "666666", font: "Arial" })] }),
      new Paragraph({ spacing: { after: 80 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Documentação Técnica do Projeto", size: 24, color: "888888", font: "Arial" })] }),
      new Paragraph({ spacing: { after: 80 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "FAE Business School  |  2025", size: 22, color: "AAAAAA", font: "Arial" })] }),
      divider(),
      new Paragraph({ spacing: { after: 600 }, children: [] }),

      // ── 1. VISÃO GERAL ──
      h1("1. Visão Geral"),
      body("O PriceLab é um projeto acadêmico desenvolvido na FAE Business School com o objetivo de criar um laboratório de precificação para consultoria de franquias. A ferramenta analisa três tipos de serviço — Expansão, Formatação e Validação — e fornece recomendações de preço baseadas em dados históricos da operação."),
      body("A metodologia central é a regressão OLS (Ordinary Least Squares) implementada com a biblioteca statsmodels, rodando um modelo independente por tipo de serviço. A margem alvo padrão adotada é de 6%, conforme definição do negócio."),
      new Paragraph({ spacing: { after: 160 }, children: [] }),

      // ── 2. ARQUITETURA ──
      h1("2. Arquitetura"),
      body("O projeto é dividido em três camadas principais:"),
      new Paragraph({ spacing: { after: 80 }, children: [] }),

      new Table({
        width: { size: 9026, type: WidthType.DXA },
        columnWidths: [2200, 6826],
        rows: [
          tableHeader(["Camada", "Descrição"]),
          tableRow(["backend/", "API REST em Django 4.2+. Contém models, views, serializers e o módulo de regressão (regression.py)."], false),
          tableRow(["frontend/", "SPA (Single Page Application) em HTML/CSS/JS vanilla com Chart.js. Servida pelo próprio Django via TemplateView."], true),
          tableRow(["bases/", "Arquivos Excel de referência e o código estatístico original do Léo (intocável em lógica)."], false),
        ],
      }),
      new Paragraph({ spacing: { after: 160 }, children: [] }),

      h2("Estrutura de pastas"),
      code("Expandir_Framework/"),
      code("├── backend/"),
      code("│   ├── app/"),
      code("│   │   ├── models.py       ← UploadedBase + ResultadoRegressao"),
      code("│   │   ├── views.py        ← upload_base, resultados_latest"),
      code("│   │   ├── regression.py   ← OLS por serviço (wrapper do código do Léo)"),
      code("│   │   └── migrations/"),
      code("│   └── projeto/"),
      code("│       ├── settings.py     ← CORS, ALLOWED_HOSTS, TEMPLATES"),
      code("│       └── urls.py         ← rotas da API + frontend"),
      code("├── frontend/"),
      code("│   └── index.html          ← SPA completa"),
      code("├── bases/                  ← Excels + código do Léo"),
      code("├── iniciar.bat             ← sobe Django + Cloudflare Tunnel"),
      code("└── requirements.txt"),
      new Paragraph({ spacing: { after: 160 }, children: [] }),

      h2("Stack tecnológica"),
      new Table({
        width: { size: 9026, type: WidthType.DXA },
        columnWidths: [2500, 6526],
        rows: [
          tableHeader(["Componente", "Tecnologia"]),
          tableRow(["Backend", "Python 3.x, Django 4.2+, Django REST Framework"], false),
          tableRow(["Estatística", "statsmodels (OLS), pandas, numpy, scikit-learn (MAE)"], true),
          tableRow(["Frontend", "HTML5, CSS3, JavaScript vanilla, Chart.js"], false),
          tableRow(["Banco de dados", "SQLite (adequado para contexto acadêmico)"], true),
          tableRow(["Hospedagem", "Cloudflare Tunnel (link público) / ngrok (backup)"], false),
        ],
      }),
      new Paragraph({ spacing: { after: 160 }, children: [] }),

      // ── 3. APIs ──
      h1("3. Endpoints da API"),
      new Table({
        width: { size: 9026, type: WidthType.DXA },
        columnWidths: [1000, 2500, 5526],
        rows: [
          tableHeader(["Método", "Endpoint", "Descrição"]),
          tableRow(["POST", "/api/upload/", "Recebe arquivo .xlsx via multipart/form-data. Roda as três regressões OLS, persiste no SQLite e retorna coeficientes + preview do dataframe."], false),
          tableRow(["GET", "/api/resultados/", "Retorna os coeficientes do último upload realizado, junto com preview das primeiras 200 linhas do dataframe."], true),
          tableRow(["GET", "/", "Serve o frontend (index.html) via Django TemplateView."], false),
        ],
      }),
      new Paragraph({ spacing: { after: 120 }, children: [] }),
      body("Todos os endpoints aceitam requisições de qualquer origem (CORS_ALLOW_ALL_ORIGINS = True) — configuração adequada para o ambiente de desenvolvimento acadêmico."),
      new Paragraph({ spacing: { after: 160 }, children: [] }),

      // ── 4. MODELO DE DADOS ──
      h1("4. Modelo de Dados"),
      h2("UploadedBase"),
      new Table({
        width: { size: 9026, type: WidthType.DXA },
        columnWidths: [2500, 2500, 4026],
        rows: [
          tableHeader(["Campo", "Tipo Django", "Descrição"]),
          tableRow(["arquivo", "FileField", "Arquivo Excel enviado, salvo em media/bases/"], false),
          tableRow(["enviado_em", "DateTimeField", "Timestamp do upload (auto_now_add=True)"], true),
        ],
      }),
      new Paragraph({ spacing: { after: 160 }, children: [] }),

      h2("ResultadoRegressao"),
      new Table({
        width: { size: 9026, type: WidthType.DXA },
        columnWidths: [2500, 2500, 4026],
        rows: [
          tableHeader(["Campo", "Tipo Django", "Descrição"]),
          tableRow(["base", "ForeignKey", "Referência ao UploadedBase (CASCADE)"], false),
          tableRow(["servico", "CharField", "'expansao' | 'formatacao' | 'validacao'"], true),
          tableRow(["beta0 – beta3", "FloatField", "Coeficientes do modelo OLS (Y = Total_Custos)"], false),
          tableRow(["beta4", "FloatField (null)", "Coeficiente de H_Advogado (só Formatação)"], true),
          tableRow(["r2 / r2_ajustado", "FloatField", "R² e R² ajustado do modelo de custo"], false),
          tableRow(["mae", "FloatField", "Mean Absolute Error do ajuste"], true),
          tableRow(["elasticidades", "JSONField", "Dict com elasticidade pontual de cada variável"], false),
          tableRow(["custo_por_contrato", "FloatField", "Custo médio previsto por contrato"], true),
          tableRow(["preco_ideal_6", "FloatField", "Preço ideal para margem de 6%"], false),
          tableRow(["margem_observada", "FloatField", "Margem % média observada no período"], true),
        ],
      }),
      new Paragraph({ spacing: { after: 160 }, children: [] }),

      // ── 5. PIPELINE DE REGRESSÃO ──
      h1("5. Pipeline de Regressão"),
      body("O módulo regression.py encapsula o código estatístico do Léo. O fluxo de execução a cada upload é:"),
      new Paragraph({ spacing: { after: 80 }, children: [] }),
      bullet("carregar_df() — tenta múltiplos nomes de aba Excel (4_Base_Regressao, Sheet1, Planilha1…) e valida as colunas obrigatórias."),
      bullet("Validação de colunas obrigatórias: Mês, Franquia, Tipo_Servico, Qtd_Contratos, H_Total, Total_Custos, Receita_Total, Margem_RS."),
      bullet("Normalização de nomes de serviço (remove variações de acentuação, capitalização e espaços)."),
      bullet("agregar() — agrupa os dados por Mês × Franquia, somando receita, custos, horas e contratos."),
      bullet("rodar_ols() — ajusta dois modelos OLS: Y = Total_Custos (base para precificação) e Y = Margem_PCT (diagnóstico de rentabilidade)."),
      bullet("elasticidades() — calcula ε = β × (X̄ / Ȳ) para cada variável, avaliado na média do período."),
      bullet("preco_ideal() — Preço ideal = Custo previsto por contrato ÷ (1 − 0,06)."),
      new Paragraph({ spacing: { after: 160 }, children: [] }),

      h2("Variáveis por serviço"),
      new Table({
        width: { size: 9026, type: WidthType.DXA },
        columnWidths: [2500, 6526],
        rows: [
          tableHeader(["Serviço", "Variáveis independentes"]),
          tableRow(["Expansão", "Qtd_Contratos, H_Total, Num_Mes"], false),
          tableRow(["Validação", "Qtd_Contratos, H_Total, Num_Mes"], true),
          tableRow(["Formatação", "Qtd_Contratos, H_Total, H_Advogado, Num_Mes"], false),
        ],
      }),
      new Paragraph({ spacing: { after: 160 }, children: [] }),

      // ── 6. HOSPEDAGEM ──
      h1("6. Hospedagem"),
      body("O projeto utiliza Cloudflare Tunnel para expor o servidor local na internet sem necessidade de configurar firewall ou contratar um host externo."),
      new Paragraph({ spacing: { after: 80 }, children: [] }),
      bullet("Executar iniciar.bat sobe o Django (porta 8000) e o tunnel simultaneamente."),
      bullet("O terminal do tunnel exibe um link .trycloudflare.com único e funcional de qualquer rede."),
      bullet("O frontend é servido pelo próprio Django (rota /), de modo que um único link cobre toda a aplicação."),
      bullet("Backup: ngrok http 8000 gera um link alternativo caso a rede da apresentação bloqueie o Cloudflare."),
      new Paragraph({ spacing: { after: 120 }, children: [] }),
      body("Comando do tunnel:", { bold: true }),
      code("cloudflared tunnel --url http://localhost:8000"),
      new Paragraph({ spacing: { after: 160 }, children: [] }),

      // ── 7. COMO RODAR ──
      h1("7. Como Rodar Localmente"),
      body("Pré-requisitos: Python 3.x, pacotes em requirements.txt instalados."),
      new Paragraph({ spacing: { after: 80 }, children: [] }),
      bullet("Instalar dependências: pip install -r requirements.txt"),
      bullet("Subir o servidor: cd backend && python manage.py runserver"),
      bullet("Acessar: abrir http://localhost:8000 no navegador, ou usar o link do Cloudflare Tunnel para acesso externo."),
      bullet("Alternativa rápida: dois cliques em iniciar.bat — sobe Django + Tunnel automaticamente."),
      new Paragraph({ spacing: { after: 160 }, children: [] }),

      // ── 8. PENDÊNCIAS ──
      h1("8. Pendências e Próximos Passos"),
      new Table({
        width: { size: 9026, type: WidthType.DXA },
        columnWidths: [500, 3000, 5526],
        rows: [
          tableHeader(["#", "Item", "Descrição"]),
          tableRow(["a", "Fix importação Excel", "Cobrir casos de Excel com formato ou aba fora do padrão previsto no carregar_df()."], false),
          tableRow(["b", "Rebranding visual PriceLab", "Aplicar identidade visual completa via Figma: logo, paleta de cores, tipografia."], true),
          tableRow(["c", "Valores dinâmicos no frontend", "Substituir valores hardcoded nas páginas de Expansão, Formatação e Validação por dados retornados pela API."], false),
          tableRow(["d", "Tradução modo Gerencial", "Renomear termos técnicos na visão gerencial (ex.: 'Curvas de Elasticidade' → 'Análise de Sensibilidade')."], true),
        ],
      }),
      new Paragraph({ spacing: { after: 400 }, children: [] }),
      divider(),
      new Paragraph({ spacing: { after: 80 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "PriceLab  |  FAE Business School  |  2025", size: 18, color: "AAAAAA", font: "Arial" })] }),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("C:\\Users\\welli\\OneDrive\\Documentos\\FAE\\Expandir_Framework\\docs\\PriceLab_Documentacao.docx", buf);
  console.log("Documento gerado com sucesso!");
});
