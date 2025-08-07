#!/usr/bin/env python3
"""
GLB File Processing Pipeline

This script processes GLB files through a series of gltf-transform commands:
1. Resize to 1024x1024
2. Convert textures to WebP format
3. Optimize with Draco compression
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List


def get_glb_files(imports_dir: Path) -> List[Path]:
    """Get all GLB files from the imports directory."""
    glb_files = []
    for file_path in imports_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == '.glb':
            glb_files.append(file_path)
    return sorted(glb_files)


def run_command(command: List[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ Success: {description}")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {description}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"Stdout: {e.stdout.strip()}")
        if e.stderr:
            print(f"Stderr: {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print(f"✗ Error: gltf-transform not found. Please ensure it's installed and in PATH.")
        return False


def process_glb_file(input_file: Path, base_dir: Path) -> bool:
    """Process a single GLB file through all transformation steps."""
    print(f"\n{'='*60}")
    print(f"Processing: {input_file.name}")
    print(f"{'='*60}")
    
    # Create output file paths
    resize_output = base_dir / "data" / "exports" / "resize" / input_file.name
    webp_output = base_dir / "data" / "exports" / "webp" / input_file.name
    draco_output = base_dir / "data" / "exports" / "draco" / input_file.name
    
    # Ensure output directories exist
    resize_output.parent.mkdir(parents=True, exist_ok=True)
    webp_output.parent.mkdir(parents=True, exist_ok=True)
    draco_output.parent.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Resize
    resize_cmd = [
        "gltf-transform", "resize",
        str(input_file),
        str(resize_output),
        "--width", "1024",
        "--height", "1024"
    ]
    
    if not run_command(resize_cmd, f"Resize {input_file.name}"):
        return False
    
    # Step 2: WebP conversion
    webp_cmd = [
        "gltf-transform", "webp",
        str(resize_output),
        str(webp_output),
        "--slots", "baseColor"
    ]
    
    if not run_command(webp_cmd, f"WebP conversion {input_file.name}"):
        return False
    
    # Step 3: Draco optimization
    draco_cmd = [
        "gltf-transform", "optimize",
        str(webp_output),
        str(draco_output),
        "--texture-compress", "webp"
    ]
    
    if not run_command(draco_cmd, f"Draco optimization {input_file.name}"):
        return False
    
    print(f"✓ Successfully processed: {input_file.name}")
    return True


def main():
    """Main function to process all GLB files."""
    # Get the script directory
    script_dir = Path(__file__).parent.absolute()
    
    # Define paths
    imports_dir = script_dir / "data" / "imports"
    
    if not imports_dir.exists():
        print(f"Error: Imports directory not found: {imports_dir}")
        sys.exit(1)
    
    # Get all GLB files
    glb_files = get_glb_files(imports_dir)
    
    if not glb_files:
        print("No GLB files found in the imports directory.")
        sys.exit(0)
    
    print(f"Found {len(glb_files)} GLB files to process:")
    for file_path in glb_files:
        print(f"  - {file_path.name}")
    
    # Process each file
    successful = 0
    failed = 0
    
    for file_path in glb_files:
        if process_glb_file(file_path, script_dir):
            successful += 1
        else:
            failed += 1
            print(f"Failed to process: {file_path.name}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total files: {len(glb_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("All files processed successfully!")


if __name__ == "__main__":
    main()
