#!/usr/bin/env python3
import os
import sys
import shutil


def detect_aircraft(script_dir):
    if os.path.isfile(os.path.join(script_dir, "a321.acf")):
        return "a321"
    elif os.path.isfile(os.path.join(script_dir, "a320.acf")):
        return "a320"
    else:
        print("Error: No a320.acf or a321.acf found in directory.")
        input("Press enter to exit.")
        sys.exit(1)

def get_variants(aircraft):
    return {
    "1": ("CEO Wingtips",   f"{aircraft}_RealWingsCEO_wingtips.acf~"),
    "2": ("CEO Sharklets",  f"{aircraft}_RealWingsCEO_Sharklets.acf~"),
    "3": ("NEO",            f"{aircraft}_RealWingsNEO.acf~"),
}

def main():
    if getattr(sys, "frozen", False):
        script_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    acf_folder = os.path.join(script_dir, "RealWings_ACF")
    aircraft = detect_aircraft(script_dir)
    VARIANTS = get_variants(aircraft)
    target_file = os.path.join(script_dir, f"{aircraft}.acf")

    print("What variant to use?")
    print("  1 - CEO Wingtips")
    print("  2 - CEO Sharklets")
    print("  3 - NEO")
    print()

    choice = input("Enter your choice (1/2/3): ").strip()

    if choice not in VARIANTS:
        print("Invalid choice. Please run the script again and enter 1, 2, or 3.")
        input("Press enter to exit.")
        return

    variant_name, source_filename = VARIANTS[choice]
    source_file = os.path.join(acf_folder, source_filename)

    if not os.path.isfile(source_file):
        print(f"Error: Source file not found:\n  {source_file}")
        input("Press enter to exit.")
        return

    # Copy the chosen .acf into the parent folder
    temp_copy = os.path.join(script_dir, source_filename)
    shutil.copy2(source_file, temp_copy)

    # Remove the existing a32X.acf
    if os.path.isfile(target_file):
        os.remove(target_file)

    # Rename the copied file to a32X.acf
    os.rename(temp_copy, target_file)

    print(f"\nDone! Active variant set to: {variant_name}")

if __name__ == "__main__":
    main()