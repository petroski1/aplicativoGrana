from config import settings


class RiskManager:
    def check(
        self,
        balance: float,
        daily_start_balance: float,
        consecutive_losses: int,
        current_hour: int,
    ) -> tuple[bool, str]:
        if consecutive_losses >= settings.MAX_CONSECUTIVE_LOSSES:
            return False, f"Bloqueado: {consecutive_losses} losses consecutivos (limite: {settings.MAX_CONSECUTIVE_LOSSES})"

        if daily_start_balance > 0:
            daily_loss_pct = ((daily_start_balance - balance) / daily_start_balance) * 100
            if daily_loss_pct >= settings.MAX_DAILY_LOSS_PCT:
                return False, f"Bloqueado: perda diária de {daily_loss_pct:.1f}% (limite: {settings.MAX_DAILY_LOSS_PCT}%)"

        if not (settings.TRADING_HOURS_START <= current_hour < settings.TRADING_HOURS_END):
            return False, f"Bloqueado: fora do horário de trading ({settings.TRADING_HOURS_START}h-{settings.TRADING_HOURS_END}h)"

        return True, "OK"


risk_manager = RiskManager()
