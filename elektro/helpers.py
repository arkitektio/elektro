from .api.schema import (
    PartialAffineTransformationViewInput,
    PartialChannelViewInput,
    PartialTimepointViewInput,
    PartialOpticsViewInput,
    PartialLabelViewInput,
    ChannelFragment,
    FluorophoreFragment,
    ObjectiveFragment,
    InstrumentFragment,
    PartialRGBViewInput,
    CameraFragment,
    EraFragment,
    AntibodyFragment,
)
from .scalars import ThreeDVector, Milliseconds, FourByFourMatrix
from rath.scalars import ID
from typing import List, Optional
import numpy as np


def accesor_from_slices(slices: List[str] = None):
    """Creates an accesor from a list of slices

    Args:
        slices (List[str]): The slices

    Returns:
        str: The accesor
    """
    return {}


def view_from_pixel_size_and_position(
    scale: ThreeDVector,
    position: ThreeDVector,
    stage: ID = None,
    **kwargs,
) -> PartialAffineTransformationViewInput:
    """Creates a view from the pixel size and position

    Args:
        x_scale (float): The x scale
        y_scale (float): The y scale
        z_scale (float): The z scale
        x_position (float): The x position
        y_position (float): The y position
        z_position (float): The z position

    Returns:
        View: The view
    """
    x_scale, y_scale, z_scale = scale
    x_position, y_position, z_position = position

    affine = np.array(
        [
            [x_scale, 0, 0, x_position],
            [0, y_scale, 0, y_position],
            [0, 0, z_scale, z_position],
            [0, 0, 0, 1],
        ]
    )

    FourByFourMatrix.validate(affine)

    return PartialAffineTransformationViewInput(
        affineMatrix=affine, stage=stage, **kwargs
    )


def view_from_channel(
    channel: ChannelFragment, c: int = None, **kwargs
) -> PartialChannelViewInput:
    """Creates a view from the channel name

    Args:
        channel_name (str): The channel name

    Returns:
        View: The view
    """
    if c is not None:
        return PartialChannelViewInput(channel=channel, cMax=c, cMin=c, **kwargs)

    return PartialChannelViewInput(channel=channel, **kwargs)


def opticsview_from_path(
    objective: ObjectiveFragment = None,
    camera: CameraFragment = None,
    instrument: InstrumentFragment = None,
    **kwargs,
) -> PartialOpticsViewInput:
    """Creates a view from the channel name

    Args:
        channel_name (str): The channel name

    Returns:
        View: The view
    """
    return PartialOpticsViewInput(
        objective=objective, camera=camera, instrument=instrument, **kwargs
    )


def timepoint_view_from_era(
    era: EraFragment,
    index_since_start: int = None,
    ms_since_start: Milliseconds = None,
    t: int = None,
) -> PartialTimepointViewInput:
    """Creates a view from the channel name

    Args:
        channel_name (str): The channel name

    Returns:
        View: The view
    """
    if t is not None:
        return PartialTimepointViewInput(
            era=era.id,
            index_since_start=index_since_start,
            ms_since_start=ms_since_start,
            tMax=t,
            tMin=t,
        )

    return PartialTimepointViewInput(
        era=era.id,
        index_since_start=index_since_start,
        ms_since_start=ms_since_start,
    )


def labelview_from_agents(
    fluorophore: Optional[FluorophoreFragment] = None,
    primary_antibody: AntibodyFragment = None,
    secondary_antibody: AntibodyFragment = None,
    c: int = None,
    **kwargs,
) -> PartialLabelViewInput:
    """Creates a view from the channel name

    Args:
        channel_name (str): The channel name

    Returns:
        View: The view
    """
    if c is not None:
        return PartialLabelViewInput(
            fluorophore=fluorophore.id,
            primary_antibody=primary_antibody.id,
            secondary_antibody=secondary_antibody.id,
            cMax=c,
            cMin=c,
            **kwargs,
        )

    return PartialLabelViewInput(
        fluorophore=fluorophore.id,
        primary_antibody=primary_antibody.id,
        secondary_antibody=secondary_antibody.id,
        **kwargs,
    )


def view_from_color(
    rgb_context: ID,
    c: int = None,
    r_scale: float = 1,
    g_scale: float = 1,
    b_scale: float = 1,
    **kwargs,
) -> PartialRGBViewInput:
    """Creates a view from the channel name

    Args:
        channel_name (str): The channel name

    Returns:
        View: The view
    """
    if c is not None:
        return PartialRGBViewInput(
            context=rgb_context,
            cMax=c,
            cMin=c,
            rScale=r_scale,
            gScale=g_scale,
            bScale=b_scale,
            **kwargs,
        )
