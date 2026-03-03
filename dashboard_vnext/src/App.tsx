import { useEffect, useMemo, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { MonitorDataset } from './types';
import { lttb } from './lib/lttb';

const domains = ['catchment_custom', 'test_domain'] as const;

type TabKey = 'time' | 'comparison' | 'validation';

function catScore(c: string): number {
  if (c.includes('extreme_drought')) return -3;
  if (c.includes('severe_drought')) return -2;
  if (c.includes('moderate_drought')) return -1;
  if (c.includes('near_normal')) return 0;
  if (c.includes('moderately_wet')) return 1;
  if (c.includes('severely_wet')) return 2;
  if (c.includes('extremely_wet')) return 3;
  return 0;
}

export default function App() {
  const [domain, setDomain] = useState<string>('catchment_custom');
  const [data, setData] = useState<MonitorDataset | null>(null);
  const [error, setError] = useState<string>('');
  const [tab, setTab] = useState<TabKey>('time');
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    setError('');
    fetch(`/data/${domain}_monitor.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d: MonitorDataset) => setData(d))
      .catch((e) => {
        setData(null);
        setError(`Daten konnten nicht geladen werden: ${String(e)}`);
      });
  }, [domain]);

  const latest = useMemo(() => (data?.points?.length ? data.points[data.points.length - 1] : null), [data]);

  const droughtDuration = useMemo(() => {
    if (!data || !data.points.length) return 0;
    let n = 0;
    for (let i = data.points.length - 1; i >= 0; i--) {
      const v = data.points[i].smi;
      if (v !== null && v <= -1) n++;
      else break;
    }
    return n;
  }, [data]);

  const status = useMemo(() => {
    const smi = latest?.smi;
    if (smi == null) return { label: 'Unknown', color: '#A0A0A0' };
    if (smi <= -2) return { label: 'Extreme Drought', color: '#FF4B4B' };
    if (smi <= -1) return { label: 'Moderate/Severe Drought', color: '#F5A623' };
    return { label: 'Near Normal / Wet', color: '#00C851' };
  }, [latest]);

  const timeSeriesOption = useMemo(() => {
    if (!data) return {};
    const x = data.points.map((p) => p.date);
    type NumericPointField =
      | 'spi_1'
      | 'spi_3'
      | 'spi_6'
      | 'spi_12'
      | 'spei_3'
      | 'smi'
      | 'discharge_observed'
      | 'discharge_simulated';
    const mk = (field: NumericPointField) => data.points.map((p) => p[field]);

    const ds = (arr: Array<number | null>) => {
      const clean = arr.map((v, i) => ({ x: i, y: v ?? NaN })).filter((p) => Number.isFinite(p.y));
      const down = lttb(clean as Array<{ x: number; y: number }>, 500);
      const downMap = new Map(down.map((d) => [d.x, d.y]));
      return arr.map((_, i) => (downMap.has(i) ? downMap.get(i) : null));
    };

    return {
      backgroundColor: '#0E1117',
      tooltip: { trigger: 'axis' },
      legend: { textStyle: { color: '#FAFAFA' } },
      dataZoom: [{ type: 'inside' }, { type: 'slider' }],
      xAxis: { type: 'category', data: x, axisLabel: { color: '#A0A0A0' } },
      yAxis: {
        type: 'value',
        min: -4,
        max: 4,
        axisLabel: { color: '#A0A0A0' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } }
      },
      visualMap: {
        show: false,
        pieces: [
          { lte: -2, color: 'rgba(255,75,75,0.10)' },
          { gt: -2, lte: -1, color: 'rgba(245,166,35,0.08)' }
        ],
        dimension: 1,
      },
      series: [
        { name: 'SPI-3', type: 'line', smooth: true, showSymbol: false, data: ds(mk('spi_3')), lineStyle: { color: '#5DADE2' } },
        { name: 'SPEI-3', type: 'line', smooth: true, showSymbol: false, data: ds(mk('spei_3')), lineStyle: { color: '#AF7AC5' } },
        { name: 'SMI', type: 'line', smooth: true, showSymbol: false, data: ds(mk('smi')), lineStyle: { color: '#FF4B4B' } }
      ]
    };
  }, [data]);

  const radarOption = useMemo(() => {
    if (!latest) return {};
    const vals = [latest.spi_1, latest.spi_3, latest.spi_6, latest.spi_12, latest.spei_3, latest.smi].map((v) => (v ?? 0));
    return {
      backgroundColor: '#0E1117',
      radar: {
        indicator: ['SPI-1', 'SPI-3', 'SPI-6', 'SPI-12', 'SPEI-3', 'SMI'].map((name) => ({ name, min: -3, max: 3 })),
        axisName: { color: '#FAFAFA' },
      },
      series: [{ type: 'radar', data: [{ value: vals, name: 'Latest' }] }],
    };
  }, [latest]);

  const splomOption = useMemo(() => {
    if (!data) return {};
    const pts = data.points.filter((p) => p.spi_3 != null && p.spei_3 != null && p.smi != null);
    return {
      backgroundColor: '#0E1117',
      tooltip: { trigger: 'item' },
      xAxis: { type: 'value', name: 'SPI-3', nameTextStyle: { color: '#FAFAFA' }, axisLabel: { color: '#A0A0A0' } },
      yAxis: { type: 'value', name: 'SPEI-3', nameTextStyle: { color: '#FAFAFA' }, axisLabel: { color: '#A0A0A0' } },
      series: [
        {
          type: 'scatter',
          data: pts.map((p) => [p.spi_3, p.spei_3, p.smi]),
          symbolSize: 6,
          itemStyle: { color: '#00C851', opacity: 0.65 },
        },
      ],
    };
  }, [data]);

  const parallelOption = useMemo(() => {
    if (!data) return {};
    const rows = data.points.filter((p) => p.spi_3 != null && p.spei_3 != null && p.smi != null && p.discharge_simulated != null);
    return {
      backgroundColor: '#0E1117',
      parallelAxis: [
        { dim: 0, name: 'SPI-3', min: -4, max: 4 },
        { dim: 1, name: 'SPEI-3', min: -4, max: 4 },
        { dim: 2, name: 'SMI', min: -4, max: 4 },
        { dim: 3, name: 'Qsim' },
      ],
      parallel: { left: 30, right: 30, bottom: 20, top: 25, axisExpandable: true },
      series: [{
        type: 'parallel',
        lineStyle: { width: 1, opacity: 0.25 },
        data: rows.slice(-240).map((p) => [p.spi_3, p.spei_3, p.smi, p.discharge_simulated]),
      }],
    };
  }, [data]);

  const consistencyOption = useMemo(() => {
    if (!data) return {};
    const rows = data.consistency.slice(-180);
    return {
      backgroundColor: '#0E1117',
      tooltip: { trigger: 'item' },
      xAxis: { type: 'category', data: rows.map((r) => r.date), axisLabel: { color: '#A0A0A0', showMaxLabel: true, showMinLabel: true } },
      yAxis: {
        type: 'category',
        data: ['SPI vs SPEI', 'SPI vs SMI', 'SPEI vs SMI'],
        axisLabel: { color: '#A0A0A0' },
      },
      visualMap: { min: 0, max: 1, calculable: false, inRange: { color: ['#FF4B4B', '#F5A623', '#00C851'] }, textStyle: { color: '#FAFAFA' } },
      series: [{
        type: 'heatmap',
        data: rows.flatMap((r, i) => {
          const a = catScore(r.spi_category) === catScore(r.spei_category) ? 1 : 0;
          const b = catScore(r.spi_category) === catScore(r.smi_category) ? 1 : 0;
          const c = catScore(r.spei_category) === catScore(r.smi_category) ? 1 : 0;
          return [[i, 0, a], [i, 1, b], [i, 2, c]];
        }),
      }],
    };
  }, [data]);

  const validationHydroOption = useMemo(() => {
    if (!data) return {};
    const pts = data.points.filter((p) => p.discharge_observed != null && p.discharge_simulated != null);
    return {
      backgroundColor: '#0E1117',
      tooltip: { trigger: 'axis' },
      legend: { textStyle: { color: '#FAFAFA' } },
      xAxis: { type: 'category', data: pts.map((p) => p.date), axisLabel: { color: '#A0A0A0' } },
      yAxis: { type: 'value', axisLabel: { color: '#A0A0A0' } },
      dataZoom: [{ type: 'inside' }, { type: 'slider' }],
      series: [
        { name: 'Qobs', type: 'line', showSymbol: false, data: pts.map((p) => p.discharge_observed), lineStyle: { color: '#00C851' } },
        { name: 'Qsim', type: 'line', showSymbol: false, data: pts.map((p) => p.discharge_simulated), lineStyle: { color: '#5DADE2' } },
      ],
    };
  }, [data]);

  return (
    <div className="min-h-screen bg-bg p-4 md:p-6">
      <div className="mx-auto max-w-7xl">
        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold">Multi-Index Hydrological Drought Monitor</h1>
            <p className="text-sm text-zinc-400">SPI · SPEI · SMI | 30+ years continuous analysis</p>
          </div>
          <select
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            className="rounded-lg border border-white/20 bg-card px-3 py-2 text-sm"
          >
            {domains.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        {error && <div className="card p-3 text-sm text-red-400">{error}</div>}
        {!data && !error && <div className="card p-3 text-sm text-zinc-300">Loading monitor data...</div>}

        {data && (
          <>
            <div className="mb-4 grid grid-cols-1 gap-3 md:grid-cols-3">
              <div className="card p-4">
                <div className="text-xs text-zinc-400">Current Status</div>
                <div className="mt-2 flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full" style={{ backgroundColor: status.color }} />
                  <span className="font-semibold">{status.label}</span>
                </div>
                <div className="mt-2 text-sm text-zinc-300">SMI: {latest?.smi?.toFixed(2) ?? 'n/a'}</div>
                <div className="text-sm text-zinc-300">Active drought duration: {droughtDuration} months</div>
              </div>
              <div className="card p-4">
                <div className="text-xs text-zinc-400">Validation (KGE primary)</div>
                <div className="mt-2 text-2xl font-bold">{Number.isFinite(data.validation.kge) ? data.validation.kge.toFixed(3) : 'n/a'}</div>
                <div className="mt-1 text-sm text-zinc-400">NSE: {Number.isFinite(data.validation.nse) ? data.validation.nse.toFixed(3) : 'n/a'}</div>
              </div>
              <div className="card p-4">
                <div className="text-xs text-zinc-400">Coverage</div>
                <div className="mt-2 text-sm text-zinc-300">{data.metadata.start} → {data.metadata.end}</div>
                <div className="text-sm text-zinc-300">Points: {data.metadata.n_points}</div>
              </div>
            </div>

            <div className="mb-4 card p-2">
              <div className="flex gap-2">
                {(['time', 'comparison', 'validation'] as TabKey[]).map((t) => (
                  <button
                    key={t}
                    className={`rounded-lg px-3 py-2 text-sm ${tab === t ? 'bg-zinc-100 text-zinc-900' : 'bg-zinc-800 text-zinc-200'}`}
                    onClick={() => setTab(t)}
                  >
                    {t === 'time' ? 'Time Series' : t === 'comparison' ? 'Comparison' : 'Validation'}
                  </button>
                ))}
              </div>
            </div>

            {tab === 'time' && (
              <div className="card p-3">
                <ReactECharts option={timeSeriesOption} style={{ height: 460 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
              </div>
            )}

            {tab === 'comparison' && (
              <div className="grid grid-cols-1 gap-4">
                <div className="card p-3">
                  <div className="mb-2 text-sm font-semibold">Radar Chart (latest state)</div>
                  <ReactECharts option={radarOption} style={{ height: 360 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
                </div>
                <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                  <div className="card p-3">
                    <div className="mb-2 text-sm font-semibold">Scatter View (SPI-3 vs SPEI-3)</div>
                    <ReactECharts option={splomOption} style={{ height: 320 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
                  </div>
                  <div className="card p-3">
                    <div className="mb-2 text-sm font-semibold">Parallel Coordinates</div>
                    <ReactECharts option={parallelOption} style={{ height: 320 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
                  </div>
                </div>
                <div className="card p-3">
                  <div className="mb-2 text-sm font-semibold">Consistency Heatmap</div>
                  <ReactECharts option={consistencyOption} style={{ height: 280 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
                </div>
              </div>
            )}

            {tab === 'validation' && (
              <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <div className="card p-3">
                  <div className="mb-2 text-sm font-semibold">Validation Metrics</div>
                  <table className="w-full text-left text-sm">
                    <tbody>
                      {Object.entries(data.validation).map(([k, v]) => (
                        <tr key={k}>
                          <td className="table-cell font-medium text-zinc-300">{k}</td>
                          <td className="table-cell text-zinc-200">{Number.isFinite(v) ? Number(v).toFixed(4) : 'n/a'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="card p-3">
                  <div className="mb-2 text-sm font-semibold">Observed vs Simulated Hydrograph</div>
                  <ReactECharts option={validationHydroOption} style={{ height: 320 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
                </div>
              </div>
            )}

            <div className="mt-4 card p-3">
              <button className="w-full rounded-lg bg-zinc-800 px-3 py-2 text-left text-sm" onClick={() => setExpanded((v) => !v)}>
                {expanded ? 'Hide advanced diagnostics' : 'Expand advanced diagnostics'}
              </button>
              {expanded && (
                <div className="mt-3 text-sm text-zinc-300">
                  <p>Includes decomposition components and index agreement diagnostics for deeper analysis.</p>
                  <p className="mt-2">DuckDB-WASM and Zustand dependencies are wired for advanced client-side query/state extensions.</p>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
