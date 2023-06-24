import io
from PyPDF4.pdf import PageObject
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch


def add_page_numbers(input_path, output_path):
    # 打开PDF文件
    with open(input_path, "rb") as file:
        pdf = PyPDF4.PdfFileReader(file)
        total_pages = pdf.getNumPages()

        # 创建一个新的PDF写入器
        output_pdf = PyPDF4.PdfFileWriter()

        # 遍历每一页
        for page_number in range(total_pages):
            # 获取页面对象
            page = pdf.getPage(page_number)

            # 创建一个Canvas对象来添加页码
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFont("Helvetica", 8)  # 设置字体和字号
            can.drawString(0.1 * inch, 11.5 * inch, str(page_number + 1))  # 设置位置和页码
            can.save()

            # 移动到起始位置并添加内容到新的页面
            packet.seek(0)
            watermark = PyPDF4.PdfFileReader(packet)
            watermark_page = watermark.getPage(0)
            page.mergePage(watermark_page)

            # 将修改后的页面添加到输出PDF
            output_pdf.addPage(page)

        # 将输出写入到新的PDF文件
        with open(output_path, "wb") as out_f:
            output_pdf.write(out_f)


input_file = "input.pdf"  # 输入的PDF文件路径
output_file = "output.pdf"  # 输出的PDF文件路径
add_page_numbers(input_file, output_file)
