import { useEffect, useRef } from 'react'
import { createChart, CrosshairMode } from 'lightweight-charts'

export default function CandleChart({ candles }) {
  const containerRef = useRef(null)
  const chartRef = useRef(null)
  const candleSeriesRef = useRef(null)
  const ema9SeriesRef = useRef(null)
  const ema21SeriesRef = useRef(null)

  useEffect(() => {
    if (!containerRef.current) return

    const chart = createChart(containerRef.current, {
      layout: {
        background: { color: '#0f1117' },
        textColor: '#9ca3af',
      },
      grid: {
        vertLines: { color: '#1f2937' },
        horzLines: { color: '#1f2937' },
      },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: { borderColor: '#374151' },
      timeScale: {
        borderColor: '#374151',
        timeVisible: true,
        secondsVisible: false,
      },
      handleScroll: { mouseWheel: true, pressedMouseMove: true },
      handleScale: { mouseWheel: true, pinch: true },
    })

    const candleSeries = chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    })

    const ema9Series = chart.addLineSeries({
      color: '#3b82f6',
      lineWidth: 1,
      title: 'EMA9',
    })

    const ema21Series = chart.addLineSeries({
      color: '#f59e0b',
      lineWidth: 1,
      title: 'EMA21',
    })

    chartRef.current = chart
    candleSeriesRef.current = candleSeries
    ema9SeriesRef.current = ema9Series
    ema21SeriesRef.current = ema21Series

    const handleResize = () => {
      chart.applyOptions({ width: containerRef.current.clientWidth })
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [])

  useEffect(() => {
    if (!candleSeriesRef.current || !candles || candles.length === 0) return

    const sorted = [...candles].sort((a, b) => a.time - b.time)

    const candleData = sorted.map(c => ({
      time: c.time,
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close,
    }))

    candleSeriesRef.current.setData(candleData)

    // Calculate simple EMA for display
    const ema9Data = calculateEMA(sorted, 9)
    const ema21Data = calculateEMA(sorted, 21)

    ema9SeriesRef.current.setData(ema9Data)
    ema21SeriesRef.current.setData(ema21Data)

    chartRef.current.timeScale().scrollToRealTime()
  }, [candles])

  return (
    <div className="w-full h-full bg-gray-900 rounded-lg overflow-hidden">
      <div ref={containerRef} className="w-full h-full" />
    </div>
  )
}

function calculateEMA(candles, period) {
  if (candles.length < period) return []
  const k = 2 / (period + 1)
  const result = []
  let ema = candles.slice(0, period).reduce((sum, c) => sum + c.close, 0) / period
  result.push({ time: candles[period - 1].time, value: ema })
  for (let i = period; i < candles.length; i++) {
    ema = candles[i].close * k + ema * (1 - k)
    result.push({ time: candles[i].time, value: parseFloat(ema.toFixed(6)) })
  }
  return result
}
