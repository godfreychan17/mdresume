"""CLI entry point: python -m app export [--feed feed.md] [--out output/]"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app", description="mdresume CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    exp = sub.add_parser("export", help="Generate PDF from feed.md without starting the server")
    exp.add_argument("--feed", default="feed.md", help="Path to feed.md (default: feed.md)")
    exp.add_argument("--out", default="output", help="Output directory (default: output/)")
    exp.add_argument("--filename", default=None, help="Override output filename")

    args = parser.parse_args()

    if args.command == "export":
        feed_path = Path(args.feed)
        if not feed_path.exists():
            print(f"Error: feed file not found: {feed_path}", file=sys.stderr)
            sys.exit(1)

        from app.feed_parser import parse_feed
        from app.pdf_export import export_pdf
        from app.template_layout import apply_template_layout

        resume = parse_feed(feed_path)

        template_path = Path("template.pdf")
        if template_path.exists():
            resume = apply_template_layout(resume, template_path)

        out = export_pdf(resume, out_dir=args.out, filename=args.filename)
        print(f"PDF exported: {out}")


if __name__ == "__main__":
    main()
