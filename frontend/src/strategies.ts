/** 策略参数字段定义 */
export interface ParamField {
  key: string;
  labelKey: string;
  default: number;
  step?: number;
}

/** 策略元数据定义 */
export interface StrategyMeta {
  id: string;
  nameKey: string;
  descKey: string;
  icon: string;
  color: string;
  params: ParamField[];
}

/** 所有可用策略列表 */
export const STRATEGIES: StrategyMeta[] = [
  {
    id: "ma_cross",
    nameKey: "strategy.ma_cross.name",
    descKey: "strategy.ma_cross.desc",
    icon: "📈",
    color: "#6366f1",
    params: [
      { key: "fast_window", labelKey: "param.fast_window", default: 10 },
      { key: "slow_window", labelKey: "param.slow_window", default: 50 },
    ],
  },
  {
    id: "rsi",
    nameKey: "strategy.rsi.name",
    descKey: "strategy.rsi.desc",
    icon: "⚡",
    color: "#8b5cf6",
    params: [
      { key: "rsi_window", labelKey: "param.rsi_window", default: 14 },
      { key: "oversold", labelKey: "param.oversold", default: 30 },
      { key: "overbought", labelKey: "param.overbought", default: 70 },
    ],
  },
  {
    id: "bollinger",
    nameKey: "strategy.bollinger.name",
    descKey: "strategy.bollinger.desc",
    icon: "📊",
    color: "#ec4899",
    params: [
      { key: "bb_window", labelKey: "param.bb_window", default: 20 },
      { key: "bb_std", labelKey: "param.bb_std", default: 2.0, step: 0.1 },
    ],
  },
  {
    id: "macd",
    nameKey: "strategy.macd.name",
    descKey: "strategy.macd.desc",
    icon: "🔀",
    color: "#3b82f6",
    params: [
      { key: "fast_window", labelKey: "param.fast_window.macd", default: 12 },
      { key: "slow_window", labelKey: "param.slow_window.macd", default: 26 },
      { key: "signal_window", labelKey: "param.signal_window", default: 9 },
    ],
  },
  {
    id: "donchian",
    nameKey: "strategy.donchian.name",
    descKey: "strategy.donchian.desc",
    icon: "🐢",
    color: "#10b981",
    params: [
      { key: "entry_window", labelKey: "param.entry_window", default: 20 },
      { key: "exit_window", labelKey: "param.exit_window", default: 10 },
    ],
  },
];
