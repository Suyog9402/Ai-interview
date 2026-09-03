"""
Mastery Document & PDF Generator for AI Voice Interview Platform.
Compiles a deep codebase review into:
1. PROJECT_INTERVIEW_MASTERY_DOCUMENT.md
2. PROJECT_INTERVIEW_MASTERY_DOCUMENT.pdf
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

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

print("Canvas class ready.")
