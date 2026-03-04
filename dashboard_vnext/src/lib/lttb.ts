export type XYPoint = { x: number; y: number };

// Largest-Triangle-Three-Buckets downsampling for long time series.
export function lttb(data: XYPoint[], threshold: number): XYPoint[] {
  if (threshold >= data.length || threshold <= 2) return data;

  const sampled: XYPoint[] = [data[0]];
  const bucketSize = (data.length - 2) / (threshold - 2);
  let a = 0;

  for (let i = 0; i < threshold - 2; i++) {
    const start = Math.floor((i + 1) * bucketSize) + 1;
    const end = Math.floor((i + 2) * bucketSize) + 1;
    const bucketEnd = Math.min(end, data.length);

    let avgX = 0;
    let avgY = 0;
    let avgCount = 0;
    for (let idx = start; idx < bucketEnd; idx++) {
      avgX += data[idx].x;
      avgY += data[idx].y;
      avgCount++;
    }
    avgX /= Math.max(1, avgCount);
    avgY /= Math.max(1, avgCount);

    const rangeOffs = Math.floor(i * bucketSize) + 1;
    const rangeTo = Math.floor((i + 1) * bucketSize) + 1;
    const rangeToSafe = Math.min(rangeTo, data.length - 1);

    let maxArea = -1;
    let nextA = rangeOffs;

    for (let idx = rangeOffs; idx < rangeToSafe; idx++) {
      const area = Math.abs(
        (data[a].x - avgX) * (data[idx].y - data[a].y) -
          (data[a].x - data[idx].x) * (avgY - data[a].y)
      );
      if (area > maxArea) {
        maxArea = area;
        nextA = idx;
      }
    }

    sampled.push(data[nextA]);
    a = nextA;
  }

  sampled.push(data[data.length - 1]);
  return sampled;
}
