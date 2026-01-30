"""
Reusable chart components for RAP Framework.
Uses Plotly for interactive visualizations with SEK branding.
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Optional

# SEK Brand Colors
SEK_COLORS = {
    "primary": "#0A1628",
    "secondary": "#1B3A5F",
    "accent": "#00D4AA",
    "accent_light": "#00E5BB",
    "text": "#FFFFFF",
    "text_muted": "#A0AEC0",
    "background": "#0D1117",
    "card": "#161B22",
    "border": "#30363D",
    "success": "#00D4AA",
    "warning": "#FFA726",
    "danger": "#FF4757",
    "info": "#00B4D8",
}

# Common layout settings
BASE_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font_color": SEK_COLORS["text"],
    "font_family": "Inter, sans-serif",
}


def create_risk_gauge(
    value: float,
    title: str = "Risk Score",
    min_val: float = 0,
    max_val: float = 10,
    thresholds: Optional[list] = None,
) -> go.Figure:
    """
    Create a gauge chart for risk scores.

    Args:
        value: Current value to display
        title: Chart title
        min_val: Minimum scale value
        max_val: Maximum scale value
        thresholds: List of (value, color) tuples for threshold steps

    Returns:
        Plotly Figure object
    """
    if thresholds is None:
        thresholds = [
            (3, SEK_COLORS["success"]),
            (5, SEK_COLORS["warning"]),
            (7, SEK_COLORS["danger"]),
            (10, "#FF0000"),
        ]

    # Determine color based on value
    color = SEK_COLORS["success"]
    for threshold, thresh_color in thresholds:
        if value <= threshold:
            color = thresh_color
            break

    # Create gauge steps
    steps = []
    prev_val = min_val
    for threshold, thresh_color in thresholds:
        steps.append({
            "range": [prev_val, threshold],
            "color": f"{thresh_color}30"  # Transparent version
        })
        prev_val = threshold

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"color": SEK_COLORS["text"]}},
        number={"font": {"color": color}},
        gauge={
            "axis": {
                "range": [min_val, max_val],
                "tickcolor": SEK_COLORS["text_muted"],
            },
            "bar": {"color": color},
            "bgcolor": SEK_COLORS["card"],
            "borderwidth": 2,
            "bordercolor": SEK_COLORS["border"],
            "steps": steps,
            "threshold": {
                "line": {"color": SEK_COLORS["text"], "width": 2},
                "thickness": 0.75,
                "value": value
            }
        }
    ))

    fig.update_layout(
        **BASE_LAYOUT,
        height=250,
        margin=dict(t=50, b=20, l=20, r=20),
    )

    return fig


def create_dimension_chart(
    dimension_data: dict,
    chart_type: str = "pie",
) -> go.Figure:
    """
    Create a chart showing risk distribution by dimension.

    Args:
        dimension_data: Dict mapping dimension names to values
        chart_type: "pie" or "bar"

    Returns:
        Plotly Figure object
    """
    labels = list(dimension_data.keys())
    values = list(dimension_data.values())

    # Dimension colors
    colors = [
        SEK_COLORS["accent"],
        SEK_COLORS["info"],
        "#9B59B6",
        "#E74C3C",
        "#F39C12",
        "#1ABC9C",
        "#3498DB",
    ]

    if chart_type == "pie":
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=colors[:len(labels)],
            textinfo="percent+label",
            textposition="outside",
            textfont=dict(color=SEK_COLORS["text"]),
        )])
    else:
        fig = go.Figure(data=[go.Bar(
            x=labels,
            y=values,
            marker_color=colors[:len(labels)],
            text=[f"R$ {v:,.0f}" for v in values],
            textposition="outside",
        )])

        fig.update_layout(
            xaxis=dict(showgrid=False),
            yaxis=dict(
                showgrid=True,
                gridcolor=f"{SEK_COLORS['border']}50",
                tickformat=",.0f",
            ),
        )

    fig.update_layout(
        **BASE_LAYOUT,
        showlegend=False,
        height=350,
        margin=dict(t=20, b=40, l=40, r=40),
    )

    return fig


def create_loss_distribution_chart(
    losses: np.ndarray,
    title: str = "Loss Distribution",
    show_var_lines: bool = True,
    currency: str = "R$",
) -> go.Figure:
    """
    Create a histogram of loss distribution with VaR lines.

    Args:
        losses: Array of loss values
        title: Chart title
        show_var_lines: Whether to show VaR reference lines
        currency: Currency symbol for formatting

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    # Histogram
    fig.add_trace(go.Histogram(
        x=losses,
        nbinsx=50,
        marker_color=SEK_COLORS["accent"],
        opacity=0.7,
        name="Distribution",
    ))

    if show_var_lines:
        mean_val = np.mean(losses)
        var_95 = np.percentile(losses, 95)
        var_99 = np.percentile(losses, 99)

        # Mean line
        fig.add_vline(
            x=mean_val,
            line_dash="dash",
            line_color=SEK_COLORS["text"],
            annotation_text=f"Mean: {currency} {mean_val:,.0f}",
            annotation_position="top",
            annotation_font_color=SEK_COLORS["text"],
        )

        # VaR 95 line
        fig.add_vline(
            x=var_95,
            line_dash="dash",
            line_color=SEK_COLORS["warning"],
            annotation_text=f"VaR 95%: {currency} {var_95:,.0f}",
            annotation_position="top",
            annotation_font_color=SEK_COLORS["warning"],
        )

        # VaR 99 line
        fig.add_vline(
            x=var_99,
            line_dash="dash",
            line_color=SEK_COLORS["danger"],
            annotation_text=f"VaR 99%: {currency} {var_99:,.0f}",
            annotation_position="top",
            annotation_font_color=SEK_COLORS["danger"],
        )

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title, font=dict(color=SEK_COLORS["text"])),
        xaxis=dict(
            title="Annual Loss",
            showgrid=True,
            gridcolor=f"{SEK_COLORS['border']}50",
            tickformat=",.0f",
        ),
        yaxis=dict(
            title="Frequency",
            showgrid=True,
            gridcolor=f"{SEK_COLORS['border']}50",
        ),
        showlegend=False,
        height=400,
        margin=dict(t=60, b=40, l=60, r=20),
    )

    return fig


def create_bar_chart(
    data: dict,
    title: str = "",
    orientation: str = "v",
    color: Optional[str] = None,
    show_values: bool = True,
) -> go.Figure:
    """
    Create a bar chart.

    Args:
        data: Dict mapping labels to values
        title: Chart title
        orientation: "v" for vertical, "h" for horizontal
        color: Bar color (uses accent if not specified)
        show_values: Whether to show value labels

    Returns:
        Plotly Figure object
    """
    labels = list(data.keys())
    values = list(data.values())

    bar_color = color or SEK_COLORS["accent"]

    if orientation == "h":
        fig = go.Figure(data=[go.Bar(
            y=labels,
            x=values,
            orientation="h",
            marker_color=bar_color,
            text=[f"R$ {v:,.0f}" for v in values] if show_values else None,
            textposition="outside",
        )])
        fig.update_layout(
            xaxis=dict(
                showgrid=True,
                gridcolor=f"{SEK_COLORS['border']}50",
                tickformat=",.0f",
            ),
            yaxis=dict(showgrid=False),
        )
    else:
        fig = go.Figure(data=[go.Bar(
            x=labels,
            y=values,
            marker_color=bar_color,
            text=[f"R$ {v:,.0f}" for v in values] if show_values else None,
            textposition="outside",
        )])
        fig.update_layout(
            xaxis=dict(showgrid=False),
            yaxis=dict(
                showgrid=True,
                gridcolor=f"{SEK_COLORS['border']}50",
                tickformat=",.0f",
            ),
        )

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title, font=dict(color=SEK_COLORS["text"])) if title else None,
        height=350,
        margin=dict(t=40 if title else 20, b=40, l=40, r=40),
    )

    return fig


def create_line_chart(
    x_data: list,
    y_data: list,
    title: str = "",
    x_title: str = "",
    y_title: str = "",
    fill: bool = False,
) -> go.Figure:
    """
    Create a line chart.

    Args:
        x_data: X-axis values
        y_data: Y-axis values
        title: Chart title
        x_title: X-axis title
        y_title: Y-axis title
        fill: Whether to fill area under the line

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode="lines",
        line=dict(color=SEK_COLORS["accent"], width=2),
        fill="tozeroy" if fill else None,
        fillcolor=f"{SEK_COLORS['accent']}20" if fill else None,
    ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title, font=dict(color=SEK_COLORS["text"])) if title else None,
        xaxis=dict(
            title=x_title,
            showgrid=True,
            gridcolor=f"{SEK_COLORS['border']}50",
        ),
        yaxis=dict(
            title=y_title,
            showgrid=True,
            gridcolor=f"{SEK_COLORS['border']}50",
        ),
        height=350,
        margin=dict(t=40 if title else 20, b=40, l=60, r=20),
    )

    return fig


def create_radar_chart(
    categories: list,
    values: list,
    title: str = "",
    max_value: float = 10,
) -> go.Figure:
    """
    Create a radar/spider chart.

    Args:
        categories: Category labels
        values: Values for each category
        title: Chart title
        max_value: Maximum value for the scale

    Returns:
        Plotly Figure object
    """
    # Close the polygon
    categories = categories + [categories[0]]
    values = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor=f"{SEK_COLORS['accent']}30",
        line=dict(color=SEK_COLORS["accent"], width=2),
        marker=dict(color=SEK_COLORS["accent"], size=8),
    ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=title, font=dict(color=SEK_COLORS["text"])) if title else None,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_value],
                gridcolor=f"{SEK_COLORS['border']}50",
                tickfont=dict(color=SEK_COLORS["text_muted"]),
            ),
            angularaxis=dict(
                gridcolor=f"{SEK_COLORS['border']}50",
                tickfont=dict(color=SEK_COLORS["text"]),
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
        height=400,
        margin=dict(t=60 if title else 20, b=20, l=60, r=60),
    )

    return fig


def format_currency(value: float, currency: str = "BRL") -> str:
    """Format a value as currency."""
    symbols = {
        "BRL": "R$",
        "USD": "$",
        "EUR": "€",
    }
    symbol = symbols.get(currency, currency)
    return f"{symbol} {value:,.2f}"
