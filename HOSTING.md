# PriceLab — Como Subir para Acesso Externo

## Opção A — Cloudflare Tunnel (principal)

Link público permanente enquanto o PC estiver ligado. Grátis, sem conta necessária.

### Instalação (fazer uma vez em cada PC)

1. Baixar o `cloudflared` para Windows:
   https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe

2. Renomear o arquivo baixado para `cloudflared.exe`

3. Mover para uma pasta no PATH — o mais simples é colocar em:
   `C:\Windows\System32\cloudflared.exe`
   (ou em qualquer pasta e adicionar ao PATH manualmente)

4. Testar no terminal:
   ```
   cloudflared --version
   ```
   Deve aparecer a versão.

### Usar (toda vez que for apresentar)

**Opção fácil:** Dar dois cliques em `iniciar.bat` na raiz do projeto.

**Opção manual:**
```bash
# Terminal 1 — backend
cd backend
python manage.py runserver

# Terminal 2 — túnel
cloudflared tunnel --url http://localhost:8000
```

O terminal do tunnel vai mostrar uma linha como:
```
INF  +--------------------------------------------------------------------------------------------+
INF  |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
INF  |  https://xxxx-xxxx-xxxx.trycloudflare.com                                                  |
INF  +--------------------------------------------------------------------------------------------+
```

Copie esse link e compartilhe. Funciona de qualquer rede.

### Atualizar o frontend para apontar para o túnel

No arquivo `frontend/index.html`, perto do topo do `<script>`, troque:
```js
const API_BASE = 'http://localhost:8000';
```
Por:
```js
const API_BASE = 'https://SEU-LINK.trycloudflare.com';
```

---

## Opção B — ngrok (backup)

Usar se o Cloudflare não funcionar na rede da faculdade.

### Instalação

1. Criar conta gratuita em https://ngrok.com
2. Baixar ngrok para Windows e extrair
3. Autenticar: `ngrok config add-authtoken SEU_TOKEN`

### Usar

```bash
ngrok http 8000
```

Vai gerar uma URL tipo `https://xxxx.ngrok-free.app`. Copiar e usar no `API_BASE` do frontend.

---

## Dica para a apresentação

- Deixar o `iniciar.bat` na área de trabalho
- Atualizar o `API_BASE` no frontend antes de abrir para o público
- Se trocar de máquina (Wellington → Léo), basta rodar o `iniciar.bat` no PC do Léo e atualizar o link no frontend
