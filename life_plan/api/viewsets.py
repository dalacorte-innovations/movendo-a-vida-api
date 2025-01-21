import io
import csv
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from life_plan.models import LifePlan, LifePlanItem
from .serializers import LifePlanSerializer, LifePlanItemSerializer
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from rest_framework import status


class LifePlanViewSet(viewsets.ModelViewSet):
    queryset = LifePlan.objects.all()
    serializer_class = LifePlanSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return LifePlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
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

    def add_footer(self, canvas, doc):
        """Adds page numbers to the footer."""
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.drawRightString(200 * mm, 15 * mm, text)

    @action(detail=True, methods=['get'], url_path='export-pdf')
    def export_pdf(self, request, pk=None):
        try:
            life_plan = LifePlan.objects.get(pk=pk, user=request.user)
        except LifePlan.DoesNotExist:
            return Response({"error": "Plano de vida não encontrado."}, status=404)

        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
        
        elements = []

        title = f"Relatório do Plano de Vida: {life_plan.name}"
        report_date = f"Data de geração: {datetime.now().strftime('%d/%m/%Y')}"
        elements.append(Paragraph(title, ParagraphStyle('Title', fontSize=16, spaceAfter=10, alignment=1)))
        elements.append(Paragraph(report_date, ParagraphStyle('Date', fontSize=10, spaceAfter=20, alignment=1)))

        categories = {}
        for item in life_plan.items.all():
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)

        for category, items in categories.items():
            elements.append(Paragraph(f"Categoria: {category}", ParagraphStyle('Category', fontSize=12, spaceAfter=10, alignment=1)))

            table_data = [["Nome", "Data", "Valor", "Meta"]]
            for item in items:
                table_data.append([
                    item.name,
                    item.date.strftime('%d/%m/%Y'),
                    f"R$ {item.value:,.2f}",
                    f"R$ {item.meta:,.2f}" if item.meta else "N/A"
                ])

            table = Table(table_data, colWidths=[150, 80, 80, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 12))

        elements.append(PageBreak())

        pdf.build(elements, onFirstPage=self.add_footer, onLaterPages=self.add_footer)
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
