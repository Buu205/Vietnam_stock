"""
PyEcharts Chart Configuration - Centralized Settings
====================================================

Cung cấp configuration chuẩn cho tất cả PyEcharts charts trong project.
Tránh lặp lại lỗi API và đảm bảo consistency.

Author: AI Assistant
Date: 2025-10-02
"""

from pyecharts import options as opts
from typing import Optional, List, Dict, Any
import numpy as np


class ChartConfig:
    """Centralized PyEcharts chart configuration"""
    
    # ==================== DISPLAY SETTINGS ====================
    
    # Decimal precision for all numeric displays
    DECIMAL_PLACES = 2  # ✅ 2 chữ số thập phân (không phải 1!)
    
    # Chart dimensions
    DEFAULT_WIDTH = "100%"
    DEFAULT_HEIGHT = "320px"
    SMALL_HEIGHT = "250px"
    LARGE_HEIGHT = "400px"
    
    # ==================== COLOR PALETTE ====================
    
    # Primary colors for charts
    COLORS = {
        'blue': '#1f77b4',
        'orange': '#ff7f0e',
        'green': '#2ca02c',
        'red': '#d62728',
        'purple': '#9467bd',
        'brown': '#8c564b',
        'pink': '#e377c2',
        'gray': '#7f7f7f',
        'olive': '#bcbd22',
        'cyan': '#17becf'
    }
    
    # MA4 line color (contrast with bars)
    MA4_COLOR = "#e91e63"
    
    # Band colors for valuation
    BAND_COLORS = {
        'mean': '#616161',
        'sigma': '#9e9e9e'
    }
    
    # ==================== LAYOUT SETTINGS ====================
    
    # Legend positioning (sát đáy - không có slider nữa)
    LEGEND_BOTTOM = "2%"  # ✅ Sát đáy (đơn giản, clean)
    LEGEND_POSITION = "center"
    LEGEND_ORIENT = "horizontal"  # Ngang
    
    # X-axis name gap (khoảng cách giữa labels và axis name)
    XAXIS_NAME_GAP = 30  # pixels - đủ để hiển thị rõ ràng (giảm từ 35 vì đã bỏ slider)
    
    # Y-axis auto-scale padding
    YAXIS_PADDING_PCT = 0.1  # 10% padding trên/dưới
    
    # ==================== VALIDATION RANGES ====================
    
    # Reasonable ranges for valuation metrics (dùng cho validation)
    VALUATION_RANGES = {
        'pe_ratio': (0.1, 500),
        'pb_ratio': (0.01, 50),
        'ev_ebitda_ratio': (0.01, 100)
    }
    
    # ==================== HELPER METHODS ====================
    
    @staticmethod
    def round_value(value: float, decimals: int = None) -> float:
        """Round value to configured decimal places"""
        if decimals is None:
            decimals = ChartConfig.DECIMAL_PLACES
        return round(float(value), decimals)
    
    @staticmethod
    def round_series(values: List[float], decimals: int = None) -> List[Optional[float]]:
        """Round a series of values with None handling"""
        if decimals is None:
            decimals = ChartConfig.DECIMAL_PLACES
        return [round(float(v), decimals) if v is not None else None for v in values]
    
    @staticmethod
    def calculate_auto_scale_range(values: List[float], 
                                   force_zero: bool = False,
                                   padding_pct: float = None) -> tuple:
        """
        Calculate auto-scale Y-axis range based on data.
        
        Args:
            values: List of data values (can include None)
            force_zero: If True, y_min = 0 (for bar charts). If False, auto-calculate (for line charts)
            padding_pct: Padding percentage (default: 0.05 = 5% cho line, tighter fit)
        
        Returns:
            (y_min, y_max) rounded to DECIMAL_PLACES
        """
        if padding_pct is None:
            # ✅ Giảm padding từ 10% → 5% để chart fill nhiều space hơn
            padding_pct = 0.05  # 5% padding (tighter fit)
        
        # Filter out None values
        valid_values = [v for v in values if v is not None and not np.isnan(v)]
        
        if not valid_values:
            return (0, 100)
        
        data_min = float(min(valid_values))
        data_max = float(max(valid_values))
        
        # Calculate padding
        value_range = data_max - data_min
        padding = value_range * padding_pct if value_range > 0 else 1.0
        
        # Calculate range
        if force_zero:
            # ✅ Bar charts: Luôn bắt đầu từ 0
            y_min = 0
            y_max = data_max + padding
        else:
            # ✅ Line charts: Auto-scale cả min và max (tighter fit)
            y_min = max(0, data_min - padding)  # Không xuống âm cho valuation
            y_max = data_max + padding
        
        # Round to configured precision
        y_min = ChartConfig.round_value(y_min)
        y_max = ChartConfig.round_value(y_max)
        
        return (y_min, y_max)
    
    @staticmethod
    def get_standard_init_opts(height: str = None) -> opts.InitOpts:
        """Get standard InitOpts for charts"""
        if height is None:
            height = ChartConfig.DEFAULT_HEIGHT
        
        return opts.InitOpts(
            width=ChartConfig.DEFAULT_WIDTH,
            height=height
        )
    
    @staticmethod
    def get_standard_legend_opts() -> opts.LegendOpts:
        """
        Get standard LegendOpts - tránh overlap với slider.
        
        ✅ SAFE - No invalid parameters
        """
        return opts.LegendOpts(
            is_show=True,
            pos_bottom=ChartConfig.LEGEND_BOTTOM,  # ✅ pos_bottom (NOT bottom!)
            pos_left=ChartConfig.LEGEND_POSITION,  # ✅ pos_left (NOT left!)
            orient=ChartConfig.LEGEND_ORIENT,
            padding=[5, 5, 5, 5]
        )
    
    @staticmethod
    def get_standard_datazoom_opts() -> None:
        """
        Datazoom disabled - bỏ scroll/slider để layout đơn giản hơn.
        
        Note: Trước có mouse wheel zoom + slider, nhưng:
        - Gây overlap với legend/x-axis
        - Không cần thiết cho most use cases
        - User có thể filter date range qua sidebar
        
        Returns None để không add datazoom vào charts.
        """
        return None  # ✅ Bỏ hết datazoom
    
    @staticmethod
    def get_standard_xaxis_opts(name: str = "Date", rotate: int = 0) -> opts.AxisOpts:
        """
        Get standard X-axis options với proper spacing.
        
        Args:
            name: Axis name (e.g., "Date", "Quarter")
            rotate: Label rotation (0, 45, 90)
        
        ✅ SAFE - All valid parameters
        """
        return opts.AxisOpts(
            name=name,
            name_location="middle",  # Center the axis name
            name_gap=ChartConfig.XAXIS_NAME_GAP,  # ✅ Gap to avoid slider overlap
            axislabel_opts=opts.LabelOpts(rotate=rotate)
        )
    
    @staticmethod
    def get_auto_scale_yaxis_opts(values: List[float],
                                   name: str = "Value",
                                   include_zero: bool = True,
                                   formatter: str = "{value}") -> opts.AxisOpts:
        """
        Get Y-axis options with auto-calculated min/max.
        
        Args:
            values: All data values (including bands if any)
            name: Y-axis name
            include_zero: Don't go below 0
            formatter: Label formatter
        
        ✅ SAFE - Uses min_/max_ (with underscore!)
        """
        y_min, y_max = ChartConfig.calculate_auto_scale_range(values, include_zero)
        
        return opts.AxisOpts(
            name=name,
            min_=y_min,  # ✅ min_ with underscore!
            max_=y_max,  # ✅ max_ with underscore!
            axislabel_opts=opts.LabelOpts(formatter=formatter)
        )
    
    @staticmethod
    def get_standard_tooltip_opts() -> opts.TooltipOpts:
        """Get standard tooltip options"""
        return opts.TooltipOpts(
            trigger="axis",  # Show all series at once
            axis_pointer_type="cross"  # Crosshair
        )
    
    @staticmethod
    def get_standard_title_opts(title: str) -> opts.TitleOpts:
        """Get standard title options"""
        return opts.TitleOpts(
            title=title,
            pos_left="center"  # ✅ pos_left (NOT left!)
        )


class ValuationChartBuilder:
    """Helper class để build valuation charts với settings chuẩn"""
    
    @staticmethod
    def build_line_with_bands(x_vals: List[str],
                            y_vals: List[float],
                            title: str,
                            color: str,
                            include_bands: bool = True) -> Any:
        """
        Build line chart with mean and ±1σ bands.
        
        Args:
            x_vals: X-axis values (dates)
            y_vals: Y-axis values (PE/PB/EV ratios)
            title: Chart title
            color: Main line color
            include_bands: Whether to show statistical bands
        
        Returns:
            PyEcharts Line chart
        
        ✅ SAFE - Uses ChartConfig for all settings
        """
        from pyecharts.charts import Line
        
        # Round values to configured precision
        y_vals_rounded = ChartConfig.round_series(y_vals)
        
        # Calculate statistics if needed
        if include_bands:
            series_mean = float(np.nanmean([v for v in y_vals if v is not None]))
            series_std = float(np.nanstd([v for v in y_vals if v is not None]))
            
            band_plus = ChartConfig.round_series([series_mean + series_std] * len(x_vals))
            band_mean = ChartConfig.round_series([series_mean] * len(x_vals))
            band_minus = ChartConfig.round_series([max(series_mean - series_std, 0.0)] * len(x_vals))
            
            # Calculate auto-scale including bands
            all_values = y_vals + band_plus + band_mean + band_minus
        else:
            all_values = y_vals
        
        # Get auto-scale range
        y_min, y_max = ChartConfig.calculate_auto_scale_range(all_values)
        
        # Build chart
        chart = (
            Line(init_opts=ChartConfig.get_standard_init_opts())
            .add_xaxis(x_vals)
            .add_yaxis(
                title,
                y_vals_rounded,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(color=color, width=2.6),
                symbol_size=5,
                label_opts=opts.LabelOpts(is_show=False)
            )
        )
        
        # Add bands if requested
        if include_bands:
            chart.add_yaxis(
                f"{title} +1σ",
                band_plus,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(
                    color=ChartConfig.BAND_COLORS['sigma'], 
                    width=1.2, 
                    type_="dashed"
                ),
                label_opts=opts.LabelOpts(is_show=False)
            ).add_yaxis(
                f"{title} mean",
                band_mean,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(
                    color=ChartConfig.BAND_COLORS['mean'], 
                    width=1.2, 
                    type_="dotted"
                ),
                label_opts=opts.LabelOpts(is_show=False)
            ).add_yaxis(
                f"{title} -1σ",
                band_minus,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(
                    color=ChartConfig.BAND_COLORS['sigma'], 
                    width=1.2, 
                    type_="dashed"
                ),
                label_opts=opts.LabelOpts(is_show=False)
            )
        
        # Apply global options
        chart.set_global_opts(
            title_opts=ChartConfig.get_standard_title_opts(title),
            xaxis_opts=ChartConfig.get_standard_xaxis_opts(),
            yaxis_opts=opts.AxisOpts(
                name=title,
                min_=y_min,  # ✅ Auto-calculated
                max_=y_max,  # ✅ Auto-calculated
                axislabel_opts=opts.LabelOpts(formatter="{value}")
            ),
            tooltip_opts=ChartConfig.get_standard_tooltip_opts(),
            legend_opts=ChartConfig.get_standard_legend_opts(),
            datazoom_opts=ChartConfig.get_standard_datazoom_opts()
            # ❌ NO grid_opts here - not valid in set_global_opts()!
        )
        
        return chart


class BarChartBuilder:
    """Helper class để build bar charts với MA4 overlay"""
    
    @staticmethod
    def build_bar_with_ma4(x_vals: List[str],
                          y_vals: List[float],
                          ma4_vals: Optional[List[float]],
                          title: str,
                          color: str,
                          ma4_color: str = None) -> Any:
        """
        Build bar chart with MA4 line overlay.
        
        Args:
            x_vals: X-axis values (quarters)
            y_vals: Y-axis values (bar heights)
            ma4_vals: MA4 growth values (can be None)
            title: Chart title
            color: Bar color
            ma4_color: MA4 line color (default: ChartConfig.MA4_COLOR)
        
        Returns:
            PyEcharts Bar chart (with Line overlay if MA4 available)
        
        ✅ SAFE - Uses ChartConfig for all settings
        """
        from pyecharts.charts import Bar, Line
        
        if ma4_color is None:
            ma4_color = ChartConfig.MA4_COLOR
        
        # Round values
        y_vals_rounded = ChartConfig.round_series(y_vals)
        
        # Calculate auto-scale for bars
        y_min, y_max = ChartConfig.calculate_auto_scale_range(y_vals)
        
        # Build bar chart
        bar = (
            Bar(init_opts=ChartConfig.get_standard_init_opts(height="300px"))
            .add_xaxis(x_vals)
            .add_yaxis(
                title,
                y_vals_rounded,
                itemstyle_opts=opts.ItemStyleOpts(color=color, opacity=0.75),
                label_opts=opts.LabelOpts(is_show=False)
            )
            .extend_axis(
                yaxis=opts.AxisOpts(
                    name="Growth (%)",
                    type_="value",
                    axislabel_opts=opts.LabelOpts(formatter="{value}%"),
                    axisline_opts=opts.AxisLineOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False)
                )
            )
            .set_global_opts(
                title_opts=ChartConfig.get_standard_title_opts(title),
                xaxis_opts=ChartConfig.get_standard_xaxis_opts(name="Quarter", rotate=45),
                yaxis_opts=opts.AxisOpts(
                    name="Value (Billion VND)",
                    min_=y_min,  # ✅ Auto-scale
                    max_=y_max,  # ✅ Auto-scale
                    axislabel_opts=opts.LabelOpts(formatter="{value}")
                ),
                tooltip_opts=ChartConfig.get_standard_tooltip_opts(),
                legend_opts=ChartConfig.get_standard_legend_opts(),
                datazoom_opts=ChartConfig.get_standard_datazoom_opts()
                # ❌ NO grid_opts!
            )
        )
        
        # Add MA4 line if available
        if ma4_vals and len(ma4_vals) == len(x_vals):
            valid_ma4_count = sum(1 for v in ma4_vals if v is not None)
            
            if valid_ma4_count >= 2:
                ma4_rounded = ChartConfig.round_series(ma4_vals)
                
                line = (
                    Line()
                    .add_xaxis(x_vals)
                    .add_yaxis(
                        f"{title} MA4",
                        ma4_rounded,
                        yaxis_index=1,  # Secondary y-axis
                        is_smooth=True,
                        linestyle_opts=opts.LineStyleOpts(color=ma4_color, width=2.6),
                        symbol_size=5,
                        label_opts=opts.LabelOpts(is_show=False)
                    )
                )
                bar.overlap(line)
        
        return bar


# ==================== KNOWN ISSUES & FIXES ====================

"""
TRÁNH CÁC LỖI SAU:

1. ❌ GridOpts parameter names
   WRONG: GridOpts(left="10%", right="10%", top="10%", bottom="10%")
   RIGHT: GridOpts(pos_left="10%", pos_right="10%", pos_top="10%", pos_bottom="10%")

2. ❌ grid_opts in set_global_opts()
   WRONG: chart.set_global_opts(grid_opts=...)
   RIGHT: Grid().add(chart, grid_opts=...)  # Only with Grid container!

3. ❌ DataZoomOpts height/width
   WRONG: DataZoomOpts(height="20px", width="100%")
   RIGHT: DataZoomOpts(pos_bottom="8%")  # Position only, no size!

4. ❌ AxisOpts min/max without underscore
   WRONG: AxisOpts(min=0, max=100)
   RIGHT: AxisOpts(min_=0, max_=100)  # With underscore!

5. ❌ Boolean parameters without is_
   WRONG: LabelOpts(show=True)
   RIGHT: LabelOpts(is_show=True)  # With is_ prefix!

NGUYÊN TẮC:
- Position parameters: Luôn dùng pos_*
- Min/Max parameters: Luôn có underscore (min_, max_)
- Boolean parameters: Thường có is_ prefix
- Size parameters: Chỉ có trong InitOpts và GridOpts, không có trong DataZoomOpts
- grid_opts: Chỉ dùng với Grid container, KHÔNG dùng trong set_global_opts()

LUÔN KIỂM TRA:
help(opts.DataZoomOpts)  # To see valid parameters
https://pyecharts.org/    # Official documentation
"""

# ==================== EXAMPLE USAGE ====================

"""
# Example 1: Valuation chart với bands
chart = ValuationChartBuilder.build_line_with_bands(
    x_vals=dates,
    y_vals=pe_values,
    title="P/E",
    color=ChartConfig.COLORS['blue'],
    include_bands=True
)

# Example 2: Bar chart với MA4
chart = BarChartBuilder.build_bar_with_ma4(
    x_vals=quarters,
    y_vals=revenue_values,
    ma4_vals=ma4_growth_values,
    title="Revenue",
    color=ChartConfig.COLORS['orange']
)

# Example 3: Custom chart với auto-scale
from pyecharts.charts import Line

y_min, y_max = ChartConfig.calculate_auto_scale_range(data_values)

chart = (
    Line(init_opts=ChartConfig.get_standard_init_opts())
    .add_xaxis(x_data)
    .add_yaxis("Series", ChartConfig.round_series(y_data))
    .set_global_opts(
        title_opts=ChartConfig.get_standard_title_opts("Title"),
        xaxis_opts=ChartConfig.get_standard_xaxis_opts(),
        yaxis_opts=opts.AxisOpts(min_=y_min, max_=y_max),
        legend_opts=ChartConfig.get_standard_legend_opts(),
        datazoom_opts=ChartConfig.get_standard_datazoom_opts()
    )
)
"""

