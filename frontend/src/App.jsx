import { useEffect, useMemo, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const formatPercent = (value) => `${(value * 100).toFixed(2)}%`
const formatNumber = (value) => value.toLocaleString('en-US')

const fetchJson = async (path, options) => {
  const response = await fetch(`${API_BASE}${path}`, options)
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }
  return response.json()
}

const LineChart = ({ series, height = 320, splitIndex = null, labels = [] }) => {
  const width = 600
  const padding = 24

  const allValues = series.flatMap((item) => item.data)
  const minValue = Math.min(...allValues)
  const maxValue = Math.max(...allValues)
  const spread = maxValue - minValue || 1

  const pointsFor = (data) =>
    data
      .map((value, index) => {
        const x = padding + (index / (data.length - 1 || 1)) * (width - padding * 2)
        const y =
          padding +
          (1 - (value - minValue) / spread) * (height - padding * 2)
        return `${x},${y}`
      })
      .join(' ')

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="w-full h-80"
      role="img"
      aria-label="Forecast chart"
    >
      <rect
        x="0"
        y="0"
        width={width}
        height={height}
        rx="16"
        fill="rgba(15, 23, 42, 0.06)"
      />
      {[0.25, 0.5, 0.75].map((ratio) => (
        <line
          key={ratio}
          x1={padding}
          x2={width - padding}
          y1={padding + ratio * (height - padding * 2)}
          y2={padding + ratio * (height - padding * 2)}
          stroke="rgba(148, 163, 184, 0.4)"
          strokeDasharray="6 6"
        />
      ))}
      {typeof splitIndex === 'number' && splitIndex >= 0 ? (
        <line
          x1={padding + (splitIndex / (series[0]?.data.length - 1 || 1)) * (width - padding * 2)}
          x2={padding + (splitIndex / (series[0]?.data.length - 1 || 1)) * (width - padding * 2)}
          y1={padding}
          y2={height - padding}
          stroke="rgba(15, 23, 42, 0.7)"
          strokeDasharray="2 6"
          strokeWidth="2"
        />
      ) : null}
      {series.map((item) => (
        <polyline
          key={item.label}
          fill="none"
          stroke={item.color}
          strokeWidth={item.muted ? '2' : '3'}
          strokeDasharray={item.dashed ? '8 6' : undefined}
          opacity={item.muted ? 0.6 : 1}
          points={pointsFor(item.data)}
        />
      ))}
      {labels.length ? (
        <g>
          {labels.map((label, index) => {
            const x = padding + (index / (labels.length - 1 || 1)) * (width - padding * 2)
            return (
              <g key={`${label}-${index}`}>
                <circle cx={x} cy={height - padding + 2} r="2" fill="rgba(15, 23, 42, 0.5)" />
                <text
                  x={x}
                  y={height - 6}
                  textAnchor="middle"
                  fontSize="10"
                  fill="rgba(15, 23, 42, 0.55)"
                >
                  {label}
                </text>
              </g>
            )
          })}
        </g>
      ) : null}
    </svg>
  )
}

const StatCard = ({ label, value, hint }) => (
  <div className="glass-panel rounded-2xl p-4">
    <p className="text-sm uppercase tracking-[0.2em] text-slate/60">{label}</p>
    <p className="text-3xl font-display text-ink mt-2">{value}</p>
    {hint ? <p className="text-sm text-slate/70 mt-2">{hint}</p> : null}
  </div>
)

const FeatureBars = ({ features, importances }) => (
  <div className="space-y-3">
    {features.map((feature, index) => (
      <div key={feature} className="space-y-1">
        <div className="flex justify-between text-sm text-slate/70">
          <span>{feature}</span>
          <span>{formatPercent(importances[index])}</span>
        </div>
        <div className="h-2 rounded-full bg-slate/10">
          <div
            className="h-2 rounded-full bg-cyan"
            style={{ width: `${Math.max(importances[index] * 100, 6)}%` }}
          ></div>
        </div>
      </div>
    ))}
  </div>
)

const ChartLegend = ({ items, columns = 2 }) => (
  <div
    className="grid gap-x-6 gap-y-3 text-xs uppercase tracking-[0.2em] text-slate/60"
    style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}
  >
    {items.map((item) => (
      <div key={item.label} className="flex items-center gap-2">
        <span
          className="h-0.5 w-8 rounded-full"
          style={{
            backgroundColor: item.color,
            borderTop: item.dashed ? `2px dashed ${item.color}` : 'none',
          }}
        ></span>
        <span>{item.label}</span>
      </div>
    ))}
  </div>
)

function App() {
  const [view, setView] = useState('evaluation')
  const [overview, setOverview] = useState(null)
  const [evaluation, setEvaluation] = useState(null)
  const [importance, setImportance] = useState(null)
  const [forecast, setForecast] = useState(null)
  const [simInput, setSimInput] = useState({
    gdpDelta: 0,
    inflationDelta: 0,
    lfprDelta: 0,
    populationDelta: 0,
    prevUnemploymentDelta: 0,
  })
  const [simResult, setSimResult] = useState(null)
  const [simLoading, setSimLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        const [overviewRes, evalRes, importanceRes, forecastRes] =
          await Promise.all([
            fetchJson('/api/overview'),
            fetchJson('/api/evaluation'),
            fetchJson('/api/feature-importance'),
            fetchJson('/api/forecast'),
          ])

        setOverview(overviewRes)
        setEvaluation(evalRes)
        setImportance(importanceRes)
        setForecast(forecastRes)
        setSimInput({
          gdpDelta: 0,
          inflationDelta: 0,
          lfprDelta: 0,
          populationDelta: 0,
          prevUnemploymentDelta: 0,
        })
        setSimResult(forecastRes)
      } catch (err) {
        setError(err.message)
      }
    }

    load()
  }, [])

  const handleSimulate = async (event) => {
    event.preventDefault()
    setSimLoading(true)
    try {
      const response = await fetchJson('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gdp_delta: simInput.gdpDelta,
          inflation_delta: simInput.inflationDelta,
          lfpr_delta: simInput.lfprDelta,
          population_delta: simInput.populationDelta,
          prev_unemployment_delta: simInput.prevUnemploymentDelta,
        }),
      })
      setSimResult(response)
    } catch (err) {
      setError(err.message)
    } finally {
      setSimLoading(false)
    }
  }

  const evaluationSeries = useMemo(() => {
    if (!evaluation) return []
    return [
      {
        label: 'Actual',
        data: evaluation.series.actual,
        color: '#0f172a',
      },
      {
        label: 'Baseline LR',
        data: evaluation.series.lr,
        color: '#fb7185',
        dashed: true,
      },
      {
        label: 'XGBoost',
        data: evaluation.series.xgb,
        color: '#2bd4bd',
      },
    ]
  }, [evaluation])

  const forecastSeries = useMemo(() => {
    if (!simResult) return []
      const history = simResult.recent_actuals
      const lastActual = simResult.recent_actuals.at(-1)
    const historyPrefix = history.slice(0, -1)
    const baseline = [...historyPrefix, lastActual, ...simResult.official.lr]
    const official = [...historyPrefix, lastActual, ...simResult.official.xgb]
    const simulated = [...historyPrefix, lastActual, ...simResult.simulated.xgb]
    return [
      {
        label: 'Baseline LR',
        data: baseline,
        color: '#f59e0b',
        dashed: true,
      },
      {
        label: 'Official XGBoost',
        data: official,
        color: '#2bd4bd',
      },
      {
        label: 'Simulated',
        data: simulated,
        color: '#fb7185',
        dashed: true,
      },
    ]
  }, [simResult])

  const forecastLabels = useMemo(() => {
    if (!simResult) return []
    const history = simResult.recent_actuals
    const historyLabels = history.map((_, index) => {
      const offset = history.length - 1 - index
      return offset === 0 ? 'Now' : `H-${offset}`
    })
    return [...historyLabels, ...simResult.quarters]
  }, [simResult])

  return (
    <div className="grid-floor min-h-screen">
      <div className="max-w-6xl mx-auto px-6 py-10 space-y-10">
        <header className="glass-panel rounded-3xl px-10 py-12 relative overflow-hidden">
          <div className="absolute inset-0 bg-aura opacity-80"></div>
          <div className="relative space-y-6">
            <p className="text-sm uppercase tracking-[0.3em] text-slate/60">Smart Forecasting</p>
            <h1 className="text-4xl md:text-5xl font-display">
              A clearer pulse on urban unemployment, rebuilt for the web.
            </h1>
            <p className="text-lg text-slate/70 max-w-3xl">
              Compare baseline projections with XGBoost intelligence, then stress-test the
              next four quarters with a live economic simulator.
            </p>
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => setView('evaluation')}
                className={`px-6 py-3 rounded-full text-sm uppercase tracking-[0.2em] transition ${
                  view === 'evaluation'
                    ? 'bg-ink text-white shadow-glow'
                    : 'bg-white/70 text-slate/70'
                }`}
              >
                Model Evaluation
              </button>
              <button
                type="button"
                onClick={() => setView('simulator')}
                className={`px-6 py-3 rounded-full text-sm uppercase tracking-[0.2em] transition ${
                  view === 'simulator'
                    ? 'bg-ink text-white shadow-glow'
                    : 'bg-white/70 text-slate/70'
                }`}
              >
                Scenario Simulator
              </button>
            </div>
          </div>
        </header>

        {error ? (
          <div className="glass-panel rounded-2xl p-6 text-coral">
            Unable to load data. {error}
          </div>
        ) : null}

        {overview ? (
          <section className="grid gap-4 md:grid-cols-4 animate-rise">
            <StatCard label="Dataset" value={`${overview.rows} rows`} hint="Quarters loaded" />
            <StatCard
              label="Latest GDP"
              value={formatPercent(overview.last.gdp)}
              hint="Last recorded"
            />
            <StatCard
              label="Inflation"
              value={formatPercent(overview.last.inflation)}
              hint="Last recorded"
            />
            <StatCard
              label="LFPR"
              value={formatPercent(overview.last.lfpr)}
              hint={`Population: ${formatNumber(overview.last.population)}`}
            />
          </section>
        ) : null}

        {view === 'evaluation' ? (
          <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="glass-panel rounded-3xl p-8 space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm uppercase tracking-[0.3em] text-slate/60">Evaluation</p>
                  <h2 className="text-2xl">Linear Regression vs XGBoost</h2>
                </div>
                <span className="px-4 py-2 rounded-full bg-ink text-white text-xs uppercase tracking-[0.3em]">
                  80/20 split
                </span>
              </div>
              {evaluation ? <LineChart series={evaluationSeries} /> : null}
              {evaluation ? (
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="rounded-2xl border border-slate/10 p-4">
                    <p className="text-sm uppercase tracking-[0.2em] text-slate/60">Baseline LR</p>
                    <div className="mt-3 space-y-2 text-sm text-slate/70">
                      <p>MAE: {formatPercent(evaluation.metrics.lr.mae)}</p>
                      <p>RMSE: {formatPercent(evaluation.metrics.lr.rmse)}</p>
                      <p>R2: {evaluation.metrics.lr.r2.toFixed(4)}</p>
                    </div>
                  </div>
                  <div className="rounded-2xl border border-slate/10 p-4">
                    <p className="text-sm uppercase tracking-[0.2em] text-slate/60">XGBoost</p>
                    <div className="mt-3 space-y-2 text-sm text-slate/70">
                      <p>MAE: {formatPercent(evaluation.metrics.xgb.mae)}</p>
                      <p>RMSE: {formatPercent(evaluation.metrics.xgb.rmse)}</p>
                      <p>R2: {evaluation.metrics.xgb.r2.toFixed(4)}</p>
                    </div>
                  </div>
                </div>
              ) : null}
            </div>

            <div className="glass-panel rounded-3xl p-8 space-y-6">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-slate/60">Feature Impact</p>
                <h2 className="text-2xl">What the model listens to</h2>
              </div>
              {importance ? (
                <FeatureBars
                  features={importance.features}
                  importances={importance.importances}
                />
              ) : null}
              <p className="text-sm text-slate/60">
                Higher percentages indicate stronger influence on the XGBoost output.
              </p>
            </div>
          </section>
        ) : null}

        {view === 'simulator' ? (
          <section className="grid gap-6 lg:grid-cols-[1.6fr_0.9fr]">
            <div className="glass-panel rounded-3xl p-8 space-y-6">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-slate/60">Trajectory</p>
                <h2 className="text-2xl">Official vs simulated track</h2>
              </div>
              {simResult ? (
                <LineChart
                  series={forecastSeries}
                  splitIndex={simResult.recent_actuals.length - 1}
                  labels={forecastLabels}
                  height={360}
                />
              ) : null}
              {simResult ? (
                <ChartLegend
                  columns={2}
                  items={[
                    ...forecastSeries.map(({ label, color, dashed }) => ({
                      label,
                      color,
                      dashed,
                    })),
                    { label: 'Prediction start', color: '#94a3b8', dashed: true },
                  ]}
                />
              ) : null}
              {simResult ? (
                <div className="space-y-3 text-sm text-slate/70">
                  <div className="grid grid-cols-4 text-xs uppercase tracking-[0.2em]">
                    <span>Quarter</span>
                    <span className="text-right">Baseline</span>
                    <span className="text-right">Official XGB</span>
                    <span className="text-right">Simulated</span>
                  </div>
                  {simResult.quarters.map((quarter, index) => (
                    <div
                      key={quarter}
                      className="grid grid-cols-4 items-center border-b border-slate/10 pb-2"
                    >
                      <span>{quarter}</span>
                      <span className="text-right">
                        {formatPercent(simResult.official.lr[index])}
                      </span>
                      <span className="text-right">
                        {formatPercent(simResult.official.xgb[index])}
                      </span>
                      <span className="text-right">
                        {formatPercent(simResult.simulated.xgb[index])}
                      </span>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>

            <div className="glass-panel rounded-3xl p-6 space-y-5">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-slate/60">Simulator</p>
                <h2 className="text-xl">Run a four-quarter scenario</h2>
              </div>
              <form className="space-y-5" onSubmit={handleSimulate}>
                <div>
                  <label className="text-sm uppercase tracking-[0.2em] text-slate/60">
                    GDP Delta
                  </label>
                  <input
                    type="range"
                    min={-0.02}
                    max={0.02}
                    step={0.001}
                    value={simInput.gdpDelta}
                    onChange={(event) =>
                      setSimInput((prev) => ({
                        ...prev,
                        gdpDelta: Number(event.target.value),
                      }))
                    }
                    className="w-full mt-2 accent-cyan"
                  />
                  <p className="text-sm text-slate/70">
                    Base: {formatPercent(overview?.last.gdp ?? 0)} | Delta:{' '}
                    {formatPercent(simInput.gdpDelta)}
                  </p>
                </div>

                <div>
                  <label className="text-sm uppercase tracking-[0.2em] text-slate/60">
                    Population Delta
                  </label>
                  <input
                    type="range"
                    min={-100000}
                    max={100000}
                    step={1000}
                    value={simInput.populationDelta}
                    onChange={(event) =>
                      setSimInput((prev) => ({
                        ...prev,
                        populationDelta: Number(event.target.value),
                      }))
                    }
                    className="w-full mt-2 accent-cyan"
                  />
                  <p className="text-sm text-slate/70">
                    Base: {formatNumber(overview?.last.population ?? 0)} | Delta:{' '}
                    {formatNumber(simInput.populationDelta)}
                  </p>
                </div>

                <div>
                  <label className="text-sm uppercase tracking-[0.2em] text-slate/60">
                    Inflation Delta
                  </label>
                  <input
                    type="range"
                    min={-0.01}
                    max={0.01}
                    step={0.001}
                    value={simInput.inflationDelta}
                    onChange={(event) =>
                      setSimInput((prev) => ({
                        ...prev,
                        inflationDelta: Number(event.target.value),
                      }))
                    }
                    className="w-full mt-2 accent-amber"
                  />
                  <p className="text-sm text-slate/70">
                    Base: {formatPercent(overview?.last.inflation ?? 0)} | Delta:{' '}
                    {formatPercent(simInput.inflationDelta)}
                  </p>
                </div>

                <div>
                  <label className="text-sm uppercase tracking-[0.2em] text-slate/60">
                    Prev Unemployment Delta
                  </label>
                  <input
                    type="range"
                    min={-0.02}
                    max={0.02}
                    step={0.001}
                    value={simInput.prevUnemploymentDelta}
                    onChange={(event) =>
                      setSimInput((prev) => ({
                        ...prev,
                        prevUnemploymentDelta: Number(event.target.value),
                      }))
                    }
                    className="w-full mt-2 accent-amber"
                  />
                  <p className="text-sm text-slate/70">
                    Base: {formatPercent(overview?.last.unemployment ?? 0)} | Delta:{' '}
                    {formatPercent(simInput.prevUnemploymentDelta)}
                  </p>
                </div>

                <div>
                  <label className="text-sm uppercase tracking-[0.2em] text-slate/60">
                    LFPR Delta
                  </label>
                  <input
                    type="range"
                    min={-0.05}
                    max={0.05}
                    step={0.005}
                    value={simInput.lfprDelta}
                    onChange={(event) =>
                      setSimInput((prev) => ({
                        ...prev,
                        lfprDelta: Number(event.target.value),
                      }))
                    }
                    className="w-full mt-2 accent-coral"
                  />
                  <p className="text-sm text-slate/70">
                    Base: {formatPercent(overview?.last.lfpr ?? 0)} | Delta:{' '}
                    {formatPercent(simInput.lfprDelta)}
                  </p>
                </div>

                <button
                  type="submit"
                  className="w-full py-3 rounded-full bg-ink text-white tracking-[0.3em] text-sm uppercase"
                  disabled={simLoading}
                >
                  {simLoading ? 'Simulating...' : 'Run Simulation'}
                </button>
              </form>

              {simResult ? (
                <div
                  className={`rounded-2xl p-4 text-sm uppercase tracking-[0.2em] ${
                    simResult.alert
                      ? 'bg-coral/15 text-coral'
                      : 'bg-cyan/15 text-cyan'
                  }`}
                >
                  {simResult.alert
                    ? 'Alert: predicted unemployment exceeds 6%'
                    : 'System nominal: unemployment remains under 6%'}
                </div>
              ) : null}
            </div>
          </section>
        ) : null}
      </div>
    </div>
  )
}

export default App
