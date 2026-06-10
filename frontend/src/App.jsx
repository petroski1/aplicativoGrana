import { useWebSocket } from './hooks/useWebSocket'
import CandleChart from './components/CandleChart'
import BotStatus from './components/BotStatus'
import Stats from './components/Stats'
import TradeHistory from './components/TradeHistory'
import Controls from './components/Controls'

export default function App() {
  const { connected, status, candles, trades, stats, lastDecision, balance, mode, asset, sendMessage } = useWebSocket()

  return (
    <div className="min-h-screen bg-gray-950 text-white p-3 md:p-4">
      <div className="max-w-screen-2xl mx-auto space-y-3">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-lg">⚡</div>
            <div>
              <h1 className="text-lg font-bold text-white">Trading Bot IA</h1>
              <p className="text-xs text-gray-500">Powered by Claude AI</p>
            </div>
          </div>
          <div className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-full border ${
            connected
              ? 'border-green-500/50 bg-green-500/10 text-green-400'
              : 'border-red-500/50 bg-red-500/10 text-red-400'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
            {connected ? 'Conectado' : 'Sem conexão'}
          </div>
        </div>

        {/* Chart */}
        <div className="bg-gray-900 rounded-xl border border-gray-700 overflow-hidden" style={{ height: '420px' }}>
          <div className="px-4 py-2 border-b border-gray-700 flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-300">
              {asset?.replace('frx', '')} — M1
            </span>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1">
                <span className="w-3 h-0.5 bg-blue-400 inline-block" /> EMA 9
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-0.5 bg-yellow-400 inline-block" /> EMA 21
              </span>
            </div>
          </div>
          <div style={{ height: 'calc(100% - 41px)' }}>
            <CandleChart candles={candles} />
          </div>
        </div>

        {/* Middle row: Status + Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="md:col-span-1">
            <BotStatus
              status={status}
              mode={mode}
              asset={asset}
              connected={connected}
              lastDecision={lastDecision}
            />
          </div>
          <div className="md:col-span-2">
            <Stats stats={stats} balance={balance} />
          </div>
        </div>

        {/* Bottom row: History + Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="md:col-span-2">
            <TradeHistory trades={trades} />
          </div>
          <div className="md:col-span-1">
            <Controls
              status={status}
              mode={mode}
              asset={asset}
              sendMessage={sendMessage}
            />
          </div>
        </div>

      </div>
    </div>
  )
}
