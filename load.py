# -*- coding: utf-8 -*-
"""
Output status info to text files for use with streaming software.

Examples of such are Open Broadcaster Software, GameShow, XSplit, etc.

* https://obsproject.com/wiki/Sources-Guide#text-gdi
* https://telestream.force.com/kb2/articles/Knowledge_Article/Gameshow-Add-Text
* https://www.xsplit.com/broadcaster/getting-started/adding-text

EDMC StreamSource Plugin - Improved version with better error handling and logging.
"""

# For Python 2&3 a version of open that supports both encoding and universal newlines
import logging
from io import open
from os import makedirs
from os.path import exists
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Optional, Tuple

from config import config
from edmc_data import coriolis_ship_map as ship_map
from l10n import Locale

VERSION = '1.11'

# Setup logging
logger = logging.getLogger(__name__)


class StreamSource:
    """Hold the global data."""

    def __init__(self) -> None:
        """Initialize StreamSource with default placeholder values."""
        # Info recorded, with initial placeholder values
        self.system: str = 'System'
        self.station: str = 'Station'
        self.star_pos: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.body: Optional[str] = 'Body'
        self.latlon: Optional[Tuple[float, float]] = (0.0, 0.0)
        self.station_or_body: Optional[str] = 'Station or Body'
        self.station_or_body_or_system: str = 'Station or Body or System'
        self.ship_type: str = 'Ship type'
        self.ship_name: str = 'Ship name'

        self.outdir = config.get_str('outdir')
        self._ensure_output_directory()

    def _ensure_output_directory(self) -> None:
        """Ensure the output directory exists."""
        if self.outdir and not exists(self.outdir):
            try:
                makedirs(self.outdir, exist_ok=True)
                logger.info(f"Created output directory: {self.outdir}")
            except OSError as e:
                logger.error(f"Failed to create output directory {self.outdir}: {e}")

    def update_output_directory(self) -> None:
        """Update output directory and ensure it exists."""
        new_outdir = config.get_str('outdir')
        if self.outdir != new_outdir:
            self.outdir = new_outdir
            self._ensure_output_directory()


stream_source = StreamSource()


def write_all() -> None:
    """Write all data out to respective files."""
    write_file('EDMC System.txt', stream_source.system)

    # Format star position coordinates
    star_pos_text = (
        f'{Locale.string_from_number(stream_source.star_pos[0], 5)} '
        f'{Locale.string_from_number(stream_source.star_pos[1], 5)} '
        f'{Locale.string_from_number(stream_source.star_pos[2], 5)}'
    )
    write_file('EDMC StarPos.txt', star_pos_text)

    write_file('EDMC Station.txt', stream_source.station)
    write_file('EDMC Body.txt', stream_source.body)

    # Format latitude/longitude if available
    if stream_source.latlon:
        latlon_text = (
            f'{Locale.string_from_number(stream_source.latlon[0], 6)} '
            f'{Locale.string_from_number(stream_source.latlon[1], 6)}'
        )
        write_file('EDMC LatLon.txt', latlon_text)
    else:
        write_file('EDMC LatLon.txt')

    write_file('EDMC Station or Body.txt', stream_source.station_or_body)
    write_file('EDMC Station or Body or System.txt', stream_source.station_or_body_or_system)
    write_file('EDMC ShipType.txt', stream_source.ship_type)
    write_file('EDMC ShipName.txt', stream_source.ship_name)


def write_file(name: str, text: Optional[str] = None) -> None:
    """
    Write text to a file safely.

    Args:
        name: Filename to write to
        text: Text content to write (optional)
    """
    if not stream_source.outdir:
        logger.warning("No output directory configured")
        return

    filepath = Path(stream_source.outdir) / name
    try:
        # File needs to be closed for the streaming software to notice its been updated.
        with open(filepath, 'w', encoding='utf-8', newline='\n') as h:
            h.write(f'{text or ""}\n')
        logger.debug(f"Updated file: {name} with content: {text or ''}")
    except (OSError, IOError) as e:
        logger.error(f"Failed to write file {name}: {e}")


def plugin_start3(plugin_dir: str) -> str:
    """Handle start-up of plugin."""
    # Write placeholder values for positioning
    write_all()

    return 'EDMC-StreamSource'


def prefs_changed(cmdr: str, is_beta: bool) -> None:
    """Handle any changes to application preferences."""
    # Write all files in new location if output directory changed.
    old_outdir = stream_source.outdir
    stream_source.update_output_directory()
    if old_outdir != stream_source.outdir:
        logger.info(f"Output directory changed from {old_outdir} to {stream_source.outdir}")
        write_all()


def journal_entry(
        cmdr: str,
        is_beta: bool,
        system: str,
        station: str,
        entry: MutableMapping[str, Any],
        state: Mapping[str, Any]
) -> Optional[str]:
    """
    Process a journal event and update relevant status files.

    Args:
        cmdr: Commander name
        is_beta: Whether running in beta mode
        system: Current system name
        station: Current station name
        entry: Journal entry data
        state: Current game state

    Returns:
        None
    """
    _update_system_info(system, entry)
    _update_station_info(station)
    _update_body_info(entry)
    _update_combined_location_info()
    _update_ship_info(state)
    return None


def _update_system_info(system: str, entry: MutableMapping[str, Any]) -> None:
    """Update system-related information."""
    if stream_source.system != system:
        stream_source.system = system
        write_file('EDMC System.txt', stream_source.system)

    # Update star position if available
    star_pos = entry.get('StarPos')
    if star_pos is not None:
        new_star_pos = tuple(star_pos)
        if stream_source.star_pos != new_star_pos:
            stream_source.star_pos = new_star_pos
            star_pos_text = (
                f'{Locale.string_from_number(stream_source.star_pos[0], 5)} '
                f'{Locale.string_from_number(stream_source.star_pos[1], 5)} '
                f'{Locale.string_from_number(stream_source.star_pos[2], 5)}'
            )
            write_file('EDMC StarPos.txt', star_pos_text)


def _update_station_info(station: str) -> None:
    """Update station information."""
    if stream_source.station != station:
        stream_source.station = station
        write_file('EDMC Station.txt', stream_source.station)


def _update_body_info(entry: MutableMapping[str, Any]) -> None:
    """Update body information based on journal entry."""
    event = entry.get('event', '')

    # Events that clear body information
    body_clearing_events = {'FSDJump', 'LeaveBody', 'Location', 'SupercruiseEntry', 'SupercruiseExit'}

    if event in body_clearing_events and entry.get('BodyType') in [None, 'Station']:
        if stream_source.body:
            stream_source.body = None
            write_file('EDMC Body.txt')
    elif 'Body' in entry:
        # Events like StartUp, ApproachBody, Location, SupercruiseExit
        new_body = entry['Body']
        if stream_source.body != new_body:
            stream_source.body = new_body
            write_file('EDMC Body.txt', stream_source.body)
    elif event == 'StartUp':
        stream_source.body = None
        write_file('EDMC Body.txt')


def _update_combined_location_info() -> None:
    """Update combined location information files."""
    # Station or Body
    new_station_or_body = stream_source.station or stream_source.body
    if stream_source.station_or_body != new_station_or_body:
        stream_source.station_or_body = new_station_or_body
        write_file('EDMC Station or Body.txt', stream_source.station_or_body)

    # Station or Body or System
    new_station_or_body_or_system = (
        stream_source.station or stream_source.body or stream_source.system
    )
    if stream_source.station_or_body_or_system != new_station_or_body_or_system:
        stream_source.station_or_body_or_system = new_station_or_body_or_system
        write_file('EDMC Station or Body or System.txt', stream_source.station_or_body_or_system)


def _update_ship_info(state: Mapping[str, Any]) -> None:
    """Update ship information."""
    ship_type = state.get('ShipType', '')
    ship_name = state.get('ShipName', '')

    # Update ship type
    if stream_source.ship_type != ship_type:
        stream_source.ship_type = ship_type
        mapped_ship_type = ship_map.get(stream_source.ship_type, stream_source.ship_type)
        write_file('EDMC ShipType.txt', mapped_ship_type)

    # Update ship name
    effective_ship_name = ship_name or stream_source.ship_type
    if stream_source.ship_name != effective_ship_name:
        stream_source.ship_name = effective_ship_name
        display_name = ship_name or ship_map.get(stream_source.ship_type, stream_source.ship_type)
        write_file('EDMC ShipName.txt', display_name)


def dashboard_entry(
        cmdr: str,
        is_beta: bool,
        entry: MutableMapping[str, Any]
) -> Optional[str]:
    """
    Handle new Status.json data for latitude/longitude updates.

    Args:
        cmdr: Commander name
        is_beta: Whether running in beta mode
        entry: Status.json data

    Returns:
        None
    """
    latitude = entry.get('Latitude')
    longitude = entry.get('Longitude')

    if latitude is not None and longitude is not None:
        new_latlon = (latitude, longitude)
        if stream_source.latlon != new_latlon:
            stream_source.latlon = new_latlon
            latlon_text = (
                f'{Locale.string_from_number(latitude, 6)} '
                f'{Locale.string_from_number(longitude, 6)}'
            )
            write_file('EDMC LatLon.txt', latlon_text)
    elif stream_source.latlon is not None:
        stream_source.latlon = None
        write_file('EDMC LatLon.txt')

    return None
