import os
import tempfile
from pdf2image import convert_from_path
from PIL import Image
from docx import Document
from fpdf import FPDF
import streamlit as st


def docx_to_pdf(docx_path, pdf_path):
    """Convert DOCX → PDF (basic formatting)."""
    doc = Document(docx_path)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for para in doc.paragraphs:
        text = para.text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, text)
    pdf.output(pdf_path)


def pdf_to_images(pdf_path, output_folder):
    images = convert_from_path(pdf_path, dpi=300)
    image_paths = []
    for i, img in enumerate(images):
        img_path = os.path.join(output_folder, f"page_{i + 1}.jpg")
        img.save(img_path, "JPEG")
        image_paths.append(img_path)
    return image_paths


def images_to_pdf(image_paths, output_pdf):
    image_list = [Image.open(img).convert("RGB") for img in image_paths]
    first_image = image_list[0]
    if len(image_list) > 1:
        first_image.save(output_pdf, save_all=True, append_images=image_list[1:])
    else:
        first_image.save(output_pdf)
    return output_pdf



st.set_page_config(page_title="PDF & DOCX Flattener", page_icon="📄", layout="centered")

st.title("📄 Document Flattener")
st.write(
    """
    Upload a **.pdf** or **.docx** file to flatten it into a non-selectable image-based PDF.  
    This ensures that text, signatures, and stamps cannot be extracted or edited.
    """
)

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])

if uploaded_file is not None:
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        working_pdf = os.path.join(tmpdir, "converted.pdf")

        with st.spinner("Processing your file..."):
            if file_ext == ".docx":
                docx_to_pdf(file_path, working_pdf)
            elif file_ext == ".pdf":
                working_pdf = file_path
            else:
                st.error("Unsupported file format.")
                st.stop()

            # Convert PDF → JPGs
            image_paths = pdf_to_images(working_pdf, tmpdir)
            # Merge JPGs → Flattened PDF
            output_pdf = os.path.join(tmpdir, "flattened.pdf")
            images_to_pdf(image_paths, output_pdf)

        st.success("✅ File flattened successfully!")

        with open(output_pdf, "rb") as f:
            st.download_button(
                label="⬇️ Download Flattened PDF",
                data=f,
                file_name="flattened.pdf",
                mime="application/pdf"
            )

st.markdown("---")
st.caption("© 2025 Document Flattener | Built by Moksh ")
