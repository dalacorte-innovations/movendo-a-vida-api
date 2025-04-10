import io
import csv
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    PageBreak, Image, Flowable, KeepTogether, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.colors import HexColor, Color
from life_plan.models import LifePlan, LifePlanItem
from life_plan.api.serializers import LifePlanSerializer, LifePlanItemSerializer
from rest_framework import viewsets, serializers, status

class LifePlanViewSet(viewsets.ModelViewSet):
    queryset = LifePlan.objects.all()
    serializer_class = LifePlanSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return LifePlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if LifePlan.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError("Você já possui um plano de vida. Não é possível criar outro.")
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if LifePlan.objects.filter(user=request.user).exists():
            return Response(
                {"error": "Você já possui um plano de vida. Não é possível criar outro."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='export-csv')
    def export_csv(self, request, pk=None):
        life_plan = self.get_object()
        items = LifePlanItem.objects.filter(life_plan=life_plan)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="life_plan_{life_plan.id}_{datetime.now().strftime("%Y%m%d")}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Category', 'Name', 'Value', 'Date', 'Meta'])
        for item in items:
            writer.writerow([item.category, item.name, item.value, item.date, item.meta])

        return response

    def add_header_footer(self, canvas, doc):
        """Adds header and footer to each page."""
        canvas.saveState()
        
        canvas.setFillColor(HexColor("#F8F9FF"))
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
        
        canvas.setFillColor(HexColor("#818CF8"))
        canvas.setFillAlpha(0.1)
        canvas.circle(doc.pagesize[0] - 50 * mm, doc.pagesize[1] - 50 * mm, 100 * mm, fill=1, stroke=0)
        
        canvas.setFillColor(HexColor("#EC4899"))
        canvas.setFillAlpha(0.1)
        canvas.circle(50 * mm, 50 * mm, 80 * mm, fill=1, stroke=0)
        
        canvas.setFillAlpha(1)
        
        canvas.setStrokeColorRGB(0.8, 0.8, 0.8)
        canvas.line(30 * mm, doc.pagesize[1] - 30 * mm, doc.pagesize[0] - 30 * mm, doc.pagesize[1] - 30 * mm)
        
        canvas.setStrokeColorRGB(0.8, 0.8, 0.8)
        canvas.line(30 * mm, 20 * mm, doc.pagesize[0] - 30 * mm, 20 * mm)
        
        canvas.setFont("Helvetica", 9)
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.setFillColor(HexColor("#DB2777"))
        canvas.drawRightString(doc.pagesize[0] - 30 * mm, 15 * mm, text)
        
        canvas.restoreState()

    def add_dark_header_footer(self, canvas, doc):
        """Adds header and footer to each page with dark theme."""
        canvas.saveState()
        
        canvas.setFillColor(HexColor("#0F172A"))
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
        
        canvas.setFillColor(HexColor("#DB2777"))
        canvas.setFillAlpha(0.1)
        canvas.circle(doc.pagesize[0] - 50 * mm, doc.pagesize[1] - 50 * mm, 100 * mm, fill=1, stroke=0)
        
        canvas.setFillColor(HexColor("#8B5CF6"))
        canvas.setFillAlpha(0.1)
        canvas.circle(50 * mm, 50 * mm, 80 * mm, fill=1, stroke=0)
        
        canvas.setFillAlpha(1)
        
        canvas.setStrokeColor(HexColor("#334155"))
        canvas.line(30 * mm, doc.pagesize[1] - 30 * mm, doc.pagesize[0] - 30 * mm, doc.pagesize[1] - 30 * mm)
        
        canvas.setStrokeColor(HexColor("#334155"))
        canvas.line(30 * mm, 20 * mm, doc.pagesize[0] - 30 * mm, 20 * mm)
        
        canvas.setFont("Helvetica", 9)
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.setFillColor(HexColor("#EC4899"))
        canvas.drawRightString(doc.pagesize[0] - 30 * mm, 15 * mm, text)
        
        canvas.restoreState()

    @action(detail=True, methods=['get'], url_path='export-pdf')
    def export_pdf(self, request, pk=None):
        try:
            life_plan = LifePlan.objects.get(pk=pk, user=request.user)
        except LifePlan.DoesNotExist:
            return Response({"error": "Plano de vida não encontrado."}, status=404)

        is_dark_mode = request.query_params.get('dark_mode', 'false').lower() == 'true'
        
        buffer = io.BytesIO()
        
        pdf = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            rightMargin=30 * mm, 
            leftMargin=30 * mm, 
            topMargin=40 * mm, 
            bottomMargin=30 * mm
        )
        
        styles = getSampleStyleSheet()
        
        if is_dark_mode:
            text_color = HexColor("#FFFFFF")
            heading_color = HexColor("#EC4899")
            subheading_color = HexColor("#8B5CF6")
            card_bg_color = HexColor("#1E293B")
            card_border_color = HexColor("#334155") 
            table_header_bg = HexColor("#334155")
            table_header_text = HexColor("#FFFFFF")
            table_odd_row_bg = HexColor("#1E293B")
            table_even_row_bg = HexColor("#0F172A")
            table_border_color = HexColor("#475569")
        else:
            text_color = HexColor("#1E293B")
            heading_color = HexColor("#DB2777")
            subheading_color = HexColor("#4F46E5")
            card_bg_color = HexColor("#FFFFFF")
            card_border_color = HexColor("#E0E7FF")
            table_header_bg = HexColor("#818CF8")
            table_header_text = HexColor("#FFFFFF")
            table_odd_row_bg = HexColor("#FFFFFF")
            table_even_row_bg = HexColor("#F1F5F9")
            table_border_color = HexColor("#E2E8F0")
        
        title_style = ParagraphStyle(
            'Title', 
            parent=styles['Title'],
            fontSize=20, 
            textColor=heading_color,
            alignment=TA_CENTER,
            spaceAfter=5 * mm
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle', 
            parent=styles['Heading2'],
            fontSize=14, 
            textColor=subheading_color,
            alignment=TA_CENTER,
            spaceAfter=10 * mm
        )
        
        date_style = ParagraphStyle(
            'Date', 
            parent=styles['Normal'],
            fontSize=10, 
            textColor=text_color,
            alignment=TA_CENTER,
            spaceAfter=15 * mm
        )
        
        category_style = ParagraphStyle(
            'Category', 
            parent=styles['Heading2'],
            fontSize=14, 
            textColor=heading_color,
            alignment=TA_LEFT,
            spaceBefore=10 * mm,
            spaceAfter=5 * mm,
            fontName='Helvetica-Bold'
        )
        
        elements = []

        elements.append(Paragraph("Relatório do Plano de Vida", title_style))
        elements.append(Paragraph(life_plan.name, subtitle_style))
        
        report_date = f"Data de geração: {datetime.now().strftime('%d/%m/%Y')}"
        elements.append(Paragraph(report_date, date_style))
        
        elements.append(HRFlowable(
            width="100%", 
            thickness=1, 
            color=card_border_color,
            spaceBefore=5 * mm,
            spaceAfter=10 * mm
        ))
        
        categories_data = {}
        for item in life_plan.items.all():
            if item.category not in categories_data:
                categories_data[item.category] = []
            categories_data[item.category].append(item)
        
        category_order = [
            "receitas",
            "estudos",
            "custos",
            "lucroPrejuizo",
            "investimentos",
            "realizacoes",
            "intercambio",
            "empresas",
            "pessoais",
        ]
        
        for category in category_order:
            if category not in categories_data:
                categories_data[category] = []
        
        for category_name in category_order:
            items = categories_data.get(category_name, [])
            
            display_category = category_name.capitalize()
            if category_name == "lucroPrejuizo":
                display_category = "Lucro/Prejuízo"
            elif category_name == "realizacoes":
                display_category = "Realizações"
            elif category_name == "intercambio":
                display_category = "Intercâmbio"
            
            elements.append(Paragraph(f"Categoria: {display_category}", category_style))
            
            table_data = [["Nome", "Data", "Valor", "Meta"]]
            
            if items:
                for item in sorted(items, key=lambda x: x.date):
                    table_data.append([
                        item.name,
                        item.date.strftime('%d/%m/%Y'),
                        f"R$ {item.value:,.2f}",
                        f"R$ {item.meta:,.2f}" if item.meta is not None else "R$ 0,00"
                    ])
            else:
                table_data.append([
                    "Sem dados",
                    datetime.now().strftime('%d/%m/%Y'),
                    "R$ 0,00",
                    "R$ 0,00"
                ])
            
            col_widths = [pdf.width * 0.4, pdf.width * 0.2, pdf.width * 0.2, pdf.width * 0.2]
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), table_header_bg),
                ('TEXTCOLOR', (0, 0), (-1, 0), table_header_text),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                ('GRID', (0, 0), (-1, -1), 0.5, table_border_color),
                
                ('BACKGROUND', (0, 1), (-1, -1), table_odd_row_bg),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [table_odd_row_bg, table_even_row_bg]),
                
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 15 * mm))
            if category_name != category_order[-1]:
                elements.append(HRFlowable(
                    width="100%", 
                    thickness=1, 
                    color=card_border_color,
                    spaceBefore=5 * mm,
                    spaceAfter=15 * mm
                ))
        
        if is_dark_mode:
            pdf.build(elements, onFirstPage=self.add_dark_header_footer, onLaterPages=self.add_dark_header_footer)
        else:
            pdf.build(elements, onFirstPage=self.add_header_footer, onLaterPages=self.add_header_footer)
            
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="plano_de_vida_{life_plan.id}.pdf"'
        return response


class LifePlanItemViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing LifePlanItem instances.
    """
    queryset = LifePlanItem.objects.all()
    serializer_class = LifePlanItemSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_staff:
            return LifePlanItem.objects.all()
        return LifePlanItem.objects.filter(life_plan__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()