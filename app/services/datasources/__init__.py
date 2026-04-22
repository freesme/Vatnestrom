"""
数据源注册表

所有数据源适配器在此注册，通过 get_datasource(name) 获取实例。
新增数据源只需：1) 创建适配器类 2) 在此注册即可。
"""

from app.services.datasources.base import BaseDataSource
from app.services.datasources.yahoo import YahooDataSource
from app.services.datasources.sina import SinaDataSource
from app.services.datasources.twelvedata import TwelveDataSource
from app.services.datasources.alphavantage import AlphaVantageDataSource
from app.services.datasources.tickflow import TickFlowDataSource
from app.services.datasources.tushare import TushareDataSource

SOURCE_REGISTRY: dict[str, BaseDataSource] = {
    "yahoo": YahooDataSource(),
    "tickflow": TickFlowDataSource(),
    "tushare": TushareDataSource(),
    "sina": SinaDataSource(),
    "twelvedata": TwelveDataSource(),
    "alphavantage": AlphaVantageDataSource(),
}


def get_datasource(name: str) -> BaseDataSource:
    """根据名称获取数据源实例"""
    if name not in SOURCE_REGISTRY:
        raise ValueError(
            f"Unknown data source: {name}. Available: {list(SOURCE_REGISTRY.keys())}"
        )
    return SOURCE_REGISTRY[name]
