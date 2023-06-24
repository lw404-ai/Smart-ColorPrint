import os
import concurrent.futures
import PyPDF4
from pdf2image import convert_from_path
from PIL import Image, ImageChops


def is_greyscale(image):
    if image.mode not in ("L", "RGB"):
        raise ValueError("Unsupported image mode")

    if image.mode == "RGB":
        rgb = image.split()
        if ImageChops.difference(rgb[0], rgb[1]).getextrema()[1] != 0:
            return False
        if ImageChops.difference(rgb[0], rgb[2]).getextrema()[1] != 0:
            return False
    return True


def split_and_convert_pdf(input_path):
    with open(input_path, 'rb') as file:
        pdf = PyPDF4.PdfFileReader(file)
        total_pages = pdf.numPages
        pdf_images = convert_from_path(input_path, first_page=1, last_page=total_pages + 1)

        grey_pages = []
        color_pages = []

        def process_page(page_number):
            image = pdf_images[page_number - 1]
            if is_greyscale(image):
                grey_pages.append(page_number)
            else:
                color_pages.append(page_number)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_page, range(1, total_pages + 1))
        grey_pages.sort()
        color_pages.sort()
        return grey_pages, color_pages


def split_pdf_by_pages(input_file, output_file, page_list):
    pdf_reader = PyPDF4.PdfFileReader(input_file)
    pdf_writer = PyPDF4.PdfFileWriter()
    for page_num in page_list:
        pdf_writer.addPage(pdf_reader.getPage(page_num - 1))
    with open(output_file, 'wb') as f:
        pdf_writer.write(f)


def split_pdf_by_pages_num(input_file, output_file_1, output_file_2, page_list_1, page_list_2):
    pdf_reader = PyPDF4.PdfFileReader(input_file)

    pdf_writer_1 = PyPDF4.PdfFileWriter()
    for index, page_num in enumerate(page_list_1):
        page = pdf_reader.getPage(page_num - 1)
        page.mergePage(page, 'Page {index + 1}')
        pdf_writer_1.addPage(page)
    with open(output_file_1, 'wb') as f:
        pdf_writer_1.write(f)

    pdf_writer_2 = PyPDF4.PdfFileWriter()
    for index, page_num in enumerate(page_list_2):
        page = pdf_reader.getPage(page_num - 1)
        page.mergePage(page, 'Page {index + 1}')
        pdf_writer_2.addPage(page)
    with open(output_file_2, 'wb') as f:
        pdf_writer_2.write(f)


input_pdf_path = 'input.pdf'
grey_file = 'output1.pdf'
color_file = 'output2.pdf'

grey_page, color_page = split_and_convert_pdf(input_pdf_path)
print(grey_page)
print(color_page)

split_pdf_by_pages(input_pdf_path, grey_file, grey_page)
split_pdf_by_pages(input_pdf_path, color_file, color_page)
