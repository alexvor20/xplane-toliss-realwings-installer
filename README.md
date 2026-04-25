# RealWings32X mod installer for Toliss A32Xceo/neo

Installer script for the [Realwings321](https://forums.x-plane.org/files/file/99442-realwings321-wing-replacement-mod-for-toliss-a321neoceo) and [Realwings320](https://forums.x-plane.org/files/file/99352-realwings320-wing-replacement-mod-for-toliss-a320neo/) mods.

## Overview

This script automates the setup described in the original mod readme.

It will:
* Create a RealWings_ACF folder
* Generate three .acf~ files (one per variant)

| Variant | Build from                                         | 
| -------- |----------------------------------------------------| 
| CEO wingtips | `Main`+`Glass`+`Secondary`+ `Flaps32X`             |
| CEO Sharklets | `MainNEO`+`GlassNEO`+`SecondaryNEO`+ `Flaps32X`    |
| NEO | `MainNEO`+`GlassNEO`+`SecondaryNEO`+ `Flaps32XNEO` |

`RealWingsSwitcher` lets you switch between variants.

Only one variant can be active at a time (mod limitation).

## Features

* Optional installation of new Window Frames
* Support for [Enhanced lights](https://forums.x-plane.org/files/file/69851-enhanced-lights-for-toliss-a319320321330340/) mod by [anndresv](https://forums.x-plane.org/profile/647102-anndresv/)

## Requirements 

* Any other mods that modify `lights_out32X_XP12.obj` or `Decals.obj` are likely incompatible. 
* Re-download RealWings mod if you already have it installed.
* Installed Crada mod with this [fork](https://github.com/alexvor20/xplane-toliss-carda-installer-RealWings) of Carda installer is expected.
  * This ensures correct coordinates if Carda is already installed.

## How to use: 


| Realwings320                                                                                                                                                                                                                                           | Realwings321                                                                                                                          | 
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------| 
| 1. Download [Realwings320](https://forums.x-plane.org/files/file/99352-realwings320-wing-replacement-mod-for-toliss-a320neo/) and [Realwings319](https://forums.x-plane.org/files/file/99042-realwings319-wing-replacement-mod-for-toliss-a319/)* mods | 1. Download [Realwings321](https://forums.x-plane.org/files/file/99442-realwings321-wing-replacement-mod-for-toliss-a321neoceo) mod   |
| 2. Merge `RealWings320` and `RealWings319`* folders' content from the corresponding mods into `objects/RealWings320` of your Toliss a320. Replace files if prompted.                                                                                    | 2. Copy `RealWings321` folder from `CEO` **_and_** `NEO` folders into your Toliss a321's objects folder. Replace files if prompted.. |
3. Download binaries for your OS from the [Releases](https://github.com/alexvor20/xplane-toliss-realwings-installer/releases/latest/)
5. Place all the installers into your Toliss a32X folder. Your final file structure should look like this:
```
A32X Base Folder/
├─ objects/
│  ├─ RealWings32X/
│  │  ├─ (33 files total)
├─ RealWings32X_installer
├─ RealWingsSwitcher
├─ install-carda-RealWings
```
5. Run `install-carda-RealWings`
6. Run `RealWings_installer`
7. Run `RealWingsSwitcher`. Any time you'd like to change the current variant, just run it again. You can also manualy switch between the variants. Simply copy the one you need from `A32X Base Folder/RealWings_ACF/` into `A32X Base Folder/`, delete the old `a32X.acf` and rename your chosen variant to `a32X.acf`.
 
\*  Skip `RealWings319` if you do not want the CEO variants.


## Credits and Licensing

This project is licensed under the GNU GPL v3.

[iy4vet's](https://github.com/iy4vet) [Carda installer](https://github.com/iy4vet/xplane-toliss-carda-installer) was used as a base for this installer.

[GeoBuilds](https://forums.x-plane.org/profile/962966-geobuilds/) and [Durantula2405](https://forums.x-plane.org/profile/843947-durantula2405/) - RealWings mod authors
