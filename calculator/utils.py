from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
from datetime import datetime

def generate_pdf_report(journee):
    """Générer le rapport PDF d'une journée"""
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Center',
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        name='Right',
        alignment=TA_RIGHT,
        fontSize=10
    ))
    
    elements = []
    
    # Titre
    elements.append(Paragraph(
        f"Rapport Journalier - {journee.date.strftime('%d/%m/%Y')}",
        styles['Center']
    ))
    
    # Date de génération
    elements.append(Paragraph(
        f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        styles['Right']
    ))
    elements.append(Spacer(1, 20))
    
    # Tableau des ventes
    data = [['Gâteau', 'Quantité', 'Prix unitaire', 'Total']]
    for vente in journee.vente_set.all():
        data.append([
            vente.recette_gateau.nom,
            str(vente.quantite_vendue),
            f"{vente.recette_gateau.prix_vente_unitaire:.2f} DA",
            f"{vente.total_vente():.2f} DA"
        ])
    
    if len(data) > 1:  # S'il y a des ventes
        table = Table(data, colWidths=[4*cm, 3*cm, 3*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4B0082')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD')),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))
    
    # Résumé financier
    resume_data = [
        ['Résumé Financier', ''],
        ['Chiffre d\'affaires total', f"{journee.chiffre_affaire:.2f} DA"],
        ['Frais ingrédients', f"{journee.total_frais_ingredients:.2f} DA"],
        ['Frais emballage', f"{journee.total_frais_emballage:.2f} DA"],
        ['Frais local', f"{journee.frais_local:.2f} DA"],
        ['Frais électricité & impôts', f"{journee.frais_electricite_impots:.2f} DA"],
        ['Salaires employés', f"{journee.total_salaires:.2f} DA"],
        ['BÉNÉFICE NET', f"{journee.benefice:.2f} DA"],
    ]
    
    resume_table = Table(resume_data, colWidths=[8*cm, 6*cm])
    resume_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28A745')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFC107')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD')),
    ]))
    
    elements.append(resume_table)
    
    # Pied de page
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        "YounYami Pâtisserie - Rapport confidentiel",
        ParagraphStyle(
            name='Footer',
            alignment=TA_CENTER,
            fontSize=8,
            textColor=colors.HexColor('#888888')
        )
    ))
    
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rapport_{journee.date}.pdf"'
    
    return response