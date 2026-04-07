import argparse
import re
import shutil
import struct
import sys
from dataclasses import dataclass
from pathlib import Path


# ─── Constants ────────────────────────────────────────────────────────────────

FLAGS_PREFILL = 4
FLAGS_ALL_VIEWS = 24
FLAGS_LIGHTNING_INSIDE = 1
FLAGS_LIGHTNING_GLASS_OUTSIDE = 2

STOCK_OBJECTS_TO_REMOVE = [
    "wing321R.obj",
    "wing321L.obj",
    "wings_glass.obj",
]

RealWings321_OBJS = [
    "RealWings321/Main.obj",
    "RealWings321/Flaps321.obj",
    "RealWings321/Secondary.obj",
    "RealWings321/Glass.obj",
    "RealWings321/Frames321.obj",
    "RealWings321/Lines321.obj",
]

NEO_OBJS = [
    "RealWings321/MainNEO.obj",
    "RealWings321/FlapsNEO.obj",    
    "RealWings321/SecondaryNEO.obj",
    "RealWings321/GlassNEO.obj",
    "RealWings321/FramesNEO.obj",
    "RealWings321/LinesNEO.obj",
]

# ─── Data Classes ─────────────────────────────────────────────────────────────


@dataclass
class ACFObject:
    """A Misc Object entry to add to the ACF."""

    file_stl: str
    flags: int = 0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    body: int = -1
    gear: int = -1
    wing: int = -1
    phi_ref: float = 0.0
    psi_ref: float = 0.0
    the_ref: float = 0.0
    is_internal: int = 0
    steers_with_gear: int = 0


# ─── Wings Definitions ──────────────────────────────────────────────────────

def _build_all_wings_objects(include_frames: bool = True) -> tuple[list[ACFObject], list[ACFObject], list[ACFObject]]:
        
    FramesLinesCEO = [] if not include_frames else [
        ACFObject(
            "RealWings321/Frames321.obj",
            FLAGS_LIGHTNING_INSIDE,
            6.00,
            2.06,
            60.98,
        ),
        ACFObject(
            "RealWings321/Lines321.obj",
            FLAGS_LIGHTNING_INSIDE,
            6.00,
            2.06,
            60.98,
        ),
    ]

    FramesLinesNEO = [] if not include_frames else [
        ACFObject(
            "RealWings321/FramesNEO.obj",
            FLAGS_LIGHTNING_INSIDE,
            6.00,
            2.06,
            60.98,
        ),
        ACFObject(
            "RealWings321/LinesNEO.obj",
            FLAGS_LIGHTNING_INSIDE,
            6.00,
            2.06,
            60.98,
        ),
    ]
    
    FlapsCEO = [
        ACFObject(
            "RealWings321/Flaps321.obj",
            FLAGS_ALL_VIEWS,
            0.00,
            0.40,
            72.30,
        ),

    ]
    
    FlapsNEO = [
        ACFObject(
            "RealWings321/FlapsNEO.obj",
            FLAGS_ALL_VIEWS,
            0.00,
            0.40,
            72.30,
        ),

    ]
    
    CEO = [
            ACFObject(
            "RealWings321/Main.obj",
            FLAGS_ALL_VIEWS,
            0.0,
            0.40,
            72.30,
        ),
            ACFObject(
            "RealWings321/Glass.obj",
            FLAGS_LIGHTNING_GLASS_OUTSIDE,
            0.00,
            0.40,
            72.30,
        ),
                ACFObject(
            "RealWings321/Secondary.obj",
            FLAGS_ALL_VIEWS,
            0.00,
            0.40,
            72.30,
        ),
        
    ]
    
    NEO = [
            ACFObject(
            "RealWings321/MainNEO.obj",
            FLAGS_ALL_VIEWS,
            0.0,
            0.40,
            72.30,
        ),
            ACFObject(
            "RealWings321/GlassNEO.obj",
            FLAGS_LIGHTNING_GLASS_OUTSIDE,
            0.00,
            0.40,
            72.30,
        ),
            ACFObject(
            "RealWings321/SecondaryNEO.obj",
            FLAGS_ALL_VIEWS,
            0.00,
            0.40,
            72.30,
        ),
    ]
    return (CEO + FlapsCEO + FramesLinesCEO), (NEO + FlapsCEO + FramesLinesCEO), (NEO + FlapsNEO + FramesLinesNEO)
    
# ─── Helpers ──────────────────────────────────────────────────────────────────


def format_float32(val: float) -> str:
    """Format a float in X-Plane's single-precision 9-decimal-place style."""
    packed = struct.pack("f", val)
    unpacked = struct.unpack("f", packed)[0]
    return f"{unpacked:.9f}"
    
# ─── ACF Editor ───────────────────────────────────────────────────────────────


class ACFEditor:
    """Reads, modifies, and writes X-Plane .acf property files."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self._header_lines: list[str] = []
        self._properties: dict[str, str] = {}
        self._footer_lines: list[str] = []
        self._read()

    def _read(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        in_properties = False
        past_properties = False

        for line in lines:
            stripped = line.rstrip("\n\r")
            if stripped.startswith("P "):
                in_properties = True
                past_properties = False
                parts = stripped.split(" ", 2)
                key = parts[1]
                value = parts[2] if len(parts) > 2 else ""
                self._properties[key] = value
            elif in_properties:
                past_properties = True
                in_properties = False
                self._footer_lines.append(line)
            elif past_properties:
                self._footer_lines.append(line)
            else:
                self._header_lines.append(line)
    
    def save(self, backup: bool = True, output_path: Path = None):
        if output_path is None:
            if backup:
                bak = self.filepath.with_suffix(self.filepath.suffix + ".bak")
                if not bak.exists():
                    shutil.copy2(self.filepath, bak)
            out = self.filepath
        else:
            out = output_path

        sorted_keys = sorted(self._properties.keys())
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            for line in self._header_lines:
                f.write(line)
            for key in sorted_keys:
                f.write(f"P {key} {self._properties[key]}\n")
            for line in self._footer_lines:
                f.write(line)

    def get_obja_entries(self) -> dict[int, dict[str, str]]:
        entries: dict[int, dict[str, str]] = {}
        for key, value in self._properties.items():
            if key.startswith("_obja/") and key != "_obja/count":
                parts = key.split("/")
                idx = int(parts[1])
                prop = "/".join(parts[2:])
                entries.setdefault(idx, {})[prop] = value
        return entries

    def get_obja_count(self) -> int:
        return int(self._properties.get("_obja/count", "0"))
    
    def has_object_by_filename(self, filename: str) -> bool:
        for key, value in self._properties.items():
            if key.endswith("/_v10_att_file_stl") and value == filename:
                return True
        return False

    def remove_and_add_objects(
        self,
        filenames_to_remove: list[str],
        objects_to_add: list[ACFObject],
    ) -> tuple[list[str], list[str]]:
        """Remove stock objects and add Carda objects, re-indexing as needed."""
        entries = self.get_obja_entries()

        indices_to_remove: set[int] = set()
        removed_names: list[str] = []
        for idx, props in entries.items():
            stl = props.get("_v10_att_file_stl", "")
            if stl in filenames_to_remove:
                indices_to_remove.add(idx)
                removed_names.append(stl)

        filenames_to_remove_set = set(filenames_to_remove)
        already_present: list[str] = []
        filtered_add: list[ACFObject] = []
        for obj in objects_to_add:
            if (
                obj.file_stl not in filenames_to_remove_set
                and self.has_object_by_filename(obj.file_stl)
            ):
                already_present.append(obj.file_stl)
            else:
                filtered_add.append(obj)

        if not indices_to_remove and not filtered_add:
            return removed_names, already_present

        # Remove old keys
        keys_to_delete = [
            k for k in self._properties if k.startswith("_obja/") and k != "_obja/count"
        ]
        for k in keys_to_delete:
            del self._properties[k]

        # Renumber survivors
        surviving = [
            (idx, props)
            for idx, props in sorted(entries.items())
            if idx not in indices_to_remove
        ]
        new_entries: dict[int, dict[str, str]] = {}
        for new_idx, (_old_idx, props) in enumerate(surviving):
            new_entries[new_idx] = props

        # Append new objects
        next_idx = len(new_entries)
        for obj in filtered_add:
            new_entries[next_idx] = self._acf_obj_to_props(obj)
            next_idx += 1

        # Write back
        for idx, props in sorted(new_entries.items()):
            for prop_name, value in sorted(props.items()):
                self._properties[f"_obja/{idx}/{prop_name}"] = value
        self._properties["_obja/count"] = str(len(new_entries))

        return removed_names, already_present

    @staticmethod
    def _acf_obj_to_props(obj: ACFObject) -> dict[str, str]:
        props: dict[str, str] = {
            "_obj_flags": str(obj.flags),
            "_v10_att_body": str(obj.body),
            "_v10_att_file_stl": obj.file_stl,
            "_v10_att_gear": str(obj.gear),
            "_v10_att_phi_ref": format_float32(obj.phi_ref),
            "_v10_att_psi_ref": format_float32(obj.psi_ref),
            "_v10_att_the_ref": format_float32(obj.the_ref),
            "_v10_att_wing": str(obj.wing),
            "_v10_att_x_acf_prt_ref": format_float32(obj.x),
            "_v10_att_y_acf_prt_ref": format_float32(obj.y),
            "_v10_att_z_acf_prt_ref": format_float32(obj.z),
            "_v10_is_internal": str(obj.is_internal),
            "_v10_steers_with_gear": str(obj.steers_with_gear),
        }
        return props

# ─── OBJ Editor ───────────────────────────────────────────────────────────────


class TRISLineDeleter:
    """Deletes specific TRIS lines at known line numbers in engine OBJ files."""

    # Map of relative path → 1-based line number to delete.
    # The line at that number must start with 'TRIS' (asserted before deletion).
    _TRIS_LINE_TARGETS: dict[str, int] = {
        "objects/V2500/iae_l_engine.obj": 56010,
        "objects/V2500/iae_r_engine.obj": 56010,
        "objects/CFM56/cfm56_l_engine.obj": 64124,
        "objects/CFM56/cfm56_r_engine.obj": 64122,
    }

    @classmethod
    def delete_tris_line(
        cls,
        filepath: Path,
        rel_path: str,
        dry_run: bool = False,
    ) -> bool:
        """Delete the target TRIS line from a known engine OBJ file.

        Args:
            filepath: Absolute path to the OBJ file.
            rel_path: Relative path key (e.g. 'objects/V2500/iae_l_engine.obj').
                      Used to look up the target line number.
            dry_run:  If True, validate but do not write changes.

        Returns:
            True if a line was (or would be) deleted, False if the file
            does not require this fix (line is already gone or wrong type).

        Raises:
            KeyError:   rel_path is not a known target.
            ValueError: The line at the target number does not start with 'TRIS'.
        """
        if rel_path not in cls._TRIS_LINE_TARGETS:
            raise KeyError(f"No TRIS deletion target registered for: {rel_path!r}")

        target_line = cls._TRIS_LINE_TARGETS[rel_path]  # 1-based

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        idx = target_line - 1  # convert to 0-based index

        if idx >= len(lines):
            raise ValueError(
                f"File has only {len(lines)} lines; "
                f"cannot access line {target_line} in {filepath}"
            )

        candidate = lines[idx]

        # Already removed — nothing to do.
        if not candidate.lstrip().startswith("TRIS"):
            if cls._tris_line_present(lines, idx):
                # TRIS shifted — surface this so the caller can investigate.
                raise ValueError(
                    f"Expected 'TRIS' at line {target_line} in {filepath!r}, "
                    f"but found: {candidate!r}. "
                    "The file may have already been partially edited."
                )
            return False  # TRIS line is simply gone — already fixed.

        if dry_run:
            return True

        # Back up before first modification.
        bak = filepath.with_suffix(filepath.suffix + ".bak")
        if not bak.exists():
            shutil.copy2(filepath, bak)

        del lines[idx]

        with open(filepath, "w", encoding="utf-8", newline="\n") as f:
            f.writelines(lines)

        return True

    @classmethod
    def needs_tris_deletion(cls, filepath: Path, rel_path: str) -> bool:
        """Return True if the target TRIS line is still present in the file."""
        if rel_path not in cls._TRIS_LINE_TARGETS:
            return False

        target_line = cls._TRIS_LINE_TARGETS[rel_path]

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        idx = target_line - 1
        if idx >= len(lines):
            return False

        return lines[idx].lstrip().startswith("TRIS")

    @classmethod
    def process_all(
        cls,
        base_dir: Path,
        dry_run: bool = False,
    ) -> dict[str, bool]:
        """Convenience method: iterate all registered targets under base_dir.

        Args:
            base_dir: Root directory of the aircraft package (the folder that
                      contains 'objects/').
            dry_run:  If True, report what would change without writing.

        Returns:
            Dict mapping rel_path → True (fixed / would fix) or False (already clean).
        """
        results: dict[str, bool] = {}
        for rel_path in cls._TRIS_LINE_TARGETS:
            filepath = base_dir / rel_path
            if not filepath.exists():
                results[rel_path] = False
                continue
            results[rel_path] = cls.delete_tris_line(filepath, rel_path, dry_run=dry_run)
        return results

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _tris_line_present(lines: list[str], around_idx: int, window: int = 5) -> bool:
        """Check if any TRIS line exists within ±window of around_idx."""
        lo = max(0, around_idx - window)
        hi = min(len(lines), around_idx + window + 1)
        return any(l.lstrip().startswith("TRIS") for l in lines[lo:hi])


# ─── Lights Editor ───────────────────────────────────────────────────────────────
class LightParamDeleter:
    """Deletes blocks of LIGHT_PARAM lines (plus surrounding blank lines) from OBJ files."""
 
    # Each entry is a list of 1-based line numbers where a LIGHT_PARAM block starts.
    # Lines are defined in DESCENDING order so deletions don't shift subsequent targets.
    _TARGETS: dict[str, list[int]] = {
        "objects/lights_out321_XP12.obj": [219, 222, 249, 252],
    }
 
    _BLOCK_SIZE = 4          # number of LIGHT_PARAM lines per block
    _MOD_LINE_OFFSET = 4     # line shift applied when the user has the mod installed
 
    @classmethod
    def delete_light_param_blocks(
        cls,
        filepath: Path,
        rel_path: str,
        mod_installed: bool = False,
        dry_run: bool = False,
    ) -> int:
        """Delete all registered LIGHT_PARAM blocks from an OBJ file.
 
        Deletions are applied in descending line-number order so that earlier
        targets are never shifted by a preceding deletion.
 
        Args:
            filepath:      Absolute path to the OBJ file.
            rel_path:      Relative path key used to look up targets.
            mod_installed: If True, adds _MOD_LINE_OFFSET to every target line
                           number to account for the mod shifting the file.
            dry_run:       If True, validate but do not write changes.
 
        Returns:
            Number of lines actually deleted (LIGHT_PARAM lines + blank lines).
 
        Raises:
            KeyError:   rel_path is not a known target.
            ValueError: A target line does not start with LIGHT_PARAM,
                        or the block contains fewer LIGHT_PARAM lines than expected.
        """
        if rel_path not in cls._TARGETS:
            raise KeyError(f"No LIGHT_PARAM targets registered for: {rel_path!r}")
 
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
 
        offset = cls._MOD_LINE_OFFSET if mod_installed else 0
 
        # Work on a mutable copy so dry_run never touches the original list.
        working = list(lines)
        total_deleted = 0
 
        # Targets are already stored descending — process them in that order.
        for target_1based in cls._TARGETS[rel_path]:
            adjusted = target_1based + offset
            idx = adjusted - 1  # convert to 0-based
 
            if idx >= len(working):
                raise ValueError(
                    f"Line {adjusted} is out of range "
                    f"(file has {len(working)} lines) in {filepath!r}."
                )
 
 
            # --- Validate the block before touching anything ---
            block_end = idx + cls._BLOCK_SIZE
            if block_end > len(working):
                raise ValueError(
                    f"Not enough lines from {adjusted} onward to form a "
                    f"{cls._BLOCK_SIZE}-line LIGHT_PARAM block in {filepath!r}."
                )
 
            for i in range(idx, block_end):
                if not working[i].lstrip().startswith("LIGHT_PARAM"):
                    raise ValueError(
                        f"Expected 'LIGHT_PARAM' at line {adjusted + (i - idx)} "
                        f"in {filepath!r}, but found: {working[i]!r}"
                    )
 
            # --- Collect indices to delete: the block + adjacent blank lines ---
            indices_to_delete = set(range(idx, block_end))
 
            # Blank line immediately before the block
            if idx > 0 and working[idx - 1].strip() == "":
                indices_to_delete.add(idx - 1)
 
            # Blank line immediately after the block
            if block_end < len(working) and working[block_end].strip() == "":
                indices_to_delete.add(block_end)
 
            # Apply deletions (descending index order to preserve positions)
            for i in sorted(indices_to_delete, reverse=True):
                del working[i]
 
            total_deleted += len(indices_to_delete)
 
        if total_deleted > 0 and not dry_run:
            bak = filepath.with_suffix(filepath.suffix + ".bak")
            if not bak.exists():
                shutil.copy2(filepath, bak)
            with open(filepath, "w", encoding="utf-8", newline="\n") as f:
                f.writelines(working)
 
        return total_deleted
 
    @classmethod
    def needs_light_param_deletion(
        cls,
        filepath: Path,
        rel_path: str,
        mod_installed: bool = False,
    ) -> bool:
        """Return True if any registered LIGHT_PARAM block is still present."""
        if rel_path not in cls._TARGETS:
            return False
 
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
 
        offset = cls._MOD_LINE_OFFSET if mod_installed else 0
 
        for target_1based in cls._TARGETS[rel_path]:
            idx = (target_1based + offset) - 1
            if idx < len(lines) and lines[idx].lstrip().startswith("LIGHT_PARAM"):
                return True
 
        return False
 
    @classmethod
    def process_all(
        cls,
        base_dir: Path,
        mod_installed: bool = False,
        dry_run: bool = False,
    ) -> dict[str, int]:
        """Iterate all registered targets under base_dir.
 
        Returns:
            Dict mapping rel_path → number of lines deleted (0 = already clean).
        """
        results: dict[str, int] = {}
        for rel_path in cls._TARGETS:
            filepath = base_dir / rel_path
            if not filepath.exists():
                results[rel_path] = 0
                continue
            results[rel_path] = cls.delete_light_param_blocks(
                filepath, rel_path, mod_installed=mod_installed, dry_run=dry_run
            )
        return results
 
# ─── Decals Editor ───────────────────────────────────────────────────────────────
 
class DecalTRISDeleter:
    """Deletes blocks of TRIS lines (plus surrounding blank lines) from decal OBJ files."""
 
    _TARGETS: dict[str, list[int]] = {
        "objects/decals.obj": [299, 307],
    }
 
    _BLOCK_SIZE = 2  # number of TRIS lines per block
 
    @classmethod
    def delete_tris_blocks(
        cls,
        filepath: Path,
        rel_path: str,
        dry_run: bool = False,
    ) -> int:
        """Delete all registered TRIS blocks from a decal OBJ file.
 
        Deletions are applied in ascending line-number order as the target
        line numbers already account for prior deletions.
 
        Args:
            filepath:  Absolute path to the OBJ file.
            rel_path:  Relative path key used to look up targets.
            dry_run:   If True, validate but do not write changes.
 
        Returns:
            Number of lines actually deleted (TRIS lines + blank lines).
 
        Raises:
            KeyError:   rel_path is not a known target.
            ValueError: A target line does not start with TRIS, or the block
                        contains fewer TRIS lines than expected.
        """
        if rel_path not in cls._TARGETS:
            raise KeyError(f"No TRIS targets registered for: {rel_path!r}")
 
        with open(filepath, "r", encoding="utf-8") as f:
            working = f.readlines()
 
        total_deleted = 0
 
        for target_1based in cls._TARGETS[rel_path]:
            idx = target_1based - 1  # convert to 0-based
 
            if idx >= len(working):
                raise ValueError(
                    f"Line {target_1based} is out of range "
                    f"(file has {len(working)} lines) in {filepath!r}."
                )
 
            # --- Validate the block ---
            block_end = idx + cls._BLOCK_SIZE
            if block_end > len(working):
                raise ValueError(
                    f"Not enough lines from {target_1based} onward to form a "
                    f"{cls._BLOCK_SIZE}-line TRIS block in {filepath!r}."
                )
 
            for i in range(idx, block_end):
                if not working[i].lstrip().startswith("TRIS"):
                    raise ValueError(
                        f"Expected 'TRIS' at line {target_1based + (i - idx)} "
                        f"in {filepath!r}, but found: {working[i]!r}"
                    )
 
            # --- Collect indices to delete: block + adjacent blank lines ---
            indices_to_delete = set(range(idx, block_end))
 
            if idx > 0 and working[idx - 1].strip() == "":
                indices_to_delete.add(idx - 1)
 
            if block_end < len(working) and working[block_end].strip() == "":
                indices_to_delete.add(block_end)
 
            for i in sorted(indices_to_delete, reverse=True):
                del working[i]
 
            total_deleted += len(indices_to_delete)
 
        if total_deleted > 0 and not dry_run:
            bak = filepath.with_suffix(filepath.suffix + ".bak")
            if not bak.exists():
                shutil.copy2(filepath, bak)
            with open(filepath, "w", encoding="utf-8", newline="\n") as f:
                f.writelines(working)
 
        return total_deleted
 
    @classmethod
    def needs_tris_deletion(
        cls,
        filepath: Path,
        rel_path: str,
    ) -> bool:
        """Return True if any registered TRIS block is still present."""
        if rel_path not in cls._TARGETS:
            return False
 
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
 
        for target_1based in cls._TARGETS[rel_path]:
            idx = target_1based - 1
            if idx < len(lines) and lines[idx].lstrip().startswith("TRIS"):
                return True
 
        return False
 
    @classmethod
    def process_all(
        cls,
        base_dir: Path,
        dry_run: bool = False,
    ) -> dict[str, int]:
        """Iterate all registered targets under base_dir.
 
        Returns:
            Dict mapping rel_path → number of lines deleted (0 = already clean).
        """
        results: dict[str, int] = {}
        for rel_path in cls._TARGETS:
            filepath = base_dir / rel_path
            if not filepath.exists():
                results[rel_path] = 0
                continue
            results[rel_path] = cls.delete_tris_blocks(
                filepath, rel_path, dry_run=dry_run
            )
        return results
 

# ─── Main ─────────────────────────────────────────────────────────────────────
 
 
def main():
    parser = argparse.ArgumentParser(
        description="RealWings 321 installer - run from the ToLiss A321 folder"
    )
    parser.add_argument(
        "--aircraft-dir",
        type=Path,
        default=Path.cwd(),
        help="Path to the ToLiss A321 aircraft folder (default: current directory)",
    )
    args = parser.parse_args()
    aircraft_dir: Path = args.aircraft_dir.resolve()
 
    print("=" * 80)
    print(" RealWings 321 Installer beta")
    print("=" * 80)
 
    # Validate: must contain *.acf files
    acf_files = sorted(aircraft_dir.glob("*.acf"))
    if not acf_files:
        print(f"\nERROR: No .acf files found in {aircraft_dir}")
        print("Run this script from the ToLiss A321 aircraft folder,")
        print("or use --aircraft-dir to specify the path.")
        input("\nPress Enter to exit...")
        sys.exit(1)
 
    print(f"\nAircraft folder: {aircraft_dir}")
    print(f"Found {len(acf_files)} ACF file(s): {', '.join(f.name for f in acf_files)}")
    
    def ask_yes_no(prompt: str, default: bool = True) -> bool:
        suffix = " [Y/n]: " if default else " [y/N]: "
        while True:
            choice = input(prompt + suffix).strip().lower()
            if not choice:
                return default
            if choice in ("y", "yes"):
                return True
            if choice in ("n", "no"):
                return False
            print("Please enter 'y' or 'n'.")
            
    SEPARATOR_WIDTH = 80
    header = f"── Configuration "
    print(f"\n{header}" + "─" * (SEPARATOR_WIDTH - len(header)))
    install_frames = ask_yes_no("Do you want to install new window frames?", True)
    fix_light_params = ask_yes_no("Do you want to delete LIGHT_PARAM blocks from lights_out321_XP12.obj? (step 7 of readme)", True)
    if fix_light_params:
        mod_installed = ask_yes_no("Do you have Enhanced Lights mod by anndresv installed?", False)
    fix_decal_tris = ask_yes_no("Do you want to delete TRIS blocks from decals.obj? (step 9 of readme)", True)
    fix_engine_tris = ask_yes_no("Do you want to delete target TRIS lines from CARDA CFM/IAE OBJs? (CEO Carda-RealWings compatibility)", True)
    
    (ALL_REALWINGS_OBJECTS, ALL_REALWINGS_OBJECTS_SHARKLETS, ALL_REALWINGS_OBJECTS_NEO,) = _build_all_wings_objects(include_frames=install_frames)
    
    try:
        # ── Steps 1-3: ACF object swap (all variants) ──
        acf_variants = [
            ("CEO wingtips",  "RealWingsCEO_wingtips",   ALL_REALWINGS_OBJECTS),
            ("CEO sharklets", "RealWingsCEO_Sharklets",  ALL_REALWINGS_OBJECTS_SHARKLETS),
            ("NEO",           "RealWingsNEO",            ALL_REALWINGS_OBJECTS_NEO),
        ]
 
        for display_name, suffix, objects in acf_variants:
            header = f"── ACF File Editing ({display_name}) "
            print(f"\n{header}" + "─" * (SEPARATOR_WIDTH - len(header)))
            all_filenames = [obj.file_stl for obj in objects]
 
            for acf_path in acf_files:
                new_name = acf_path.stem + f"_{suffix}" + acf_path.suffix + "~"
                out_path = acf_path.parent / "RealWings_ACF" / new_name
                out_path.parent.mkdir(exist_ok=True)
                shutil.copy2(acf_path, out_path)
                print(f"\n  {acf_path.name} → {new_name}:")
                editor = ACFEditor(out_path)
 
                removed, already_present = editor.remove_and_add_objects(
                    filenames_to_remove=STOCK_OBJECTS_TO_REMOVE + all_filenames,
                    objects_to_add=objects,
                )
 
                stock_removed = [n for n in removed if n in STOCK_OBJECTS_TO_REMOVE]
                rw_refreshed  = [n for n in removed if n in all_filenames]
 
                if stock_removed:
                    print(f"    Removed stock: {', '.join(stock_removed)}")
                if rw_refreshed:
                    print(f"    Refreshed {len(rw_refreshed)} existing RealWings object(s)")
                else:
                    print(f"    Added {len(objects)} RealWings object(s)")
                if already_present:
                    print(f"    Already present (skipped): {', '.join(already_present)}")
                print(f"    Total object count: {editor.get_obja_count()}")
                editor.save(backup=False)
                print(f"    Saved: {new_name}")
 
        # ── Step 4: TRIS line deletions (engine OBJs) ──
        header = f"── Engine OBJ TRIS Line Deletions "
        print(f"\n{header}" + "─" * (SEPARATOR_WIDTH - len(header)))
        if not fix_engine_tris:
            print("  Skipped.")
        else:
            try:
                for rel_path, filepath in (
                    (rp, aircraft_dir / rp) for rp in TRISLineDeleter._TRIS_LINE_TARGETS
                ):
                    label = rel_path.split("/")[-1]
                    if not filepath.exists():
                        print(f"  {label}: Not found, skipping")
                        continue
                    if not TRISLineDeleter.needs_tris_deletion(filepath, rel_path):
                        print(f"  {label}: OK (already clean)")
                        continue
                    TRISLineDeleter.delete_tris_line(filepath, rel_path)
                    print(f"  {label}: Deleted target TRIS line")
            except (ValueError, KeyError) as e:
                print(f"  WARNING: Engine TRIS deletion failed — {e}")
 
        # ── Step 5: LIGHT_PARAM block deletions ──
        header = f"── Lights OBJ LIGHT_PARAM Block Deletions "
        print(f"\n{header}" + "─" * (SEPARATOR_WIDTH - len(header)))
        if not fix_light_params:
            print("  Skipped.")
        else:
            try:
                for rel_path, filepath in (
                    (rp, aircraft_dir / rp) for rp in LightParamDeleter._TARGETS
                ):
                    label = rel_path.split("/")[-1]
                    if not filepath.exists():
                        print(f"  {label}: Not found, skipping")
                        continue
                    if not LightParamDeleter.needs_light_param_deletion(filepath, rel_path, mod_installed):
                        print(f"  {label}: OK (already clean)")
                        continue
                    count = LightParamDeleter.delete_light_param_blocks(
                        filepath, rel_path, mod_installed=mod_installed
                    )
                    print(f"  {label}: Deleted {count} line(s)")
            except (ValueError, KeyError) as e:
                print(f"  WARNING: LIGHT_PARAM deletion failed — {e}")
 
        # ── Step 6: Decal TRIS block deletions ──
        header = f"── Decals OBJ TRIS Block Deletions "
        print(f"\n{header}" + "─" * (SEPARATOR_WIDTH - len(header)))
        if not fix_decal_tris:
            print("  Skipped.")
        else:
            try:
                for rel_path, filepath in (
                    (rp, aircraft_dir / rp) for rp in DecalTRISDeleter._TARGETS
                ):
                    label = rel_path.split("/")[-1]
                    if not filepath.exists():
                        print(f"  {label}: Not found, skipping")
                        continue
                    if not DecalTRISDeleter.needs_tris_deletion(filepath, rel_path):
                        print(f"  {label}: OK (already clean)")
                        continue
                    count = DecalTRISDeleter.delete_tris_blocks(filepath, rel_path)
                    print(f"  {label}: Deleted {count} line(s)")
            except (ValueError, KeyError) as e:
                print(f"  WARNING: Decal TRIS deletion failed — {e}")
 
        print("\n" + "=" * 80)
        print(" Done!")
        print("=" * 80)
        
 
    except (ValueError, KeyError) as e:
        print(f"\nERROR: {e}")
 
    input("\nPress Enter to exit...")
 
 
if __name__ == "__main__":
    main()