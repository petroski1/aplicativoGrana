export default function TradeHistory({ trades }) {
  const formatTime = (ts) => {
    if (!ts) return '-'
    try {
      return new Date(ts).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    } catch {
      return ts
    }
  }

  return (
    <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-4 h-full">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
        Histórico de Operações
      </h2>
      <div className="overflow-auto max-h-64">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-500 text-xs uppercase">
              <th className="text-left pb-2">Hora</th>
              <th className="text-left pb-2">Ativo</th>
              <th className="text-left pb-2">Dir.</th>
              <th className="text-right pb-2">Valor</th>
              <th className="text-right pb-2">Resultado</th>
              <th className="text-right pb-2">PnL</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700/50">
            {trades.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center text-gray-500 py-6">
                  Nenhuma operação ainda
                </td>
              </tr>
            ) : (
              trades.map((trade) => {
                const isWin = trade.resultado === 'WIN'
                const isLoss = trade.resultado === 'LOSS'
                const rowClass = isWin ? 'bg-green-500/5' : isLoss ? 'bg-red-500/5' : ''
                return (
                  <tr key={trade.id} className={`${rowClass} hover:bg-gray-700/20 transition-colors`}>
                    <td className="py-1.5 text-gray-400">{formatTime(trade.timestamp)}</td>
                    <td className="py-1.5 text-gray-300">{trade.ativo?.replace('frx', '')}</td>
                    <td className="py-1.5">
                      <span className={`px-1.5 py-0.5 rounded text-xs font-bold ${
                        trade.direcao === 'CALL'
                          ? 'bg-green-500/20 text-green-400'
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {trade.direcao}
                      </span>
                    </td>
                    <td className="py-1.5 text-right text-gray-300">${trade.valor?.toFixed(2)}</td>
                    <td className="py-1.5 text-right">
                      {trade.resultado ? (
                        <span className={`px-1.5 py-0.5 rounded text-xs font-bold ${
                          isWin ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                        }`}>
                          {trade.resultado}
                        </span>
                      ) : (
                        <span className="text-yellow-400 text-xs">Pendente</span>
                      )}
                    </td>
                    <td className={`py-1.5 text-right font-mono text-xs ${
                      trade.pnl > 0 ? 'text-green-400' : trade.pnl < 0 ? 'text-red-400' : 'text-gray-500'
                    }`}>
                      {trade.pnl !== undefined ? `${trade.pnl >= 0 ? '+' : ''}$${trade.pnl?.toFixed(2)}` : '-'}
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
