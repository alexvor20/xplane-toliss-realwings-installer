#!/usr/bin/env python3
import argparse
import shutil
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ─── Constants ────────────────────────────────────────────────────────────────

FLAGS_PREFILL                = 4
FLAGS_ALL_VIEWS              = 24
FLAGS_LIGHTNING_INSIDE       = 1
FLAGS_LIGHTNING_GLASS_OUTSIDE = 2

SEPARATOR_WIDTH = 80


# ─── Data Class ───────────────────────────────────────────────────────────────

@dataclass
class ACFObject:
    """A Misc Object entry to add to the ACF."""
    file_stl: str
    flags:    int   = 0
    x:        float = 0.0
    y:        float = 0.40   # most objects share this default
    z:        float = 72.30  # most objects share this default
    body:     int   = -1
    gear:     int   = -1
    wing:     int   = -1
    phi_ref:  float = 0.0
    psi_ref:  float = 0.0
    the_ref:  float = 0.0
    is_internal:      int = 0
    steers_with_gear: int = 0

# ─── OBJ to remove ────────────────────────────────────────────────────────────

def _build_obj_to_remove(conf: str = "") -> list[str]:
    """Build list of stock objects to remove based on aircraft variant."""
    if conf not in ("320", "321"):
        raise ValueError(
            f"Expected variant '320' or '321', but got '{conf}'"
        )
    suffix = "" if conf == "320" else conf
    return [
        f"wing{suffix}R.obj",
        f"wing{suffix}L.obj",
        "wings_glass.obj",
    ]

# ─── Wing Object Definitions ──────────────────────────────────────────────────

def _obj(file_stl: str, flags: int, x: float = 0.0, y: float = 0.40, z: float = 72.30) -> ACFObject:
    return ACFObject(file_stl, flags=flags, x=x, y=y, z=z)


def _build_all_wings_objects(include_frames: bool = True, conf: str = "") -> tuple[
    list[ACFObject], list[ACFObject], list[ACFObject]
]:
    """Return (CEO_wingtips, CEO_sharklets, NEO) object lists."""

    frames_lines = []
    if include_frames:
        frames_lines = [
            _obj(f"RealWings{conf}/Frames{conf}.obj", FLAGS_LIGHTNING_INSIDE, x=6.00, y=2.06, z=60.98),
            _obj(f"RealWings{conf}/Lines{conf}.obj", FLAGS_LIGHTNING_INSIDE, x=6.00, y=2.06, z=60.98),
        ]

    ceo_body = [
        _obj(f"RealWings{conf}/Main.obj",      FLAGS_ALL_VIEWS),
        _obj(f"RealWings{conf}/Glass.obj",     FLAGS_LIGHTNING_GLASS_OUTSIDE),
        _obj(f"RealWings{conf}/Secondary.obj", FLAGS_ALL_VIEWS),
    ]
    neo_body = [
        _obj(f"RealWings{conf}/MainNEO.obj",      FLAGS_ALL_VIEWS),
        _obj(f"RealWings{conf}/GlassNEO.obj",     FLAGS_LIGHTNING_GLASS_OUTSIDE),
        _obj(f"RealWings{conf}/SecondaryNEO.obj", FLAGS_ALL_VIEWS),
    ]

    if conf == "321":
        flaps_ceo = [_obj("RealWings321/Flaps321.obj", FLAGS_ALL_VIEWS)]
        flaps_neo = [_obj("RealWings321/Flaps321NEO.obj", FLAGS_ALL_VIEWS)]
    elif conf == "320":
        flaps_ceo = [_obj("RealWings320/Flaps.obj", FLAGS_ALL_VIEWS)]
        flaps_neo = [_obj("RealWings320/FlapsNEO.obj", FLAGS_ALL_VIEWS)]
    else:
        raise ValueError(f"Invalid aircraft variant: {conf}")

    return (
        ceo_body + flaps_ceo + frames_lines,   # CEO wingtips
        neo_body + flaps_ceo + frames_lines,   # CEO sharklets
        neo_body + flaps_neo + frames_lines,   # NEO
    )

# ─── Helpers ──────────────────────────────────────────────────────────────────

def format_float32(val: float) -> str:
    """Format a float in X-Plane's single-precision 9-decimal-place style."""
    (unpacked,) = struct.unpack("f", struct.pack("f", val))
    return f"{unpacked:.9f}"


def section_header(title: str) -> str:
    return f"\n── {title} " + "─" * (SEPARATOR_WIDTH - len(title) - 4)


def _backup(filepath: Path, suffix: str = ".bak") -> None:
    """Create a backup of *filepath* if one does not already exist."""
    bak = filepath.with_suffix(filepath.suffix + suffix)
    if not bak.exists():
        shutil.copy2(filepath, bak)


def _read_lines(filepath: Path) -> list[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.readlines()


def _write_lines(filepath: Path, lines: list[str]) -> None:
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(lines)


# ─── ACF Editor ───────────────────────────────────────────────────────────────

class ACFEditor:
    """Reads, modifies, and writes X-Plane .acf property files."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self._header_lines: list[str] = []
        self._properties:   dict[str, str] = {}
        self._footer_lines: list[str] = []
        self._read()

    # ── I/O ───────────────────────────────────────────────────────────────────

    def _read(self) -> None:
        in_props = past_props = False
        for line in _read_lines(self.filepath):
            stripped = line.rstrip("\n\r")
            if stripped.startswith("P "):
                in_props, past_props = True, False
                parts = stripped.split(" ", 2)
                self._properties[parts[1]] = parts[2] if len(parts) > 2 else ""
            elif in_props:
                in_props, past_props = False, True
                self._footer_lines.append(line)
            elif past_props:
                self._footer_lines.append(line)
            else:
                self._header_lines.append(line)

    def save(self, backup: bool = True, output_path: Path | None = None) -> None:
        if output_path is None:
            if backup:
                _backup(self.filepath, ".backup")
            out = self.filepath
        else:
            out = output_path

        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.writelines(self._header_lines)
            for key in sorted(self._properties):
                f.write(f"P {key} {self._properties[key]}\n")
            f.writelines(self._footer_lines)

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_obja_count(self) -> int:
        return int(self._properties.get("_obja/count", "0"))

    def get_obja_entries(self) -> dict[int, dict[str, str]]:
        entries: dict[int, dict[str, str]] = {}
        for key, value in self._properties.items():
            if key.startswith("_obja/") and key != "_obja/count":
                _, idx_str, *prop_parts = key.split("/")
                entries.setdefault(int(idx_str), {})["/".join(prop_parts)] = value
        return entries

    def has_object_by_filename(self, filename: str) -> bool:
        return any(
            k.endswith("/_v10_att_file_stl") and v == filename
            for k, v in self._properties.items()
        )

    # ── Mutation ──────────────────────────────────────────────────────────────

    def remove_and_add_objects(
        self,
        filenames_to_remove: list[str],
        objects_to_add: list[ACFObject],
    ) -> tuple[list[str], list[str]]:
        """Remove stock objects and add RealWings objects, re-indexing as needed."""
        entries = self.get_obja_entries()
        remove_set = set(filenames_to_remove)

        # Find what to remove
        indices_to_remove: set[int] = set()
        removed_names: list[str] = []
        for idx, props in entries.items():
            stl = props.get("_v10_att_file_stl", "")
            if stl in remove_set:
                indices_to_remove.add(idx)
                removed_names.append(stl)

        # Separate objects that are genuinely new vs already present
        already_present: list[str] = []
        filtered_add: list[ACFObject] = []
        for obj in objects_to_add:
            if obj.file_stl not in remove_set and self.has_object_by_filename(obj.file_stl):
                already_present.append(obj.file_stl)
            else:
                filtered_add.append(obj)

        if not indices_to_remove and not filtered_add:
            return removed_names, already_present

        # Rebuild the _obja/* key space from scratch
        keys_to_delete = [k for k in self._properties if k.startswith("_obja/") and k != "_obja/count"]
        for k in keys_to_delete:
            del self._properties[k]

        survivors = [
            props for idx, props in sorted(entries.items())
            if idx not in indices_to_remove
        ]
        new_entries = {i: props for i, props in enumerate(survivors)}
        next_idx = len(new_entries)
        for obj in filtered_add:
            new_entries[next_idx] = self._acf_obj_to_props(obj)
            next_idx += 1

        for idx, props in sorted(new_entries.items()):
            for prop_name, value in sorted(props.items()):
                self._properties[f"_obja/{idx}/{prop_name}"] = value
        self._properties["_obja/count"] = str(len(new_entries))

        return removed_names, already_present

    @staticmethod
    def _acf_obj_to_props(obj: ACFObject) -> dict[str, str]:
        return {
            "_obj_flags":            str(obj.flags),
            "_v10_att_body":         str(obj.body),
            "_v10_att_file_stl":     obj.file_stl,
            "_v10_att_gear":         str(obj.gear),
            "_v10_att_phi_ref":      format_float32(obj.phi_ref),
            "_v10_att_psi_ref":      format_float32(obj.psi_ref),
            "_v10_att_the_ref":      format_float32(obj.the_ref),
            "_v10_att_wing":         str(obj.wing),
            "_v10_att_x_acf_prt_ref": format_float32(obj.x),
            "_v10_att_y_acf_prt_ref": format_float32(obj.y),
            "_v10_att_z_acf_prt_ref": format_float32(obj.z),
            "_v10_is_internal":      str(obj.is_internal),
            "_v10_steers_with_gear": str(obj.steers_with_gear),
        }


# ─── Shared block-deletion mixin ──────────────────────────────────────────────

class _BlockDeleter:
    """
    Shared logic for deleting fixed-size line blocks (TRIS / LIGHT_PARAM)
    from OBJ files, including adjacent blank-line cleanup.

    Subclasses must define:
        _TARGETS   : dict[str, list[int]]  — rel_path → list of 1-based start lines
        _BLOCK_SIZE: int                   — number of lines per block
        _KEYWORD   : str                   — expected line prefix (e.g. 'TRIS')
    """

    _TARGETS:    dict[str, list[int]] = {}
    _BLOCK_SIZE: int = 1
    _KEYWORD:    str = ""

    # ── Shared methods ────────────────────────────────────────────────────────

    @classmethod
    def needs_deletion(cls, filepath: Path, rel_path: str, line_offset: int = 0) -> bool:
        if rel_path not in cls._TARGETS:
            return False
        lines = _read_lines(filepath)
        return any(
            (i := (t + line_offset) - 1) < len(lines) and
            lines[i].lstrip().startswith(cls._KEYWORD)
            for t in cls._TARGETS[rel_path]
        )

    @classmethod
    def delete_blocks(
        cls,
        filepath: Path,
        rel_path: str,
        line_offset: int = 0,
        dry_run:     bool = False,
    ) -> int:
        """
        Delete all registered blocks from *filepath*.

        Returns:
            Number of lines deleted (block lines + surrounding blanks).
        Raises:
            KeyError:   *rel_path* not registered.
            ValueError: A target line does not start with the expected keyword,
                        or the file is too short.
        """
        if rel_path not in cls._TARGETS:
            raise KeyError(f"No {cls._KEYWORD} targets registered for: {rel_path!r}")

        working = _read_lines(filepath)
        total_deleted = 0

        for target_1based in cls._TARGETS[rel_path]:
            adjusted = target_1based + line_offset
            idx = adjusted - 1

            if idx >= len(working):
                raise ValueError(
                    f"Line {adjusted} out of range "
                    f"(file has {len(working)} lines) in {filepath!r}."
                )

            block_end = idx + cls._BLOCK_SIZE
            if block_end > len(working):
                raise ValueError(
                    f"Not enough lines from {adjusted} onward to form a "
                    f"{cls._BLOCK_SIZE}-line {cls._KEYWORD} block in {filepath!r}."
                )

            for i in range(idx, block_end):
                if not working[i].lstrip().startswith(cls._KEYWORD):
                    raise ValueError(
                        f"Expected '{cls._KEYWORD}' at line {adjusted + (i - idx)} "
                        f"in {filepath!r}, but found: {working[i]!r}"
                    )

            indices = set(range(idx, block_end))
            if idx > 0 and working[idx - 1].strip() == "":
                indices.add(idx - 1)
            if block_end < len(working) and working[block_end].strip() == "":
                indices.add(block_end)

            for i in sorted(indices, reverse=True):
                del working[i]
            total_deleted += len(indices)

        if total_deleted > 0 and not dry_run:
            _backup(filepath)
            _write_lines(filepath, working)

        return total_deleted

    @classmethod
    def process_all(cls, base_dir: Path, **kwargs) -> dict[str, int]:
        """Apply deletion to every registered target under *base_dir*."""
        results: dict[str, int] = {}
        for rel_path in cls._TARGETS:
            fp = base_dir / rel_path
            if not fp.exists():
                results[rel_path] = 0
                continue
            results[rel_path] = cls.delete_blocks(fp, rel_path, **kwargs)
        return results


# ─── Concrete Deleters ────────────────────────────────────────────────────────

class TRISLineDeleter:
    """Deletes a single TRIS line at a known line number in engine OBJ files."""

    _TRIS_LINE_TARGETS: dict[str, int] = {
        "objects/V2500/iae_l_engine.obj":   56010,
        "objects/V2500/iae_r_engine.obj":   56010,
        "objects/CFM56/cfm56_l_engine.obj": 64124,
        "objects/CFM56/cfm56_r_engine.obj": 64122,
    }

    @classmethod
    def needs_tris_deletion(cls, filepath: Path, rel_path: str) -> bool:
        if rel_path not in cls._TRIS_LINE_TARGETS:
            return False
        lines = _read_lines(filepath)
        idx = cls._TRIS_LINE_TARGETS[rel_path] - 1
        return idx < len(lines) and lines[idx].lstrip().startswith("TRIS")

    @classmethod
    def delete_tris_line(cls, filepath: Path, rel_path: str, dry_run: bool = False) -> bool:
        """
        Delete the single target TRIS line.

        Returns True if a deletion was (or would be) made.
        Raises KeyError / ValueError on bad inputs.
        """
        if rel_path not in cls._TRIS_LINE_TARGETS:
            raise KeyError(f"No TRIS deletion target registered for: {rel_path!r}")

        target_line = cls._TRIS_LINE_TARGETS[rel_path]
        lines = _read_lines(filepath)
        idx = target_line - 1

        if idx >= len(lines):
            raise ValueError(
                f"File has only {len(lines)} lines; "
                f"cannot access line {target_line} in {filepath}"
            )

        if not lines[idx].lstrip().startswith("TRIS"):
            # Check nearby to detect a shift rather than a clean state
            lo = max(0, idx - 5)
            hi = min(len(lines), idx + 6)
            if any(l.lstrip().startswith("TRIS") for l in lines[lo:hi]):
                raise ValueError(
                    f"Expected 'TRIS' at line {target_line} in {filepath!r}, "
                    f"but found: {lines[idx]!r}. File may have been partially edited."
                )
            return False  # already removed — nothing to do

        if dry_run:
            return True

        _backup(filepath)
        del lines[idx]
        _write_lines(filepath, lines)
        return True

    @classmethod
    def process_all(cls, base_dir: Path, dry_run: bool = False) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for rel_path in cls._TRIS_LINE_TARGETS:
            fp = base_dir / rel_path
            if not fp.exists():
                results[rel_path] = False
                continue
            results[rel_path] = cls.delete_tris_line(fp, rel_path, dry_run=dry_run)
        return results


class LightParamDeleter(_BlockDeleter):
    """Deletes LIGHT_PARAM blocks from lights OBJ files."""

    # Target definitions for both aircraft variants
    _TARGETS_320: dict[str, list[int]] = {
        "objects/lights_out320_XP12.obj": [234, 237, 264, 267],
    }
    _TARGETS_321: dict[str, list[int]] = {
        "objects/lights_out321_XP12.obj": [219, 222, 249, 252],
    }

    # Default to 320 (will be overridden by set_variant)
    _TARGETS: dict[str, list[int]] = _TARGETS_320

    _BLOCK_SIZE = 4
    _KEYWORD = "LIGHT_PARAM"
    _MOD_LINE_OFFSET = 4

    @classmethod
    def set_variant(cls, conf: str) -> None:
        """Set the targets based on aircraft variant."""
        if conf == "320":
            cls._TARGETS = cls._TARGETS_320
        elif conf == "321":
            cls._TARGETS = cls._TARGETS_321
        else:
            raise ValueError(f"Invalid aircraft variant: {conf}")

    @classmethod
    def needs_light_param_deletion(cls, filepath: Path, rel_path: str, mod_installed: bool = False) -> bool:
        return cls.needs_deletion(
            filepath, rel_path,
            line_offset=cls._MOD_LINE_OFFSET if mod_installed else 0,
        )

    @classmethod
    def delete_light_param_blocks(
        cls, filepath: Path, rel_path: str,
        mod_installed: bool = False, dry_run: bool = False,
    ) -> int:
        return cls.delete_blocks(
            filepath, rel_path,
            line_offset=cls._MOD_LINE_OFFSET if mod_installed else 0,
            dry_run=dry_run,
        )


class DecalTRISDeleter(_BlockDeleter):
    """Deletes TRIS blocks from decal OBJ files."""

    _TARGETS: dict[str, list[int]] = {
        "objects/decals.obj": [299, 307],
    }
    _BLOCK_SIZE = 2
    _KEYWORD    = "TRIS"

    @classmethod
    def needs_tris_deletion(cls, filepath: Path, rel_path: str) -> bool:
        return cls.needs_deletion(filepath, rel_path)

    @classmethod
    def delete_tris_blocks(cls, filepath: Path, rel_path: str, dry_run: bool = False) -> int:
        return cls.delete_blocks(filepath, rel_path, dry_run=dry_run)


# ─── Main ─────────────────────────────────────────────────────────────────────

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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RealWings 32X installer – run from the ToLiss A32X folder"
    )
    parser.add_argument(
        "--aircraft-dir",
        type=Path,
        default=Path.cwd(),
        help="Path to the ToLiss A32X aircraft folder (default: current directory)",
    )
    args = parser.parse_args()
    aircraft_dir: Path = args.aircraft_dir.resolve()

    print("=" * SEPARATOR_WIDTH)
    print(" RealWings 32X Installer v1.5")
    print("=" * SEPARATOR_WIDTH)

    try:
        print("\nWhich aircraft are you installing for?")
        print("  1 - ToLiss A320")
        print("  2 - ToLiss A321")
        while True:
            raw = input("\nEnter 1 or 2: ").strip()
            if raw in ("1", "2"):
                conf = {"1": "320", "2": "321"}[raw]
                break
            print(" Invalid choice. Please enter 1 or 2.")

        STOCK_OBJECTS_TO_REMOVE = _build_obj_to_remove(conf)

        TARGET_ACF = f"a{conf}.acf"
        acf_path = aircraft_dir / TARGET_ACF
        if not acf_path.exists():
            print(f"\nERROR: {TARGET_ACF} not found in {aircraft_dir}")
            print("Run this script from the ToLiss A32X aircraft folder,")
            print("or use --aircraft-dir to specify the path.")
            raise FileNotFoundError(f"{TARGET_ACF} not found")

        print(f"\nAircraft folder: {aircraft_dir}")
        print(f"Found ACF file: {acf_path.name}")

        # ── Configuration ─────────────────────────────────────────────────────────
        print(section_header("Configuration"))

        if not ask_yes_no("Do you want to install RealWings mod?"):
            print("\nInstallation cancelled by user.")
            return

        install_frames = ask_yes_no("Do you want to install new window frames?", True)
        mod_installed = ask_yes_no("Do you have Enhanced Lights mod by anndresv installed?", False)

        (
            ALL_REALWINGS_OBJECTS,
            ALL_REALWINGS_OBJECTS_SHARKLETS,
            ALL_REALWINGS_OBJECTS_NEO,
        ) = _build_all_wings_objects(include_frames=install_frames, conf=conf)

        # ── Backup: original a32X.acf  ───────────────────────────────────────
        print(section_header(f"Backup Original ACF"))
        acf_bak = acf_path.with_suffix(acf_path.suffix + ".backup")
        if acf_bak.exists():
            print(f"  Backup already exists, skipping: {acf_bak.name}")
        else:
            shutil.copy2(acf_path, acf_bak)
            print(f"  Backed up: {acf_path.name} → {acf_bak.name}")

        # ── Steps 1-3: ACF object swap (all variants) ─────────────────────────
        acf_variants = [
            ("CEO wingtips",  "RealWingsCEO_wingtips",  ALL_REALWINGS_OBJECTS),
            ("CEO sharklets", "RealWingsCEO_Sharklets", ALL_REALWINGS_OBJECTS_SHARKLETS),
            ("NEO",           "RealWingsNEO",           ALL_REALWINGS_OBJECTS_NEO),
        ]

        for display_name, suffix, objects in acf_variants:
            print(section_header(f"ACF File Editing ({display_name})"))
            all_filenames = [obj.file_stl for obj in objects]

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
            rw_refreshed = [n for n in removed if n in all_filenames]

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

        # ── Step 4: Engine OBJ TRIS line deletions ────────────────────────────
        print(section_header("Engine OBJ TRIS Line Deletions"))
        for rel_path in TRISLineDeleter._TRIS_LINE_TARGETS:
            fp = aircraft_dir / rel_path
            label = rel_path.split("/")[-1]
            if not fp.exists():
                print(f"  {label}: Not found, skipping")
                continue
            if not TRISLineDeleter.needs_tris_deletion(fp, rel_path):
                print(f"  {label}: OK (already clean)")
                continue
            try:
                TRISLineDeleter.delete_tris_line(fp, rel_path)
                print(f"  {label}: Deleted target TRIS line")
            except (ValueError, KeyError) as e:
                print(f"  WARNING: {label}: {e}")

        # ── Step 5: LIGHT_PARAM block deletions ───────────────────────────────
        print(section_header("Lights OBJ LIGHT_PARAM Block Deletions"))
        LightParamDeleter.set_variant(conf)
        for rel_path in LightParamDeleter._TARGETS:
            fp = aircraft_dir / rel_path
            label = rel_path.split("/")[-1]
            if not fp.exists():
                print(f"  {label}: Not found, skipping")
                continue
            if not LightParamDeleter.needs_light_param_deletion(fp, rel_path, mod_installed):
                print(f"  {label}: OK (already clean)")
                continue
            try:
                count = LightParamDeleter.delete_light_param_blocks(fp, rel_path, mod_installed)
                print(f"  {label}: Deleted {count} line(s)")
            except (ValueError, KeyError) as e:
                print(f"  WARNING: {label}: {e}")

        # ── Step 6: Decal TRIS block deletions ────────────────────────────────
        print(section_header("Decals OBJ TRIS Block Deletions"))
        for rel_path in DecalTRISDeleter._TARGETS:
            fp = aircraft_dir / rel_path
            label = rel_path.split("/")[-1]
            if not fp.exists():
                print(f"  {label}: Not found, skipping")
                continue
            if not DecalTRISDeleter.needs_tris_deletion(fp, rel_path):
                print(f"  {label}: OK (already clean)")
                continue
            try:
                count = DecalTRISDeleter.delete_tris_blocks(fp, rel_path)
                print(f"  {label}: Deleted {count} line(s)")
            except (ValueError, KeyError) as e:
                print(f"  WARNING: {label}: {e}")

        print("\n" + "=" * SEPARATOR_WIDTH)
        print(" Done!")
        print("=" * SEPARATOR_WIDTH)

    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
    except (ValueError, KeyError) as e:
        print(f"\nERROR: {e}")
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()