# RealWings321 mod installer for Toliss A321ceo/neo

Installer script for the [Realwings321](https://forums.x-plane.org/files/file/99442-realwings321-wing-replacement-mod-for-toliss-a321neoceo) mod.

## What it does
Everything from the mod readme.
The script would create RealWings_ACF folder and 3 .acf~ files for each variant in that folder.

| Variant | Build from | 
| -------- | ------------- | 
| CEO wingtips | All the files from CEO folder |
| CEO Sharklets | `MainNEO`+`GlassNEO`+`SecondaryNEO`+ the rest from the CEO folder |
| NEO | All the files from NEO folder |

RealWingsSwitcher Would allow you to easily switch between variants 

## Features

Optional installation of new Window Frames
Optional editing of ceo engines OBJs, lights_out321_XP12.obj and decals.obj
Support for [Enhanced lights](https://forums.x-plane.org/files/file/69851-enhanced-lights-for-toliss-a319320321330340/) mod by anndresv

## Requirements 

Installed crada mod with this [fork](https://github.com/alexvor20/xplane-toliss-carda-installer-RealWings) of carda installer is expected. (support for existing carda installation, it would correct the coordinates for 
compatibility)

I didn't quite figured the original idea so a change in the file structure is required to support simultaneous installation of CEO wingtips/CEO Sharklets/NEO variants.

File renamings in 
```
RealWings321 mod folder/
├─ NEO/
│  ├─ RealWings321/
```

* 321_Flaps_ALB --> 321_FlapsNEO_ALB
* 321_Flaps_NRM --> 321_FlapsNEO_NRM
* Flaps321 --> FlapsNEO (it does require tweaking .obj to for the corresponding texture and nrm above)
* Frames321 --> FramesNEO 
* Lines321 --> LinesNEO

Obviously renaming of the first two files leads to changes in FlapsNEO.obj
Lines 6 and 7 resectively changes.

```
TEXTURE	321_FlapsNEO_ALB.dds
TEXTURE_NORMAL	321_FlapsNEO_NRM.png
```

^Desperate need for feedback on this.^  

## Instalation: 

* AFTER the change in files copy all the content from CEO and NEO folders into Toliss a321 objects folder. (yes, in one folder) (only one file should be overwritten `custom_decal.png`, which is identical for both folders)
* run Carda_installer_realwings
* run RealWings_installer
* run RealWingsSwitcher

## Known issues

A wrong answer to the question regarding the Enhanced Light mod could lead to the wrong assumption that lights_out321_XP12.obj was already modified.

## Credits and Licensing

[iy4vet's](https://github.com/iy4vet) [carda installer](https://github.com/iy4vet/xplane-toliss-carda-installer) was used as a base for this installer

[GeoBuilds](https://forums.x-plane.org/profile/962966-geobuilds/) [Durantula2405](https://forums.x-plane.org/profile/843947-durantula2405/) - RealWings mod authors
