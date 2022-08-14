# -*- coding: utf-8 -*-
"""
Output status info to text files for use with streaming software.

Examples of such are Open Broadcaster Software, GameShow, XSplit, etc.

* https://obsproject.com/wiki/Sources-Guide#text-gdi
* https://telestream.force.com/kb2/articles/Knowledge_Article/Gameshow-Add-Text
* https://www.xsplit.com/broadcaster/getting-started/adding-text
"""

# For Python 2&3 a version of open that supports both encoding and universal newlines
from io import open
from os.path import join
from typing import List

from config import config
from edmc_data import coriolis_ship_map as ship_map
from l10n import Locale

VERSION = '1.10'


class StreamSource():
    """Hold the global data."""

    def __init__(self):
        # Info recorded, with initial placeholder values
        self.system: str = 'System'
        self.station: str = 'Station'
        self.starpos: List[float, float, float] = (0.0, 0.0, 0.0)
        self.body: str = 'Body'
        self.latlon: List[float, float] = (0.0, 0.0)
        self.stationorbody: str = 'Station or Body'
        self.stationorbodyorsystem: str = 'Station or Body or System'
        self.shiptype: str = 'Ship type'
        self.shipname: str = 'Ship name'

        self.outdir = config.get_str('outdir')


stream_source = StreamSource()


def write_all():
    """Write all data out to respective files."""
    write_file('EDMC System.txt', stream_source.system)
    write_file(
        'EDMC StarPos.txt',
        f'{Locale.string_from_number(stream_source.starpos[0], 5)} '
        f'{Locale.string_from_number(stream_source.starpos[1], 5)} '
        f'{Locale.string_from_number(stream_source.starpos[2], 5)}'
    )
    write_file('EDMC Station.txt', stream_source.station)
    write_file('EDMC Body.txt', stream_source.body)
    write_file(
        'EDMC LatLon.txt',
        f'{Locale.string_from_number(stream_source.latlon[0], 6)} '
        f'{Locale.string_from_number(stream_source.latlon[1], 6)}'
    )
    write_file('EDMC Station or Body.txt', stream_source.stationorbody)
    write_file('EDMC Station or Body or System.txt', stream_source.stationorbodyorsystem)
    write_file('EDMC ShipType.txt', stream_source.shiptype)
    write_file('EDMC ShipName.txt', stream_source.shipname)


def write_file(name: str, text: str = None) -> None:
    """Write one file's text."""
    # File needs to be closed for the streaming software to notice its been updated.
    with open(join(stream_source.outdir, name), 'w', encoding='utf-8') as h:
        h.write(f'{text or ""}\n')
        h.close()

    return None


def plugin_start3(plugin_dir: str) -> str:
    """Handle start-up of plugin."""
    # Write placeholder values for positioning
    write_all()

    return 'EDMC-StreamSource'

# Write placeholder values for positioning
def plugin_start():
    write_all()


# Write all files in new location if output directory changed
def prefs_changed(cmdr, is_beta):
    if stream_source.outdir != config.get('outdir'):
        stream_source.outdir = config.get('outdir')
        write_all()


# Write any files with changed data
def journal_entry(cmdr, is_beta, system, station, entry, state):

    if stream_source.system != system:
        stream_source.system = system
        write_file('EDMC System.txt', stream_source.system)

    if 'StarPos' in entry and stream_source.starpos != tuple(entry['StarPos']):
        stream_source.starpos = tuple(entry['StarPos'])
        write_file('EDMC StarPos.txt', '%s %s %s' % (
            Locale.string_from_number(stream_source.starpos[0], 5),
            Locale.string_from_number(stream_source.starpos[1], 5),
            Locale.string_from_number(stream_source.starpos[2], 5)))

    if stream_source.station != station:
        stream_source.station = station
        write_file('EDMC Station.txt', stream_source.station)

    if entry['event'] in ['FSDJump', 'LeaveBody', 'Location', 'SupercruiseEntry', 'SupercruiseExit'] and entry.get('BodyType') in [None, 'Station']:
        if stream_source.body:
            stream_source.body = None
            write_file('EDMC Body.txt')
    elif 'Body' in entry:	# StartUp, ApproachBody, Location, SupercruiseExit
        if stream_source.body != entry['Body']:
            stream_source.body = entry['Body']
            write_file('EDMC Body.txt', stream_source.body)
    elif entry['event'] == 'StartUp':
        stream_source.body = None
        write_file('EDMC Body.txt')

    if stream_source.stationorbody != (stream_source.station or stream_source.body):
        stream_source.stationorbody = (stream_source.station or stream_source.body)
        write_file('EDMC Station or Body.txt', stream_source.stationorbody)

    if stream_source.stationorbodyorsystem != (stream_source.station or stream_source.body or stream_source.system):
        stream_source.stationorbodyorsystem = (stream_source.station or stream_source.body or stream_source.system)
        write_file('EDMC Station or Body or System.txt', stream_source.stationorbodyorsystem)

    if stream_source.shiptype != state['ShipType']:
        stream_source.shiptype = state['ShipType']
        write_file('EDMC ShipType.txt', ship_map.get(stream_source.shiptype, stream_source.shiptype))

    if stream_source.shipname != (state['ShipName'] or stream_source.shiptype):
        stream_source.shipname = (state['ShipName'] or stream_source.shiptype)
        write_file('EDMC ShipName.txt', state['ShipName'] and state['ShipName'] or ship_map.get(stream_source.shiptype, stream_source.shiptype))


# Write any files with changed data
def dashboard_entry(cmdr, is_beta, entry):
    if 'Latitude' in entry and 'Longitude' in entry:
        if stream_source.latlon != (entry['Latitude'], entry['Longitude']):
            stream_source.latlon = (entry['Latitude'], entry['Longitude'])
            write_file('EDMC LatLon.txt', '%s %s' % (
                Locale.string_from_number(stream_source.latlon[0], 6),
                Locale.string_from_number(stream_source.latlon[1], 6)))
    elif stream_source.latlon:
        stream_source.latlon = None
        write_file('EDMC LatLon.txt')
