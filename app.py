from flask import Flask, request, render_template, jsonify
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


def find_name_in_page(list_of_details, result):

    for idx in range(len(result)):
        res = result[idx]

        for line_number in range(len(res)):
            print([res[line_number][1][0]])
            textual_data = res[line_number][1][0].lower()

            for detail in list_of_details:

                if textual_data.find(detail) >= 0:

                    print([res[line_number][0]])
                    return {
                        "name searched" : f"{detail}",
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


def apply_ocr_and_find_name(list_of_details, path_to_resume):


    pages = convert_from_path(path_to_resume, 500, poppler_path='poppler-23.11.0/Library/bin')

    final_results = []

    for page_number in range(len(pages)):

        print(page_number)

        

        result = ocr.ocr(np.array(pages[page_number]), cls=True)  # Convert PIL image to NumPy array

        # print(len(result[0]))
        # print("------------------------\n\n\n" )

        name_found = find_name_in_page(list_of_details, result)

        if name_found is not None:

            name_found["page number"] = f"{page_number + 1}"
            
            updated_image = draw_bounding_box(image=pages[page_number], coordinates=name_found['coordinates'])

            pages[page_number] = updated_image

            convert_images_to_pdf(pages)

            dict_to_append = {
                f"{name_found['name searched']}" : name_found
            }

            final_results.append(dict_to_append)
            # return name_found

    return final_results




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
        deportation_text_to_be_found = request.form.get('text_to_be_found')
        tranfer_cert_to_be_found = request.form.get('transfer_cert_to_be_found')
        Type_of_Application = request.form.get("Type_of_Application")
        random_text = request.form.get("CPADIFOKI2")




        list_of_details = [name_to_be_found, deportation_text_to_be_found, tranfer_cert_to_be_found, Type_of_Application, random_text]

        list_of_details = [x. lower() for x in list_of_details]

        print(name_to_be_found)

        if uploaded_file_path:

            global result

            result = apply_ocr_and_find_name(list_of_details, uploaded_file_path)
            print(result)

            if len(result) > 0:
                

                return render_template("index3.html", updated_file=r"static\\temp\\bbd1.pdf", results=result, main_file_path = uploaded_file_path)

                
            return render_template("index2.html", pdf_file = uploaded_file_path, message="No Match found")
    
    # return render_template("index3.html", updated_file=r"static\\temp\\bbd1.pdf", results=result, main_file_path = uploaded_file_path)
        

@app.route("/button_redirect", methods=['GET', 'POST'])
def button_redirect():
    uploaded_file_path = r"static\\temp\\PassPort_Appointment_Receipt_organized_2.pdf"
    page_number= "2"
    return render_template("button_redirect.html", pdf_file = uploaded_file_path, file_path = r"static\\temp\\PassPort_Appointment_Receipt_organized_2.pdf", message="No Match found", page_number = page_number)



@app.route("/dynamic-buttons", methods=['GET', 'POST'])
def dynamic_buttons():


    result = [{'cpadifoki2': {'name searched': 'cpadifoki2',
   'string extracted': 'cpadifoki2',
   'line number': '25',
   'coordinates': [[[[2709.0, 1442.0],
      [3107.0, 1463.0],
      [3102.0, 1548.0],
      [2704.0, 1527.0]]]],
   'page number': '1'}},
 {'harsh kumar': {'name searched': 'harsh kumar',
   'string extracted': 'harsh kumar',
   'line number': '28',
   'coordinates': [[[[904.0, 1504.0],
      [1328.0, 1504.0],
      [1328.0, 1571.0],
      [904.0, 1571.0]]]],
   'page number': '1'}},
 {'type of application': {'name searched': 'type of application',
   'string extracted': 'type of application',
   'line number': '23',
   'coordinates': [[[[215.0, 1413.0],
      [713.0, 1413.0],
      [713.0, 1492.0],
      [215.0, 1492.0]]]],
   'page number': '1'}},
 {'b. transfer/school leaving/matriculation certificate issued by the school last attended/recognised educational board having the date of birth of the': {'name searched': 'b. transfer/school leaving/matriculation certificate issued by the school last attended/recognised educational board having the date of birth of the',
   'string extracted': 'b. transfer/school leaving/matriculation certificate issued by the school last attended/recognised educational board having the date of birth of the',
   'line number': '88',
   'coordinates': [[[[713.0, 5116.0],
      [3738.0, 5116.0],
      [3738.0, 5177.0],
      [713.0, 5177.0]]]],
   'page number': '2'}},
 {'8.proof of refund of repatriation /deportation cost (if any) to ministry of external affairs': {'name searched': '8.proof of refund of repatriation /deportation cost (if any) to ministry of external affairs',
   'string extracted': '8.proof of refund of repatriation /deportation cost (if any) to ministry of external affairs',
   'line number': '9',
   'coordinates': [[[[498.0, 828.0],
      [2300.0, 828.0],
      [2300.0, 889.0],
      [498.0, 889.0]]]],
   'page number': '3'}}]


    page_number = "3"

    return render_template("dynamic_buttons.html", file=r"static\\temp\\bbd1.pdf", results=result)


if __name__ == '__main__':
    app.run(debug=True, port=5500)
