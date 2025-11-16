"""
Colorbar Utilities
Standardized colorbar creation for visualizations.
"""

from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from typing import Optional


def add_colorbar(ax, mappable, location: str = 'lower center',
                 width: str = '40%', height: str = '4%',
                 label: str = '', theme_manager=None,
                 orientation: str = 'horizontal', **kwargs):
    """
    Add standardized colorbar to axis.

    Args:
        ax: Matplotlib axis
        mappable: The mappable object (e.g., hexbin, scatter, pcolormesh)
        location: Position of colorbar (e.g., 'lower center', 'right')
        width: Colorbar width as percentage string
        height: Colorbar height as percentage string
        label: Colorbar label text
        theme_manager: ThemeManager instance for styling (optional)
        orientation: 'horizontal' or 'vertical'
        **kwargs: Additional arguments passed to inset_axes

    Returns:
        Colorbar object
    """
    # Default bbox settings based on location
    bbox_kwargs = kwargs.pop('bbox_to_anchor', None)
    if bbox_kwargs is None:
        if location == 'lower center':
            bbox_kwargs = (0, 0.05, 1, 1)
        elif location == 'upper center':
            bbox_kwargs = (0, 0.95, 1, 1)
        else:
            bbox_kwargs = (0, 0, 1, 1)

    # Create inset axes for colorbar
    cax = inset_axes(
        ax,
        width=width,
        height=height,
        loc=location,
        bbox_to_anchor=bbox_kwargs,
        bbox_transform=ax.transAxes,
        **kwargs
    )

    # Create colorbar
    cb = ax.figure.colorbar(mappable, cax=cax, orientation=orientation)

    # Apply theme styling if provided
    if theme_manager:
        # Style colorbar outline
        cb.outline.set_edgecolor(theme_manager.get_color('border'))
        cb.outline.set_linewidth(0.5)

        # Style colorbar ticks
        cb.ax.tick_params(
            colors=theme_manager.get_color('text_primary'),
            labelsize=8,
            length=3,
            width=0.5
        )

        # Style colorbar label
        if label:
            cb.set_label(
                label,
                color=theme_manager.get_color('text_primary'),
                size=9,
                weight='500'
            )
    else:
        # Basic styling without theme
        if label:
            cb.set_label(label, size=9)
        cb.ax.tick_params(labelsize=8)

    return cb


def remove_colorbar(colorbar):
    """
    Remove a colorbar from the figure.

    Args:
        colorbar: Colorbar object to remove
    """
    if colorbar is not None:
        try:
            colorbar.remove()
        except Exception:
            pass
