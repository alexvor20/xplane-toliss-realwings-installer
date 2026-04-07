# RealWings321 mod installer for Toliss A321ceo/neo

Installer script for the [Realwings321](https://forums.x-plane.org/files/file/99442-realwings321-wing-replacement-mod-for-toliss-a321neoceo) mod.

## What it does

Everything from the mod readme.
The script would create RealWings_ACF folder and 3 .acf~ files for each variant in that folder.

| Variant | Build from | 
| -------- | ------------- | 
| CEO wingtips | `Main`+`Glass`+`Secondary`+ `Flaps321` |
| CEO Sharklets | `MainNEO`+`GlassNEO`+`SecondaryNEO`+ `Flaps321` |
| NEO | `MainNEO`+`GlassNEO`+`SecondaryNEO`+ `Flaps321NEO` |

RealWingsSwitcher would allow you to easily switch between variants. (Only one can be used at a time — limitation of the mod)

## Features

* Optional installation of new Window Frames
* Support for [Enhanced lights](https://forums.x-plane.org/files/file/69851-enhanced-lights-for-toliss-a319320321330340/) mod by [anndresv](https://forums.x-plane.org/profile/647102-anndresv/)

## Requirements 

* Re-download RealWings321 mod if you already had it before.
* Installed Crada mod with this [fork](https://github.com/alexvor20/xplane-toliss-carda-installer-RealWings) of Carda installer is expected. It would correct the coordinates for compatibility if Carda mod was already installed.

## How to use: 

1. Copy `RealWings321` folder from `CEO` AND `NEO` folders into your toliss a321's objects folder. Replace the files if needed.
2. Download the binaries for your OS from the [Releases](https://github.com/alexvor20/xplane-toliss-realwings-installer/releases/latest/) page:
3. Place all the installers into your toliss a321 folder
4. Run Carda_installer_RealWings
5. Run RealWings_installer
6. Run RealWingsSwitcher

Your final file structure should look like this:
```
A321 Base Folder/
├─ objects/
│  ├─ RealWings321/
│  │  ├─ A total of 33 files should be here
├─ RealWings321_installer
├─ RealWingsSwitcher
├─ install-carda-RealWings
```

## Credits and Licensing

This project is licensed under the GNU GPL v3.

[iy4vet's](https://github.com/iy4vet) [Carda installer](https://github.com/iy4vet/xplane-toliss-carda-installer) was used as a base for this installer.

[GeoBuilds](https://forums.x-plane.org/profile/962966-geobuilds/) and [Durantula2405](https://forums.x-plane.org/profile/843947-durantula2405/) - RealWings mod authors
