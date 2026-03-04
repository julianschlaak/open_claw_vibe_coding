import { useEffect, useMemo, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { MonitorDataset, DroughtDataPoint } from './types';
import { lttb } from './lib/lttb';

const domains = ['catchment_custom', 'test_domain'] as const;

type Domain = (typeof domains)[number];
type TabKey = 'spatial' | 'time' | 'propagation' | 'extreme' | 'diagnostics' | 'validation';
type WindowMode = 'full' | 'last30' | 'event' | 'custom';
type EventKey = 'drought_2003' | 'drought_2018' | 'drought_2019' | 'drought_2020';

type CorrelationCell = [number, number, number];

const domainCoords: Record<Domain, { lon: number; lat: number; label: string }> = {
  catchment_custom: { lon: 11.0, lat: 51.0, label: 'Catchment Custom' },
  test_domain: { lon: 10.2, lat: 50.2, label: 'Test Domain' },
};

const eventWindows: Record<EventKey, { label: string; start: string; end: string }> = {
  drought_2003: { label: '2003 Event', start: '2002-01-01', end: '2004-12-31' },
  drought_2018: { label: '2018 Event', start: '2017-01-01', end: '2019-12-31' },
  drought_2019: { label: '2019 Event', start: '2018-01-01', end: '2020-12-31' },
  drought_2020: { label: '2020 Event', start: '2019-01-01', end: '2021-12-31' },
};

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

function pearson(xs: Array<number | null>, ys: Array<number | null>): number {
  const pairs: Array<[number, number]> = [];
  for (let i = 0; i < xs.length; i++) {
    const x = xs[i];
    const y = ys[i];
    if (x != null && y != null && Number.isFinite(x) && Number.isFinite(y)) pairs.push([x, y]);
  }
  if (pairs.length < 3) return NaN;
  const xm = pairs.reduce((s, p) => s + p[0], 0) / pairs.length;
  const ym = pairs.reduce((s, p) => s + p[1], 0) / pairs.length;
  let num = 0;
  let xd = 0;
  let yd = 0;
  for (const [x, y] of pairs) {
    num += (x - xm) * (y - ym);
    xd += (x - xm) * (x - xm);
    yd += (y - ym) * (y - ym);
  }
  if (xd === 0 || yd === 0) return NaN;
  return num / Math.sqrt(xd * yd);
}

function lagCorr(a: Array<number | null>, b: Array<number | null>, lag: number): number {
  const xs: Array<number | null> = [];
  const ys: Array<number | null> = [];
  if (lag < 0) {
    for (let i = 0; i < a.length + lag; i++) {
      xs.push(a[i]);
      ys.push(b[i - lag]);
    }
  } else if (lag > 0) {
    for (let i = lag; i < a.length; i++) {
      xs.push(a[i]);
      ys.push(b[i - lag]);
    }
  } else {
    return pearson(a, b);
  }
  return pearson(xs, ys);
}

function downsample(arr: Array<number | null>): Array<number | null> {
  const clean = arr.map((v, i) => ({ x: i, y: v ?? NaN })).filter((p) => Number.isFinite(p.y));
  const down = lttb(clean as Array<{ x: number; y: number }>, 700);
  const m = new Map(down.map((d) => [d.x, d.y]));
  return arr.map((_, i) => (m.has(i) ? m.get(i)! : null));
}

function norm01(arr: Array<number | null>): Array<number | null> {
  const vals = arr.filter((v): v is number => v != null && Number.isFinite(v));
  if (!vals.length) return arr.map(() => null);
  const min = Math.min(...vals);
  const max = Math.max(...vals);
  if (max === min) return arr.map((v) => (v == null ? null : 0.5));
  return arr.map((v) => (v == null ? null : (v - min) / (max - min)));
}

export default function App() {
  const [domain, setDomain] = useState<Domain>('catchment_custom');
  const [allData, setAllData] = useState<Record<string, MonitorDataset>>({});
  const [error, setError] = useState<string>('');
  const [tab, setTab] = useState<TabKey>('spatial');
  const [windowMode, setWindowMode] = useState<WindowMode>('full');
  const [eventKey, setEventKey] = useState<EventKey>('drought_2018');
  const [customStart, setCustomStart] = useState<string>('1991-01-01');
  const [customEnd, setCustomEnd] = useState<string>('2020-12-31');

  useEffect(() => {
    setError('');
    Promise.all(
      domains.map((d) =>
        fetch(`/data/${d}_monitor.json`)
          .then((r) => {
            if (!r.ok) throw new Error(`${d}: HTTP ${r.status}`);
            return r.json();
          })
          .then((payload: MonitorDataset) => [d, payload] as const)
      )
    )
      .then((pairs) => {
        const next: Record<string, MonitorDataset> = {};
        for (const [d, payload] of pairs) next[d] = payload;
        setAllData(next);
        const active = next[domain];
        if (active) {
          setCustomStart(active.metadata.start);
          setCustomEnd(active.metadata.end);
        }
      })
      .catch((e) => {
        setAllData({});
        setError(`Daten konnten nicht geladen werden: ${String(e)}`);
      });
  }, []);

  const data = allData[domain] ?? null;

  useEffect(() => {
    if (!data) return;
    setCustomStart(data.metadata.start);
    setCustomEnd(data.metadata.end);
  }, [domain, data?.metadata.start, data?.metadata.end]);

  const filteredPoints = useMemo(() => {
    if (!data) return [] as DroughtDataPoint[];
    const pts = data.points;
    if (windowMode === 'full') return pts;

    const endDate = new Date(pts[pts.length - 1]?.date ?? data.metadata.end);
    if (windowMode === 'last30') {
      const start = new Date(endDate);
      start.setFullYear(start.getFullYear() - 30);
      return pts.filter((p) => new Date(p.date) >= start && new Date(p.date) <= endDate);
    }

    if (windowMode === 'event') {
      const w = eventWindows[eventKey];
      const ws = new Date(w.start);
      const we = new Date(w.end);
      return pts.filter((p) => {
        const d = new Date(p.date);
        return d >= ws && d <= we;
      });
    }

    const cs = new Date(customStart);
    const ce = new Date(customEnd);
    if (Number.isNaN(cs.getTime()) || Number.isNaN(ce.getTime())) return pts;
    return pts.filter((p) => {
      const d = new Date(p.date);
      return d >= cs && d <= ce;
    });
  }, [customEnd, customStart, data, eventKey, windowMode]);

  const latest = useMemo(() => (filteredPoints.length ? filteredPoints[filteredPoints.length - 1] : null), [filteredPoints]);

  const droughtDuration = useMemo(() => {
    if (!filteredPoints.length) return 0;
    let n = 0;
    for (let i = filteredPoints.length - 1; i >= 0; i--) {
      const v = filteredPoints[i].smi;
      if (v !== null && v <= -1) n++;
      else break;
    }
    return n;
  }, [filteredPoints]);

  const status = useMemo(() => {
    const smi = latest?.smi;
    if (smi == null) return { label: 'Unknown', color: '#A0A0A0' };
    if (smi <= -2) return { label: 'Extreme Drought', color: '#BA181B' };
    if (smi <= -1.5) return { label: 'Severe Drought', color: '#E85D04' };
    if (smi <= -1) return { label: 'Moderate Drought', color: '#FAA307' };
    return { label: 'Near Normal / Wet', color: '#2A9D8F' };
  }, [latest]);

  const spatialOption = useMemo(() => {
    const rows = domains
      .map((d) => {
        const dd = allData[d];
        if (!dd?.points?.length) return null;
        const l = dd.points[dd.points.length - 1];
        const score = l.smi ?? l.spi_3 ?? 0;
        return {
          name: domainCoords[d].label,
          value: [domainCoords[d].lon, domainCoords[d].lat, score],
          domain: d,
          smi: l.smi,
          spi_3: l.spi_3,
          spei_3: l.spei_3,
        };
      })
      .filter((x): x is NonNullable<typeof x> => x !== null);

    return {
      tooltip: {
        trigger: 'item',
        formatter: (p: { data?: { name: string; smi: number | null; spi_3: number | null; spei_3: number | null; domain: string } }) => {
          const d = p.data;
          if (!d) return '';
          return `${d.name}<br/>Domain: ${d.domain}<br/>SMI: ${d.smi?.toFixed(2) ?? 'n/a'}<br/>SPI-3: ${d.spi_3?.toFixed(2) ?? 'n/a'}<br/>SPEI-3: ${d.spei_3?.toFixed(2) ?? 'n/a'}`;
        },
      },
      xAxis: {
        type: 'value',
        name: 'Longitude [deg]',
        min: 5,
        max: 16,
        axisLabel: { color: '#A0A0A0' },
      },
      yAxis: {
        type: 'value',
        name: 'Latitude [deg]',
        min: 47,
        max: 56,
        axisLabel: { color: '#A0A0A0' },
      },
      visualMap: {
        min: -3,
        max: 3,
        right: 10,
        top: 10,
        calculable: false,
        inRange: { color: ['#8B0000', '#D00000', '#E85D04', '#FAA307', '#2A9D8F', '#0077B6'] },
        textStyle: { color: '#FAFAFA' },
      },
      series: [
        {
          type: 'scatter',
          symbolSize: 18,
          data: rows,
          itemStyle: {
            borderColor: '#FFFFFF',
            borderWidth: 1,
          },
          label: {
            show: true,
            formatter: '{b}',
            position: 'top',
            color: '#FAFAFA',
          },
        },
      ],
      grid: { left: 60, right: 30, top: 30, bottom: 50 },
      backgroundColor: '#0E1117',
    };
  }, [allData]);

  const timeSeriesOption = useMemo(() => {
    if (!filteredPoints.length) return {};
    const x = filteredPoints.map((p) => p.date);
    const seriesVals = {
      spi3: downsample(filteredPoints.map((p) => p.spi_3)),
      spei3: downsample(filteredPoints.map((p) => p.spei_3)),
      smi: downsample(filteredPoints.map((p) => p.smi)),
      sdi: downsample(filteredPoints.map((p) => p.discharge_simulated)),
    };

    return {
      backgroundColor: '#0E1117',
      tooltip: { trigger: 'axis' },
      legend: { textStyle: { color: '#FAFAFA' } },
      dataZoom: [{ type: 'inside' }, { type: 'slider' }],
      xAxis: { type: 'category', data: x, axisLabel: { color: '#A0A0A0' } },
      yAxis: [
        {
          type: 'value',
          name: 'Standardized index [-]',
          min: -4,
          max: 4,
          axisLabel: { color: '#A0A0A0' },
          splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
        },
        {
          type: 'value',
          name: 'Qsim [model units]',
          axisLabel: { color: '#A0A0A0' },
          splitLine: { show: false },
        },
      ],
      series: [
        { name: 'SPI-3', type: 'line', smooth: true, showSymbol: false, data: seriesVals.spi3, lineStyle: { color: '#4EA8DE' } },
        { name: 'SPEI-3', type: 'line', smooth: true, showSymbol: false, data: seriesVals.spei3, lineStyle: { color: '#9D4EDD' } },
        { name: 'SMI', type: 'line', smooth: true, showSymbol: false, data: seriesVals.smi, lineStyle: { color: '#D00000' } },
        {
          name: 'Discharge (Qsim)',
          type: 'line',
          smooth: true,
          showSymbol: false,
          yAxisIndex: 1,
          data: seriesVals.sdi,
          lineStyle: { color: '#2A9D8F', width: 1.5, opacity: 0.7 },
        },
      ],
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { type: 'dashed', color: '#F77F00' },
        data: [{ yAxis: -1 }, { yAxis: -1.5 }, { yAxis: -2 }],
      },
    };
  }, [filteredPoints]);

  const propagationOption = useMemo(() => {
    if (!filteredPoints.length) return {};
    const x = filteredPoints.map((p) => p.date);
    const p = norm01(filteredPoints.map((r) => r.precip));
    const sm = norm01(filteredPoints.map((r) => r.soil_moisture));
    const rch = norm01(filteredPoints.map((r) => r.recharge));
    const q = norm01(filteredPoints.map((r) => r.discharge_simulated));

    return {
      backgroundColor: '#0E1117',
      tooltip: { trigger: 'axis' },
      legend: { textStyle: { color: '#FAFAFA' } },
      xAxis: { type: 'category', data: x, axisLabel: { color: '#A0A0A0' } },
      yAxis: { type: 'value', min: 0, max: 1, name: 'Normalized anomaly [0-1]', axisLabel: { color: '#A0A0A0' } },
      dataZoom: [{ type: 'inside' }, { type: 'slider' }],
      series: [
        { name: 'Precipitation', type: 'line', showSymbol: false, data: downsample(p), lineStyle: { color: '#4EA8DE' } },
        { name: 'Soil moisture', type: 'line', showSymbol: false, data: downsample(sm), lineStyle: { color: '#D00000' } },
        { name: 'Recharge', type: 'line', showSymbol: false, data: downsample(rch), lineStyle: { color: '#FAA307' } },
        { name: 'Discharge', type: 'line', showSymbol: false, data: downsample(q), lineStyle: { color: '#2A9D8F' } },
      ],
    };
  }, [filteredPoints]);

  const lagOption = useMemo(() => {
    if (!filteredPoints.length) return {};
    const maxLag = 12;
    const lags = Array.from({ length: 2 * maxLag + 1 }, (_, i) => i - maxLag);
    const p = filteredPoints.map((r) => r.precip);
    const sm = filteredPoints.map((r) => r.soil_moisture);
    const rch = filteredPoints.map((r) => r.recharge);
    const q = filteredPoints.map((r) => r.discharge_simulated);

    return {
      backgroundColor: '#0E1117',
      tooltip: { trigger: 'axis' },
      legend: { textStyle: { color: '#FAFAFA' } },
      xAxis: { type: 'category', data: lags.map((l) => String(l)), name: 'Lag [months]', axisLabel: { color: '#A0A0A0' } },
      yAxis: { type: 'value', min: -1, max: 1, name: 'Cross-correlation r', axisLabel: { color: '#A0A0A0' } },
      series: [
        { name: 'P -> SM', type: 'line', data: lags.map((l) => lagCorr(p, sm, l)), showSymbol: false, lineStyle: { color: '#4EA8DE' } },
        { name: 'SM -> Recharge', type: 'line', data: lags.map((l) => lagCorr(sm, rch, l)), showSymbol: false, lineStyle: { color: '#FAA307' } },
        { name: 'Recharge -> Q', type: 'line', data: lags.map((l) => lagCorr(rch, q, l)), showSymbol: false, lineStyle: { color: '#2A9D8F' } },
      ],
    };
  }, [filteredPoints]);

  const extremesOption = useMemo(() => {
    if (!filteredPoints.length) return {};
    const x = filteredPoints.map((p) => p.date);
    const smi = filteredPoints.map((p) => p.smi);
    return {
      backgroundColor: '#0E1117',
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: x, axisLabel: { color: '#A0A0A0' } },
      yAxis: { type: 'value', min: -4, max: 4, name: 'SMI [-]', axisLabel: { color: '#A0A0A0' } },
      dataZoom: [{ type: 'inside' }, { type: 'slider' }],
      series: [
        {
          name: 'SMI',
          type: 'line',
          showSymbol: false,
          data: downsample(smi),
          lineStyle: { color: '#D00000' },
          markLine: {
            silent: true,
            symbol: 'none',
            lineStyle: { type: 'dashed' },
            data: [
              { yAxis: -1, lineStyle: { color: '#FAA307' }, label: { formatter: 'Moderate' } },
              { yAxis: -1.5, lineStyle: { color: '#E85D04' }, label: { formatter: 'Severe' } },
              { yAxis: -2, lineStyle: { color: '#BA181B' }, label: { formatter: 'Extreme' } },
            ],
          },
        },
      ],
    };
  }, [filteredPoints]);

  const extremeCountsOption = useMemo(() => {
    const values = filteredPoints.map((p) => p.smi).filter((v): v is number => v != null);
    const c1 = values.filter((v) => v <= -1).length;
    const c2 = values.filter((v) => v <= -1.5).length;
    const c3 = values.filter((v) => v <= -2).length;
    return {
      backgroundColor: '#0E1117',
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['<= -1', '<= -1.5', '<= -2'], axisLabel: { color: '#A0A0A0' } },
      yAxis: { type: 'value', name: 'Months', axisLabel: { color: '#A0A0A0' } },
      series: [
        {
          type: 'bar',
          data: [c1, c2, c3],
          itemStyle: { color: '#F77F00' },
        },
      ],
    };
  }, [filteredPoints]);

  const corrHeatmapOption = useMemo(() => {
    if (!filteredPoints.length) return {};
    const names = ['SPI-3', 'SPEI-3', 'SMI', 'Recharge', 'Discharge'];
    const fields: Array<(p: DroughtDataPoint) => number | null> = [
      (p) => p.spi_3,
      (p) => p.spei_3,
      (p) => p.smi,
      (p) => p.recharge,
      (p) => p.discharge_simulated,
    ];
    const cells: CorrelationCell[] = [];
    for (let i = 0; i < fields.length; i++) {
      for (let j = 0; j < fields.length; j++) {
        const c = pearson(filteredPoints.map(fields[i]), filteredPoints.map(fields[j]));
        cells.push([i, j, Number.isFinite(c) ? c : 0]);
      }
    }

    return {
      backgroundColor: '#0E1117',
      tooltip: { trigger: 'item' },
      xAxis: { type: 'category', data: names, axisLabel: { color: '#A0A0A0' } },
      yAxis: { type: 'category', data: names, axisLabel: { color: '#A0A0A0' } },
      visualMap: {
        min: -1,
        max: 1,
        calculable: false,
        orient: 'vertical',
        right: 10,
        top: 'center',
        inRange: { color: ['#023E8A', '#00B4D8', '#F8F9FA', '#F77F00', '#9D0208'] },
        textStyle: { color: '#FAFAFA' },
      },
      series: [
        {
          type: 'heatmap',
          data: cells,
          label: {
            show: true,
            formatter: (p: { value: [number, number, number] }) => p.value[2].toFixed(2),
            color: '#111',
            fontSize: 10,
          },
        },
      ],
    };
  }, [filteredPoints]);

  const consistencyOption = useMemo(() => {
    if (!data) return {};
    const rows = data.consistency
      .filter((r) => filteredPoints.some((p) => p.date === r.date))
      .slice(-220);
    return {
      backgroundColor: '#0E1117',
      tooltip: { trigger: 'item' },
      xAxis: { type: 'category', data: rows.map((r) => r.date), axisLabel: { color: '#A0A0A0', showMaxLabel: true, showMinLabel: true } },
      yAxis: {
        type: 'category',
        data: ['SPI vs SPEI', 'SPI vs SMI', 'SPEI vs SMI'],
        axisLabel: { color: '#A0A0A0' },
      },
      visualMap: { min: 0, max: 1, calculable: false, inRange: { color: ['#BA181B', '#FAA307', '#2A9D8F'] }, textStyle: { color: '#FAFAFA' } },
      series: [
        {
          type: 'heatmap',
          data: rows.flatMap((r, i) => {
            const a = catScore(r.spi_category) === catScore(r.spei_category) ? 1 : 0;
            const b = catScore(r.spi_category) === catScore(r.smi_category) ? 1 : 0;
            const c = catScore(r.spei_category) === catScore(r.smi_category) ? 1 : 0;
            return [[i, 0, a], [i, 1, b], [i, 2, c]];
          }),
        },
      ],
    };
  }, [data, filteredPoints]);

  const validationHydroOption = useMemo(() => {
    const pts = filteredPoints.filter((p) => p.discharge_observed != null && p.discharge_simulated != null);
    if (!pts.length) return {};
    return {
      backgroundColor: '#0E1117',
      tooltip: { trigger: 'axis' },
      legend: { textStyle: { color: '#FAFAFA' } },
      xAxis: { type: 'category', data: pts.map((p) => p.date), axisLabel: { color: '#A0A0A0' } },
      yAxis: { type: 'value', axisLabel: { color: '#A0A0A0' } },
      dataZoom: [{ type: 'inside' }, { type: 'slider' }],
      series: [
        { name: 'Qobs', type: 'line', showSymbol: false, data: pts.map((p) => p.discharge_observed), lineStyle: { color: '#2A9D8F' } },
        { name: 'Qsim', type: 'line', showSymbol: false, data: pts.map((p) => p.discharge_simulated), lineStyle: { color: '#4EA8DE' } },
      ],
    };
  }, [filteredPoints]);

  return (
    <div className="min-h-screen bg-bg p-4 md:p-6">
      <div className="mx-auto max-w-7xl">
        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold">Scientific Drought Monitoring Dashboard</h1>
            <p className="text-sm text-zinc-400">Multi-index: SPI · SPEI · SMI · recharge · discharge</p>
          </div>
          <select
            value={domain}
            onChange={(e) => setDomain(e.target.value as Domain)}
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
                <div className="text-xs text-zinc-400">Current drought status</div>
                <div className="mt-2 flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full" style={{ backgroundColor: status.color }} />
                  <span className="font-semibold">{status.label}</span>
                </div>
                <div className="mt-2 text-sm text-zinc-300">SMI: {latest?.smi?.toFixed(2) ?? 'n/a'}</div>
                <div className="text-sm text-zinc-300">Active drought duration: {droughtDuration} months</div>
              </div>
              <div className="card p-4">
                <div className="text-xs text-zinc-400">Hydrological validation (KGE primary)</div>
                <div className="mt-2 text-2xl font-bold">{Number.isFinite(data.validation.kge) ? data.validation.kge.toFixed(3) : 'n/a'}</div>
                <div className="mt-1 text-sm text-zinc-400">NSE: {Number.isFinite(data.validation.nse) ? data.validation.nse.toFixed(3) : 'n/a'}</div>
              </div>
              <div className="card p-4">
                <div className="text-xs text-zinc-400">Data coverage</div>
                <div className="mt-2 text-sm text-zinc-300">{data.metadata.start} {'->'} {data.metadata.end}</div>
                <div className="text-sm text-zinc-300">Points: {data.metadata.n_points}</div>
                <div className="text-sm text-zinc-300">Scales: {data.metadata.timescales.join(', ')} months</div>
              </div>
            </div>

            <div className="mb-4 grid grid-cols-1 gap-3 lg:grid-cols-2">
              <div className="card p-3">
                <div className="mb-2 text-sm font-semibold">Time window</div>
                <div className="flex flex-wrap gap-2">
                  {(['full', 'last30', 'event', 'custom'] as WindowMode[]).map((w) => (
                    <button
                      key={w}
                      className={`rounded-lg px-3 py-2 text-sm ${windowMode === w ? 'bg-zinc-100 text-zinc-900' : 'bg-zinc-800 text-zinc-200'}`}
                      onClick={() => setWindowMode(w)}
                    >
                      {w === 'full' ? 'Full record' : w === 'last30' ? 'Last 30 years' : w === 'event' ? 'Drought event' : 'Custom'}
                    </button>
                  ))}
                </div>
                {windowMode === 'event' && (
                  <div className="mt-2">
                    <select
                      value={eventKey}
                      onChange={(e) => setEventKey(e.target.value as EventKey)}
                      className="rounded-lg border border-white/20 bg-card px-3 py-2 text-sm"
                    >
                      {Object.entries(eventWindows).map(([k, w]) => (
                        <option key={k} value={k}>{w.label}: {w.start} - {w.end}</option>
                      ))}
                    </select>
                  </div>
                )}
                {windowMode === 'custom' && (
                  <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                    <input type="date" value={customStart} onChange={(e) => setCustomStart(e.target.value)} className="rounded-lg border border-white/20 bg-card px-3 py-2 text-sm" />
                    <input type="date" value={customEnd} onChange={(e) => setCustomEnd(e.target.value)} className="rounded-lg border border-white/20 bg-card px-3 py-2 text-sm" />
                  </div>
                )}
              </div>
              <div className="card p-3">
                <div className="mb-2 text-sm font-semibold">Panels</div>
                <div className="flex flex-wrap gap-2">
                  {(['spatial', 'time', 'propagation', 'extreme', 'diagnostics', 'validation'] as TabKey[]).map((t) => (
                    <button
                      key={t}
                      className={`rounded-lg px-3 py-2 text-sm ${tab === t ? 'bg-zinc-100 text-zinc-900' : 'bg-zinc-800 text-zinc-200'}`}
                      onClick={() => setTab(t)}
                    >
                      {t[0].toUpperCase() + t.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {tab === 'spatial' && (
              <div className="card p-3">
                <div className="mb-2 text-sm font-semibold">Spatial drought overview (domain centroids)</div>
                <ReactECharts option={spatialOption} style={{ height: 440 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
              </div>
            )}

            {tab === 'time' && (
              <div className="card p-3">
                <div className="mb-2 text-sm font-semibold">Time series comparison (multi-index)</div>
                <ReactECharts option={timeSeriesOption} style={{ height: 470 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
              </div>
            )}

            {tab === 'propagation' && (
              <div className="grid grid-cols-1 gap-4">
                <div className="card p-3">
                  <div className="mb-2 text-sm font-semibold">Hydrological drought propagation (P {'->'} SM {'->'} recharge {'->'} Q)</div>
                  <ReactECharts option={propagationOption} style={{ height: 400 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
                </div>
                <div className="card p-3">
                  <div className="mb-2 text-sm font-semibold">Lag and cross-correlation diagnostics (1,3,6,12 month context)</div>
                  <ReactECharts option={lagOption} style={{ height: 330 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
                </div>
              </div>
            )}

            {tab === 'extreme' && (
              <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <div className="card p-3">
                  <div className="mb-2 text-sm font-semibold">Extreme drought analysis (SMI thresholds)</div>
                  <ReactECharts option={extremesOption} style={{ height: 340 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
                </div>
                <div className="card p-3">
                  <div className="mb-2 text-sm font-semibold">Threshold exceedance counts</div>
                  <ReactECharts option={extremeCountsOption} style={{ height: 340 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
                </div>
              </div>
            )}

            {tab === 'diagnostics' && (
              <div className="grid grid-cols-1 gap-4">
                <div className="card p-3">
                  <div className="mb-2 text-sm font-semibold">Index comparison diagnostics (correlation matrix)</div>
                  <ReactECharts option={corrHeatmapOption} style={{ height: 360 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
                </div>
                <div className="card p-3">
                  <div className="mb-2 text-sm font-semibold">Category agreement diagnostics</div>
                  <ReactECharts option={consistencyOption} style={{ height: 280 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
                </div>
              </div>
            )}

            {tab === 'validation' && (
              <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <div className="card p-3">
                  <div className="mb-2 text-sm font-semibold">Validation metrics</div>
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
                  <div className="mb-2 text-sm font-semibold">Observed vs simulated hydrograph</div>
                  <ReactECharts option={validationHydroOption} style={{ height: 340 }} notMerge lazyUpdate opts={{ renderer: 'canvas' }} />
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
