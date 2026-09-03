"""
Master script to assemble the complete 24-chapter mastery document
and compile both Markdown (.md) and PDF (.pdf) versions.
"""

import os
import sys
import re

# ReportLab imports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Import content chapters
from content_chapters_1_to_8 import (
    CHAPTER_1, CHAPTER_2, CHAPTER_3, CHAPTER_4,
    CHAPTER_5, CHAPTER_6, CHAPTER_7, CHAPTER_8
)
from content_chapters_9_to_16 import (
    CHAPTER_9, CHAPTER_10, CHAPTER_11, CHAPTER_12,
    CHAPTER_13, CHAPTER_14, CHAPTER_15, CHAPTER_16
)
from content_chapters_17_to_24 import (
    CHAPTER_17, CHAPTER_18, CHAPTER_19, CHAPTER_20,
    CHAPTER_21, CHAPTER_22, CHAPTER_23, CHAPTER_24
)

WORKSPACE_ROOT = os.path.abspath("f:/ai-interview/ai-interview-main")
DOC_MD_PATH = os.path.join(WORKSPACE_ROOT, "PROJECT_INTERVIEW_MASTERY_DOCUMENT.md")
DOC_PDF_PATH = os.path.join(WORKSPACE_ROOT, "PROJECT_INTERVIEW_MASTERY_DOCUMENT.pdf")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "AI Interview Platform — Deep Technical Architecture & Interview Mastery Guide")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        
        self.drawString(54, 32, "Confidential — Prepared for AI Engineer & System Design Technical Interviews")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_text)
        self.restoreState()


def clean_markdown_for_pdf(text):
    """Converts markdown formatting to ReportLab XML tags safely."""
    if not text:
        return ""
    # Normalize line breaks
    text = text.replace("<br>", "<br/>")
    
    # Clean raw ampersands not part of valid entities
    text = re.sub(r'&(?!(amp|lt|gt|quot|apos|nbsp);)', '&amp;', text)
    
    # Convert bold **text** to <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Convert italic *text* to <i>text</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Convert inline code `code` to <font name="Courier">code</font>
    text = re.sub(r'`(.*?)`', r'<font name="Courier" color="#1E293B"><b>\1</b></font>', text)
    
    # Clean unescaped angle brackets that are not valid tags
    # Keep standard tags: <b>, </b>, <i>, </i>, <font ...>, </font>, <br/>, <para>, </para>
    
    # Clean math formulas for plain text readability
    text = text.replace("$$", "").replace("$", "")
    text = text.replace(r"\sum_{m \in M}", "Sum_m")
    text = text.replace(r"\frac{1}{k + rank_m(d)}", "1 / (k + rank_m(d))")
    text = text.replace(r"\frac{||p_2 - p_6|| + ||p_3 - p_5||}{2 \times ||p_1 - p_4||}", "(||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)")
    text = text.replace(r"\text{ ms}", " ms")
    
    return text


def build_markdown_document():
    """Concatenates all 24 chapters and writes the complete .md file."""
    all_chapters = [
        "# AI VOICE INTERVIEW PLATFORM — DEEP TECHNICAL MASTERY & INTERVIEW DEFENSE GUIDE\n\n"
        "> **Target Roles**: AI Engineer | Applied AI Engineer | Full-Stack AI Architect | Forward Deployed Engineer\n"
        "> **Project Repository**: `https://github.com/Suyog9402/Ai-interview`\n"
        "> **Generated Date**: " + str(os.getenv("CURRENT_DATE", "March 2026")) + "\n\n---\n\n",
        CHAPTER_1, "\n\n---\n\n",
        CHAPTER_2, "\n\n---\n\n",
        CHAPTER_3, "\n\n---\n\n",
        CHAPTER_4, "\n\n---\n\n",
        CHAPTER_5, "\n\n---\n\n",
        CHAPTER_6, "\n\n---\n\n",
        CHAPTER_7, "\n\n---\n\n",
        CHAPTER_8, "\n\n---\n\n",
        CHAPTER_9, "\n\n---\n\n",
        CHAPTER_10, "\n\n---\n\n",
        CHAPTER_11, "\n\n---\n\n",
        CHAPTER_12, "\n\n---\n\n",
        CHAPTER_13, "\n\n---\n\n",
        CHAPTER_14, "\n\n---\n\n",
        CHAPTER_15, "\n\n---\n\n",
        CHAPTER_16, "\n\n---\n\n",
        CHAPTER_17, "\n\n---\n\n",
        CHAPTER_18, "\n\n---\n\n",
        CHAPTER_19, "\n\n---\n\n",
        CHAPTER_20, "\n\n---\n\n",
        CHAPTER_21, "\n\n---\n\n",
        CHAPTER_22, "\n\n---\n\n",
        CHAPTER_23, "\n\n---\n\n",
        CHAPTER_24
    ]
    
    full_md_content = "".join(all_chapters)
    
    with open(DOC_MD_PATH, "w", encoding="utf-8") as f:
        f.write(full_md_content)
        
    print(f"[+] Full Markdown Document written successfully to: {DOC_MD_PATH}")
    return full_md_content


def build_pdf_document(md_content):
    """Parses markdown lines and builds a styled publication-grade PDF."""
    doc = SimpleDocTemplate(
        DOC_PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=12
    )
    
    h1_style = ParagraphStyle(
        'ChapterH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0369A1"),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h3_style = ParagraphStyle(
        'SubSectionH3',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=5
    )
    
    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        leftIndent=15,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=3
    )
    
    quote_style = ParagraphStyle(
        'DocQuote',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        leftIndent=15,
        rightIndent=15,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=4,
        spaceAfter=6
    )
    
    code_block_style = ParagraphStyle(
        'DocCodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=4,
        spaceAfter=6
    )
    
    table_text_style = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1E293B")
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#FFFFFF")
    )
    
    flowables = []
    
    # Title Banner Block
    flowables.append(Paragraph("AI VOICE INTERVIEW PLATFORM", title_style))
    flowables.append(Paragraph("<b>Deep Technical Architecture & Comprehensive Interview Mastery Guide</b>", h2_style))
    flowables.append(Paragraph("<i>Prepared for AI Engineer, Applied AI, and System Design Technical Interviews</i>", quote_style))
    flowables.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceBefore=6, spaceAfter=12))
    
    lines = md_content.split('\n')
    i = 0
    in_code_block = False
    code_lines = []
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
            
        # Code block handling
        if line.startswith("```"):
            if in_code_block:
                # End code block
                code_text = "<br/>".join(code_lines).replace(" ", "&nbsp;")
                code_table = Table([[Paragraph(code_text, code_block_style)]], colWidths=[504])
                code_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ]))
                flowables.append(code_table)
                flowables.append(Spacer(1, 4))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
                code_lines = []
            i += 1
            continue
            
        if in_code_block:
            # Escape HTML in code blocks
            escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            code_lines.append(escaped)
            i += 1
            continue
            
        # Table handling
        if line.startswith("|") and line.endswith("|"):
            table_raw_rows = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                row_str = lines[i].strip()
                # Skip markdown separator row like | :--- | :--- |
                if not re.match(r'^\|[\s\:\-\|]+$', row_str):
                    cols = [c.strip() for c in row_str.split('|')[1:-1]]
                    table_raw_rows.append(cols)
                i += 1
                
            if table_raw_rows:
                num_cols = len(table_raw_rows[0])
                col_width = 504.0 / num_cols
                
                table_data = []
                for r_idx, row in enumerate(table_raw_rows):
                    row_data = []
                    is_header = (r_idx == 0)
                    for cell in row:
                        cell_clean = clean_markdown_for_pdf(cell)
                        p_style = table_header_style if is_header else table_text_style
                        row_data.append(Paragraph(cell_clean, p_style))
                    table_data.append(row_data)
                    
                pdf_table = Table(table_data, colWidths=[col_width] * num_cols)
                pdf_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ]))
                flowables.append(pdf_table)
                flowables.append(Spacer(1, 6))
            continue

        # Headings and structural elements
        if line.startswith("# "):
            heading_text = clean_markdown_for_pdf(line[2:])
            flowables.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#E2E8F0"), spaceBefore=10, spaceAfter=8))
            flowables.append(Paragraph(heading_text, h1_style))
        elif line.startswith("## "):
            heading_text = clean_markdown_for_pdf(line[3:])
            flowables.append(Paragraph(heading_text, h2_style))
        elif line.startswith("### "):
            heading_text = clean_markdown_for_pdf(line[4:])
            flowables.append(Paragraph(heading_text, h3_style))
        elif line.startswith("> "):
            quote_text = clean_markdown_for_pdf(line[2:])
            quote_box = Table([[Paragraph(quote_text, quote_style)]], colWidths=[504])
            quote_box.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BFDBFE")),
                ('LINELEFT', (0,0), (0,-1), 3.0, colors.HexColor("#2563EB")),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]))
            flowables.append(quote_box)
            flowables.append(Spacer(1, 4))
        elif line.startswith("* ") or line.startswith("- "):
            bullet_text = "• " + clean_markdown_for_pdf(line[2:])
            flowables.append(Paragraph(bullet_text, bullet_style))
        elif re.match(r'^\d+\.\s', line):
            num_text = clean_markdown_for_pdf(line)
            flowables.append(Paragraph(num_text, bullet_style))
        elif line.startswith("---"):
            flowables.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceBefore=6, spaceAfter=6))
        else:
            para_text = clean_markdown_for_pdf(line)
            flowables.append(Paragraph(para_text, body_style))
            
        i += 1
        
    doc.build(flowables, canvasmaker=NumberedCanvas)
    print(f"[+] Publication-Grade PDF Document generated successfully at: {DOC_PDF_PATH}")

if __name__ == "__main__":
    print("Starting mastery document generation...")
    md_text = build_markdown_document()
    build_pdf_document(md_text)
    print("ALL ARTIFACTS SUCCESSFULLY GENERATED!")
