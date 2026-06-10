import logging
from datetime import datetime
from deriv_ws import deriv_ws
from risk_manager import risk_manager
from database import save_trade, update_trade_result, save_balance, get_consecutive_losses
from config import settings

logger = logging.getLogger(__name__)


class Executor:
    def __init__(self):
        self.daily_start_balance: float = 0.0
        self.trade_count_today: int = 0
        self._today: str = ""

    def _reset_daily_if_needed(self, balance: float):
        today = datetime.utcnow().date().isoformat()
        if today != self._today:
            self._today = today
            self.daily_start_balance = balance
            self.trade_count_today = 0

    async def execute(self, decision: str, reason: str, asset: str, amount: float, balance: float) -> dict:
        # Em modo demo com saldo zero, usa saldo simulado de 10000
        effective_balance = balance if balance > 0 else 10000.0
        self._reset_daily_if_needed(effective_balance)

        consecutive_losses = await get_consecutive_losses()
        current_hour = datetime.utcnow().hour

        allowed, risk_reason = risk_manager.check(
            balance=effective_balance,
            daily_start_balance=self.daily_start_balance,
            consecutive_losses=consecutive_losses,
            current_hour=current_hour,
        )

        if not allowed:
            logger.warning(f"Operação bloqueada: {risk_reason}")
            return {"blocked": True, "reason": risk_reason, "decision": decision}

        if decision == "AGUARDAR":
            return {"blocked": False, "reason": "IA decidiu aguardar", "decision": "AGUARDAR"}

        logger.info(f"Executando {decision} em {asset} por ${amount}")

        if settings.DERIV_TOKEN == "your_deriv_token_here" or not settings.DERIV_TOKEN:
            import random
            result_str = random.choice(["WIN", "LOSS"])
            pnl = amount * 0.85 if result_str == "WIN" else -amount
            trade_id = await save_trade(asset, decision, amount, result_str, pnl)
            logger.info(f"[SIMULAÇÃO] {result_str} | PnL: {pnl:.2f}")
            return {
                "blocked": False,
                "decision": decision,
                "result": result_str,
                "pnl": pnl,
                "asset": asset,
                "amount": amount,
                "simulated": True,
            }

        trade_id = await save_trade(asset, decision, amount)

        contract_result = await deriv_ws.buy_contract(asset, decision, amount, settings.TRADE_DURATION)

        if "error" in contract_result:
            logger.error(f"Erro na ordem: {contract_result['error']}")
            return {"blocked": False, "decision": decision, "error": contract_result["error"]}

        result_str = contract_result.get("result", "UNKNOWN")
        pnl = contract_result.get("pnl", 0.0)

        await update_trade_result(trade_id, result_str, pnl)

        new_balance = await deriv_ws.get_balance()
        await save_balance(new_balance)

        logger.info(f"Resultado: {result_str} | PnL: {pnl:.2f} | Saldo: {new_balance:.2f}")

        return {
            "blocked": False,
            "decision": decision,
            "result": result_str,
            "pnl": pnl,
            "asset": asset,
            "amount": amount,
            "balance": new_balance,
        }


executor = Executor()
