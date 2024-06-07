import streamlit as st

PAGE_TITLE = "STREAMLIT TEMPLATE"


def configure() -> None:
    st.set_page_config(page_title=PAGE_TITLE, page_icon="🔥", layout="centered")
    # ? remove the deploy button
    st.html(r"<style>.stDeployButton {visibility: hidden;}</style>")
