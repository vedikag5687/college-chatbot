import streamlit as st
import pandas as pd
from data_loader import load_sheets, save_user_chat_json
from recommender import filter_colleges

st.title("🎓 JEE College Recommendation Bot")

# Introduction
st.markdown("""
### Hello! I can recommend colleges based on your JEE rank.

**Currently supported:** JEE Mains based recommendations
**Coming soon:** JEE Advanced based recommendations

**New Features:**
- ✅ Shows only colleges where Close Rank ≥ Your Rank (you can get admission)
- ✅ College State filter for NITs (Home State: HS quota only, Other State: OS quota only)
- ✅ Results sorted by close rank in ascending order (easiest to get first)
- ✅ Complete chat history saved as JSON in local folder
- ✅ No Google Sheets storage - everything saved locally
""")

# --- Hardcoded Selections ---
gender_options = ["Gender-Neutral", "Female-only (including Supernumerary)"]
category_options = ["SC", "ST", "EWS", "EWS (PwD)", "OBC-NCL", "OBC-NCL (PwD)", "OPEN", "OPEN (PwD)", "SC (PwD)", "ST (PwD)"]
state_options = ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Manipur", "Meghalaya", "Mizoram", "Maharashtra", "Nagaland", "Odisha", "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]

degree_options = [
    "Bachelor of Technology",
    "Bachelor and Master of Technology (Dual Degree)",
    "Integrated Master of Science",
    "Integrated B. Tech. and M. Tech",
    "Bachelor of Architecture",
    "Bachelor of Planning",
    "Bachelor of Science and Master of Science (Dual Degree)",
    "B.Tech. + M.Tech./MS (Dual Degree)",
]

branch_options = [
    "Artificial Intelligence",
    "Aerospace Engineering",
    "Architecture",
    "Architecture and Planning",
    "Artificial Intelligence and Data Engineering",
    "Artificial Intelligence and Data Science",
    "Artificial Intelligence and Machine Learning",
    "B.Tech in Mathematics and Computing",
    "B.Tech in Mechanical Engineering and M.Tech in AI and Robotics",
    "B.Tech. in Electronics and Communication Engineering and M.Tech. in Communication Systems",
    "B.Tech. in Electronics and Communication Engineering and M.Tech. in VLSI Design",
    "Bio Medical Engineering",
    "Bio Technology",
    "Biotechnology",
    "Biotechnology and Biochemical Engineering",
    "Civil Engineering",
    "Ceramic Engineering",
    "Ceramic Engineering and M.Tech Industrial Ceramic",
    "Chemical Engineering",
    "Chemical Technology",
    "Chemistry",
    "Civil Engineering with Specialization in Construction Technology and Management",
    "Computational and Data Science",
    "Computational Mathematics",
    "Computer Science",
    "Computer Science and Artificial Intelligence",
    "Computer Science and Business",
    "Computer Science and Engineering",
    "Computer Science and Engineering (Artificial Intelligence)",
    "Computer Science Engineering (Artificial lntelligence and Machine Learning)",
    "Computer Science Engineering (Data Science and Analytics)",
    "Computer Science and Engineering (Cyber Physical System)",
    "Computer Science and Engineering (Cyber Security)",
    "Computer Science and Engineering (Data Science)",
    "Computer Science and Engineering (with Specialization of Data Science and Artificial Intelligence)",
    "Computer Science Engineering (Human Computer lnteraction and Gaming Technology)",
    "CSE ( Data Science & Analytics)",
    "Data Science and Engineering",
    "Data Science and Artificial Intelligence",
    "Electronics and Communication Engineering",
    "Electrical and Electronics Engineering",
    "Electrical Engineering",
    "Electrical Engineering with Specialization In Power System Engineering",
    "Electronics and Communication Engineering (Internet of Things)",
    "Electronics and Communication Engineering (with Specialization of Embedded Systems and Internet of Things)",
    "Electronics and Communication Engineering with specialization in Design and Manufacturing",
    "Electronics and Communication Engineering (VLSI Design and Technology)",
    "Electronics and Communication Engineering with Specialization in Microelectronics and VLSI System Design",
    "Electronics and Communication Engineering with specialization in VLSI and Embedded Systems",
    "Electronics and Instrumentation Engineering",
    "Electronics and Telecommunication Engineering",
    "Electronics and VLSI Engineering",
    "Engineering and Computational Mechanics",
    "Engineering Physics",
    "Food Process Engineering",
    "Industrial and Production Engineering",
    "Information Technology-Business Informatics",
    "Integrated B. Tech.(IT) and M. Tech (IT)",
    "Integrated B. Tech.(IT) and MBA",
    "Industrial Chemistry",
    "Industrial Design",
    "Industrial Internet of Things",
    "Information Technology",
    "Instrumentation and Control Engineering",
    "Life Science",
    "Material Science and Engineering",
    "Materials Engineering",
    "Materials Science and Engineering",
    "Materials Science and Metallurgical Engineering",
    "Mathematics",
    "Mathematics & Computing",
    "Mathematics and Computing",
    "Mathematics and Computing Technology",
    "Mathematics and Scientific Computing",
    "Mathematics and Data Science",
    "Mechanical Engineering",
    "Mechanical Engineering with Specialization in Manufacturing and Industrial Engineering",
    "Mechanical Engineering with specialization in Design and Manufacturing",
    "Mechatronics and Automation Engineering",
    "Metallurgical and Materials Engineering",
    "Metallurgy and Materials Engineering",
    "Microelectronics & VLSI Engineering",
    "Mining Engineering",
    "Physics",
    "Planning",
    "Production and Industrial Engineering",
    "Production Engineering",
    "ROBOTICS & AUTOMATION",
    "SUSTAINABLE ENERGY TECHNOLOGIES",
    "Smart Manufacturing",
    "Textile Technology",
    "VLSI Design and Technology"
]

# --- UI Inputs ---
st.sidebar.header("Personal Information")
name = st.sidebar.text_input("Enter your Name")
phone = st.sidebar.text_input("Enter your Phone Number")

st.sidebar.header("Your Preferences")

gender = st.sidebar.selectbox("Select your Gender", gender_options)
category = st.sidebar.selectbox("Select your Category", category_options)
state = st.sidebar.selectbox("Select your Home State", state_options)

degrees = st.sidebar.multiselect("Select Preferred Degree(s)", degree_options)
branches = st.sidebar.multiselect("Select Preferred Branch(es)", branch_options)

rank = st.sidebar.number_input("Enter your JEE Mains Rank", min_value=1, value=10000)

# Add info about the filtering logic
st.sidebar.markdown("---")
st.sidebar.info("""
**Updated Filtering Logic:**
- ✅ Shows only colleges where Close Rank ≥ Your Rank
- ✅ Home State colleges: Only HS quota seats
- ✅ Other State colleges: Only OS quota seats
- ✅ Results sorted by close rank (easiest first)
- ✅ Data saved locally as JSON files
""")

if st.sidebar.button("🔍 Get Recommendations"):
    if not name or not phone:
        st.error("❌ Please enter your Name and Phone Number.")
    elif not degrees or not branches:
        st.error("❌ Please select at least one Degree and one Branch.")
    else:
        with st.spinner("📥 Loading and filtering colleges..."):
            try:
                sheets = load_sheets()
                
                # --- NITs with College State & Quota filtering ---
                nits_df = filter_colleges(
                    sheets["nits round 5"],
                    gender,
                    category,
                    rank,
                    degrees,
                    branches,
                    state=state,
                    is_nit=True
                )

                # --- IIITs without state sorting (same logic as NITs but no state filter) ---
                iiits_df = filter_colleges(
                    sheets["iiits round 5"],
                    gender,
                    category,
                    rank,
                    degrees,
                    branches,
                    state=None,  # No state filtering for IIITs
                    is_nit=False
                )

                st.success("✅ Recommendations generated successfully!")
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🟢 NITs")
                    if nits_df.empty:
                        st.warning("No NITs found where you can get admission with your current rank.")
                    else:
                        # Display without index
                        st.dataframe(nits_df, use_container_width=True, hide_index=True)
                        st.info(f"Found {len(nits_df)} NIT options where you can get admission")

                with col2:
                    st.subheader("🟣 IIITs")
                    if iiits_df.empty:
                        st.warning("No IIITs found where you can get admission with your current rank.")
                    else:
                        # Display without index
                        st.dataframe(iiits_df, use_container_width=True, hide_index=True)
                        st.info(f"Found {len(iiits_df)} IIIT options where you can get admission")

                # Prepare user data
                user_data = {
                    'name': name,
                    'phone': phone,
                    'gender': gender,
                    'category': category,
                    'state': state,
                    'degrees': ', '.join(degrees),
                    'branches': ', '.join(branches),
                    'rank': rank,
                    'nit_count': len(nits_df),
                    'iiit_count': len(iiits_df)
                }
                
                # Save complete chat as JSON (removed Google Sheets)
                try:
                    json_filename = save_user_chat_json(user_data, nits_df, iiits_df)
                    st.success(f"✅ Complete chat saved as: {json_filename}")
                except Exception as e:
                    st.warning(f"⚠️ Could not save chat JSON: {e}")
                
                
                
                        
            except Exception as e:
                st.error(f"❌ Error occurred: {str(e)}")
                st.error("Please check your Google Sheets connection and data.")

# Add explanation sectio