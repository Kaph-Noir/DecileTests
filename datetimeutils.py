from datetime import datetime as dt
from datetime import timedelta


class DateTimeUtils:
    """_summary_

    Returns:
        _type_: _description_
    """

    def get_str_yyyy(self, yyyymmdd: int) -> str:
        return str(yyyymmdd)[0:4]
    
    @staticmethod
    def get_str_yyyymm(yyyymmdd: int) -> str:
        return str(yyyymmdd)[0:6]

    @staticmethod
    def get_int_yyyy(yyyymmdd: int) -> int:
        return int(str(yyyymmdd)[0:4])  # yyyymmdd // 10000

    @staticmethod
    def get_int_yyyymm(yyyymmdd: int) -> int:
        return int(str(yyyymmdd)[0:6])  # yyyymmdd // 100
    
    def get_str_yyyymmdd(self, yyyymmdd: int) -> str:
        return str(yyyymmdd)

    @staticmethod
    def get_str_yyyy_mm_dd(yyyymmdd: int) -> str:
        return dt.strftime(dt.strptime(str(yyyymmdd), "%Y%m%d"), "%Y-%m-%d")

    def get_str_yyyy_mm_dd_next_y(self, yyyymmdd: int) -> str:
        if self.get_int_yyyy(self.get_str_yyyy(yyyymmdd)) % 4 == 3:
            return dt.strftime(dt.strptime(self.get_str_yyyymmdd(yyyymmdd), "%Y%m%d") + timedelta(days=365), "%Y-%m-%d")
        else:
            return dt.strftime(dt.strptime(self.get_str_yyyymmdd(yyyymmdd), "%Y%m%d") + timedelta(days=364), "%Y-%m-%d")
