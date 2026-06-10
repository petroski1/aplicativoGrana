export default function BotStatus({ status, mode, asset, connected, lastDecision }) {
  const statusConfig = {
    RODANDO: { bg: 'bg-green-500/20', border: 'border-green-500', text: 'text-green-400', dot: 'bg-green-400' },
    PARADO: { bg: 'bg-gray-500/20', border: 'border-gray-500', text: 'text-gray-400', dot: 'bg-gray-400' },
    ERRO: { bg: 'bg-red-500/20', border: 'border-red-500', text: 'text-red-400', dot: 'bg-red-400' },
  }

  const cfg = statusConfig[status] || statusConfig.PARADO

  const decisionColor = {
    CALL: 'text-green-400 bg-green-500/20 border-green-500',
    PUT: 'text-red-400 bg-red-500/20 border-red-500',
    AGUARDAR: 'text-yellow-400 bg-yellow-500/20 border-yellow-500',
  }

  return (
    <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-4 space-y-3">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Status do Bot</h2>

      <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${cfg.bg} ${cfg.border}`}>
        <span className={`w-2 h-2 rounded-full ${cfg.dot} ${status === 'RODANDO' ? 'animate-pulse' : ''}`} />
        <span className={`font-bold text-lg ${cfg.text}`}>{status}</span>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div className="bg-gray-900/50 rounded-lg p-2">
          <p className="text-xs text-gray-500">Modo</p>
          <p className={`font-semibold text-sm ${mode === 'real' ? 'text-orange-400' : 'text-blue-400'}`}>
            {mode?.toUpperCase()}
          </p>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-2">
          <p className="text-xs text-gray-500">Ativo</p>
          <p className="font-semibold text-sm text-white">{asset?.replace('frx', '')}</p>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-2 col-span-2">
          <p className="text-xs text-gray-500">WebSocket</p>
          <p className={`font-semibold text-sm ${connected ? 'text-green-400' : 'text-red-400'}`}>
            {connected ? 'Conectado' : 'Desconectado'}
          </p>
        </div>
      </div>

      {lastDecision && (
        <div className="space-y-1">
          <p className="text-xs text-gray-500">Última Decisão IA</p>
          <div className={`border rounded-lg px-3 py-2 ${decisionColor[lastDecision.decision] || decisionColor.AGUARDAR}`}>
            <div className="flex items-center justify-between">
              <span className="font-bold">{lastDecision.decision}</span>
              <span className="text-xs opacity-70">{lastDecision.confidence}</span>
            </div>
            <p className="text-xs mt-1 opacity-80 line-clamp-2">{lastDecision.reason}</p>
          </div>
        </div>
      )}
    </div>
  )
}
