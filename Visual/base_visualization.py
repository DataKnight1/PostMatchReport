"""
Base Visualization
Base class for all visualizations with common functionality.
"""

from Visual.theme_manager import ThemeManager
from Visual.pitch_factory import PitchFactory
from Visual.utils import add_colorbar
from mplsoccer import Pitch


class BaseVisualization:
    """Base class for all visualizations."""

    def __init__(self, theme_manager: ThemeManager = None,
                 pitch_color: str = None, line_color: str = None,
                 show_colorbars: bool = True):
        """
        Initialize base visualization.

        Args:
            theme_manager: ThemeManager instance (if None, creates default)
            pitch_color: Override pitch color (for backward compatibility)
            line_color: Override line color (for backward compatibility)
            show_colorbars: Whether to show colorbars on visualizations
        """
        # Initialize theme manager
        if theme_manager is None:
            # Create theme based on colors for backward compatibility
            if line_color == '#d0d7de':
                self.theme = ThemeManager('dark')
            else:
                self.theme = ThemeManager('light')
        else:
            self.theme = theme_manager

        # Store legacy color parameters for backward compatibility
        self.pitch_color = pitch_color or self.theme.get_color('pitch')
        self.line_color = line_color or self.theme.get_color('pitch_lines')
        self.show_colorbars = show_colorbars

        # Initialize pitch factory
        self.pitch_factory = PitchFactory(self.theme)

    def create_pitch(self, **kwargs) -> Pitch:
        """
        Create a standard pitch with theme colors.

        Args:
            **kwargs: Additional arguments passed to pitch creation

        Returns:
            Pitch object
        """
        return self.pitch_factory.create_standard_pitch(**kwargs)

    def prepare_axis(self, ax, title: str = '', apply_theme: bool = True):
        """
        Prepare axis with standard styling.

        Args:
            ax: Matplotlib axis
            title: Optional title for the axis
            apply_theme: Whether to apply theme styling
        """
        # Set title if provided
        if title:
            ax.set_title(
                title,
                color=self.theme.get_color('text_primary'),
                fontsize=11,
                fontweight='600',
                pad=10
            )

        # Apply theme styling
        if apply_theme:
            self.theme.apply_to_axis(ax)

    def add_colorbar(self, ax, mappable, **kwargs):
        """
        Add themed colorbar to axis.

        Args:
            ax: Matplotlib axis
            mappable: Mappable object for colorbar
            **kwargs: Additional arguments passed to add_colorbar

        Returns:
            Colorbar object or None if show_colorbars is False
        """
        if not self.show_colorbars:
            return None

        return add_colorbar(ax, mappable, theme_manager=self.theme, **kwargs)

    def get_text_color(self) -> str:
        """Get primary text color from theme."""
        return self.theme.get_color('text_primary')

    def get_secondary_text_color(self) -> str:
        """Get secondary text color from theme."""
        return self.theme.get_color('text_secondary')

    def get_background_color(self) -> str:
        """Get background color from theme."""
        return self.theme.get_color('background')

    def get_surface_color(self) -> str:
        """Get surface/panel color from theme."""
        return self.theme.get_color('surface')

    def is_dark_theme(self) -> bool:
        """Check if using dark theme."""
        return self.theme.is_dark_theme()

    def is_monochrome(self) -> bool:
        """Check if using monochrome theme."""
        return self.theme.is_monochrome()

    def get_heatmap_cmap(self, team_color: str = None) -> str:
        """
        Get appropriate colormap for heatmaps.

        Args:
            team_color: Optional team color (ignored for monochrome theme)

        Returns:
            Colormap name
        """
        if self.is_monochrome():
            return 'Greys'
        else:
            return self.theme.get_heatmap_cmap()

    def apply_monochrome_team_style(self, ax, elements, team_type='home'):
        """
        Apply monochrome styling to team elements.

        Args:
            ax: Matplotlib axis
            elements: Plot elements to style
            team_type: 'home' or 'away'
        """
        if not self.is_monochrome():
            return

        style = self.theme.get_team_style(team_type)

        # Apply style based on element type
        if hasattr(elements, 'set_color'):
            elements.set_color(style['color'])
        if hasattr(elements, 'set_linestyle'):
            elements.set_linestyle(style['linestyle'])
        if hasattr(elements, 'set_linewidth'):
            elements.set_linewidth(style['linewidth'])
        if hasattr(elements, 'set_alpha'):
            elements.set_alpha(style['alpha'])
