import io
from django.http import HttpResponse, Http404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.cases.models import FIR
from apps.users.models import UserRole
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class CaseReportView(APIView):
    """
    APIView to compile case records, victims, suspects, and logs
    and generate a formatted PDF case document.
    Enforces PII redactions for users with the POLICYMAKER role.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            # Prefetch to minimize database queries
            fir = FIR.objects.prefetch_related('victims', 'accused', 'entities', 'logs').get(pk=pk)
        except (FIR.DoesNotExist, ValueError):
            raise Http404("Case not found.")

        # Check if the user role is Policymaker
        is_policymaker = request.user.role == UserRole.POLICYMAKER

        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=40, 
            leftMargin=40,
            topMargin=40, 
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        
        # Custom styles for the PDF layout
        title_style = ParagraphStyle(
            name='TitleStyle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#1A365D'),
            spaceAfter=12
        )
        subtitle_style = ParagraphStyle(
            name='SubtitleStyle',
            parent=styles['Heading3'],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#2B6CB0'),
            spaceAfter=8,
            spaceBefore=12
        )
        normal_style = styles['Normal']
        normal_style.fontSize = 9
        normal_style.leading = 12
        
        label_style = ParagraphStyle(
            name='LabelStyle',
            parent=normal_style,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2D3748')
        )

        elements = []

        # Document Header
        elements.append(Paragraph("VigilX - Case Investigation Report", title_style))
        elements.append(Spacer(1, 8))

        # Section 1: FIR Information
        elements.append(Paragraph("1. First Information Report (FIR) Details", subtitle_style))
        
        officer_name = fir.officer_in_charge.username if fir.officer_in_charge else "Unassigned"
        badge = fir.officer_in_charge.badge_number if fir.officer_in_charge and fir.officer_in_charge.badge_number else "N/A"
        
        case_info = [
            [
                Paragraph("FIR Number:", label_style), Paragraph(fir.fir_number, normal_style),
                Paragraph("Crime Type:", label_style), Paragraph(fir.get_crime_type_display(), normal_style)
            ],
            [
                Paragraph("Status:", label_style), Paragraph(fir.get_status_display(), normal_style),
                Paragraph("Officer Assigned:", label_style), Paragraph(f"{officer_name} (Badge: {badge})", normal_style)
            ],
            [
                Paragraph("Incident Date:", label_style), Paragraph(fir.incident_date_time.strftime('%Y-%m-%d %H:%M') if fir.incident_date_time else 'N/A', normal_style),
                Paragraph("Reported Date:", label_style), Paragraph(fir.reported_date_time.strftime('%Y-%m-%d %H:%M') if fir.reported_date_time else 'N/A', normal_style)
            ],
            [
                Paragraph("Location:", label_style), Paragraph(fir.location, normal_style),
                Paragraph("Coordinates:", label_style), Paragraph(f"{fir.latitude or 'N/A'}, {fir.longitude or 'N/A'}", normal_style)
            ]
        ]
        
        t = Table(case_info, colWidths=[90, 170, 90, 170])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#EDF2F7')),
            ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#EDF2F7')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        
        elements.append(t)
        elements.append(Spacer(1, 10))

        # Description
        elements.append(Paragraph("Description / Details of Incident:", label_style))
        elements.append(Paragraph(fir.description, normal_style))
        elements.append(Spacer(1, 10))

        # Section 2: Victims Profile
        elements.append(Paragraph("2. Victims Profile", subtitle_style))
        victims_data = [[
            Paragraph("Name", label_style), 
            Paragraph("Age/Gender", label_style), 
            Paragraph("Contact Number", label_style), 
            Paragraph("Address & Statement", label_style)
        ]]
        
        victims = fir.victims.all()
        if not victims:
            victims_data.append([Paragraph("No victim records associated.", normal_style), "", "", ""])
        else:
            for v in victims:
                contact = "[REDACTED]" if is_policymaker else (v.contact_number or "N/A")
                address = "[REDACTED]" if is_policymaker else (v.address or "N/A")
                statement = "[REDACTED]" if is_policymaker else (v.statement or "N/A")
                
                details_text = f"<b>Address:</b> {address}<br/><b>Statement:</b> {statement}"
                
                victims_data.append([
                    Paragraph(v.name, normal_style),
                    Paragraph(f"{v.age or 'N/A'} / {v.get_gender_display()}", normal_style),
                    Paragraph(contact, normal_style),
                    Paragraph(details_text, normal_style)
                ])
                
        vt = Table(victims_data, colWidths=[90, 70, 90, 270])
        vt.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(vt)
        elements.append(Spacer(1, 10))

        # Section 3: Accused Section
        elements.append(Paragraph("3. Accused & Suspects Profile", subtitle_style))
        accused_data = [[
            Paragraph("Name", label_style), 
            Paragraph("Age/Gender", label_style), 
            Paragraph("Status", label_style), 
            Paragraph("Contact & History", label_style)
        ]]
        
        accused_list = fir.accused.all()
        if not accused_list:
            accused_data.append([Paragraph("No accused records associated.", normal_style), "", "", ""])
        else:
            for a in accused_list:
                contact = "[REDACTED]" if is_policymaker else (a.contact_number or "N/A")
                history = "[REDACTED]" if is_policymaker else (a.criminal_history or "None")
                
                details_text = f"<b>Contact:</b> {contact}<br/><b>History:</b> {history}"
                
                accused_data.append([
                    Paragraph(a.name, normal_style),
                    Paragraph(f"{a.age or 'N/A'} / {a.get_gender_display()}", normal_style),
                    Paragraph(a.get_status_display(), normal_style),
                    Paragraph(details_text, normal_style)
                ])
                
        at = Table(accused_data, colWidths=[90, 70, 90, 270])
        at.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(at)
        elements.append(Spacer(1, 10))

        # Section 4: Clues Section
        elements.append(Paragraph("4. Clues & Relational Entities", subtitle_style))
        clues_data = [[
            Paragraph("Entity Type", label_style), 
            Paragraph("Value", label_style), 
            Paragraph("Description", label_style)
        ]]
        
        clues = fir.entities.all()
        if not clues:
            clues_data.append([Paragraph("No relational entities registered.", normal_style), "", ""])
        else:
            for c in clues:
                clues_data.append([
                    Paragraph(c.get_entity_type_display(), normal_style),
                    Paragraph(c.value, normal_style),
                    Paragraph(c.description or "N/A", normal_style)
                ])
                
        ct = Table(clues_data, colWidths=[120, 130, 270])
        ct.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(ct)
        elements.append(Spacer(1, 10))

        # Section 5: Case Diaries
        elements.append(Paragraph("5. Investigation Diary History", subtitle_style))
        logs_data = [[
            Paragraph("Date / Time", label_style), 
            Paragraph("Notes / Activities", label_style), 
            Paragraph("Recorded By", label_style)
        ]]
        
        logs = fir.logs.all().order_by('entry_date_time')
        if not logs:
            logs_data.append([Paragraph("No investigation logs recorded.", normal_style), "", ""])
        else:
            for l in logs:
                rec_by = l.recorded_by.username if l.recorded_by else "Unknown"
                logs_data.append([
                    Paragraph(l.entry_date_time.strftime('%Y-%m-%d %H:%M'), normal_style),
                    Paragraph(l.notes, normal_style),
                    Paragraph(rec_by, normal_style)
                ])
                
        lt = Table(logs_data, colWidths=[100, 320, 100])
        lt.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(lt)

        # Build PDF and generate download response
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(content_type='application/pdf')
        filename = f"Case_Report_{fir.fir_number.replace('/', '_')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf)
        
        return response
