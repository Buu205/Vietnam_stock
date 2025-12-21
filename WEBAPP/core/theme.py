"""
Theme Configuration - Crypto Terminal Dark Mode
================================================

Modern fintech/crypto dashboard with glassmorphism effects.
Optimized for OLED displays and trading interfaces.

Design Direction:
- Dark mode fintech/crypto aesthetic
- Glassmorphism cards with blur effects
- Trading terminal color scheme
- Space Grotesk + DM Sans typography

Updated: 2025-12-21
"""

# ============================================================================
# CRYPTO TERMINAL COLOR PALETTE
# ============================================================================

# Primary accent colors (Fintech/Crypto style)
PURPLE = {
    'primary': '#8B5CF6',      # Electric Purple (main CTA)
    'dark': '#7C3AED',         # Darker purple (hover states)
    'light': '#A78BFA',        # Lighter purple (highlights)
    'pale': '#C4B5FD',         # Very light purple (text accents)
    'glow': 'rgba(139, 92, 246, 0.4)',  # Glow effect
}

CYAN = {
    'primary': '#06B6D4',      # Cyan (secondary actions)
    'dark': '#0891B2',         # Darker cyan
    'light': '#22D3EE',        # Lighter cyan (highlights)
    'pale': '#A5F3FC',         # Very light cyan
    'glow': 'rgba(6, 182, 212, 0.4)',   # Glow effect
}

AMBER = {
    'primary': '#F59E0B',      # Amber Gold (highlights, warnings)
    'dark': '#D97706',         # Darker amber
    'light': '#FBBF24',        # Lighter amber
    'pale': '#FDE68A',         # Very light amber
}

# ============================================================================
# SEMANTIC COLORS (Trading Terminal)
# ============================================================================

SEMANTIC = {
    # Market indicators (Trading colors)
    'positive': '#10B981',     # Emerald Green (bullish, gains)
    'negative': '#EF4444',     # Red (bearish, losses)
    'neutral': '#6B7280',      # Gray (unchanged, hold)

    # Alert levels
    'success': '#10B981',      # Emerald (success messages)
    'warning': '#F59E0B',      # Amber (warnings)
    'error': '#EF4444',        # Red (errors, critical)
    'info': '#8B5CF6',         # Purple (information)

    # Chart colors (Trading terminal)
    'bullish': '#10B981',      # Green (up candles)
    'bearish': '#EF4444',      # Red (down candles)
    'volume': '#8B5CF6',       # Purple (volume bars)
    'primary_line': '#06B6D4', # Cyan (main trend line)
    'secondary_line': '#F59E0B', # Amber (comparison line)
    'area_fill': '#8B5CF6',    # Purple (area charts)
}

# ============================================================================
# DARK THEME (Crypto Terminal - OLED Optimized)
# ============================================================================

DARK_THEME = {
    # Backgrounds (Deep purple-black for OLED)
    'background': '#0F0B1E',          # Deep purple-black (OLED friendly)
    'surface': '#1A1625',             # Card surface
    'elevated': '#252033',            # Elevated cards
    'hover': '#2D2640',               # Hover state

    # Text (WCAG AA Compliant)
    'text_primary': '#F8FAFC',        # White text
    'text_secondary': '#94A3B8',      # Muted gray
    'text_accent': '#C4B5FD',         # Purple tint
    'text_disabled': '#475569',       # Disabled gray

    # Borders
    'border': 'rgba(255, 255, 255, 0.08)',   # Subtle glass border
    'border_hover': 'rgba(139, 92, 246, 0.3)', # Purple glow border
    'divider': 'rgba(255, 255, 255, 0.05)',  # Subtle dividers

    # Accents
    'accent_primary': '#8B5CF6',      # Electric Purple
    'accent_secondary': '#06B6D4',    # Cyan
    'accent_tertiary': '#F59E0B',     # Amber

    # Status colors
    'positive': '#10B981',            # Emerald green
    'negative': '#EF4444',            # Red
    'neutral': '#6B7280',             # Gray
}

# ============================================================================
# GLASSMORPHISM EFFECTS
# ============================================================================

GLASS = {
    # Card backgrounds
    'bg_subtle': 'rgba(255, 255, 255, 0.03)',
    'bg_medium': 'rgba(255, 255, 255, 0.05)',
    'bg_strong': 'rgba(255, 255, 255, 0.08)',

    # Borders
    'border': 'rgba(255, 255, 255, 0.08)',
    'border_hover': 'rgba(139, 92, 246, 0.3)',

    # Blur
    'blur': 'blur(12px)',
    'blur_strong': 'blur(20px)',

    # Shadows
    'shadow': '0 8px 32px rgba(0, 0, 0, 0.3)',
    'shadow_hover': '0 8px 32px rgba(139, 92, 246, 0.15)',
    'shadow_glow': '0 0 15px rgba(139, 92, 246, 0.4)',

    # Inner highlight
    'inner_highlight': 'inset 0 1px 0 rgba(255, 255, 255, 0.05)',
    'inner_highlight_hover': 'inset 0 1px 0 rgba(255, 255, 255, 0.08)',
}

# ============================================================================
# CHART COLOR PALETTES
# ============================================================================

# Main chart palette (categorical data - Fintech style)
CHART_PALETTE = [
    '#8B5CF6',  # Electric Purple
    '#06B6D4',  # Cyan
    '#F59E0B',  # Amber
    '#10B981',  # Emerald
    '#EC4899',  # Pink
    '#3B82F6',  # Blue
    '#A78BFA',  # Light Purple
    '#22D3EE',  # Light Cyan
]

# Trading chart colors
TRADING_COLORS = {
    'bullish': '#10B981',         # Green candles
    'bearish': '#EF4444',         # Red candles
    'volume_up': 'rgba(16, 185, 129, 0.4)',   # Green volume
    'volume_down': 'rgba(239, 68, 68, 0.4)',  # Red volume
    'ma_20': '#8B5CF6',           # MA 20 line
    'ma_50': '#06B6D4',           # MA 50 line
    'ma_200': '#F59E0B',          # MA 200 line
    'grid': 'rgba(255, 255, 255, 0.05)',      # Grid lines
}

# Sequential palette (heatmaps, gradients)
SEQUENTIAL = {
    'purple': ['#1E1B4B', '#4C1D95', '#6D28D9', '#8B5CF6', '#A78BFA', '#C4B5FD'],
    'cyan': ['#083344', '#155E75', '#0891B2', '#06B6D4', '#22D3EE', '#67E8F9'],
    'emerald': ['#022C22', '#064E3B', '#047857', '#10B981', '#34D399', '#6EE7B7'],
}

# Diverging palette (positive/negative comparison)
DIVERGING = {
    'green_red': [
        '#047857',  # Dark green (very positive)
        '#10B981',  # Emerald (positive)
        '#34D399',  # Light green (slightly positive)
        '#374151',  # Neutral gray
        '#FCA5A5',  # Light red (slightly negative)
        '#EF4444',  # Red (negative)
        '#B91C1C',  # Dark red (very negative)
    ]
}

# ============================================================================
# GRADIENTS
# ============================================================================

GRADIENTS = {
    # Primary gradient (purple → cyan)
    'primary': 'linear-gradient(135deg, #8B5CF6 0%, #06B6D4 100%)',

    # Accent gradient (cyan → emerald)
    'accent': 'linear-gradient(135deg, #06B6D4 0%, #10B981 100%)',

    # Warning gradient (amber)
    'warning': 'linear-gradient(135deg, #FBBF24 0%, #D97706 100%)',

    # Dark background gradient (deep purple)
    'dark_bg': 'linear-gradient(180deg, #0F0B1E 0%, #1A1625 100%)',

    # Neon glow gradient
    'neon_purple': 'linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(6, 182, 212, 0.2) 100%)',

    # Card gradient (glass effect)
    'glass_card': 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)',
}

# ============================================================================
# TYPOGRAPHY (Tech Terminal Style)
# ============================================================================

TYPOGRAPHY = {
    # Font families (Space Grotesk + DM Sans + JetBrains Mono)
    'display': '"Space Grotesk", "Inter", -apple-system, BlinkMacSystemFont, sans-serif',
    'heading': '"Space Grotesk", "Inter", -apple-system, BlinkMacSystemFont, sans-serif',
    'body': '"DM Sans", "Inter", -apple-system, BlinkMacSystemFont, sans-serif',
    'mono': '"JetBrains Mono", "SF Mono", "Fira Code", monospace',

    # Font sizes
    'h1': '36px',
    'h2': '30px',
    'h3': '24px',
    'h4': '20px',
    'h5': '18px',
    'h6': '16px',
    'body': '14px',
    'small': '12px',
    'tiny': '10px',

    # Font weights
    'thin': 300,
    'regular': 400,
    'medium': 500,
    'semibold': 600,
    'bold': 700,
    'extrabold': 800,
}

# ============================================================================
# SPACING & LAYOUT
# ============================================================================

SPACING = {
    'xs': '4px',
    'sm': '8px',
    'md': '16px',
    'lg': '24px',
    'xl': '32px',
    '2xl': '48px',
    '3xl': '64px',
}

RADIUS = {
    'none': '0',
    'sm': '6px',
    'md': '12px',
    'lg': '16px',
    'xl': '20px',
    '2xl': '24px',
    'full': '9999px',
}

SHADOWS = {
    'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.2)',
    'md': '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
    'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.4)',
    'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
    'glow_purple': '0 0 20px rgba(139, 92, 246, 0.3)',
    'glow_cyan': '0 0 20px rgba(6, 182, 212, 0.3)',
}

# ============================================================================
# COMPONENT SIZES
# ============================================================================

COMPONENTS = {
    # Cards (Glassmorphism)
    'card_padding': SPACING['lg'],
    'card_radius': RADIUS['lg'],

    # Metrics
    'metric_card_height': '140px',
    'metric_card_padding': SPACING['lg'],

    # Charts
    'chart_height_sm': '300px',
    'chart_height_md': '400px',
    'chart_height_lg': '500px',
    'chart_height_xl': '600px',

    # Tables
    'table_max_height': '600px',
    'table_row_height': '52px',

    # Sidebar
    'sidebar_width': '280px',
}

# ============================================================================
# Z-INDEX SCALE
# ============================================================================

Z_INDEX = {
    'base': 1,
    'dropdown': 100,
    'sticky': 150,
    'modal': 200,
    'popover': 250,
    'toast': 300,
    'tooltip': 400,
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_theme(mode='dark'):
    """
    Get theme configuration.
    Note: Only dark theme is available for crypto terminal design.

    Args:
        mode: 'dark' (light mode not supported in this theme)

    Returns:
        Theme dictionary
    """
    return DARK_THEME


def get_chart_color(index, palette='default'):
    """
    Get chart color by index.

    Args:
        index: Color index (0-based)
        palette: 'default', 'trading', or 'sequential_purple' etc.

    Returns:
        Hex color code
    """
    if palette == 'default':
        return CHART_PALETTE[index % len(CHART_PALETTE)]
    elif palette == 'trading':
        keys = list(TRADING_COLORS.keys())
        return TRADING_COLORS[keys[index % len(keys)]]
    elif palette.startswith('sequential_'):
        color_key = palette.replace('sequential_', '')
        return SEQUENTIAL[color_key][index % len(SEQUENTIAL[color_key])]
    else:
        return CHART_PALETTE[0]


def get_semantic_color(metric_type, value=None):
    """
    Get semantic color based on metric type and value.

    Args:
        metric_type: 'growth', 'change', 'ratio', 'bullish', 'bearish', etc.
        value: Numeric value (optional, for conditional coloring)

    Returns:
        Hex color code
    """
    if value is None:
        return SEMANTIC['neutral']

    if metric_type in ['growth', 'change', 'delta', 'pnl']:
        return SEMANTIC['positive'] if value >= 0 else SEMANTIC['negative']
    elif metric_type in ['bullish', 'buy']:
        return SEMANTIC['bullish']
    elif metric_type in ['bearish', 'sell']:
        return SEMANTIC['bearish']
    elif metric_type == 'ratio':
        return SEMANTIC['neutral']
    else:
        return SEMANTIC['info']


def get_glass_style(variant='default'):
    """
    Get glassmorphism CSS properties.

    Args:
        variant: 'default', 'hover', 'elevated'

    Returns:
        Dictionary of CSS properties
    """
    base = {
        'background': GLASS['bg_subtle'],
        'backdrop_filter': GLASS['blur'],
        'border': f"1px solid {GLASS['border']}",
        'border_radius': RADIUS['lg'],
        'box_shadow': f"{GLASS['shadow']}, {GLASS['inner_highlight']}",
    }

    if variant == 'hover':
        base['background'] = GLASS['bg_medium']
        base['border'] = f"1px solid {GLASS['border_hover']}"
        base['box_shadow'] = f"{GLASS['shadow_hover']}, {GLASS['inner_highlight_hover']}"
    elif variant == 'elevated':
        base['background'] = GLASS['bg_strong']
        base['backdrop_filter'] = GLASS['blur_strong']

    return base


# ============================================================================
# CSS EXPORT
# ============================================================================

def generate_css_variables(theme='dark'):
    """
    Generate CSS variables for the Crypto Terminal theme.

    Args:
        theme: 'dark' (only dark mode supported)

    Returns:
        CSS string with variables
    """
    theme_config = get_theme(theme)

    css = ":root {\n"

    # Theme colors
    for key, value in theme_config.items():
        css += f"  --{key.replace('_', '-')}: {value};\n"

    # Purple palette
    for key, value in PURPLE.items():
        css += f"  --purple-{key}: {value};\n"

    # Cyan palette
    for key, value in CYAN.items():
        css += f"  --cyan-{key}: {value};\n"

    # Semantic colors
    for key, value in SEMANTIC.items():
        css += f"  --semantic-{key.replace('_', '-')}: {value};\n"

    # Glass effects
    for key, value in GLASS.items():
        css += f"  --glass-{key.replace('_', '-')}: {value};\n"

    # Spacing
    for key, value in SPACING.items():
        css += f"  --spacing-{key}: {value};\n"

    # Typography
    css += f"  --font-display: {TYPOGRAPHY['display']};\n"
    css += f"  --font-heading: {TYPOGRAPHY['heading']};\n"
    css += f"  --font-body: {TYPOGRAPHY['body']};\n"
    css += f"  --font-mono: {TYPOGRAPHY['mono']};\n"

    # Z-index
    for key, value in Z_INDEX.items():
        css += f"  --z-{key}: {value};\n"

    css += "}\n"

    return css


# Example usage
if __name__ == '__main__':
    # Print dark theme CSS
    print(generate_css_variables('dark'))

    # Test color functions
    print(f"\nChart color 0: {get_chart_color(0)}")
    print(f"Chart color 1: {get_chart_color(1)}")
    print(f"Bullish color: {get_semantic_color('bullish', 1)}")
    print(f"Bearish color: {get_semantic_color('bearish', -1)}")
    print(f"\nGlass style: {get_glass_style('default')}")
