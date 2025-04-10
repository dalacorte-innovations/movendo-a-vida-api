import io
import csv
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
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
from collections import defaultdict

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
        canvas.line(15 * mm, doc.pagesize[1] - 20 * mm, doc.pagesize[0] - 15 * mm, doc.pagesize[1] - 20 * mm)
        
        canvas.setStrokeColorRGB(0.8, 0.8, 0.8)
        canvas.line(15 * mm, 15 * mm, doc.pagesize[0] - 15 * mm, 15 * mm)
        
        canvas.setFont("Helvetica", 9)
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.setFillColor(HexColor("#DB2777"))
        canvas.drawRightString(doc.pagesize[0] - 15 * mm, 10 * mm, text)

        canvas.setFont("Helvetica-Bold", 12)
        canvas.setFillColor(HexColor("#DB2777"))
        canvas.drawString(15 * mm, doc.pagesize[1] - 15 * mm, doc.title)
        
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
        canvas.line(15 * mm, doc.pagesize[1] - 20 * mm, doc.pagesize[0] - 15 * mm, doc.pagesize[1] - 20 * mm)
        
        canvas.setStrokeColor(HexColor("#334155"))
        canvas.line(15 * mm, 15 * mm, doc.pagesize[0] - 15 * mm, 15 * mm)
        
        canvas.setFont("Helvetica", 9)
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.setFillColor(HexColor("#EC4899"))
        canvas.drawRightString(doc.pagesize[0] - 15 * mm, 10 * mm, text)
        
        canvas.setFont("Helvetica-Bold", 12)
        canvas.setFillColor(HexColor("#EC4899"))
        canvas.drawString(15 * mm, doc.pagesize[1] - 15 * mm, doc.title)
        
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
            pagesize=landscape(A4), 
            rightMargin=15 * mm, 
            leftMargin=15 * mm, 
            topMargin=25 * mm, 
            bottomMargin=20 * mm,
            title=life_plan.name
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
            positive_value_color = HexColor("#10B981")
            negative_value_color = HexColor("#EF4444")
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
            positive_value_color = HexColor("#059669")
            negative_value_color = HexColor("#DC2626")
        
        title_style = ParagraphStyle(
            'Title', 
            parent=styles['Title'],
            fontSize=16, 
            textColor=heading_color,
            alignment=TA_CENTER,
            spaceAfter=5 * mm
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle', 
            parent=styles['Heading2'],
            fontSize=12, 
            textColor=subheading_color,
            alignment=TA_CENTER,
            spaceAfter=10 * mm
        )
        
        date_style = ParagraphStyle(
            'Date', 
            parent=styles['Normal'],
            fontSize=9, 
            textColor=text_color,
            alignment=TA_CENTER,
            spaceAfter=10 * mm
        )
        
        category_style = ParagraphStyle(
            'Category', 
            parent=styles['Heading2'],
            fontSize=12, 
            textColor=heading_color,
            alignment=TA_LEFT,
            spaceBefore=8 * mm,
            spaceAfter=4 * mm,
            fontName='Helvetica-Bold'
        )
        
        header_cell_style = ParagraphStyle(
            'HeaderCell',
            parent=styles['Normal'],
            fontSize=9,
            textColor=table_header_text,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        name_cell_style = ParagraphStyle(
            'NameCell',
            parent=styles['Normal'],
            fontSize=8,
            textColor=text_color,
            alignment=TA_LEFT,
            fontName='Helvetica'
        )
        
        value_cell_style = ParagraphStyle(
            'ValueCell',
            parent=styles['Normal'],
            fontSize=8,
            textColor=text_color,
            alignment=TA_RIGHT,
            fontName='Helvetica'
        )
        
        positive_value_style = ParagraphStyle(
            'PositiveValueCell',
            parent=value_cell_style,
            textColor=positive_value_color
        )
        
        negative_value_style = ParagraphStyle(
            'NegativeValueCell',
            parent=value_cell_style,
            textColor=negative_value_color
        )
        
        subtotal_cell_style = ParagraphStyle(
            'SubtotalCell',
            parent=styles['Normal'],
            fontSize=8,
            textColor=table_header_text,
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        )
        
        subtotal_name_style = ParagraphStyle(
            'SubtotalNameCell',
            parent=subtotal_cell_style,
            alignment=TA_LEFT
        )
        
        elements = []

        elements.append(Paragraph("Plano de Vida", title_style))
        elements.append(Paragraph(life_plan.name, subtitle_style))
        
        report_date = f"Data de geração: {datetime.now().strftime('%d/%m/%Y')}"
        elements.append(Paragraph(report_date, date_style))
        
        categories_data = defaultdict(lambda: defaultdict(list))
        all_dates = set()
        
        for item in life_plan.items.all():
            date_str = item.date.strftime('%Y-%m')
            all_dates.add(date_str)
            categories_data[item.category][item.name].append({
                'date': date_str,
                'value': item.value,
                'meta': item.meta
            })
        
        all_dates = sorted(list(all_dates))
        
        months = {
            '01': 'jan', '02': 'fev', '03': 'mar', '04': 'abr',
            '05': 'mai', '06': 'jun', '07': 'jul', '08': 'ago',
            '09': 'set', '10': 'out', '11': 'nov', '12': 'dez'
        }
        
        category_order = [
            "receitas",
            "renda_extra",
            "estudos",
            "custos",
            "lucroPrejuizo",
            "investimentos",
            "realizacoes",
            "intercambio",
            "empresas",
            "pessoais",
        ]
        
        category_display_names = {
            "receitas": "Receitas",
            "renda_extra": "Renda Extra",
            "estudos": "Estudos",
            "custos": "Custos",
            "lucroPrejuizo": "Lucro/Prejuízo",
            "investimentos": "Investimentos",
            "realizacoes": "Realizações",
            "intercambio": "Intercâmbio",
            "empresas": "Empresas",
            "pessoais": "Pessoais",
        }
        
        for category_name in category_order:
            if category_name not in categories_data and category_name != "lucroPrejuizo":
                continue
                
            display_category = category_display_names.get(category_name, category_name.capitalize())
            
            elements.append(Paragraph(display_category, category_style))
            
            header_row = [Paragraph("Nome", header_cell_style)]
            for date_str in all_dates:
                year, month = date_str.split('-')
                header_row.append(Paragraph(f"{months[month]} - {year}", header_cell_style))
            header_row.append(Paragraph("Total", header_cell_style))
            
            table_data = [header_row]
            
            category_items = categories_data.get(category_name, {})
            
            if category_name == "lucroPrejuizo":
                profit_loss_row = [Paragraph("Lucro/Prejuízo", name_cell_style)]
                total_profit = 0
                
                for date_str in all_dates:
                    receitas_total = sum(item['value'] for items in categories_data.get("receitas", {}).values() 
                                        for item in items if item['date'] == date_str)
                    renda_extra_total = sum(item['value'] for items in categories_data.get("renda_extra", {}).values()
                                       for item in items if item['date'] == date_str)                                            
                    custos_total = sum(item['value'] for items in categories_data.get("custos", {}).values() 
                                      for item in items if item['date'] == date_str)
                    estudos_total = sum(item['value'] for items in categories_data.get("estudos", {}).values() 
                                       for item in items if item['date'] == date_str)
                    
                    profit = (receitas_total + renda_extra_total) - custos_total - estudos_total
                    total_profit += profit
                    
                    style = positive_value_style if profit >= 0 else negative_value_style
                    profit_loss_row.append(Paragraph(f"R$ {profit:,.2f}", style))
                
                style = positive_value_style if total_profit >= 0 else negative_value_style
                profit_loss_row.append(Paragraph(f"R$ {total_profit:,.2f}", style))
                table_data.append(profit_loss_row)
            else:
                for item_name, items in category_items.items():
                    row = [Paragraph(item_name, name_cell_style)]
                    total_value = 0
                    
                    for date_str in all_dates:
                        value = 0
                        for item in items:
                            if item['date'] == date_str:
                                value = item['value']
                                total_value += value
                                break
                        
                        row.append(Paragraph(f"R$ {value:,.2f}", value_cell_style))
                    
                    row.append(Paragraph(f"R$ {total_value:,.2f}", value_cell_style))
                    table_data.append(row)
            
            if len(table_data) > 1:
                subtotal_row = [Paragraph("Subtotal", subtotal_name_style)]
                total_subtotal = 0
                
                for i, date_str in enumerate(all_dates):
                    if category_name == "lucroPrejuizo":
                        cell_value = table_data[1][i+1]
                        if isinstance(cell_value, Paragraph):
                            value_str = cell_value.text
                        else:
                            value_str = cell_value
                        
                        value_str = value_str.replace('R$ ', '').replace('.', '').replace(',', '.')
                        subtotal = float(value_str)
                    else:
                        subtotal = 0
                        for row in table_data[1:]:
                            cell_value = row[i+1]
                            if isinstance(cell_value, Paragraph):
                                value_str = cell_value.text
                            else:
                                value_str = cell_value
                            
                            value_str = value_str.replace('R$ ', '').replace('.', '').replace(',', '.')
                            subtotal += float(value_str)
                    
                    total_subtotal += subtotal
                    subtotal_row.append(Paragraph(f"R$ {subtotal:,.2f}", subtotal_cell_style))
                
                subtotal_row.append(Paragraph(f"R$ {total_subtotal:,.2f}", subtotal_cell_style))
                table_data.append(subtotal_row)
            
            available_width = pdf.width
            name_col_width = available_width * 0.2
            total_col_width = available_width * 0.1
            date_col_width = (available_width - name_col_width - total_col_width) / len(all_dates)
            
            col_widths = [name_col_width] + [date_col_width] * len(all_dates) + [total_col_width]
            
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), table_header_bg),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                
                ('GRID', (0, 0), (-1, -1), 0.5, table_border_color),
                
                ('BACKGROUND', (0, 1), (-1, -2), table_odd_row_bg),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [table_odd_row_bg, table_even_row_bg]),
                
                ('BACKGROUND', (0, -1), (-1, -1), table_header_bg),
                
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                
                ('WORDWRAP', (0, 0), (-1, -1), True),
            ]
            
            table.setStyle(TableStyle(table_style))
            
            elements.append(table)
            elements.append(Spacer(1, 5 * mm))
        
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