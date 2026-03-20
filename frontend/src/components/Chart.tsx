import { useEffect, useRef } from "react";
import {
  createChart,
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  createSeriesMarkers,
} from "lightweight-charts";
import type { OhlcvItem, Signal, Indicator } from "../types";
import { useI18n } from "../i18n";

interface Props {
  ohlcv: OhlcvItem[];
  signals: Signal[];
  indicators: Indicator[];
  symbol: string;
}

export default function Chart({ ohlcv, signals, indicators, symbol }: Props) {
  const { t } = useI18n();
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || ohlcv.length === 0) return;

    const chart = createChart(container, {
      width: container.clientWidth,
      height: 500,
      layout: {
        background: { color: "#1a1a2e" },
        textColor: "#94a3b8",
      },
      grid: {
        vertLines: { color: "#2d2d44" },
        horzLines: { color: "#2d2d44" },
      },
      crosshair: { mode: 0 },
      timeScale: { timeVisible: false, borderColor: "#2d2d44" },
      rightPriceScale: {
        autoScale: true,
        scaleMargins: { top: 0.05, bottom: 0.2 },
        borderColor: "#2d2d44",
      },
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderUpColor: "#22c55e",
      borderDownColor: "#ef4444",
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
    });
    candleSeries.setData(ohlcv);

    for (const indicator of indicators) {
      const lineSeries = chart.addSeries(LineSeries, {
        color: indicator.color,
        lineWidth: 2,
        title: indicator.name,
        priceLineVisible: false,
        lastValueVisible: false,
      });
      lineSeries.setData(indicator.data);
    }

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    });
    chart.priceScale("volume").applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });
    volumeSeries.setData(
      ohlcv.map((item) => ({
        time: item.time,
        value: item.volume,
        color: item.close >= item.open ? "rgba(34,197,94,0.25)" : "rgba(239,68,68,0.25)",
      }))
    );

    const markers = signals.map((s) => ({
      time: s.date,
      position: s.action === "buy" ? ("belowBar" as const) : ("aboveBar" as const),
      color: s.action === "buy" ? "#22c55e" : "#ef4444",
      shape: s.action === "buy" ? ("arrowUp" as const) : ("arrowDown" as const),
      text: s.action === "buy" ? `${t("chart.buy")} ${s.price}` : `${t("chart.sell")} ${s.price}`,
    }));
    const seriesMarkers = createSeriesMarkers(candleSeries, markers);

    chart.timeScale().fitContent();

    const handleResize = () => {
      chart.applyOptions({ width: container.clientWidth });
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      seriesMarkers.detach();
      chart.remove();
    };
  }, [ohlcv, signals, indicators, symbol, t]);

  return (
    <div className="overflow-hidden rounded-xl border border-dark-border">
      <div ref={containerRef} className="chart-container" />
    </div>
  );
}
