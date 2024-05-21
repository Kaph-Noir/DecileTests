import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
from datetimeutils import DateTimeUtils
import streamlit as st


class SingleFactorDataHandler:
    """

    """
    def __init__(self, ts_daily_returns: pd.DataFrame, ratio: pd.DataFrame, yyyy: int, duration: str="y"):
        self.starting_date = '0401'
        self.yyyymmdd = int(str(yyyy) + self.starting_date)
        self.ts_daily_returns = ts_daily_returns
        self.ratio = ratio
        self.duration = duration

    def get_annual_ts_data(self, ts_data):
        if self.duration == "y":
            self.ts_data = ts_data.loc[DateTimeUtils.get_str_yyyy_mm_dd(self.yyyymmdd):DateTimeUtils.get_str_yyyy_mm_dd_next_y(self.yyyymmdd)]  # get specific period ts data
            self.ts_data = self.ts_data.dropna(how="all", axis="columns")  # drop columns with only NaN values
            self.ts_data = self.ts_data.loc[:, self.ts_data.iloc[0].notna()]  # drop columns with NaN values at the begin
        else:
            pass
        return self.ts_data
        
    def get_tickers_intersection(self, ts_rets: pd.DataFrame, ratio: pd.DataFrame) -> pd.Index:
        target_tickers = ts_rets.columns.intersection(ratio.columns)
        return target_tickers
    
    def __call__(self):
        ts_daily_returns = self.get_annual_ts_data(self.ts_daily_returns)
        ratio = self.get_annual_ts_data(self.ratio)
        target_tickers = self.get_tickers_intersection(ts_daily_returns, ratio)
        ratio = ratio[target_tickers]
        return ts_daily_returns, ratio


class Filter:
    """

    Returns:
        _type_: _description_
    """
    @staticmethod
    def get_profitables(ts_earnings: pd.DataFrame) -> pd.DataFrame:
        return ts_earnings.loc[:, ts_earnings.iloc[0] > 0]
    
    # size filter
    

class SingleFactorStats:
    """

    """
    def __init__(self, ts_rets: pd.DataFrame, ratio: pd.DataFrame, factor_name: str, q: int=10):
        self.target_date = ts_rets.index[0]
        self.ts_rets = ts_rets
        self.ratio = ratio
        self.factor_name = factor_name
        self.q = q
        self.data_dir_path = Path(r"./input")
        self.kospi200 = pd.read_excel(self.data_dir_path / "KOSPI200.xlsx", index_col="Date").loc[ts_rets.index.to_list()]
        self.benchmark_daily_return = self.kospi200.pct_change()
        self.benchmark_cumulative_return = (self.benchmark_daily_return + 1).cumprod() - 1

    def get_factor_groups(self) -> pd.Series:
        groups = pd.qcut(self.ratio.loc[self.target_date], q=self.q, labels=[i for i in range(1, self.q + 1)])
        return groups

    def get_factor_group_means(self) -> list:
        groups = self.get_factor_groups()
        group_means = [self.ratio.loc[self.target_date, groups[groups==i].index].mean() for i in range(1, self.q + 1)]
        return group_means

    def get_factor_group_medians(self) -> list:
        groups = self.get_factor_groups()
        group_medians = list()
        group_medians = [self.ratio.loc[self.target_date, groups[groups==i].index].median() for i in range(1, self.q + 1)]
        return group_medians
    
    def get_same_weight_returns(self):
        groups = self.get_factor_groups()
        weighted_returnss = list()
        for i in range(1, self.q + 1):
            group = groups[groups==i]
            target_tickers = group.index
            weight = 1 / len(target_tickers)
            weighted_returns = self.ts_rets[target_tickers] * weight
            weighted_returnss.append(weighted_returns.sum(axis="columns"))
        return weighted_returnss

    def get_same_weight_ts_prtf_returns(self):
        groups = self.get_factor_groups()
        ts_prtf_returns = list()
        for i in range(1, self.q + 1):
            group = groups[groups==i]
            target_tickers = group.index
            weight = 1 / len(target_tickers)
            weighted_returns = self.ts_rets[target_tickers] * weight
            ts_prtf_return = ((weighted_returns.sum(axis="columns") + 1).cumprod()) - 1
            ts_prtf_returns.append(ts_prtf_return)
        return ts_prtf_returns

    def get_prtf_annual_returns(self):
        ts_prtf_returns = self.get_same_weight_ts_prtf_returns()
        prtf_returns = list()
        for ret in ts_prtf_returns:
            prtf_returns.append(ret.iloc[-1])
        return prtf_returns
    
    def show_entire_groups_returns(self):
        pass

    def show_annual_groups_returns(self):
        ts_quantile_returns = self.get_same_weight_ts_prtf_returns()
        fig = go.Figure()
        for i, ret in enumerate(ts_quantile_returns):
            if i == 0 or i == 9:
                fig.add_trace(go.Scatter(x=ret.index, y=ret.values, mode='lines', name=f'{i + 1}분위'))
                fig.update_xaxes(
                tickformat="%Y-%m-%d",
                title='Date')
        fig.add_trace(go.Scatter(x=self.benchmark_cumulative_return['Close'].index, y=self.benchmark_cumulative_return['Close'].values, mode='lines', name='KOSPI200'))
        fig.update_xaxes(
        tickformat="%Y-%m-%d",
        title='Date')
        fig.update_layout(title_text=f"{self.factor_name} 10분위 누적 수익률 {str(self.target_date)[0:4]}", title_x=0.5)
        fig.show()
        # st.plotly_chart(fig)

    def show_annual_groups_CAGR(self):
        quantile_returns = self.get_prtf_annual_returns()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[i + 1 for i in range(self.q)],
            y=quantile_returns,
            name='CAGR',
            yaxis='y',
            offsetgroup=0
        ))
        fig.add_trace(go.Scatter(x=[i + 1 for i in range(self.q)], y=self.benchmark_cumulative_return['Close'].values[-1], mode='lines', name='Benchmark'))
        fig.update_layout(title_text=f"{self.factor_name} 10분위 연환산 수익률 {str(self.target_date)[0:4]}",
                        title_x=0.5,
                        showlegend=True,
                        xaxis=dict(title='Rank', dtick=1),
                        yaxis=dict(title='CAGR (%)', side='left', range=[min(-max(quantile_returns) * 1.05, -0.5), max(max(quantile_returns) * 1.05, 0.5)]))
        fig.update_yaxes(showgrid=False)
        fig.show()
        # st.plotly_chart(fig)

    def show_annual_groups_stats(self):
            quantile_means = self.get_factor_group_means()
            quantile_medians = self.get_factor_group_medians()
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[i + 1 for i in range(self.q)],
                y=quantile_means,
                name='CAGR',
                yaxis='y',
                offsetgroup=0
            ))
            fig.add_trace(go.Bar(
                x=[i + 1 for i in range(self.q)],
                y=quantile_medians,
                name=f'분위별 {self.factor_name} median',
                yaxis='y2',
                offsetgroup=1
            ))
            # fig.add_trace(go.Scatter(x=[i + 1 for i in range(self.q)], y=self.benchmark_cumulative_return['Close'].values[-1], mode='lines', name='Benchmark'))
            fig.update_layout(title_text=f"{self.factor_name} 10분위 연환산 수익률 {str(self.target_date)[0:4]}",
                            title_x=0.5,
                            showlegend=True,
                            xaxis=dict(title='Rank', dtick=1),
                            yaxis=dict(title='CAGR (%)', side='left', range=[min(-max(quantile_means) * 1.05, -0.5), max(max(quantile_means) * 1.05, 0.5)]),  # 왼쪽 Y축 설정
                            yaxis2=dict(title=f'분위별 {self.factor_name} median', overlaying='y', side='right', range=[-max(quantile_medians) * 1.05, max(quantile_medians) * 1.05]),  # 오른쪽 Y축 설정
                            barmode='group',
                            legend_yanchor="bottom")
            fig.update_yaxes(showgrid=False)
            fig.show()
            # st.plotly_chart(fig)