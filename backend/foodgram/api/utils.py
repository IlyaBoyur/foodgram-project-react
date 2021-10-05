from fpdf import FPDF

PDF_INGREDIENT_LINE = '{name} ({unit}) - {amount}'
PDF_HEAD_LINE = 'Список покупок для {name} {surname}'
PDF_CELL_WIDTH = 200
PDF_CELL_HEGHT = 10
PDF_ALIGN_CENTER = 'C'
PDF_ALIGN_LEFT = 'L'
PDF_FONT_FAMILY = 'DejaVu'
PDF_FONT_STYLE = ''
PDF_FONT_NAME = 'DejaVuSansCondensed.ttf'
PDF_FONT_SIZE = 14
PDF_LINE_BRAKE_BIG = PDF_CELL_HEGHT * 2
PDF_LINE_BRAKE_SMALL = PDF_CELL_HEGHT


def create_shop_list(pdf_name, user, ingredients):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font(PDF_FONT_FAMILY,
                 PDF_FONT_STYLE,
                 PDF_FONT_NAME,
                 uni=True)
    pdf.set_font(PDF_FONT_FAMILY, size=PDF_FONT_SIZE)
    pdf.cell(
        PDF_CELL_WIDTH,
        PDF_CELL_HEGHT,
        txt=PDF_HEAD_LINE.format(name=user.first_name,
                                 surname=user.last_name),
        align=PDF_ALIGN_CENTER
    )
    pdf.ln(PDF_LINE_BRAKE_BIG)
    for name, unit, amount in ((name, unit, ingredients[name, unit])
                               for name, unit in ingredients):
        pdf.cell(
            PDF_CELL_WIDTH,
            PDF_CELL_HEGHT,
            txt=PDF_INGREDIENT_LINE.format(name=name.capitalize(),
                                           unit=unit,
                                           amount=str(amount)),
            align=PDF_ALIGN_LEFT,
        )
        pdf.ln(PDF_LINE_BRAKE_SMALL)
    pdf.output(pdf_name)
    return pdf_name
