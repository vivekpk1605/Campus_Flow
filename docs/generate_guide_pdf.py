import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer


DOCS_DIR = Path(__file__).resolve().parent
SOURCE = DOCS_DIR / 'CampusFlow_Project_Guide.md'
OUTPUT = DOCS_DIR / 'CampusFlow_Project_Guide.pdf'

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name='GuideTitle', parent=styles['Title'], fontName='Helvetica-Bold',
    fontSize=25, leading=30, textColor=colors.HexColor('#102A43'),
    alignment=TA_CENTER, spaceAfter=18,
))
styles.add(ParagraphStyle(
    name='GuideHeading1', parent=styles['Heading1'], fontName='Helvetica-Bold',
    fontSize=16, leading=20, textColor=colors.HexColor('#102A43'),
    spaceBefore=14, spaceAfter=8,
))
styles.add(ParagraphStyle(
    name='GuideHeading2', parent=styles['Heading2'], fontName='Helvetica-Bold',
    fontSize=12, leading=16, textColor=colors.HexColor('#C94D32'),
    spaceBefore=10, spaceAfter=5,
))
styles.add(ParagraphStyle(
    name='GuideBody', parent=styles['BodyText'], fontName='Helvetica',
    fontSize=9.5, leading=14, textColor=colors.HexColor('#17324D'),
    spaceAfter=6,
))
styles.add(ParagraphStyle(
    name='GuideBullet', parent=styles['BodyText'], fontName='Helvetica',
    fontSize=9.5, leading=14, leftIndent=14, firstLineIndent=-8,
    textColor=colors.HexColor('#17324D'), spaceAfter=3,
))
styles.add(ParagraphStyle(
    name='GuideSmall', parent=styles['BodyText'], fontName='Helvetica',
    fontSize=8, leading=10, textColor=colors.HexColor('#64748B'),
))


def footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#80CBC4'))
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#64748B'))
    canvas.drawString(18 * mm, 9 * mm, 'CampusFlow Project Guide')
    canvas.drawRightString(192 * mm, 9 * mm, f'Page {document.page}')
    canvas.restoreState()


def build_story(source):
    story = []
    in_code = False
    code_lines = []
    first_heading = True

    for raw_line in source.read_text(encoding='utf-8').splitlines():
        line = raw_line.rstrip()
        if line.startswith('```'):
            if in_code:
                story.append(Preformatted('\n'.join(code_lines), styles['Code']))
                story.append(Spacer(1, 5))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line:
            story.append(Spacer(1, 3))
            continue
        if line.startswith('# '):
            story.append(Paragraph(escape(line[2:]), styles['GuideTitle']))
            first_heading = False
        elif line.startswith('## '):
            story.append(Paragraph(escape(line[3:]), styles['GuideHeading1']))
        elif line.startswith('### '):
            story.append(Paragraph(escape(line[4:]), styles['GuideHeading2']))
        elif line.startswith('- '):
            story.append(Paragraph('&bull; ' + escape(line[2:]), styles['GuideBullet']))
        elif line.startswith('|'):
            story.append(Paragraph(escape(line.replace('|', '   ')), styles['GuideSmall']))
        else:
            story.append(Paragraph(escape(line), styles['GuideBody']))

    if first_heading:
        story.insert(0, Paragraph('CampusFlow Project Guide', styles['GuideTitle']))
    return story


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    document = SimpleDocTemplate(
        str(args.output), pagesize=A4,
        rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=20 * mm,
        title='CampusFlow Project Guide', author='CampusFlow',
    )
    document.build(build_story(args.source), onFirstPage=footer, onLaterPages=footer)
    print(args.output)


if __name__ == '__main__':
    main()
