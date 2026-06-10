import { useState } from 'react'

const ASSETS = [
  { value: 'frxEURUSD', label: 'EUR/USD' },
  { value: 'frxGBPUSD', label: 'GBP/USD' },
  { value: 'frxUSDJPY', label: 'USD/JPY' },
  { value: 'frxAUDUSD', label: 'AUD/USD' },
  { value: 'R_100', label: 'Volatility 100' },
  { value: 'R_50', label: 'Volatility 50' },
]

export default function Controls({ status, mode, asset, sendMessage }) {
  const [tradeValue, setTradeValue] = useState('1.00')
  const [localAsset, setLocalAsset] = useState(asset || 'frxEURUSD')
  const [localMode, setLocalMode] = useState(mode || 'demo')

  const isRunning = status === 'RODANDO'

  const handleToggle = () => {
    sendMessage({ action: isRunning ? 'stop' : 'start' })
  }

  const handleConfig = () => {
    sendMessage({
      action: 'config',
      asset: localAsset,
      trade_value: parseFloat(tradeValue) || 1,
      mode: localMode,
    })
  }

  return (
    <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-4 space-y-4">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Controles</h2>

      <button
        onClick={handleToggle}
        className={`w-full py-3 rounded-xl font-bold text-lg transition-all ${
          isRunning
            ? 'bg-red-600 hover:bg-red-700 text-white'
            : 'bg-green-600 hover:bg-green-700 text-white'
        }`}
      >
        {isRunning ? '⏹ Parar Bot' : '▶ Iniciar Bot'}
      </button>

      <div className="space-y-3">
        <div>
          <label className="text-xs text-gray-500 block mb-1">Valor por Operação (USD)</label>
          <input
            type="number"
            min="1"
            step="0.5"
            value={tradeValue}
            onChange={(e) => setTradeValue(e.target.value)}
            className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="text-xs text-gray-500 block mb-1">Ativo</label>
          <select
            value={localAsset}
            onChange={(e) => setLocalAsset(e.target.value)}
            className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
          >
            {ASSETS.map((a) => (
              <option key={a.value} value={a.value}>{a.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs text-gray-500 block mb-1">Modo</label>
          <div className="flex gap-2">
            {['demo', 'real'].map((m) => (
              <button
                key={m}
                onClick={() => setLocalMode(m)}
                className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${
                  localMode === m
                    ? m === 'real'
                      ? 'bg-orange-600 text-white'
                      : 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                }`}
              >
                {m.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={handleConfig}
          className="w-full py-2 bg-gray-700 hover:bg-gray-600 text-gray-200 rounded-lg text-sm font-semibold transition-all"
        >
          Aplicar Configurações
        </button>
      </div>
    </div>
  )
}
