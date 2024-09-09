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
            label="Select",
            options=["Folder", "Single"],
            
        )

       # with st.sidebar:
       #     app = option_menu(
       #         menu_title ="Select",
       #         options =["Folder", "Single"],
       #         icons=["folder","file-earmark-arrow-down"],
       #         default_index=0,)
        
        if app == "Single":
            Single.app()
        if app=="Folder":
            Folder.app()
    run()
