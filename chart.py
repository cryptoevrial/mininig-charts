from typing import List, Tuple
from datetime import timedelta
import plotly.graph_objects as go
import pandas as pd


def find_continuous_ranges(df: pd.DataFrame, col1: str, col2: str) -> List[Tuple[int, int]]:
    """
    Находит диапазоны непрерывных индексов, где значения в col1 меньше значений в col2.

    Parameters:
    -----------
    df : pandas.DataFrame
        Датафрейм с данными
    col1 : str
        Имя первого столбца для сравнения
    col2 : str
        Имя второго столбца для сравнения

    Returns:
    --------
    List[Tuple[int, int]]
        Список кортежей (начальный_индекс, конечный_индекс) для каждого непрерывного диапазона

    Examples:
    --------
    df = pd.DataFrame({
         'A': [1, 2, 1, 4, 1, 1, 7],
         'B': [3, 3, 2, 3, 2, 2, 6]
    })
    find_continuous_ranges(df, 'A', 'B')
    [(0, 1), (4, 5)]  # Диапазоны где A < B
    """
    # Создаем маску где значения col1 меньше col2
    mask = df[col1] < df[col2]

    if not mask.any():
        return []

    ranges = []
    start_idx = None

    # Проходим по маске и ищем непрерывные диапазоны
    for idx, is_less in enumerate(mask):
        if is_less and start_idx is None:
            # Начало нового диапазона
            start_idx = idx
        elif not is_less and start_idx is not None:
            # Конец текущего диапазона
            ranges.append((start_idx, idx - 1))
            start_idx = None

    # Обработка случая, когда последний диапазон доходит до конца датафрейма
    if start_idx is not None:
        ranges.append((start_idx, len(df) - 1))

    return ranges

def create_fill_for_negative_total_mining_cost(df, ranges, fig):
    for range in ranges:
        filtered_df = df[(df.index >= range[0]) & (df.index <= range[1])]

        # Добавляем базовую линию для заливки
        fig.add_trace(
            go.Scatter(
                x=filtered_df['date'],
                y=filtered_df['mining_cost_in_usd'],  # Создаём базовую линию по нулям
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            )
        )

        # Добавляем верхнюю линию с заливкой
        fig.add_trace(
            go.Scatter(
                x=filtered_df['date'],
                y=filtered_df['total_mining_cost_in_usd'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',  # Заливка до предыдущей линии
                fillcolor='rgba(239, 71, 111, 0.5)',
                showlegend=False,
                hoverinfo='skip'
            )
        )

def create_fill_for_positive_mining_cost(df, ranges, fig):
    for range in ranges:
        filtered_df = df[(df.index >= range[0]-1) & (df.index <= range[1]+1)]

        # Добавляем базовую линию для заливки
        fig.add_trace(
            go.Scatter(
                x=filtered_df['date'],
                y=filtered_df['mining_cost_in_usd'],
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            )
        )

        # Добавляем верхнюю линию с заливкой
        fig.add_trace(
            go.Scatter(
                x=filtered_df['date'],
                y=filtered_df['total_mining_cost_in_usd'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',  # Заливка до предыдущей линии
                fillcolor='rgba(142, 202, 230, 0.5)',
                showlegend=False,
                hoverinfo='skip'
            )
        )

def add_asics_name(df, fig):
    dates = pd.to_datetime(
                [2019, 2020, 2021, 2022, 2023, 2024, 2025],
                format='%Y'
            )
    for date in dates:
        idx = df[df['date']==date.date()].index[0]
        fig.add_vline(x=df.loc[idx, 'date'], line_dash="dash", line_color="gray")
        # Добавляем прямоугольник с текстом
        fig.add_shape(
            type="rect",
            x0=df.loc[idx, 'date'],  # Начало прямоугольника
            x1=df.loc[idx, 'date']+ timedelta(days=365),  # Конец прямоугольника
            y0=0,  # Нижняя граница
            y1=0,  # Верхняя граница
            line=dict(
                color="gray",
                width=1,
            ),
            fillcolor="white",
            opacity=0.8
        )
        # Добавляем текст внутри прямоугольника
        fig.add_annotation(
            x=df.loc[idx, 'date']+ timedelta(days=182),  # Середина прямоугольника
            y=1250,  # Середина прямоугольника по высоте
            text=df.loc[idx]['asics_name'],
            showarrow=False,
            font=dict(size=12),
            bgcolor="white",  # Цвет фона текста
            bordercolor="gray",  # Цвет границы текста
            borderwidth=1  # Ширина границы текста
        )

def create_chart(df):
    fig = go.Figure()

    # Настройка темы и фона
    fig.update_layout(
        template='plotly_white',  # Используем светлую тему
    )

    # Добавляем график цены Bitcoin
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['btc_price'],
            name='Bitcoin Price',
            line=dict(color='rgb(2, 48, 71)'),
            mode='lines'
        )
    )

    # Добавляем линию себестоимости майнинга (нижняя граница)
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['mining_cost_in_usd'],
            name='Mining Cost',
            line=dict(color='rgb(33, 158, 188)'),
            mode='lines'
        )
    )
    # Добавляем верхнюю границу
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['total_mining_cost_in_usd'],
            name='Total Mining Cost',
            line=dict(color='rgb(120, 0, 0)'),
            mode='lines'
        )
    )
    btc_price_lower_total_cost = find_continuous_ranges(df, 'btc_price', 'total_mining_cost_in_usd')
    create_fill_for_negative_total_mining_cost(df, btc_price_lower_total_cost, fig)

    total_mining_cost_lower_bitcoin_price = find_continuous_ranges(df, 'total_mining_cost_in_usd', 'btc_price')
    create_fill_for_positive_mining_cost(df, total_mining_cost_lower_bitcoin_price, fig)

    add_asics_name(df, fig)

    fig.show(renderer='browser')
    fig.write_html("mining_chart.html")