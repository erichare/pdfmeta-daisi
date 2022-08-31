import streamlit as st
import pydaisi as pyd
import os
import io

metadata_extraction = pyd.Daisi("laiglejm/GPT 3 PDF metadata extraction")
text_cleaning = pyd.Daisi("laiglejm/GPT 3 Text Cleaning")
bib_refs = pyd.Daisi("laiglejm/GPT 3 Extract Bibliographical Refs")
pdf_plumbing = pyd.Daisi("erichare/PDF Plumber")

os.environ["OPENAI_KEY"] = "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"
openai_api_key = os.environ["OPENAI_KEY"]

def st_ui():
    st.set_page_config(layout = "wide")
    st.title("PDF Processing Pipeline")

    st.write("Daisies are the ideal tool for an end-to-end pipeline, starting from a raw PDF, to all the features that can be extracted, including images, tables, authors, titles, and more. Try it out!")
    with st.sidebar:
        uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])
    
    if uploaded_file is not None:
        pdfbytes = uploaded_file.getvalue()
    else:
        st.text("Using example.pdf for illustration")
        with open("example.pdf", 'rb') as f:
            pdfbytes = f.read()


    # Get the data
    with st.spinner("Plumbing your PDF..."):
        pdf = pdf_plumbing.plumb(pdfbytes).value

    # Author / title metadata 
    with st.spinner("Extracting Metadata..."):        
        met_dat = metadata_extraction.get_metadata(pdfbytes, openai_api_key, nb_chars=2000, max_response_tokens=500).value

        st.markdown("## PDF Metadata")
        st.write(met_dat)

    # Cleaned text
    with st.spinner("Cleaning text..."):
        raw_text = "\n\n".join([x.extract_text() for x in pdf.pages])
        cleaned_text = text_cleaning.clean_text(raw_text, openai_api_key, prompt_type="Scientific", nb_chars=10000, max_response_tokens=1000).value

        st.markdown("## Cleaned Text")
        st.write(cleaned_text)

    # References
    with st.spinner("Extracting references..."):
        refs = bib_refs.extract_biblio(cleaned_text, openai_api_key, nb_chars=10000, max_response_tokens=2000).value

        st.markdown("## References")
        st.write(refs)

    # Tables
    with st.spinner("Extracting tables..."):
        raw_tables = [x.extract_tables() for x in pdf.pages]
        st.markdown("## Tables")
        for table in raw_tables:
            st.dataframe(table)

    # Page Images
    with st.spinner("Extracting images..."):
        raw_images = [x.to_image() for x in pdf.pages]
        st.markdown("## Images")
        for img in raw_images:
            with io.BytesIO() as output:
                img.save(output, format="PNG")
                contents = output.getvalue()

                st.image(contents)

if __name__ == "__main__":
    st_ui()