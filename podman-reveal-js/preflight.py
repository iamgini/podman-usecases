#!/usr/bin/env python3
"""
slide-preflight: Detect overflow risk in reveal-md slides before presenting.

Parses slides.md, estimates rendered height of each slide based on font-size
and slide dimensions, and reports which slides are likely to overflow.
"""

import re
import sys
import math
import argparse
from pathlib import Path


# Heading size multipliers — must match custom.css
HEADING_MULTIPLIERS = {1: 2.5, 2: 1.6, 3: 1.3, 4: 1.1, 5: 1.0}

# Top margin above each heading level (px)
HEADING_MARGINS = {1: 24, 2: 20, 3: 16, 4: 12, 5: 8}

# Margin below each bullet / paragraph line (px)
ITEM_MARGIN = 8

# Line height multiplier
LINE_HEIGHT = 1.3

# Average character width as a fraction of font-size (Red Hat Display, proportional)
CHAR_WIDTH_RATIO = 0.55
BOLD_CHAR_WIDTH_RATIO = 0.65  # bold text is wider

# Internal slide padding (reveal.js adds padding inside each section)
SLIDE_PADDING = 40


def parse_frontmatter(content):
    """Strip YAML frontmatter and return (frontmatter_str, body_str)."""
    if content.startswith('---'):
        end = content.find('\n---', 3)
        if end != -1:
            return content[3:end], content[end + 4:]
    return '', content


def detect_font_size(slides_path, frontmatter):
    """
    Detect base font-size from custom.css referenced in frontmatter.
    Returns int (px) or None if not found.
    """
    css_match = re.search(r'^css:\s*(\S+)', frontmatter, re.MULTILINE)
    if not css_match:
        return None
    css_file = css_match.group(1)
    css_path = Path(slides_path).parent / css_file
    try:
        css = css_path.read_text()
        # Match: .reveal { ... font-size: 28px ... }
        match = re.search(
            r'\.reveal\s*\{[^}]*?font-size:\s*(\d+(?:\.\d+)?)(px|em)[^}]*\}',
            css, re.DOTALL
        )
        if match:
            size = float(match.group(1))
            return int(size * 42 if match.group(2) == 'em' else size)
    except FileNotFoundError:
        pass
    return None


def split_slides(body):
    """
    Split body into slides.
    Returns list of dicts: {index, label, content}
    Horizontal separator: --- (own line)
    Vertical separator:   --  (own line)
    """
    slides = []
    h_slides = re.split(r'\n---\n', body)
    for h_idx, h_slide in enumerate(h_slides, 1):
        v_slides = re.split(r'\n--\n', h_slide)
        for v_idx, slide in enumerate(v_slides, 1):
            label = str(h_idx) if len(v_slides) == 1 else f"{h_idx}.{v_idx}"
            slides.append({'index': len(slides) + 1, 'label': label, 'content': slide.strip()})
    return slides


def slide_title(content):
    """Return first heading or first non-empty line, truncated."""
    for line in content.splitlines():
        m = re.match(r'^#{1,5}\s+(.*)', line)
        if m:
            return m.group(1)[:55]
        if line.strip():
            return line.strip()[:55]
    return '(empty)'


def strip_markdown(text):
    """Remove markdown formatting for character counting."""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)   # bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)         # italic
    text = re.sub(r'`(.*?)`', r'\1', text)            # inline code
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # links
    return text


def count_lines(text, chars_per_line):
    """Estimate wrapped line count for a text block."""
    text = strip_markdown(text).strip()
    if not text:
        return 0
    return max(1, math.ceil(len(text) / chars_per_line))


def estimate_height(content, font_size, slide_width, margin):
    """
    Estimate rendered height (px) of a single slide's content.
    """
    avail_width = slide_width * (1 - 2 * margin) - 80  # 80px horizontal padding
    chars_per_line = max(10, int(avail_width / (font_size * CHAR_WIDTH_RATIO)))
    bold_chars_per_line = max(10, int(avail_width / (font_size * BOLD_CHAR_WIDTH_RATIO)))

    total = 20  # top padding
    in_code = False

    for line in content.splitlines():
        # Code fence toggle
        if line.strip().startswith('```'):
            in_code = not in_code
            total += 8
            continue

        if in_code:
            total += font_size * 0.85 * LINE_HEIGHT + 2
            continue

        # Heading
        m = re.match(r'^(#{1,5})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            h_size = font_size * HEADING_MULTIPLIERS.get(level, 1.0)
            h_chars = max(10, int(avail_width / (h_size * CHAR_WIDTH_RATIO)))
            n = count_lines(m.group(2), h_chars)
            total += HEADING_MARGINS[level] + h_size * LINE_HEIGHT * n + 8
            continue

        # Table row
        if line.strip().startswith('|'):
            total += font_size * LINE_HEIGHT + 8
            continue

        # Bullet point (handles nested indentation)
        m = re.match(r'^(\s*)[-*+]\s+(.*)', line)
        if m:
            indent = len(m.group(1))
            width_factor = max(0.5, 1 - indent * 0.02)
            eff_chars = max(10, int(bold_chars_per_line * width_factor))
            n = count_lines(m.group(2), eff_chars)
            total += font_size * LINE_HEIGHT * n + ITEM_MARGIN
            continue

        # Numbered list
        m = re.match(r'^\s*\d+\.\s+(.*)', line)
        if m:
            n = count_lines(m.group(1), bold_chars_per_line)
            total += font_size * LINE_HEIGHT * n + ITEM_MARGIN
            continue

        # Blockquote
        if line.strip().startswith('>'):
            text = line.strip()[1:].strip()
            n = count_lines(text, chars_per_line)
            total += font_size * LINE_HEIGHT * n + ITEM_MARGIN
            continue

        # Empty line
        if not line.strip():
            total += font_size * 0.3
            continue

        # Paragraph text
        n = count_lines(line, chars_per_line)
        total += font_size * LINE_HEIGHT * n + ITEM_MARGIN

    total += 20  # bottom padding
    return total


def main():
    parser = argparse.ArgumentParser(
        description='Pre-flight overflow check for reveal-md slides.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  preflight /slides/slides.md
  preflight /slides/slides.md --verbose
  preflight /slides/slides.md --font-size 32
  preflight /slides/slides.md --width 1920 --height 1080 --margin 0.05
        """
    )
    parser.add_argument('slides', help='Path to slides.md')
    parser.add_argument('--font-size', type=int,
                        help='Base font size in px (overrides CSS auto-detection)')
    parser.add_argument('--width',   type=int,   default=1280, help='Slide width px  (default: 1280)')
    parser.add_argument('--height',  type=int,   default=720,  help='Slide height px (default: 720)')
    parser.add_argument('--margin',  type=float, default=0.04, help='Reveal margin   (default: 0.04)')
    parser.add_argument('--verbose', action='store_true',
                        help='Show all slides, not just overflowing/tight ones')
    args = parser.parse_args()

    # Read file
    try:
        content = Path(args.slides).read_text()
    except FileNotFoundError:
        print(f"Error: file not found: {args.slides}")
        sys.exit(2)

    frontmatter, body = parse_frontmatter(content)

    # Resolve font-size
    font_size = args.font_size or detect_font_size(args.slides, frontmatter) or 42
    source = 'CLI override' if args.font_size else \
             ('CSS detected' if detect_font_size(args.slides, frontmatter) else 'reveal.js default')

    avail_height = args.height * (1 - 2 * args.margin) - SLIDE_PADDING
    warn_threshold = avail_height * 0.85  # within 15% → TIGHT

    SEP = '─' * 70
    print(f"\n{SEP}")
    print(f"  Slide Preflight Check")
    print(SEP)
    print(f"  File        : {args.slides}")
    print(f"  Dimensions  : {args.width} × {args.height} px  |  margin {args.margin}")
    print(f"  Font size   : {font_size} px  ({source})")
    print(f"  Available   : ~{int(avail_height)} px per slide  |  warn at {int(warn_threshold)} px (85%)")
    print(SEP)

    slides = split_slides(body)
    overflow_count = 0
    tight_count = 0

    for slide in slides:
        est = estimate_height(slide['content'], font_size, args.width, args.margin)
        pct = est / avail_height * 100
        title = slide_title(slide['content'])
        overflow = est > avail_height
        tight = not overflow and est > warn_threshold

        if overflow:
            overflow_count += 1
            icon, tag = '⚠ ', 'OVERFLOW'
        elif tight:
            tight_count += 1
            icon, tag = '△ ', 'TIGHT   '
        else:
            icon, tag = '✓ ', 'OK      '

        if overflow or tight or args.verbose:
            ref = f"#{slide['label']:>5}"
            bar_filled = int(pct / 5)
            bar = ('█' * min(bar_filled, 20)) + ('░' * (20 - min(bar_filled, 20)))
            print(f"  {icon}{tag}  {ref}  [{bar}] {int(pct):>3}%  {title}")

    print(SEP)
    if overflow_count or tight_count:
        if overflow_count:
            print(f"  ⚠  {overflow_count} slide(s) will overflow  →  split with  --  in slides.md")
        if tight_count:
            print(f"  △  {tight_count} slide(s) are tight (>85%)  →  consider splitting")
    else:
        print(f"  ✓  All {len(slides)} slides within bounds")
    print(SEP + '\n')

    sys.exit(1 if overflow_count else 0)


if __name__ == '__main__':
    main()
