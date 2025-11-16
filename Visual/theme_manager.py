"""
Theme Manager
Centralized theme and styling management for all visualizations.
"""

from typing import Dict, Any


class ThemeManager:
    """Centralized theme and styling management."""

    THEMES = {
        'monochrome': {
            'background': '#ffffff',
            'surface': '#fafafa',
            'border': '#e0e0e0',
            'text_primary': '#000000',
            'text_secondary': '#666666',
            'text_tertiary': '#999999',
            'pitch': '#fafafa',
            'pitch_lines': '#666666',
            'interactive': '#000000',
            'interactive_hover': '#333333',
        },
        'dark': {
            'background': '#22272e',
            'surface': '#2b313a',
            'border': '#9aa6b2',
            'text_primary': '#e6edf3',
            'text_secondary': '#9aa6b2',
            'text_tertiary': '#6e7681',
            'pitch': '#2b313a',
            'pitch_lines': '#d0d7de',
            'interactive': '#e6edf3',
            'interactive_hover': '#ffffff',
        },
        'light': {
            'background': '#f0f0f0',
            'surface': '#ffffff',
            'border': '#cccccc',
            'text_primary': '#000000',
            'text_secondary': '#333333',
            'text_tertiary': '#666666',
            'pitch': '#d6c39f',
            'pitch_lines': '#0e1117',
            'interactive': '#4CAF50',
            'interactive_hover': '#45a049',
        }
    }

    def __init__(self, theme: str = 'dark'):
        """
        Initialize theme manager.

        Args:
            theme: Theme name ('monochrome', 'dark', or 'light')
        """
        self.theme = theme.lower()
        if self.theme not in self.THEMES:
            raise ValueError(f"Unknown theme: {theme}. Available: {list(self.THEMES.keys())}")
        self.colors = self.THEMES[self.theme]

    def get_color(self, key: str) -> str:
        """
        Get color value for a given key.

        Args:
            key: Color key (e.g., 'background', 'text_primary')

        Returns:
            Hex color string
        """
        return self.colors.get(key, '#000000')

    def apply_to_axis(self, ax):
        """
        Apply theme styling to a matplotlib axis.

        Args:
            ax: Matplotlib axis object
        """
        try:
            # Set background
            ax.set_facecolor(self.get_color('surface'))

            # Style spines (borders)
            for spine in ax.spines.values():
                spine.set_color(self.get_color('border'))
                spine.set_linewidth(0.5)

            # Style ticks
            ax.tick_params(
                colors=self.get_color('text_primary'),
                labelsize=8,
                length=3,
                width=0.5
            )

            # Style tick labels
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_color(self.get_color('text_primary'))

            # Style title
            if ax.get_title():
                ax.set_title(
                    ax.get_title(),
                    color=self.get_color('text_primary'),
                    fontsize=11,
                    fontweight='600',
                    pad=10
                )

            # Style axis labels
            if ax.xaxis.label.get_text():
                ax.xaxis.label.set_color(self.get_color('text_secondary'))
                ax.xaxis.label.set_fontsize(9)

            if ax.yaxis.label.get_text():
                ax.yaxis.label.set_color(self.get_color('text_secondary'))
                ax.yaxis.label.set_fontsize(9)

            # Style legend
            legend = ax.get_legend()
            if legend is not None:
                legend.get_frame().set_facecolor(self.get_color('surface'))
                legend.get_frame().set_edgecolor(self.get_color('border'))
                legend.get_frame().set_linewidth(0.5)
                for text in legend.get_texts():
                    text.set_color(self.get_color('text_primary'))
                    text.set_fontsize(8)

        except Exception as e:
            # Fail gracefully if any styling fails
            pass

    def get_team_style(self, team_type: str = 'home') -> Dict[str, Any]:
        """
        Get visualization style for a team based on theme.

        Args:
            team_type: 'home' or 'away'

        Returns:
            Dictionary with style properties
        """
        if self.theme == 'monochrome':
            # Black & white differentiation using patterns and shapes
            if team_type == 'home':
                return {
                    'color': '#000000',
                    'marker': 'o',          # Circle
                    'linestyle': '-',       # Solid
                    'linewidth': 2,
                    'alpha': 0.8,
                    'hatch': '///',         # Diagonal lines
                }
            else:  # away
                return {
                    'color': '#666666',
                    'marker': 's',          # Square
                    'linestyle': '--',      # Dashed
                    'linewidth': 1.5,
                    'alpha': 0.6,
                    'hatch': '...',         # Dots
                }
        else:
            # For colored themes, return basic style (color will be provided separately)
            return {
                'marker': 'o',
                'linestyle': '-',
                'linewidth': 2,
                'alpha': 0.8,
            }

    def get_shot_style(self, is_goal: bool = False, is_on_target: bool = False,
                       team_color: str = None) -> Dict[str, Any]:
        """
        Get style for shot markers based on outcome and theme.

        Args:
            is_goal: Whether shot was a goal
            is_on_target: Whether shot was on target
            team_color: Team color (ignored for monochrome theme)

        Returns:
            Dictionary with marker style properties
        """
        if self.theme == 'monochrome':
            if is_goal:
                return {
                    'marker': 'o',
                    'facecolor': '#000000',
                    'edgecolor': '#000000',
                    'linewidth': 1.5,
                    'label': 'Goal'
                }
            elif is_on_target:
                return {
                    'marker': 'o',
                    'facecolor': 'none',
                    'edgecolor': '#000000',
                    'linewidth': 1.5,
                    'label': 'On Target'
                }
            else:
                return {
                    'marker': 'x',
                    'facecolor': '#666666',
                    'edgecolor': '#666666',
                    'linewidth': 1.5,
                    'label': 'Off Target'
                }
        else:
            # Colored themes
            color = team_color or self.get_color('interactive')
            if is_goal:
                return {
                    'marker': 'o',
                    'facecolor': '#00ff00',
                    'edgecolor': color,
                    'linewidth': 1.5,
                    'label': 'Goal'
                }
            elif is_on_target:
                return {
                    'marker': 'o',
                    'facecolor': color,
                    'edgecolor': color,
                    'linewidth': 1.5,
                    'label': 'On Target'
                }
            else:
                return {
                    'marker': 'x',
                    'facecolor': color,
                    'edgecolor': color,
                    'linewidth': 1.5,
                    'label': 'Off Target'
                }

    def get_heatmap_cmap(self) -> str:
        """
        Get appropriate colormap for heatmaps based on theme.

        Returns:
            Matplotlib colormap name
        """
        if self.theme == 'monochrome':
            return 'Greys'
        elif self.theme == 'dark':
            return 'hot'
        else:
            return 'YlOrRd'

    def is_dark_theme(self) -> bool:
        """Check if current theme is dark."""
        return self.theme == 'dark'

    def is_monochrome(self) -> bool:
        """Check if current theme is monochrome."""
        return self.theme == 'monochrome'

    def __repr__(self):
        return f"ThemeManager(theme='{self.theme}')"
