"""Render the frozen proposal-recursion Markdown specification as a PDF."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


NAVY = colors.HexColor("#14283D")
TEAL = colors.HexColor("#137C8B")
PALE = colors.HexColor("#EAF3F5")
INK = colors.HexColor("#1F2933")
MUTED = colors.HexColor("#52616B")


def _inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(
        r"`([^`]+)`",
        r'<font name="Courier" color="#0B6673">\1</font>',
        escaped,
    )
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    return escaped


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ProtocolTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=30,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=16,
        ),
        "subtitle": ParagraphStyle(
            "ProtocolSubtitle",
            parent=base["Heading2"],
            fontName="Helvetica",
            fontSize=14,
            leading=19,
            textColor=TEAL,
            spaceAfter=18,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=NAVY,
            spaceBefore=14,
            spaceAfter=8,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=15,
            textColor=TEAL,
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.4,
            leading=13.2,
            textColor=INK,
            spaceAfter=7,
            alignment=TA_LEFT,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.1,
            leading=12.5,
            leftIndent=15,
            firstLineIndent=-8,
            bulletIndent=3,
            textColor=INK,
            spaceAfter=4,
        ),
        "quote": ParagraphStyle(
            "Quote",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.1,
            leading=14.5,
            leftIndent=14,
            rightIndent=10,
            borderColor=TEAL,
            borderWidth=2,
            borderPadding=9,
            backColor=PALE,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=13,
        ),
        "code": ParagraphStyle(
            "Code",
            fontName="Courier",
            fontSize=7.5,
            leading=10.2,
            leftIndent=7,
            rightIndent=7,
            borderColor=colors.HexColor("#C8D7DB"),
            borderWidth=0.6,
            borderPadding=7,
            backColor=colors.HexColor("#F4F8F9"),
            textColor=colors.HexColor("#173042"),
            spaceBefore=4,
            spaceAfter=9,
        ),
        "footer": ParagraphStyle(
            "Footer",
            fontName="Helvetica",
            fontSize=7.5,
            leading=9,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }


def _header_footer(canvas, doc) -> None:  # type: ignore[no-untyped-def]
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(colors.HexColor("#B8C8CE"))
    canvas.setLineWidth(0.5)
    canvas.line(0.72 * inch, height - 0.55 * inch, width - 0.72 * inch, height - 0.55 * inch)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(0.72 * inch, height - 0.42 * inch, "MORALITY LAB - PROPOSAL-CHANNEL RECURSION PROTOCOL")
    canvas.drawRightString(width - 0.72 * inch, 0.42 * inch, f"Page {doc.page}")
    canvas.drawString(0.72 * inch, 0.42 * inch, "Version 1.0.0 - prereveal methods specification")
    canvas.restoreState()


def markdown_flowables(source: str) -> list[object]:
    styles = _styles()
    lines = source.splitlines()
    story: list[object] = []
    paragraph: list[str] = []
    code: list[str] = []
    in_code = False
    first_heading = True

    def flush_paragraph() -> None:
        if paragraph:
            story.append(Paragraph(_inline(" ".join(paragraph)), styles["body"]))
            paragraph.clear()

    for line in lines:
        stripped = line.rstrip()
        if stripped.startswith("```"):
            flush_paragraph()
            if in_code:
                story.append(Preformatted("\n".join(code), styles["code"]))
                code.clear()
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code.append(stripped)
            continue
        if not stripped:
            flush_paragraph()
            continue
        if stripped.startswith("# "):
            flush_paragraph()
            if not first_heading:
                story.append(PageBreak())
            story.append(Spacer(1, 0.45 * inch if first_heading else 0.0))
            story.append(Paragraph(_inline(stripped[2:]), styles["title"]))
            first_heading = False
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            text = stripped[3:]
            style = "subtitle" if len(story) <= 3 else "h2"
            story.append(Paragraph(_inline(text), styles[style]))
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(_inline(stripped[4:]), styles["h3"]))
            continue
        if stripped.startswith("> "):
            flush_paragraph()
            story.append(Paragraph(_inline(stripped[2:]), styles["quote"]))
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            story.append(Paragraph(_inline(stripped[2:]), styles["bullet"], bulletText="-"))
            continue
        ordered = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if ordered:
            flush_paragraph()
            story.append(
                Paragraph(
                    _inline(ordered.group(2)),
                    styles["bullet"],
                    bulletText=f"{ordered.group(1)}.",
                )
            )
            continue
        paragraph.append(stripped)
    flush_paragraph()
    if code:
        story.append(Preformatted("\n".join(code), styles["code"]))
    return story


def build(source_path: Path, output_path: Path) -> None:
    source = source_path.read_text(encoding="utf-8")
    if not source.isascii():
        raise ValueError("frozen PDF source must be ASCII")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.72 * inch,
        leftMargin=0.72 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.68 * inch,
        title="Proposal-Channel Recursive Improvement",
        author="Morality Lab",
        subject="Frozen prereveal methods specification",
    )
    document.build(
        markdown_flowables(source),
        onFirstPage=_header_footer,
        onLaterPages=_header_footer,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.source.resolve(), args.output.resolve())
    print(args.output.resolve())


if __name__ == "__main__":
    main()
