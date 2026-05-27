from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter

path_md = 'DD.md'
path_pdf = 'DD.pdf'

with open(path_md, 'r', encoding='utf-8') as f:
    lines = [line.rstrip() for line in f.readlines()]

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CustomHeading1', parent=styles['Heading1'], spaceAfter=12, spaceBefore=12))
styles.add(ParagraphStyle(name='CustomHeading2', parent=styles['Heading2'], spaceAfter=8, spaceBefore=8))
styles.add(ParagraphStyle(name='CustomBodyText', parent=styles['BodyText'], leading=14, spaceAfter=6))

story = []
for line in lines:
    if line.startswith('# '):
        story.append(Paragraph(line[2:], styles['CustomHeading1']))
    elif line.startswith('## '):
        story.append(Paragraph(line[3:], styles['CustomHeading2']))
    elif line.startswith('### '):
        style = ParagraphStyle(name='CustomHeading3', parent=styles['Heading3'], spaceAfter=6, spaceBefore=6)
        story.append(Paragraph(line[4:], style))
    elif line.startswith('- '):
        story.append(Paragraph('• ' + line[2:], styles['CustomBodyText']))
    elif line.strip() == '':
        story.append(Spacer(1, 6))
    else:
        story.append(Paragraph(line, styles['CustomBodyText']))

pdf = SimpleDocTemplate(path_pdf, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
pdf.build(story)
print('PDF generated:', path_pdf)
