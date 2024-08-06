import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from skimage.transform import resize
from skimage.draw import line_aa
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import math
from io import BytesIO

original_pixel_values = []
current_pixel_values = []
IMAGE_RESOLUTION = 300
ITERATIONS = 5000
NO_OF_NAILS = 300
STRING_WIDTH = 0.15
STRING_STRENGTH = 0.1
RADIUS_CIRCLE = (IMAGE_RESOLUTION // 2) - 0.5
NAILS = {}
NAIL_SEQUENCE = []

image_path = ""

def open_image():
    global image_path
    image_path = st.file_uploader("Upload an image", type=['png', 'jpg'])

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

def create_art():
    global original_pixel_values, current_pixel_values
    if image_path:
        img = plt.imread(image_path)
        img = resize(img, (IMAGE_RESOLUTION, IMAGE_RESOLUTION))
        original_pixel_values = rgb2gray(img)
        original_pixel_values = original_pixel_values*0.9

        current_pixel_values = np.ones((IMAGE_RESOLUTION, IMAGE_RESOLUTION))
        main()
        return True
    else:
        st.warning("Please upload an image.", icon="⚠️")
        return False

def update_iterations():
    global ITERATIONS
    try:
        ITERATIONS = int(st.text_input("Iterations", ITERATIONS))
        if ITERATIONS < 25:
            st.warning('Too less iterations!! Enter Iterations more than 25.', icon="⚠️")
            return False
        else:
            return True
    
    except ValueError:
        st.error("Please enter a valid integer for iterations.")
        return False

def update_nails():
    global NO_OF_NAILS
    try:
        NO_OF_NAILS = int(st.text_input("Number of Nails", NO_OF_NAILS))
        return True
    except ValueError:
        st.error("Please enter a valid integer for number of nails.")
        return False
    
def generate_circle_coordinates(ax):
    for i in range(NO_OF_NAILS):
        angle = 2 * math.pi * i / NO_OF_NAILS
        x = (RADIUS_CIRCLE) * math.cos(angle) + RADIUS_CIRCLE 
        y = (RADIUS_CIRCLE) * math.sin(-angle) + RADIUS_CIRCLE 
        NAILS["N" + str(i)] = (x, y)
        ax.scatter(x, y, color="black", s = 2)
    print(NAILS)

def is_fittest_point(row, col, intensity):
    global best_improvement_value, current_pixel_values
    before_diff = (current_pixel_values[col, row] - original_pixel_values[col, row]) ** 2
    after_diff = (np.subtract(current_pixel_values[col, row], STRING_STRENGTH * intensity) - original_pixel_values[
            col, row]) ** 2

    cumilative_improvement = np.sum(before_diff - after_diff)
    # print(cumilative_improvement)
    if cumilative_improvement >= best_improvement_value:
        best_improvement_value = cumilative_improvement
        return True
    else:
        return False

def choose_best_point(x, y, prev_x, prev_y):
    global current_pixel_values, best_improvement_value
    x2, y2 = -1, -1
    best_improvement_value = -999999

    for i in range(NO_OF_NAILS):
        angle = 2 * math.pi * i / NO_OF_NAILS
        x1 = (RADIUS_CIRCLE) * math.cos(angle) + RADIUS_CIRCLE 
        y1 = (RADIUS_CIRCLE) * math.sin(-angle) + RADIUS_CIRCLE 

        if (x1 != x and y1 != y):
            row, col, intensity = line_aa(int(x), int(y), int(x1), int(y1))
            if prev_x != x1 and prev_y != y1 and is_fittest_point(row, col, intensity):
                x2, y2 = x1, y1

    row, col, intensity = line_aa(int(x), int(y), int(x2), int(y2))
    current_pixel_values[col, row] -= STRING_STRENGTH * intensity
    current_pixel_values = np.clip(current_pixel_values, 0, 1)

    return [x2, y2]

def nail_no(x2, y2):
    for key, value in NAILS.items():
        if value == (x2, y2):
            return key

def save_numbers_to_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(250, 740, "String Art")
    c.setFont("Helvetica-Bold", 12)
    x = 60
    y = 720

    vertical_spacing = 15


    for i in range(0, len(NAIL_SEQUENCE), 1):

        if(x >= 550):
            y -= vertical_spacing
            x = 60

        if y <= 50:
            c.showPage()
            c.setFont("Helvetica-Bold", 12)
            x = 60
            y = 750

        c.drawString(x, y, str(NAIL_SEQUENCE[i]))
        x += 50

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def main():
    global best_improvement_value, cumilative_improvement
    x1, y1, prev_x, prev_y = IMAGE_RESOLUTION - 1, IMAGE_RESOLUTION // 2 - 1, -1, -1
    fig, ax = plt.subplots(figsize=(8, 8))
    generate_circle_coordinates(ax)

    for i in range(1,ITERATIONS + 1):
        x2, y2 = choose_best_point(x1, y1, prev_x, prev_y)
        ax.plot((x1, x2), (y1, y2), color="black", linewidth=STRING_WIDTH,
                alpha=1)
        NAIL_SEQUENCE.append(nail_no(x2, y2))
        prev_x, prev_y = x1, y1
        x1, y1 = x2, y2
    
    ax.grid(False)
    ax.invert_yaxis()
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    fig.canvas.draw()
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    st.image(image, caption='String Art', use_column_width=True)
    

if __name__ == "__main__":
    st.title("String Art Generator")

    open_image()

    st.sidebar.image("https://yt3.googleusercontent.com/ytc/AIdro_m_FFw3OGZ5SH0U-l_37_HQMQCyqfoL2co8iCBJQgQJ-q4b=s900-c-k-c0x00ffffff-no-rj", use_column_width=True)
    
    st.sidebar.markdown("<p style='font-size:20px; font-weight:bold;'>Center For Creative Learning (CCL), IIT Gandhinagar</p>", unsafe_allow_html=True)

    itr = nls = True
    if st.checkbox("Show Parameters", False):
        itr = update_iterations()
        nls = update_nails()

    if st.button("Generate String Art") and itr and nls:
        if create_art():
            filename = "output_StringArt.pdf"
            pdf_bytes = save_numbers_to_pdf()
            st.download_button(
                label="Download Pdf",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf"
            )

    
