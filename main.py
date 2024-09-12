import streamlit as st 
from streamlit_option_menu import option_menu 
import Single ,Folder 

st.set_page_config(
    page_title="Pondering",
)

class MultiApp:
    def __init__(self):
        self.apps= []

    def add_app(self,title,function):
        self.apps.append({
            "title": title,
            "function" : function
        })
    def run():
        # Radio button selection
        with st.sidebar:
            app = st.radio(
            label="Choose File Selection Method",
            options=["Provide Folder Path", "Upload File"],
            
        )

    # with st.sidebar:
    #     app = option_menu(
    #         menu_title ="Select",
    #         options =["Folder", "Single"],
    #         icons=["folder","file-earmark-arrow-down"],
    #         default_index=0,)
        
        if app == "Upload File":
            with st.spinner("Processing folder..."):
                Single.app()
        if app=="Provide Folder Path":
            Folder.app()
    run()
