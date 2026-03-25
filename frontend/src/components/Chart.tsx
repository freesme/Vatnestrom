import { useEffect, useRef } from "react";
import {
  createChart,
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  createSeriesMarkers,
  type IChartApi,
  type LogicalRange,
} from "lightweight-charts";
import type { OhlcvItem, Signal, Indicator } from "../types";
import { useI18n } from "../i18n";

interface Props {
  ohlcv: OhlcvItem[];
  signals: Signal[];
  indicators: Indicator[];
  symbol: string;
  interval?: string;
}

const CHART_THEME = {
  background: "#1a1a2e",
  text: "#94a3b8",
  grid: "#2d2d44",
  border: "#2d2d44",
} as const;

function computePriceFormat(ohlcv: OhlcvItem[]) {
  const prices = ohlcv.flatMap((d) => [d.high, d.low]);
  const maxPrice = Math.max(...prices);
  const minPrice = Math.min(...prices);
  const priceRange = maxPrice - minPrice;
  const avgPrice = (maxPrice + minPrice) / 2;

  let precision: number;
  let minMove: number;
  if (avgPrice < 1) {
    precision = 4; minMove = 0.0001;
  } else if (avgPrice < 10) {
    precision = 3; minMove = 0.001;
  } else if (avgPrice < 1000) {
    precision = 2; minMove = 0.01;
  } else {
    precision = 1; minMove = 0.1;
  }
  if (priceRange > 0 && priceRange < avgPrice * 0.01 && precision < 4) {
    precision += 1;
    minMove /= 10;
  }
  return { type: "price" as const, precision, minMove };
}

function makeChartOptions(width: number, height: number) {
  return {
    width,
    height,
    layout: {
      background: { color: CHART_THEME.background },
      textColor: CHART_THEME.text,
    },
    grid: {
      vertLines: { color: CHART_THEME.grid },
      horzLines: { color: CHART_THEME.grid },
    },
    crosshair: { mode: 0 as const },
    timeScale: {
      timeVisible: true,
      borderColor: CHART_THEME.border,
      minBarSpacing: 1,
      fixLeftEdge: true,
      fixRightEdge: true,
    },
    rightPriceScale: {
      autoScale: true,
      borderColor: CHART_THEME.border,
    },
  };
}

/** 同步两个图表的时间轴可见范围 */
function syncTimeScales(main: IChartApi, sub: IChartApi) {
  let syncing = false;

  const onMainChange = (range: LogicalRange | null) => {
    if (syncing || !range) return;
    syncing = true;
    sub.timeScale().setVisibleLogicalRange(range);
    syncing = false;
  };

  const onSubChange = (range: LogicalRange | null) => {
    if (syncing || !range) return;
    syncing = true;
    main.timeScale().setVisibleLogicalRange(range);
    syncing = false;
  };

  main.timeScale().subscribeVisibleLogicalRangeChange(onMainChange);
  sub.timeScale().subscribeVisibleLogicalRangeChange(onSubChange);

  return () => {
    main.timeScale().unsubscribeVisibleLogicalRangeChange(onMainChange);
    sub.timeScale().unsubscribeVisibleLogicalRangeChange(onSubChange);
  };
}

export default function Chart({ ohlcv, signals, indicators, symbol, interval = "1d" }: Props) {
  const { t } = useI18n();
  const mainRef = useRef<HTMLDivElement>(null);
  const subRef = useRef<HTMLDivElement>(null);

  // 分离叠加指标和独立面板指标
  const overlayIndicators = indicators.filter((ind) => ind.overlay !== false);
  const panelIndicators = indicators.filter((ind) => ind.overlay === false);
  const hasSubPanel = panelIndicators.length > 0;

  useEffect(() => {
    const mainContainer = mainRef.current;
    if (!mainContainer || ohlcv.length === 0) return;

    const barSpacing = ohlcv.length > 500 ? 3 : ohlcv.length > 200 ? 5 : 7;
    const priceFormat = computePriceFormat(ohlcv);

    // ── 主图表：K 线 + 叠加指标 + 成交量 ──
    const mainHeight = hasSubPanel ? 380 : 500;
    const mainChart = createChart(mainContainer, {
      ...makeChartOptions(mainContainer.clientWidth, mainHeight),
      rightPriceScale: {
        autoScale: true,
        scaleMargins: { top: 0.08, bottom: 0.22 },
        borderColor: CHART_THEME.border,
      },
      timeScale: {
        ...makeChartOptions(0, 0).timeScale,
        barSpacing,
        // 有子面板时隐藏主图时间轴标签，由子面板显示
        visible: !hasSubPanel,
      },
    });

    const candleSeries = mainChart.addSeries(CandlestickSeries, {
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderUpColor: "#22c55e",
      borderDownColor: "#ef4444",
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
      priceFormat,
    });
    candleSeries.setData(ohlcv);

    for (const indicator of overlayIndicators) {
      const lineSeries = mainChart.addSeries(LineSeries, {
        color: indicator.color,
        lineWidth: 2,
        title: indicator.name,
        priceLineVisible: false,
        lastValueVisible: false,
        priceFormat,
      });
      lineSeries.setData(indicator.data);
    }

    // 成交量
    const volumeSeries = mainChart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    });
    mainChart.priceScale("volume").applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });
    volumeSeries.setData(
      ohlcv.map((item) => ({
        time: item.time,
        value: item.volume,
        color: item.close >= item.open ? "rgba(34,197,94,0.25)" : "rgba(239,68,68,0.25)",
      }))
    );

    // 买卖标记
    const markers = signals.map((s) => ({
      time: s.date,
      position: s.action === "buy" ? ("belowBar" as const) : ("aboveBar" as const),
      color: s.action === "buy" ? "#22c55e" : "#ef4444",
      shape: s.action === "buy" ? ("arrowUp" as const) : ("arrowDown" as const),
      text: s.action === "buy" ? `${t("chart.buy")} ${s.price}` : `${t("chart.sell")} ${s.price}`,
    }));
    const seriesMarkers = createSeriesMarkers(candleSeries, markers);

    mainChart.timeScale().fitContent();

    // ── 子面板：独立指标（RSI / MACD 等） ──
    let subChart: IChartApi | null = null;
    let unsyncFn: (() => void) | null = null;

    const subContainer = subRef.current;
    if (hasSubPanel && subContainer) {
      subChart = createChart(subContainer, {
        ...makeChartOptions(subContainer.clientWidth, 160),
        rightPriceScale: {
          autoScale: true,
          scaleMargins: { top: 0.1, bottom: 0.1 },
          borderColor: CHART_THEME.border,
        },
        timeScale: {
          ...makeChartOptions(0, 0).timeScale,
          barSpacing,
        },
      });

      for (const indicator of panelIndicators) {
        const lineSeries = subChart.addSeries(LineSeries, {
          color: indicator.color,
          lineWidth: 2,
          title: indicator.name,
          priceLineVisible: false,
          lastValueVisible: false,
        });
        lineSeries.setData(indicator.data);
      }

      subChart.timeScale().fitContent();
      unsyncFn = syncTimeScales(mainChart, subChart);
    }

    // ── resize ──
    const handleResize = () => {
      if (mainContainer) {
        mainChart.applyOptions({ width: mainContainer.clientWidth });
      }
      if (subChart && subContainer) {
        subChart.applyOptions({ width: subContainer.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      unsyncFn?.();
      seriesMarkers.detach();
      subChart?.remove();
      mainChart.remove();
    };
  }, [ohlcv, signals, indicators, symbol, interval, t, overlayIndicators, panelIndicators, hasSubPanel]);

  return (
    <div className="overflow-hidden rounded-xl border border-dark-border">
      <div ref={mainRef} className="chart-container" />
      {hasSubPanel && (
        <div
          ref={subRef}
          className="chart-container border-t border-dark-border"
        />
      )}
    </div>
  );
}
