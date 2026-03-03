export interface DroughtDataPoint {
  date: string;
  spi_1: number | null;
  spi_3: number | null;
  spi_6: number | null;
  spi_12: number | null;
  spei_3: number | null;
  smi: number | null;
  discharge_observed: number | null;
  discharge_simulated: number | null;
}

export interface ValidationMetrics {
  kge: number;
  kge_r: number;
  kge_alpha: number;
  kge_beta: number;
  nse: number;
  rmse: number;
  mae: number;
  bias: number;
  peak_error: number;
  timing_error_days: number;
}

export interface IndexConsistency {
  date: string;
  spi_category: string;
  spei_category: string;
  smi_category: string;
  agreement_score: number;
  dominant_drought: string | null;
}

export interface MonitorDataset {
  domain: string;
  metadata: {
    start: string;
    end: string;
    n_points: number;
    timescales: number[];
  };
  validation: ValidationMetrics;
  decomposition: {
    trend: Array<number | null>;
    seasonal: Array<number | null>;
    resid: Array<number | null>;
  };
  points: DroughtDataPoint[];
  consistency: IndexConsistency[];
}
