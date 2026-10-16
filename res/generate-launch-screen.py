#!/usr/bin/env python3
"""Render Moonlight's native Samsung TV splash: animation plus static hold.

Eight sectors fade in sequentially. The logo then makes a clear, controlled
bounce while the gray disc and app name fade in; the final frame is held for
six additional seconds so the completed logo remains readable on the TV.
"""
import argparse
import math
import random
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

FPS = 30
SECTOR_INTERVAL_FRAMES = 9  # 300 ms at 30 fps
SECTOR_FADE_FRAMES = 9      # 300 ms fade-in for each sector
SECTOR_PHASE_FRAMES = 8 * SECTOR_INTERVAL_FRAMES
SETTLE_FRAMES = 36          # 1.2 s for the bounce and accompanying fade
ANIMATED_FRAME_COUNT = SECTOR_PHASE_FRAMES + SETTLE_FRAMES
STATIC_HOLD_FRAMES = 6 * FPS
TOTAL_FRAMES = ANIMATED_FRAME_COUNT + STATIC_HOLD_FRAMES

FINAL_LOGO_SCALE = 0.78
OVERSIZED_LOGO_SCALE = FINAL_LOGO_SCALE * 1.15
BOUNCE_LOW_SCALE = FINAL_LOGO_SCALE * 0.93
BOUNCE_HIGH_SCALE = FINAL_LOGO_SCALE * 1.06
LOGO_CENTER_X = 639.84
LOGO_CENTER_Y = 274.84

# Starfield parameters ported from the supplied canvas animation.
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
STAR_COUNT = 1000
STAR_SPEED = 18.0
MAX_STAR_DEPTH = 1500.0
STAR_COLOR = "#FFFFFF"
STARFIELD_SEED = 0x4D4F4F4E  # Keep the generated splash reproducible between builds.


def find_by_id(root, target_id):
    for element in root.iter():
        if element.get("id") == target_id:
            return element
    raise RuntimeError(f"Missing expected SVG element id={target_id!r}")


def smoothstep(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def interpolate(start, end, progress):
    return start + (end - start) * smoothstep(progress)


def smootherstep(progress):
    """Quintic easing with a gentle start and a gentle, gradual finish."""
    progress = max(0.0, min(1.0, progress))
    return progress ** 3 * (progress * (progress * 6.0 - 15.0) + 10.0)


def star_speed_for_frame(frame_number):
    """Decelerate across the full settling phase and reach zero smoothly with the logo."""
    if frame_number < SECTOR_PHASE_FRAMES:
        return STAR_SPEED

    settle_frame = frame_number - SECTOR_PHASE_FRAMES
    progress = min(1.0, (settle_frame + 1) / SETTLE_FRAMES)
    # Interpolate the loss of speed using quintic smootherstep. This avoids
    # dropping almost all velocity early; motion remains perceptible through
    # the logo/text reveal, then eases gently into a complete stop.
    return STAR_SPEED * (1.0 - smootherstep(progress))


class Star:
    def __init__(self, rng):
        self.rng = rng
        self.z = self.rng.random() * MAX_STAR_DEPTH
        self.x = 0.0
        self.y = 0.0
        self.size = 0.5
        self.color = STAR_COLOR
        self.randomize_position()

    def randomize_position(self):
        angle = self.rng.random() * 2.0 * math.pi
        distance = math.sqrt(self.rng.random()) * (FRAME_WIDTH / 2.0)
        self.x = math.cos(angle) * distance
        self.y = math.sin(angle) * distance
        self.size = (1.0 - distance / (FRAME_WIDTH / 2.0)) * 0.1 + 0.5
        self.color = STAR_COLOR

    def reset(self):
        self.z = MAX_STAR_DEPTH
        self.randomize_position()

    def update(self, speed):
        self.z -= speed * (2.0 - self.z / MAX_STAR_DEPTH)
        if self.z <= 0.0:
            self.reset()

    def projected(self):
        if self.z <= 0.0:
            return None

        x = ((self.x / self.z) * FRAME_WIDTH) / 2.0 + FRAME_WIDTH / 2.0
        y = ((self.y / self.z) * FRAME_HEIGHT) / 2.0 + FRAME_HEIGHT / 2.0
        radius = (1.0 - self.z / MAX_STAR_DEPTH) * self.size * 3.0

        # Canvas drawing clips anything outside the screen; skip those nodes here.
        if radius <= 0.02 or x + radius < 0 or x - radius > FRAME_WIDTH:
            return None
        if y + radius < 0 or y - radius > FRAME_HEIGHT:
            return None
        return x, y, radius


class StarField:
    def __init__(self):
        rng = random.Random(STARFIELD_SEED)
        self.stars = [Star(rng) for _ in range(STAR_COUNT)]

    def update(self, speed):
        for star in self.stars:
            star.update(speed)

    def append_to_svg(self, root):
        group = ET.Element(f"{{{SVG_NS}}}g", {"id": "starfield"})
        for star in self.stars:
            point = star.projected()
            if point is None:
                continue
            x, y, radius = point
            ET.SubElement(
                group,
                f"{{{SVG_NS}}}circle",
                {
                    "cx": f"{x:.2f}",
                    "cy": f"{y:.2f}",
                    "r": f"{radius:.2f}",
                    "fill": star.color,
                },
            )

        # The first template child is the black full-canvas background. Insert
        # the stars directly above it and below the unchanged logo/text layers.
        root.insert(1, group)


def settling_scale(progress):
    """Bounce clearly below the final size, rebound above it, then settle."""
    if progress <= 0.42:
        return interpolate(OVERSIZED_LOGO_SCALE, BOUNCE_LOW_SCALE, progress / 0.42)
    if progress <= 0.72:
        return interpolate(BOUNCE_LOW_SCALE, BOUNCE_HIGH_SCALE, (progress - 0.42) / 0.30)
    return interpolate(BOUNCE_HIGH_SCALE, FINAL_LOGO_SCALE, (progress - 0.72) / 0.28)


def configure_frame(root, frame_number):
    logo_group = find_by_id(root, "logo-group")
    background = find_by_id(root, "background-circle")
    app_name = find_by_id(root, "app-name")
    sectors = [find_by_id(root, f"sector-{i}") for i in range(8)]

    if frame_number < SECTOR_PHASE_FRAMES:
        scale = OVERSIZED_LOGO_SCALE
        fade = 0.0
    else:
        settle_frame = frame_number - SECTOR_PHASE_FRAMES
        progress = min(1.0, (settle_frame + 1) / SETTLE_FRAMES)
        scale = settling_scale(progress)
        fade = progress

    # Keep the logo centered while its scale changes. At 0.78 this transform
    # is geometrically identical to the original translate(540 175) scale(0.78).
    logo_group.set(
        "transform",
        f"translate({LOGO_CENTER_X} {LOGO_CENTER_Y}) "
        f"scale({scale:.5f}) translate(-128 -128)",
    )
    background.set("fill-opacity", f"{fade:.4f}")
    app_name.set("opacity", f"{fade:.4f}")

    for index, sector in enumerate(sectors):
        start_frame = index * SECTOR_INTERVAL_FRAMES
        if frame_number < start_frame:
            opacity = 0.0
        else:
            opacity = min(1.0, (frame_number - start_frame + 1) / SECTOR_FADE_FRAMES)
        sector.set("opacity", f"{opacity:.4f}")


def render_svg(template_path, output_path, frame_number=None, starfield=None, star_speed=0.0):
    root = ET.parse(template_path).getroot()
    if frame_number is not None:
        configure_frame(root, frame_number)
    if starfield is not None:
        if frame_number is not None:
            starfield.update(star_speed)
        starfield.append_to_svg(root)
    output_path.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--frames", required=True, type=Path)
    parser.add_argument("--static-svg", required=True, type=Path)
    args = parser.parse_args()

    if not args.template.is_file():
        raise SystemExit(f"SVG template not found: {args.template}")
    args.frames.mkdir(parents=True, exist_ok=True)
    args.static_svg.parent.mkdir(parents=True, exist_ok=True)

    starfield = StarField()

    for frame_number in range(ANIMATED_FRAME_COUNT):
        frame_svg = args.frames / "frame.svg"
        frame_png = args.frames / f"frame-{frame_number:03d}.png"
        render_svg(
            args.template,
            frame_svg,
            frame_number,
            starfield=starfield,
            star_speed=star_speed_for_frame(frame_number),
        )
        subprocess.run(
            [
                "rsvg-convert", "-w", "1280", "-h", "720", "--format", "png",
                "-o", str(frame_png), str(frame_svg),
            ],
            check=True,
        )

    # The static fallback uses the final frozen star positions and the unchanged
    # assembled logo/text from the SVG template.
    render_svg(args.template, args.static_svg, starfield=starfield)

    # Repeat the completed frame instead of re-rendering identical PNGs.
    final_frame = args.frames / f"frame-{ANIMATED_FRAME_COUNT - 1:03d}.png"
    for frame_number in range(ANIMATED_FRAME_COUNT, TOTAL_FRAMES):
        (args.frames / f"frame-{frame_number:03d}.png").write_bytes(final_frame.read_bytes())

    (args.frames / "frame.svg").unlink(missing_ok=True)
    print(
        f"Generated {ANIMATED_FRAME_COUNT} animated frames plus "
        f"{STATIC_HOLD_FRAMES} static frames: {TOTAL_FRAMES} frames total at "
        f"{FPS} fps ({ANIMATED_FRAME_COUNT / FPS:.1f} s animation + "
        f"{STATIC_HOLD_FRAMES / FPS:.1f} s static hold = {TOTAL_FRAMES / FPS:.1f} s)."
    )


if __name__ == "__main__":
    main()
