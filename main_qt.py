import os
import sys
import concurrent.futures
import PyPDF4
from pdf2image import convert_from_path
from PIL import Image, ImageChops
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLineEdit, QMessageBox
from PyQt6.QtWidgets import QProgressBar, QLabel
from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtGui import QFont


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
        window.process_output(15)

        def process_page(page_number):
            window.process_output(40)
            image = pdf_images[page_number - 1]
            if is_greyscale(image):
                grey_pages.append(page_number)
            else:
                color_pages.append(page_number)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_page, range(1, total_pages + 1))
        window.process_output(50)
        grey_pages.sort()
        color_pages.sort()
        window.process_output(60)
        return grey_pages, color_pages


def split_pdf_by_pages(input_file, output_file, page_list):
    pdf_reader = PyPDF4.PdfFileReader(input_file)
    pdf_writer = PyPDF4.PdfFileWriter()
    for page_num in page_list:
        pdf_writer.addPage(pdf_reader.getPage(page_num - 1))
    with open(output_file, 'wb') as f:
        pdf_writer.write(f)


def run_script(path):
    window.process_output(5)
    last_slash_index = path.rfind("/")
    input_pdf_name = path[last_slash_index + 1:]
    directory = path[:last_slash_index + 1]

    grey_file = f'{directory}黑白_{input_pdf_name}'
    color_file = f'{directory}彩色_{input_pdf_name}'

    grey_page, color_page = split_and_convert_pdf(path)

    split_pdf_by_pages(path, grey_file, grey_page)
    split_pdf_by_pages(path, color_file, color_page)
    window.process_output(100)

    window.process_finished()
    # print(grey_page)
    # print(color_page)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart-ColorPrint")
        self.setGeometry(300, 300, 500, 300)
        self.setMinimumSize(500, 300)

        self.button = QPushButton("开始选择文件", self)
        self.button.setGeometry(200, 80, 100, 40)
        self.button.clicked.connect(self.select_file)

        self.file_path_line = QLineEdit(self)
        self.file_path_line.setGeometry(130, 150, 300, 30)
        self.file_path_line.setReadOnly(True)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(130, 200, 300, 30)
        self.progress_bar.setValue(0)

        label1 = QLabel("文档文件地址：", self)
        label1.setFont(QFont(QFont("Microsoft YaHei", 10, QFont.Weight.ExtraBold)))
        label1.setGeometry(20, 150, 300, 30)
        label2 = QLabel("进度百分比：", self)
        label2.setFont(QFont(QFont("Microsoft YaHei", 10, QFont.Weight.ExtraBold)))
        label2.setGeometry(20, 200, 300, 30)
        label3 = QLabel("√ 实现了提取文档中彩页页面与黑白页面\n√ 能节约一些打印带来的费用", self)
        label3.setFont(QFont(QFont("Microsoft YaHei", 10, QFont.Weight.ExtraBold)))
        label3.setGeometry(20, 25, 300, 30)
        label4 = QLabel("★项目地址：https://github.com/lw404-ai/Smart-ColorPrint", self)
        label4.setFont(QFont(QFont("Microsoft YaHei", 8, QFont.Weight.ExtraBold)))
        label4.setGeometry(20, 270, 300, 30)

        self.show_dialog()

    def select_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择文档文件", "", "文档文件 (*.pdf)")

        if file_path:
            self.file_path_line.setText(file_path)
            self.run_main_script(file_path)

    def run_main_script(self, file_path):
        run_script(file_path)

    def process_output(self, flag):
        # 根据输出更新进度条
        progress = int(flag)  # 假设输出的是整数形式的进度值
        self.progress_bar.setValue(progress)

    def process_finished(self):
        print("Process finished with exit code!")
        self.show_completion_dialog()

    def show_completion_dialog(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.ExtraBold))
        msg_box.setWindowTitle("运行完成")
        msg_box.setText(
            "运行已完成!\n\n如果感觉还不错，请给项目一个Star★\n\nhttps://github.com/lw404-ai/Smart-ColorPrint ")
        msg_box.exec()

    def show_dialog(self):
        msg_box = QMessageBox()
        msg_box.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.ExtraBold))
        msg_box.setWindowTitle("项目介绍")
        msg_box.setText("\n项目作者：lw404-ai\n\n请给项目一个Star★以示鼓励~\n")
        msg_box.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
