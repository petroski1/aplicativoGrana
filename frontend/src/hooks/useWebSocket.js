import { useState, useEffect, useRef, useCallback } from 'react'

const WS_URL = 'ws://localhost:8765'

export function useWebSocket() {
  const [connected, setConnected] = useState(false)
  const [status, setStatus] = useState('PARADO')
  const [candles, setCandles] = useState([])
  const [trades, setTrades] = useState([])
  const [stats, setStats] = useState({})
  const [lastDecision, setLastDecision] = useState(null)
  const [balance, setBalance] = useState(0)
  const [mode, setMode] = useState('demo')
  const [asset, setAsset] = useState('frxEURUSD')

  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)
  const reconnectDelay = useRef(1000)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      reconnectDelay.current = 1000
      clearTimeout(reconnectTimer.current)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.status !== undefined) setStatus(data.status)
        if (data.candles !== undefined) setCandles(data.candles)
        if (data.recent_trades !== undefined) setTrades(data.recent_trades)
        if (data.stats !== undefined) setStats(data.stats)
        if (data.last_decision !== undefined) setLastDecision(data.last_decision)
        if (data.balance !== undefined) setBalance(data.balance)
        if (data.mode !== undefined) setMode(data.mode)
        if (data.asset !== undefined) setAsset(data.asset)
      } catch (e) {
        console.error('Erro ao parsear mensagem WS:', e)
      }
    }

    ws.onclose = () => {
      setConnected(false)
      reconnectTimer.current = setTimeout(() => {
        reconnectDelay.current = Math.min(reconnectDelay.current * 2, 30000)
        connect()
      }, reconnectDelay.current)
    }

    ws.onerror = () => {
      ws.close()
    }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [connect])

  const sendMessage = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  return { connected, status, candles, trades, stats, lastDecision, balance, mode, asset, sendMessage }
}
