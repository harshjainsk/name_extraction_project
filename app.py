from flask import Flask, request, render_template
from pdf2image import convert_from_path
from PIL import Image
import numpy as np

import os

from paddleocr import PaddleOCR


ocr = PaddleOCR(use_angle_cls=True, lang='en')


def find_name_in_page(name, result):

    for idx in range(len(result)):
        res = result[idx]
        # print(res)
        # print("-----------------")
        for line_number in range(len(res)):
            # print([res[line_number][1][0]])
            # print("-----------------")

            textual_data = res[line_number][1][0].lower()

            if textual_data.find(name) >= 0:
                return {
                    "name searched" : f"{name}",
                    "string extracted" : f"{textual_data}",
                    "line number" : f"{line_number + 1}"
                }

    # return "Name not present in the document"
    return None


def apply_ocr_and_find_name(name, path_to_resume):


    pages = convert_from_path(path_to_resume, 500, poppler_path='poppler-23.11.0/Library/bin')

    for page_number in range(len(pages)):

        print(page_number)
        

        result = ocr.ocr(np.array(pages[page_number]), cls=True)  # Convert PIL image to NumPy array

        print(len(result[0]))
        print("------------------------\n\n\n" )

        name_found = find_name_in_page(name, result)

        if name_found is not None:

            name_found["page number"] = f"{page_number + 1}"

            return name_found

        # print(name_found)




app = Flask(__name__)


@app.route("/", methods = ['GET', 'POST'])
def get_file_from_frontend():

    return render_template("index.html")

    
@app.route("/name_of_file", methods = ['POST'])
def name_of_file():

    if request.method == 'POST':

        file = request.files['file']
        print(file)

        temp_path = os.path.join("static","temp", file.filename)
        file.save(temp_path)

        print(temp_path)


        return render_template("index2.html", pdf_file = temp_path)

if __name__ == '__main__':
    app.run(debug=True, port=5500)
