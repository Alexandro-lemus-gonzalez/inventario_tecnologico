import os
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

def generar_reporte_inventario_general(activos):
    """
    Genera un reporte PDF con el listado completo de activos.
    """
    filename = f"reporte_general_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(settings.MEDIA_ROOT, 'reportes', filename)
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()
    
    # Título y encabezado
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#00324D'),
        alignment=1,
        spaceAfter=20
    )
    
    elements.append(Paragraph("SISTEMA DE INVENTARIO TECNOLÓGICO SENA", title_style))
    elements.append(Paragraph(f"Reporte General de Activos - {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Heading2']))
    elements.append(Spacer(1, 20))
    
    # Datos de la tabla
    data = [['CÓDIGO', 'NOMBRE DEL ACTIVO', 'CATEGORÍA', 'UBICACIÓN', 'ESTADO', 'VALOR ADQ.']]
    
    total_valor = 0
    for a in activos:
        valor = float(a.valor_adquisicion) if a.valor_adquisicion else 0
        total_valor += valor
        data.append([
            a.codigo_inventario,
            a.nombre[:40],
            a.categoria.nombre,
            a.ubicacion.nombre if a.ubicacion else 'N/A',
            a.estado.nombre,
            f"${valor:,.2f}"
        ])
    
    # Fila de totales
    data.append(['', '', '', '', 'TOTAL:', f"${total_valor:,.2f}"])
    
    # Estilo de la tabla
    table = Table(data, colWidths=[100, 200, 100, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#39A900')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ]))
    
    elements.append(table)
    
    # Pie de página
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"Generado por sistema de auditoría - SENA ADSO", styles['Italic']))
    
    doc.build(elements)
    return filepath

def generar_reporte_activos_por_ubicacion(ubicacion, activos):
    """
    Genera un reporte PDF de los activos en una ubicación específica.
    """
    filename = f"reporte_ubicacion_{ubicacion.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(settings.MEDIA_ROOT, 'reportes', filename)
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    elements.append(Paragraph(f"REPORTE DE ACTIVOS POR UBICACIÓN", styles['Heading1']))
    elements.append(Spacer(1, 10))
    
    # Información de la ubicación
    info_data = [
        ['Ubicación:', ubicacion.nombre],
        ['Piso:', str(ubicacion.piso)],
        ['Total Activos:', str(activos.count())],
        ['Valor Total:', f"${sum(float(a.valor_adquisicion) for a in activos if a.valor_adquisicion):,.2f}"]
    ]
    
    info_table = Table(info_data, colWidths=[120, 300])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('SIZE', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Tabla de activos
    data = [['CÓDIGO', 'ACTIVO', 'ESTADO', 'RESPONSABLE']]
    for a in activos:
        data.append([
            a.codigo_inventario,
            a.nombre[:35],
            a.estado.nombre,
            a.responsable or 'No asignado'
        ])
    
    table = Table(data, colWidths=[100, 200, 100, 140])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF5722')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
    ]))
    
    elements.append(table)
    doc.build(elements)
    return filepath
