function StatCard({ label, value, sub, positive }) {
  const color = positive === true ? 'text-green-400' : positive === false ? 'text-red-400' : 'text-white'
  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-4">
      <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  )
}

export default function Stats({ stats, balance }) {
  const winRate = stats?.win_rate ?? 0
  const totalPnl = stats?.total_pnl ?? 0
  const maxDrawdown = stats?.max_drawdown ?? 0
  const tradesToday = stats?.trades_today ?? 0
  const totalTrades = stats?.total_trades ?? 0

  return (
    <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-4">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Métricas</h2>
      <div className="grid grid-cols-2 gap-3">
        <StatCard
          label="Assertividade"
          value={`${winRate.toFixed(1)}%`}
          sub={`${stats?.wins ?? 0} / ${totalTrades} operações`}
          positive={winRate >= 50 ? true : winRate > 0 ? null : false}
        />
        <StatCard
          label="PnL Total"
          value={`$${totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(2)}`}
          positive={totalPnl > 0 ? true : totalPnl < 0 ? false : null}
        />
        <StatCard
          label="Saldo Atual"
          value={`$${balance.toFixed(2)}`}
        />
        <StatCard
          label="Drawdown Máx."
          value={`$${maxDrawdown.toFixed(2)}`}
          positive={maxDrawdown >= 0 ? null : false}
        />
        <StatCard
          label="Operações Hoje"
          value={tradesToday}
          sub={`${totalTrades} no total`}
        />
        <StatCard
          label="Wins / Losses"
          value={`${stats?.wins ?? 0} / ${(totalTrades - (stats?.wins ?? 0))}`}
        />
      </div>
    </div>
  )
}
