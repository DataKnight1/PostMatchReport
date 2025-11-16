"""
Pitch Factory
Factory for creating standardized pitch objects with consistent styling.
"""

from mplsoccer import Pitch, VerticalPitch
from Visual.theme_manager import ThemeManager


class PitchFactory:
    """Factory for creating standardized pitch objects."""

    def __init__(self, theme_manager: ThemeManager):
        """
        Initialize pitch factory.

        Args:
            theme_manager: ThemeManager instance for consistent styling
        """
        self.theme = theme_manager

    def create_pitch(self, pitch_type: str = 'custom', vertical: bool = False,
                     pitch_length: int = 105, pitch_width: int = 68,
                     linewidth: float = 1.5, **kwargs) -> Pitch:
        """
        Create a standard pitch with theme colors.

        Args:
            pitch_type: Type of pitch ('custom', 'statsbomb', 'opta', etc.)
            vertical: If True, create vertical pitch
            pitch_length: Length of pitch in meters
            pitch_width: Width of pitch in meters
            linewidth: Width of pitch lines
            **kwargs: Additional arguments passed to Pitch constructor

        Returns:
            Pitch or VerticalPitch object
        """
        # Get theme colors
        pitch_color = self.theme.get_color('pitch')
        line_color = self.theme.get_color('pitch_lines')

        # Common parameters
        params = {
            'pitch_type': pitch_type,
            'pitch_color': pitch_color,
            'line_color': line_color,
            'linewidth': linewidth,
            **kwargs
        }

        # Add dimensions for custom pitch
        if pitch_type == 'custom':
            params['pitch_length'] = pitch_length
            params['pitch_width'] = pitch_width

        # Create pitch
        if vertical:
            return VerticalPitch(**params)
        else:
            return Pitch(**params)

    def create_standard_pitch(self, **kwargs) -> Pitch:
        """
        Create standard horizontal pitch (105x68m).

        Args:
            **kwargs: Additional arguments passed to Pitch constructor

        Returns:
            Pitch object
        """
        return self.create_pitch(
            pitch_type='custom',
            pitch_length=105,
            pitch_width=68,
            linewidth=1.5,
            **kwargs
        )

    def create_vertical_pitch(self, **kwargs) -> VerticalPitch:
        """
        Create standard vertical pitch (105x68m).

        Args:
            **kwargs: Additional arguments passed to VerticalPitch constructor

        Returns:
            VerticalPitch object
        """
        return self.create_pitch(
            pitch_type='custom',
            pitch_length=105,
            pitch_width=68,
            linewidth=1.5,
            vertical=True,
            **kwargs
        )
