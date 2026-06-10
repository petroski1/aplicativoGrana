# Trading Bot IA

Sistema de trading automatizado com análise de IA usando Claude + Deriv API.

## Requisitos

- Python 3.10+
- Node.js 18+
- Conta na [Deriv](https://deriv.com) (demo gratuito)
- Chave da [API Anthropic](https://console.anthropic.com)

## Instalação e Configuração

### 1. Configure o `.env`

Edite `backend/.env`:

```env
DERIV_TOKEN=seu_token_deriv_aqui
ANTHROPIC_API_KEY=sua_chave_anthropic_aqui
ASSET=frxEURUSD
TRADE_VALUE=1.0
MODE=demo
```

**Como obter o token Deriv:**
1. Acesse https://app.deriv.com/account/api-token
2. Crie um token com permissões de Leitura + Trading
3. Cole no campo `DERIV_TOKEN`

**Como obter a chave Anthropic:**
1. Acesse https://console.anthropic.com/keys
2. Crie uma nova chave de API
3. Cole no campo `ANTHROPIC_API_KEY`

### 2. Inicie o sistema

```bash
chmod +x start.sh
./start.sh
```

O script instala todas as dependências automaticamente e inicia backend + frontend.

### 3. Acesse o painel

- **No computador:** http://localhost:5173
- **No celular (mesma rede Wi-Fi):** http://[SEU-IP-LOCAL]:5173

## Estrutura

```
├── backend/
│   ├── main.py          # Ponto de entrada + FastAPI
│   ├── deriv_ws.py      # WebSocket persistente com Deriv
│   ├── indicators.py    # Cálculo de indicadores técnicos
│   ├── ai_analyst.py    # Análise com Claude AI
│   ├── risk_manager.py  # Gerenciamento de risco
│   ├── executor.py      # Execução de ordens
│   ├── ws_server.py     # WebSocket para frontend
│   ├── database.py      # SQLite (trades, decisões, saldo)
│   └── config.py        # Configurações
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── hooks/useWebSocket.js
│       └── components/
│           ├── CandleChart.jsx
│           ├── BotStatus.jsx
│           ├── Stats.jsx
│           ├── TradeHistory.jsx
│           └── Controls.jsx
├── requirements.txt
└── start.sh
```

## Configurações de Risco (em `config.py`)

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `MAX_CONSECUTIVE_LOSSES` | 3 | Para após N losses seguidos |
| `MAX_DAILY_LOSS_PCT` | 5% | Limite de perda diária |
| `TRADING_HOURS_START` | 8 | Hora de início (UTC) |
| `TRADING_HOURS_END` | 22 | Hora de término (UTC) |
| `TRADE_DURATION` | 5 | Duração do contrato (minutos) |

## Como Funciona

1. **Dados:** Conecta à Deriv via WebSocket e recebe candles OHLCV em tempo real
2. **Indicadores:** Calcula RSI(14), EMA(9/21), MACD(12,26,9), Bollinger Bands(20)
3. **IA:** Envia indicadores para o Claude, que retorna CALL/PUT/AGUARDAR
4. **Risco:** Verifica limites antes de executar
5. **Execução:** Envia ordem à Deriv e registra resultado
6. **Frontend:** Exibe tudo em tempo real via WebSocket local

## Modo Demo vs Real

- **Demo:** Usa conta demo da Deriv (dinheiro fictício). Ideal para testar.
- **Real:** Usa conta real. **Use com cautela e responsabilidade.**

> ⚠️ **Aviso:** Trading envolve risco de perda financeira. Use sempre modo demo primeiro.
