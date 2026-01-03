"""
Display settings and theme configuration.
Cấu hình hiển thị và theme cho ứng dụng.
"""

import streamlit as st
from typing import Dict, Any, Optional
from .config import DisplayConfig

class DisplaySettings:
    """Manage display settings and themes."""
    
    def __init__(self):
        self.config = DisplayConfig()
        self._setup_page_config()
        self._inject_custom_css()
    
    def _setup_page_config(self):
        """Setup Streamlit page configuration."""
        st.set_page_config(
            page_title="VN Finance Dashboard",
            page_icon=":material/analytics:",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/your-repo/stock_dashboard',
                'Report a bug': 'https://github.com/your-repo/stock_dashboard/issues',
                'About': "VN Finance Dashboard - Phân tích tài chính chứng khoán Việt Nam"
            }
        )
    
    def _inject_custom_css(self):
        """Inject custom CSS for better styling."""
        css = """
        <style>
        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 100%;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            padding-top: 2rem;
        }
        
        /* Header styling */
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .section-header {
            font-size: 1.5rem;
            font-weight: 600;
            color: #2c3e50;
            margin-top: 2rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 0.5rem;
        }
        
        /* Metric styling */
        .metric-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
            margin-bottom: 1rem;
        }
        
        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #6c757d;
            margin-top: 0.25rem;
        }
        
        /* Chart styling */
        .chart-container {
            background-color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        
        /* Table styling */
        .dataframe {
            font-size: 0.9rem;
        }
        
        .dataframe th {
            background-color: #f8f9fa;
            font-weight: 600;
            text-align: center;
        }
        
        .dataframe td {
            text-align: right;
        }
        
        /* Button styling */
        .stButton > button {
            background-color: #1f77b4;
            color: white;
            border: none;
            border-radius: 0.25rem;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        
        .stButton > button:hover {
            background-color: #1565c0;
        }
        
        /* Navigation buttons */
        .nav-button {
            width: 100%;
            margin-bottom: 0.5rem;
        }
        
        .nav-button.active {
            background-color: #2ca02c;
        }
        
        /* Alert styling */
        .alert-info {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 0.25rem;
            padding: 0.75rem;
            margin-bottom: 1rem;
        }
        
        .alert-warning {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 0.25rem;
            padding: 0.75rem;
            margin-bottom: 1rem;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            
            .main-header {
                font-size: 2rem;
            }
            
            .section-header {
                font-size: 1.25rem;
            }
        }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    
    def get_chart_config(self, chart_type: str = 'default') -> Dict[str, Any]:
        """
        Get chart configuration based on type.
        
        Args:
            chart_type: Type of chart ('valuation', 'financial', 'technical')
        
        Returns:
            Dictionary with chart configuration
        """
        base_config = {
            'font': {
                'family': 'Arial, sans-serif',
                'size': self.config.CHART_CONFIG['font_sizes']['axis_label']
            },
            'margin': self.config.CHART_CONFIG['margins'],
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white'
        }
        
        if chart_type == 'valuation':
            base_config.update({
                'xaxis': {
                    'title': 'Ngày',
                    'titlefont': {'size': self.config.CHART_CONFIG['font_sizes']['axis_label']},
                    'tickfont': {'size': self.config.CHART_CONFIG['font_sizes']['tick']}
                },
                'yaxis': {
                    'title': 'Tỷ lệ định giá',
                    'titlefont': {'size': self.config.CHART_CONFIG['font_sizes']['axis_label']},
                    'tickfont': {'size': self.config.CHART_CONFIG['font_sizes']['tick']}
                }
            })
        elif chart_type == 'financial':
            base_config.update({
                'xaxis': {
                    'title': 'Kỳ báo cáo',
                    'titlefont': {'size': self.config.CHART_CONFIG['font_sizes']['axis_label']},
                    'tickfont': {'size': self.config.CHART_CONFIG['font_sizes']['tick']}
                },
                'yaxis': {
                    'title': 'Giá trị (tỷ VND)',
                    'titlefont': {'size': self.config.CHART_CONFIG['font_sizes']['axis_label']},
                    'tickfont': {'size': self.config.CHART_CONFIG['font_sizes']['tick']}
                }
            })
        elif chart_type == 'technical':
            base_config.update({
                'xaxis': {
                    'title': 'Ngày',
                    'titlefont': {'size': self.config.CHART_CONFIG['font_sizes']['axis_label']},
                    'tickfont': {'size': self.config.CHART_CONFIG['font_sizes']['tick']}
                },
                'yaxis': {
                    'title': 'Giá trị',
                    'titlefont': {'size': self.config.CHART_CONFIG['font_sizes']['axis_label']},
                    'tickfont': {'size': self.config.CHART_CONFIG['font_sizes']['tick']}
                }
            })
        
        return base_config
    
    def get_color_scheme(self, scheme: str = 'default') -> Dict[str, str]:
        """
        Get color scheme for charts.
        
        Args:
            scheme: Color scheme name ('default', 'banking', 'technical')
        
        Returns:
            Dictionary with color mappings
        """
        if scheme == 'banking':
            return {
                'primary': '#1f77b4',
                'secondary': '#ff7f0e',
                'success': '#2ca02c',
                'warning': '#d62728',
                'info': '#9467bd'
            }
        elif scheme == 'technical':
            return {
                'primary': '#2ca02c',
                'secondary': '#d62728',
                'success': '#1f77b4',
                'warning': '#ff7f0e',
                'info': '#9467bd'
            }
        else:
            return self.config.CHART_CONFIG['colors']
    
    def show_metric_card(self, label: str, value: str, delta: Optional[str] = None, 
                        delta_color: str = "normal") -> None:
        """
        Display a metric card with consistent styling.
        
        Args:
            label: Metric label
            value: Metric value (formatted string)
            delta: Optional delta value
            delta_color: Color for delta ('normal', 'inverse', 'off')
        """
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**{label}**")
            st.markdown(f'<div class="metric-value">{value}</div>', unsafe_allow_html=True)
        
        if delta:
            with col2:
                st.metric("Change", "", delta=delta, delta_color=delta_color)
    
    def show_section_header(self, title: str, level: int = 2) -> None:
        """
        Display a section header with consistent styling.
        
        Args:
            title: Header title
            level: Header level (1-6)
        """
        if level == 1:
            st.markdown(f'<h1 class="main-header">{title}</h1>', unsafe_allow_html=True)
        elif level == 2:
            st.markdown(f'<h2 class="section-header">{title}</h2>', unsafe_allow_html=True)
        else:
            st.markdown(f'<h{level}>{title}</h{level}>')

# Global display settings instance
display_settings = DisplaySettings()
