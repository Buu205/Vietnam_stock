"""
Theme Configuration - Company Brand Colors
==========================================

Official company colors + extended palette for financial dashboard.

Brand Colors:
- Primary Blue: #295CA9 (R:41 G:92 B:169)
- Accent Teal: #009B87 (R:0 G:155 B:135)
- Warning Gold: #FFC132 (R:255 G:193 B:50)

Created: 2025-12-15
"""

# ============================================================================
# BRAND COLORS (Official Company Palette)
# ============================================================================

BRAND = {
    'primary': '#295CA9',      # Company Blue
    'accent': '#009B87',       # Company Teal
    'warning': '#FFC132',      # Company Gold
}

# ============================================================================
# EXTENDED PALETTE (Based on Brand Colors)
# ============================================================================

# Primary Blue Family (Based on #295CA9)
BLUE = {
    'primary': '#295CA9',      # Main brand blue
    'dark': '#1E4580',         # Darker blue (hover states, emphasis)
    'light': '#4A7BC8',        # Lighter blue (backgrounds, subtle elements)
    'pale': '#E3EBF7',         # Very light blue (cards, sections)
    'navy': '#0A1E42',         # Deep navy (dark theme background)
}

# Teal/Green Family (Based on #009B87)
TEAL = {
    'primary': '#009B87',      # Main brand teal
    'dark': '#007766',         # Darker teal (positive metrics)
    'light': '#00C9AD',        # Lighter teal (highlights)
    'pale': '#E0F5F2',         # Very light teal (success backgrounds)
    'success': '#00A878',      # Success messages
}

# Gold/Orange Family (Based on #FFC132)
GOLD = {
    'primary': '#FFC132',      # Main brand gold
    'dark': '#E6A000',         # Darker gold (warnings)
    'light': '#FFD366',        # Lighter gold (highlights)
    'pale': '#FFF8E6',         # Very light gold (warning backgrounds)
    'amber': '#FFB000',        # Amber warning
}

# ============================================================================
# SEMANTIC COLORS (Financial Dashboard)
# ============================================================================

SEMANTIC = {
    # Market indicators
    'positive': '#00A878',     # Gains, growth, buy signals (teal-based)
    'negative': '#E63946',     # Losses, decline, sell signals (red)
    'neutral': '#6B7280',      # Unchanged, hold (gray)

    # Alert levels
    'success': '#00A878',      # Success messages (teal)
    'warning': '#FFC132',      # Warnings (brand gold)
    'error': '#E63946',        # Errors, critical (red)
    'info': '#295CA9',         # Information (brand blue)

    # Chart colors
    'revenue': '#009B87',      # Revenue (brand teal)
    'profit': '#00C9AD',       # Profit (light teal)
    'expense': '#E63946',      # Expenses (red)
    'asset': '#295CA9',        # Assets (brand blue)
    'liability': '#FFC132',    # Liabilities (brand gold)
    'equity': '#4A7BC8',       # Equity (light blue)
}

# ============================================================================
# THEME CONFIGURATIONS
# ============================================================================

# Dark Theme (Professional Financial - Bloomberg style)
DARK_THEME = {
    # Backgrounds
    'background': '#0A1E42',          # Deep navy (from BLUE.navy)
    'surface': '#1E4580',             # Dark blue surface (from BLUE.dark)
    'card': '#295CA9',                # Card background (brand blue)
    'hover': '#4A7BC8',               # Hover state (light blue)

    # Text
    'text_primary': '#FFFFFF',        # White text
    'text_secondary': '#E3EBF7',      # Light blue text (from BLUE.pale)
    'text_disabled': '#6B7280',       # Gray text

    # Borders
    'border': '#4A7BC8',              # Light blue borders
    'divider': '#1E4580',             # Dark blue dividers

    # Accents
    'accent_primary': '#009B87',      # Teal accent (brand)
    'accent_secondary': '#FFC132',    # Gold accent (brand)

    # Status colors
    'positive': '#00C9AD',            # Light teal (stands out on dark)
    'negative': '#FF6B6B',            # Bright red (softer than #E63946)
    'neutral': '#9CA3AF',             # Light gray
}

# Light Theme (Modern Minimalist - Clean style)
LIGHT_THEME = {
    # Backgrounds
    'background': '#FFFFFF',          # Pure white
    'surface': '#F8FAFC',             # Off-white
    'card': '#FFFFFF',                # White cards
    'hover': '#E3EBF7',               # Light blue hover (from BLUE.pale)

    # Text
    'text_primary': '#0A1E42',        # Deep navy text (from BLUE.navy)
    'text_secondary': '#1E4580',      # Dark blue text (from BLUE.dark)
    'text_disabled': '#9CA3AF',       # Gray text

    # Borders
    'border': '#E3EBF7',              # Light blue borders
    'divider': '#F1F5F9',             # Very light gray dividers

    # Accents
    'accent_primary': '#295CA9',      # Brand blue accent
    'accent_secondary': '#009B87',    # Teal accent

    # Status colors
    'positive': '#00A878',            # Teal green
    'negative': '#E63946',            # Red
    'neutral': '#6B7280',             # Gray
}

# ============================================================================
# CHART COLOR PALETTES
# ============================================================================

# Main chart palette (categorical data)
CHART_PALETTE = [
    '#295CA9',  # Brand Blue
    '#009B87',  # Brand Teal
    '#FFC132',  # Brand Gold
    '#4A7BC8',  # Light Blue
    '#00C9AD',  # Light Teal
    '#FFD366',  # Light Gold
    '#1E4580',  # Dark Blue
    '#007766',  # Dark Teal
]

# Sequential palette (heatmaps, gradients)
SEQUENTIAL = {
    'blue': ['#E3EBF7', '#4A7BC8', '#295CA9', '#1E4580', '#0A1E42'],
    'teal': ['#E0F5F2', '#00C9AD', '#009B87', '#007766', '#005544'],
    'gold': ['#FFF8E6', '#FFD366', '#FFC132', '#E6A000', '#CC8F00'],
}

# Diverging palette (comparing positive/negative)
DIVERGING = {
    'teal_red': [
        '#007766',  # Dark teal (very positive)
        '#009B87',  # Teal (positive)
        '#00C9AD',  # Light teal (slightly positive)
        '#F1F5F9',  # Neutral gray
        '#FFB4AB',  # Light red (slightly negative)
        '#E63946',  # Red (negative)
        '#C62828',  # Dark red (very negative)
    ]
}

# ============================================================================
# GRADIENTS
# ============================================================================

GRADIENTS = {
    # Brand gradient (blue → teal)
    'primary': 'linear-gradient(135deg, #295CA9 0%, #009B87 100%)',

    # Success gradient (light teal → dark teal)
    'success': 'linear-gradient(135deg, #00C9AD 0%, #007766 100%)',

    # Warning gradient (light gold → dark gold)
    'warning': 'linear-gradient(135deg, #FFD366 0%, #E6A000 100%)',

    # Dark background gradient
    'dark_bg': 'linear-gradient(180deg, #0A1E42 0%, #1E4580 100%)',

    # Card gradient (subtle blue)
    'card': 'linear-gradient(135deg, #295CA9 0%, #4A7BC8 100%)',
}

# ============================================================================
# TYPOGRAPHY
# ============================================================================

TYPOGRAPHY = {
    # Font families
    'heading': '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    'body': '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    'mono': '"JetBrains Mono", "Fira Code", "Courier New", monospace',

    # Font sizes
    'h1': '32px',
    'h2': '28px',
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
    'sm': '4px',
    'md': '8px',
    'lg': '12px',
    'xl': '16px',
    'full': '9999px',
}

SHADOWS = {
    'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
}

# ============================================================================
# COMPONENT SIZES
# ============================================================================

COMPONENTS = {
    # Cards
    'card_padding': SPACING['lg'],
    'card_radius': RADIUS['lg'],

    # Metrics
    'metric_card_height': '120px',
    'metric_card_padding': SPACING['md'],

    # Charts
    'chart_height_sm': '300px',
    'chart_height_md': '400px',
    'chart_height_lg': '500px',
    'chart_height_xl': '600px',

    # Tables
    'table_max_height': '600px',
    'table_row_height': '48px',

    # Sidebar
    'sidebar_width': '280px',
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_theme(mode='dark'):
    """
    Get theme configuration.

    Args:
        mode: 'dark' or 'light'

    Returns:
        Theme dictionary
    """
    return DARK_THEME if mode == 'dark' else LIGHT_THEME


def get_chart_color(index, palette='default'):
    """
    Get chart color by index.

    Args:
        index: Color index (0-based)
        palette: 'default' or 'sequential_blue' etc.

    Returns:
        Hex color code
    """
    if palette == 'default':
        return CHART_PALETTE[index % len(CHART_PALETTE)]
    elif palette.startswith('sequential_'):
        color_key = palette.replace('sequential_', '')
        return SEQUENTIAL[color_key][index % len(SEQUENTIAL[color_key])]
    else:
        return CHART_PALETTE[0]


def get_semantic_color(metric_type, value=None):
    """
    Get semantic color based on metric type and value.

    Args:
        metric_type: 'growth', 'change', 'ratio', etc.
        value: Numeric value (optional, for conditional coloring)

    Returns:
        Hex color code
    """
    if value is None:
        return SEMANTIC['neutral']

    if metric_type in ['growth', 'change', 'delta']:
        return SEMANTIC['positive'] if value >= 0 else SEMANTIC['negative']
    elif metric_type == 'ratio':
        # For ratios, green if good range, red if bad
        return SEMANTIC['neutral']  # Default, override in specific use cases
    else:
        return SEMANTIC['info']


# ============================================================================
# CSS EXPORT
# ============================================================================

def generate_css_variables(theme='dark'):
    """
    Generate CSS variables for the theme.

    Args:
        theme: 'dark' or 'light'

    Returns:
        CSS string with variables
    """
    theme_config = get_theme(theme)

    css = ":root {\n"

    # Theme colors
    for key, value in theme_config.items():
        css += f"  --{key.replace('_', '-')}: {value};\n"

    # Brand colors
    for key, value in BRAND.items():
        css += f"  --brand-{key}: {value};\n"

    # Semantic colors
    for key, value in SEMANTIC.items():
        css += f"  --semantic-{key.replace('_', '-')}: {value};\n"

    # Spacing
    for key, value in SPACING.items():
        css += f"  --spacing-{key}: {value};\n"

    # Typography
    css += f"  --font-heading: {TYPOGRAPHY['heading']};\n"
    css += f"  --font-body: {TYPOGRAPHY['body']};\n"
    css += f"  --font-mono: {TYPOGRAPHY['mono']};\n"

    css += "}\n"

    return css


# Example usage
if __name__ == '__main__':
    # Print dark theme CSS
    print(generate_css_variables('dark'))

    # Test color functions
    print(f"\nChart color 0: {get_chart_color(0)}")
    print(f"Chart color 1: {get_chart_color(1)}")
    print(f"Positive change color: {get_semantic_color('change', 5.2)}")
    print(f"Negative change color: {get_semantic_color('change', -3.1)}")
