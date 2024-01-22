from flask import Flask, request, render_template
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import numpy as np

import os

from paddleocr import PaddleOCR


ocr = PaddleOCR(use_angle_cls=True, lang='en')

def draw_bounding_box(image, coordinates):

    draw = ImageDraw.Draw(image)

    for i, box in enumerate(coordinates):
    # for i, box in enumerate([temp_result[0][0]]):  # replace with coordinates
        box = np.array(box[0]).astype(np.int32)
        xmin = min(box[:, 0])
        ymin = min(box[:, 1])
        xmax = max(box[:, 0])
        ymax = max(box[:, 1])
        draw.rectangle((xmin, ymin, xmax, ymax), outline="red", width=10)
        draw.text((xmin, ymin), f"{i}", fill="black")

        return image


def find_name_in_page(name, result):

    for idx in range(len(result)):
        res = result[idx]

        for line_number in range(len(res)):
            print([res[line_number][1][0]])
            textual_data = res[line_number][1][0].lower()
            if textual_data.find(name) >= 0:

                print([res[line_number][0]])
                return {
                    "name searched" : f"{name}",
                    "string extracted" : f"{textual_data}",
                    "line number" : f"{line_number + 1}",
                    "coordinates" : [[res[line_number][0]]]
                }

            print("-----------------")


    # return "Name not present in the document"
    return None

    
    
def convert_images_to_pdf(list_of_images):

    images = list_of_images

    pdf_path = "static/temp/bbd1.pdf"
        
    images[0].save(
        pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:]
    )


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
            
            updated_image = draw_bounding_box(image=pages[page_number], coordinates=name_found['coordinates'])

            pages[page_number] = updated_image

            convert_images_to_pdf(pages)

            return name_found




app = Flask(__name__)


@app.route("/", methods = ['GET', 'POST'])
def get_file_from_frontend():

    return render_template("index.html")

    
@app.route("/name_of_file", methods = ['POST'])
def name_of_file():

    global uploaded_file_path

    if request.method == 'POST':

        file = request.files['file']
        print(file)

        if str(file.filename).split(".")[-1] != 'pdf':
            
            return render_template('file_not_found_index.html', message = "Upload PDF files only")

        temp_path = os.path.join("static","temp", file.filename)

        uploaded_file_path = temp_path

        file.save(temp_path)

        print(temp_path)


        return render_template("index2.html", pdf_file = temp_path,message="Document Upload Success")
    

@app.route("/find_name_in_pdf", methods = ['POST', 'GET'])
def find_name_in_pdf():

    if request.method == 'POST':

        name_to_be_found = request.form.get('name_to_be_found')

        print(name_to_be_found)

        if uploaded_file_path:

            result = apply_ocr_and_find_name(name_to_be_found.lower(), uploaded_file_path)
            print(result)

            if result is not None:

                return render_template("index3.html", page_number=result['page number'], file = "static\\temp\\bbd1.pdf",
                                        message=f"name searched {result['name searched']} line number {result['line number']} page number {result['page number']}")
            
            return render_template("index2.html", pdf_file = uploaded_file_path, message="No Match found")

if __name__ == '__main__':
    app.run(debug=True, port=5500)
