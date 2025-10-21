# Live streaming software plugin for [ED Market Connector](https://github.com/EDCD/EDMarketConnector/wiki)

This plugin outputs status info from the game
[Elite Dangerous](https://www.elitedangerous.com/) to files for use as
[text sources](https://obsproject.com/wiki/Sources-Guide#text-gdi) in live
streaming software such as
[Open Broadcaster Software](https://obsproject.com/),
[GameShow](http://gameshow.net/),
[XSplit](https://www.xsplit.com/), etc.

## Installation

NB: If you previously used the Marginal version of this with older EDMC, then
just remove that version and entirely, replacing it with this one.

* On EDMC's Plugins settings tab press the “Open” button. This reveals the
  `plugins` folder where EDMC looks for plugins.
* Download the
  [latest release](https://github.com/Athanasius/EDMC-StreamSource/releases/latest).
* Open the `.zip` archive that you downloaded.  At its top level will be a
  folder named like `EDMC-StreamSource-Release-<version>`.
  1. Copy this into the EDMC `plugins` folder.
  2. Remove, or rename, any existing `EDMC-StreamSource` folder.
  3. Rename this new version's folder to `EDMC-StreamSource`.

You will need to re-start EDMC for it to notice and load the new/updated 
plugin.

## Output

The plugin writes the following status files into the folder that you specify
in EDMC's Output settings tab:

* `EDMC System.txt` - Name or the current star system.
* `EDMC StarPos.txt` - Star system's galactic coordinates.
* `EDMC Station.txt` - Name of the planetary or space station at which the
  player is docked. Empty if not docked.
* `EDMC Body.txt` - Name of the nearby star, planet or ring. Empty if not near
  any celestial body.
* `EDMC LatLon.txt` - Latitude and longitude coordinates. Empty if not near a
  planet.
* `EDMC Station or Body.txt` - Name of the station if docked, otherwise the
  name of the nearby celestial body, or empty.
* `EDMC Station or Body or System.txt` - Name of the station if docked,
  otherwise the name of the nearby celestial body, otherwise the name of the 
  star system.
* `EDMC ShipType.txt` - Ship type, e.g. Krait Phantom.
* `EDMC ShipName.txt` - Ship name, if the ship has been named. Otherwise, ship
  type.

If the app is started while the game is not running these files hold
placeholder values, which can be used to position the text in OBS Studio and
other streaming software.

## License

Copyright © 2019 Jonathan Harris.

Copyright © 2022 Athanasius.

Licensed under the
[GNU Public License (GPL)](http://www.gnu.org/licenses/gpl-2.0.html) version 2
or later.
