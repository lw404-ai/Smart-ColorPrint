import os
import sys
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
        pdf_images = convert_from_path(input_path, poppler_path=r'poppler\\bin', first_page=1,
                                       last_page=total_pages + 1)

        grey_pages = []
        color_pages = []
        print(20)

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
        print(60)
        return grey_pages, color_pages


def split_pdf_by_pages(input_file, output_file, page_list):
    pdf_reader = PyPDF4.PdfFileReader(input_file)
    pdf_writer = PyPDF4.PdfFileWriter()
    for page_num in page_list:
        pdf_writer.addPage(pdf_reader.getPage(page_num - 1))
    with open(output_file, 'wb') as f:
        pdf_writer.write(f)


print(5)
path = ""

last_slash_index = path.rfind("/")
input_pdf_name = path[last_slash_index + 1:]
directory = path[:last_slash_index + 1]

grey_file = f'{directory}黑白_{input_pdf_name}'
color_file = f'{directory}彩色_{input_pdf_name}'

grey_page, color_page = split_and_convert_pdf(path)

split_pdf_by_pages(path, grey_file, grey_page)
split_pdf_by_pages(path, color_file, color_page)
print(100)
# print(grey_page)
# print(color_page)
