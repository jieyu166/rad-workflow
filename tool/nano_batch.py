#!/usr/bin/env python3
"""
nano-banana Batch Image Generator
==================================
Reads a JSON file, extracts slide prompts, and calls nano-banana for each slide.

Usage:
  python nano_batch.py slides.json
  python nano_batch.py slides.json --output-dir my_images
  python nano_batch.py slides.json --dry-run
  python nano_batch.py slides.json --flash
  python nano_batch.py slides.json --model gemini-2.0-flash
  python nano_batch.py slides.json --extra-args "--someFlag value"
"""

import json
import subprocess
import sys
import os
import argparse
import re
import tempfile
import platform
from pathlib import Path
from datetime import datetime

# On Windows, npm global installs are .cmd files.
# subprocess needs shell=True to resolve them.
IS_WINDOWS = platform.system() == "Windows"


def find_slides(data):
    """
    Recursively search JSON for a 'slides' array.
    Supports various JSON structures:
      - { "presentation": { "slides": [...] } }
      - { "slides": [...] }
      - { "主題": "<json-string with slides>" }
      - or any nested structure containing a 'slides' key
    """
    if isinstance(data, str):
        # Try to parse JSON strings (e.g. "主題" field contains a JSON string)
        try:
            parsed = json.loads(data)
            result = find_slides(parsed)
            if result:
                return result
        except (json.JSONDecodeError, TypeError):
            pass
        return None

    if isinstance(data, list):
        # Check if this list itself looks like slides (has slide_number)
        if data and isinstance(data[0], dict) and "slide_number" in data[0]:
            return data
        # Otherwise search each element
        for item in data:
            result = find_slides(item)
            if result:
                return result
        return None

    if isinstance(data, dict):
        # Direct match
        if "slides" in data and isinstance(data["slides"], list):
            return data["slides"]
        # Search all values
        for key, value in data.items():
            result = find_slides(value)
            if result:
                return result
    return None


def extract_prompt(slide):
    """
    Extract the image generation prompt from a slide object.
    Priority: visual_note > visual > title + subtitle fallback
    """
    content = slide.get("content", slide)

    # Try visual_note first (most common)
    if isinstance(content, dict):
        vn = content.get("visual_note")
        if vn:
            return vn

        # Try visual (used in some title slides)
        vis = content.get("visual")
        if vis:
            return vis

    # Fallback: combine title + subtitle
    title = slide.get("title", content.get("title", ""))
    subtitle = slide.get("subtitle", content.get("subtitle", ""))
    if title:
        return f"{title}. {subtitle}" if subtitle else title

    return None


def sanitize_filename(text, max_len=40):
    """Create a safe filename from text."""
    # Remove non-ASCII and special chars
    safe = re.sub(r'[^\w\s-]', '', text.strip())
    safe = re.sub(r'[\s]+', '_', safe)
    return safe[:max_len].rstrip('_') if safe else "slide"


def main():
    parser = argparse.ArgumentParser(
        description="Batch generate images from a JSON slide deck using nano-banana"
    )
    parser.add_argument("json_file", help="Path to the JSON file containing slide prompts")
    parser.add_argument("--output-dir", "-o", default="output",
                        help="Output directory for generated images (default: output)")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="Print commands without executing them")
    parser.add_argument("--flash", action="store_true",
                        help="Use --flash flag (gemini-2.0-flash, faster)")
    parser.add_argument("--model", default=None,
                        help="Specify model name (passed as --model to nano-banana)")
    parser.add_argument("--extra-args", default="",
                        help="Additional arguments to pass to nano-banana (quoted string)")
    parser.add_argument("--prefix", default="slide",
                        help="Filename prefix (default: slide)")
    parser.add_argument("--start-from", type=int, default=1,
                        help="Start from slide N (skip earlier slides)")

    args = parser.parse_args()

    # --- Load JSON ---
    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"[ERROR] File not found: {json_path}")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # --- Find slides ---
    slides = find_slides(data)
    if not slides:
        print("[ERROR] Could not find 'slides' array in the JSON.")
        print("  Supported structures:")
        print('    { "presentation": { "slides": [...] } }')
        print('    { "slides": [...] }')
        print('    { "主題": "<json-string>" }  (nested JSON string)')
        sys.exit(1)

    total = len(slides)
    print(f"{'=' * 50}")
    print(f"  nano-banana Batch Generator")
    print(f"  Found {total} slides in: {json_path.name}")
    print(f"  Output dir: {args.output_dir}")
    if args.dry_run:
        print(f"  ** DRY RUN - no images will be generated **")
    print(f"{'=' * 50}\n")

    # --- Prepare output dir ---
    os.makedirs(args.output_dir, exist_ok=True)

    # --- Process each slide ---
    success = 0
    failed = 0
    skipped = 0

    for slide in slides:
        num = slide.get("slide_number", slides.index(slide) + 1)

        if num < args.start_from:
            skipped += 1
            continue

        prompt = extract_prompt(slide)
        if not prompt:
            print(f"  [{num}/{total}] SKIP - no visual_note or visual found")
            skipped += 1
            continue

        # Build output filename
        slide_type = slide.get("type", "")
        name_part = sanitize_filename(slide_type) if slide_type else f"{num:02d}"
        output_file = os.path.join(args.output_dir, f"{args.prefix}_{num:02d}_{name_part}.png")

        # Build command using --prompt-file to avoid shell escaping issues
        # with special chars like (), <>, &, | in prompts
        cmd = ["nano-banana", "--output", output_file]

        if args.flash:
            cmd.append("--flash")
        if args.model:
            cmd.extend(["--model", args.model])
        if args.extra_args:
            cmd.extend(args.extra_args.split())

        print(f"  [{num}/{total}] Generating: {os.path.basename(output_file)}")
        print(f"    Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")

        if args.dry_run:
            print(f"    CMD: nano-banana --prompt-file <tmpfile> --output {output_file}"
                  f"{' --flash' if args.flash else ''}"
                  f"{' --model ' + args.model if args.model else ''}\n")
            success += 1
            continue

        # Write prompt to a temp file, then pass via --prompt-file
        tmp_prompt = None
        try:
            tmp_prompt = tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", encoding="utf-8", delete=False
            )
            tmp_prompt.write(prompt)
            tmp_prompt.close()

            run_cmd = cmd + ["--prompt-file", tmp_prompt.name]
            result = subprocess.run(
                run_cmd, capture_output=True, text=True,
                timeout=300, shell=IS_WINDOWS
            )

            if result.returncode == 0:
                print(f"    [OK] Saved to {output_file}\n")
                success += 1
            else:
                print(f"    [FAIL] Exit code {result.returncode}")
                if result.stderr:
                    print(f"    stderr: {result.stderr.strip()[:200]}")
                if result.stdout:
                    print(f"    stdout: {result.stdout.strip()[:200]}")
                print()
                failed += 1
        except subprocess.TimeoutExpired:
            print(f"    [TIMEOUT] Exceeded 300s\n")
            failed += 1
        except FileNotFoundError:
            print(f"    [ERROR] 'nano-banana' command not found. Is it installed globally?")
            print(f"    Try: npm install -g nano-banana")
            sys.exit(1)
        finally:
            # Clean up temp file
            if tmp_prompt and os.path.exists(tmp_prompt.name):
                os.unlink(tmp_prompt.name)

    # --- Summary ---
    print(f"{'=' * 50}")
    print(f"  Results: {success} OK / {failed} failed / {skipped} skipped")
    print(f"  Output dir: {os.path.abspath(args.output_dir)}")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
