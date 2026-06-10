import anthropic
from config import settings


client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def build_prompt(indicators: dict, asset: str) -> str:
    rsi = indicators.get("rsi_14")
    ema9 = indicators.get("ema_9")
    ema21 = indicators.get("ema_21")
    close = indicators.get("close")
    macd = indicators.get("macd")
    macd_signal = indicators.get("macd_signal")
    macd_hist = indicators.get("macd_hist")
    bb_upper = indicators.get("bb_upper")
    bb_mid = indicators.get("bb_mid")
    bb_lower = indicators.get("bb_lower")
    trend = indicators.get("trend", "NEUTRO")

    rsi_status = "SOBRECOMPRADO" if rsi and rsi > 70 else ("SOBREVENDIDO" if rsi and rsi < 30 else "NEUTRO")
    bb_position = "N/A"
    if close and bb_upper and bb_lower:
        if close > bb_upper:
            bb_position = "ACIMA DA BANDA SUPERIOR (sobrecomprado)"
        elif close < bb_lower:
            bb_position = "ABAIXO DA BANDA INFERIOR (sobrevendido)"
        else:
            bb_position = "DENTRO DAS BANDAS"

    macd_cross = "N/A"
    if macd and macd_signal:
        if macd > macd_signal:
            macd_cross = "MACD ACIMA DO SINAL (momentum de alta)"
        else:
            macd_cross = "MACD ABAIXO DO SINAL (momentum de baixa)"

    prompt = f"""Você é um analista especialista em trading de opções binárias (forex). Analise os indicadores técnicos abaixo para o ativo {asset} e tome uma decisão de trading.

## Indicadores Técnicos Atuais

**Preço Atual:** {close}
**Tendência (EMA9 vs EMA21):** {trend}

**RSI (14):** {rsi} → {rsi_status}
**EMA 9:** {ema9}
**EMA 21:** {ema21}

**MACD:** {macd}
**Sinal MACD:** {macd_signal}
**Histograma MACD:** {macd_hist}
→ {macd_cross}

**Bollinger Bands (20):**
- Superior: {bb_upper}
- Média: {bb_mid}
- Inferior: {bb_lower}
→ Posição: {bb_position}

## Instruções de Análise

Analise a CONFLUÊNCIA dos indicadores:
1. RSI indica sobrecompra/sobrevenda?
2. As EMAs confirmam tendência?
3. MACD confirma o momentum?
4. Bollinger Bands indica reversão ou continuação?

## Formato de Resposta OBRIGATÓRIO

Responda EXATAMENTE neste formato:
DECISÃO: [CALL ou PUT ou AGUARDAR]
CONFIANÇA: [ALTA ou MÉDIA ou BAIXA]
JUSTIFICATIVA: [Explicação concisa em 2-3 frases sobre a confluência dos indicadores]

Regras:
- Use CALL quando os indicadores apontam para subida de preço
- Use PUT quando os indicadores apontam para queda de preço
- Use AGUARDAR quando os sinais são contraditórios ou inconclusos
- Prefira AGUARDAR em caso de dúvida"""

    return prompt


def analyze(indicators: dict, asset: str) -> dict:
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "your_anthropic_api_key_here":
        return {
            "decision": "AGUARDAR",
            "reason": "ANTHROPIC_API_KEY não configurada",
            "confidence": "BAIXA",
        }

    prompt = build_prompt(indicators, asset)

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()

    decision = "AGUARDAR"
    confidence = "BAIXA"
    reason = response_text

    for line in response_text.split("\n"):
        line = line.strip()
        if line.startswith("DECISÃO:"):
            val = line.split(":", 1)[1].strip().upper()
            if "CALL" in val:
                decision = "CALL"
            elif "PUT" in val:
                decision = "PUT"
            else:
                decision = "AGUARDAR"
        elif line.startswith("CONFIANÇA:"):
            val = line.split(":", 1)[1].strip().upper()
            if "ALTA" in val:
                confidence = "ALTA"
            elif "MÉDIA" in val or "MEDIA" in val:
                confidence = "MÉDIA"
            else:
                confidence = "BAIXA"
        elif line.startswith("JUSTIFICATIVA:"):
            reason = line.split(":", 1)[1].strip()

    return {
        "decision": decision,
        "reason": reason,
        "confidence": confidence,
    }
