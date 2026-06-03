import streamlit as st
from database import init_db, save_complaint, read_complaints
from ml.predictor import predict_priority

# Initialize DB
init_db()

st.set_page_config(page_title="Smart Complaint Management", layout="wide")

menu = ["Submit Complaint", "Admin Panel"]
choice = st.sidebar.selectbox("Menu", menu)

# ------------------- SUBMIT COMPLAINT PAGE -------------------
if choice == "Submit Complaint":
    st.title("Submit a Complaint: (AI APP)")

    name = st.text_input("Your Name")
    department = st.text_input("Department")
    complaint = st.text_area("Complaint")

    if st.button("Submit Complaint"):
        if not name or not department or not complaint:
            st.error("Please fill all fields")
        else:
            priority_label = predict_priority(complaint)
            save_complaint(name, department, complaint, priority_label)
            st.success(f"Complaint submitted successfully! Priority: {priority_label}")

# ------------------- ADMIN PANEL -------------------
elif choice == "Admin Panel":
    st.title("Admin Panel - Complaints Overview")

    complaints = read_complaints()
    if complaints:
        import pandas as pd

        # Create DataFrame
        df = pd.DataFrame(complaints, columns=["ID", "Name", "Department", "Complaint", "Priority"])

        # Map priority to colors
        def priority_color(val):
            color_map = {
                "Critical": "red",
                "High": "orange",
                "Medium": "yellow",
                "Low": "green"
            }
            color = color_map.get(val, "white")
            return f"background-color: {color}"

        # Style DataFrame
        st.dataframe(df.style.map(priority_color, subset=["Priority"]))
    else:
        st.info("No complaints found.")
