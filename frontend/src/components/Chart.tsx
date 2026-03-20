import { useEffect, useRef } from "react";
import {
  createChart,
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  createSeriesMarkers,
} from "lightweight-charts";
import type { OhlcvItem, Signal, Indicator } from "../types";

interface Props {
  ohlcv: OhlcvItem[];
  signals: Signal[];
  indicators: Indicator[];
  symbol: string;
}

/** K 线图 + 技术指标线 + 买卖标记组件 */
export default function Chart({ ohlcv, signals, indicators, symbol }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || ohlcv.length === 0) return;

    // 创建图表实例，使用深色主题
    const chart = createChart(container, {
      width: container.clientWidth,
      height: 500,
      layout: {
        background: { color: "#1e1e2f" },
        textColor: "#d1d5db",
      },
      grid: {
        vertLines: { color: "#2d2d44" },
        horzLines: { color: "#2d2d44" },
      },
      crosshair: { mode: 0 },
      timeScale: { timeVisible: false, borderColor: "#3d3d5c" },
    });

    // 添加 K 线系列（红绿配色）
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderUpColor: "#22c55e",
      borderDownColor: "#ef4444",
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
    });
    candleSeries.setData(ohlcv);

    // 叠加技术指标线（如均线），每条线一个 LineSeries
    for (const indicator of indicators) {
      const lineSeries = chart.addSeries(LineSeries, {
        color: indicator.color,
        lineWidth: 2,
        title: indicator.name,
        priceLineVisible: false,       // 不在右侧价格轴显示当前值横线
        lastValueVisible: false,       // 不在右侧价格轴显示最新值标签
      });
      lineSeries.setData(indicator.data);
    }

    // 添加成交量柱状图（半透明，贴底显示）
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
        color: item.close >= item.open ? "rgba(34,197,94,0.3)" : "rgba(239,68,68,0.3)",
      }))
    );

    // 在 K 线上标注买卖信号（v5 使用 createSeriesMarkers）
    const markers = signals.map((s) => ({
      time: s.date,
      position: s.action === "buy" ? ("belowBar" as const) : ("aboveBar" as const),
      color: s.action === "buy" ? "#22c55e" : "#ef4444",
      shape: s.action === "buy" ? ("arrowUp" as const) : ("arrowDown" as const),
      text: s.action === "buy" ? `买 ${s.price}` : `卖 ${s.price}`,
    }));
    const seriesMarkers = createSeriesMarkers(candleSeries, markers);

    // 自适应显示全部数据
    chart.timeScale().fitContent();

    // 窗口大小变化时自动调整图表宽度
    const handleResize = () => {
      chart.applyOptions({ width: container.clientWidth });
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      seriesMarkers.detach();
      chart.remove();
    };
  }, [ohlcv, signals, indicators, symbol]);

  return <div ref={containerRef} className="chart-container" />;
}
