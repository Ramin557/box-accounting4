import jdatetime
from datetime import datetime, date
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os

def to_jalali(date_obj):
    """Convert Gregorian date to Jalali string"""
    if not date_obj:
        return ''
    
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
        except:
            return ''
    
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    try:
        jalali_date = jdatetime.date.fromgregorian(date=date_obj)
        return jalali_date.strftime('%Y/%m/%d')
    except:
        return ''

def from_jalali(jalali_str):
    """Convert Jalali string to Gregorian date"""
    if not jalali_str:
        return None
    
    try:
        parts = jalali_str.split('/')
        if len(parts) != 3:
            return None
        
        year, month, day = map(int, parts)
        jalali_date = jdatetime.date(year, month, day)
        return jalali_date.togregorian()
    except:
        return None

def validate_date(date_str):
    """Validate Jalali date string format (YYYY/MM/DD)"""
    if not date_str:
        return False
    
    try:
        parts = date_str.split('/')
        if len(parts) != 3:
            return False
        
        year, month, day = map(int, parts)
        # Basic validation for Jalali calendar
        if year < 1300 or year > 1500:  # Reasonable range for Persian years
            return False
        if month < 1 or month > 12:
            return False
        if day < 1 or day > 31:
            return False
        
        # Try to create a Jalali date object to validate
        jdatetime.date(year, month, day)
        return True
    except:
        return False

def validate_gregorian_date(date_str):
    """Validate Gregorian date string format (YYYY-MM-DD)"""
    if not date_str:
        return False
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except:
        return False

def format_currency(amount):
    """Format currency with Persian separators"""
    if amount is None:
        return "0"
    
    try:
        return f"{amount:,.0f}".replace(',', '٬')
    except:
        return str(amount)

def export_to_pdf(financial_data, start_date=None, end_date=None):
    """Export financial report to PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Create styles
    styles = getSampleStyleSheet()
    
    # Define custom styles for RTL text
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontSize=16,
        alignment=2,  # Right alignment
        spaceAfter=20
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=2,  # Right alignment
        spaceAfter=10
    )
    
    # Build content
    content = []
    
    # Title
    title = "گزارش مالی جعبه‌سازی"
    if start_date and end_date:
        title += f" - از {to_jalali(start_date)} تا {to_jalali(end_date)}"
    
    content.append(Paragraph(title, title_style))
    content.append(Spacer(1, 20))
    
    # Financial summary table
    data = [
        ['مبلغ (تومان)', 'شرح'],
        [format_currency(financial_data['revenue']), 'کل درآمد'],
        [format_currency(financial_data['materials_cost']), 'هزینه مواد اولیه'],
        [format_currency(financial_data['production_cost']), 'هزینه تولید'],
        [format_currency(financial_data['expenses']), 'سایر هزینه‌ها'],
        [format_currency(financial_data['worker_wages']), 'حقوق کارگران'],
        [format_currency(financial_data['total_costs']), 'کل هزینه‌ها'],
        [format_currency(financial_data['profit_loss']), 'سود/زیان خالص'],
    ]
    
    table = Table(data, colWidths=[2*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    # Highlight profit/loss row
    if financial_data['profit_loss'] >= 0:
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgreen),
        ]))
    else:
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightcoral),
        ]))
    
    content.append(table)
    content.append(Spacer(1, 20))
    
    # Generate date
    content.append(Paragraph(f"تاریخ تولید گزارش: {to_jalali(date.today())}", normal_style))
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    
    return buffer

def get_persian_months():
    """Get list of Persian month names"""
    return [
        'فروردین', 'اردیبهشت', 'خرداد', 'تیر',
        'مرداد', 'شهریور', 'مهر', 'آبان',
        'آذر', 'دی', 'بهمن', 'اسفند'
    ]

def get_current_jalali_date():
    """Get current date in Jalali format"""
    return to_jalali(date.today())
