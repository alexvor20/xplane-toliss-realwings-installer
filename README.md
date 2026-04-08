# RealWings321 mod installer for Toliss A321ceo/neo

Installer script for the [Realwings321](https://forums.x-plane.org/files/file/99442-realwings321-wing-replacement-mod-for-toliss-a321neoceo) mod.

## What it does

Everything from the mod readme.
The script would create `RealWings_ACF` folder and three `.acf~` files for each variant in that folder.

| Variant | Build from | 
| -------- | ------------- | 
| CEO wingtips | `Main`+`Glass`+`Secondary`+ `Flaps321` |
| CEO Sharklets | `MainNEO`+`GlassNEO`+`SecondaryNEO`+ `Flaps321` |
| NEO | `MainNEO`+`GlassNEO`+`SecondaryNEO`+ `Flaps321NEO` |

`RealWingsSwitcher` would allow you to easily switch between variants. (Only one can be used at a time — limitation of the mod)

## Features

* Optional installation of new Window Frames
* Support for [Enhanced lights](https://forums.x-plane.org/files/file/69851-enhanced-lights-for-toliss-a319320321330340/) mod by [anndresv](https://forums.x-plane.org/profile/647102-anndresv/)

## Requirements 

* Any other mods that change `lights_out321_XP12.obj` and/or `Decals.obj` is unlikely to be supported. 
* Re-download RealWings321 mod if you already had it before.
* Installed Crada mod with this [fork](https://github.com/alexvor20/xplane-toliss-carda-installer-RealWings) of Carda installer is expected. It would correct the coordinates for compatibility if Carda mod was already installed.

## How to use: 


1. Download [Realwings321](https://forums.x-plane.org/files/file/99442-realwings321-wing-replacement-mod-for-toliss-a321neoceo) mod
2. Copy `RealWings321` folder from `CEO` **_and_** `NEO` folders into your Toliss a321's objects folder. Replace the files if needed.
3. Download the binaries for your OS from the [Releases](https://github.com/alexvor20/xplane-toliss-realwings-installer/releases/latest/) page:
4. Place all the installers into your Toliss a321 folder. Your final file structure should look like this:
```
A321 Base Folder/
├─ objects/
│  ├─ RealWings321/
│  │  ├─ A total of 33 files should be here
├─ RealWings321_installer
├─ RealWingsSwitcher
├─ install-carda-RealWings
```
5. Run `install-carda-RealWings`
6. Run `RealWings_installer`
7. Run `RealWingsSwitcher`. Any time you'd like to change the current variant, just run it again. You can also manualy switch between the variants. Simply copy the one you need from `A321 Base Folder/RealWings_ACF/` into `A321 Base Folder/`, delete the old `a321.acf` and rename your chosen variant to `a321.acf`.



## Credits and Licensing

This project is licensed under the GNU GPL v3.

[iy4vet's](https://github.com/iy4vet) [Carda installer](https://github.com/iy4vet/xplane-toliss-carda-installer) was used as a base for this installer.

[GeoBuilds](https://forums.x-plane.org/profile/962966-geobuilds/) and [Durantula2405](https://forums.x-plane.org/profile/843947-durantula2405/) - RealWings mod authors
