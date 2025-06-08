import streamlit as st
import pandas as pd
from data_loader import load_sheets, create_user_csv_report, save_user_data_to_master_csv, get_master_csv_download
from recommender import filter_colleges
import io
from datetime import datetime

st.title("🎓 JEE College Recommendation Bot")

# Introduction
st.markdown("""
### Hello! I can recommend colleges based on your JEE rank.

**Currently supported:** JEE Mains based recommendations
**Coming soon:** JEE Advanced based recommendations

**New Features:**
- 🎯 Smart State-based Quota Filtering (HS for home state, OS for other states)
- 📊 Auto-updating Master Database
- 💾 Individual CSV Downloads
- 📈 Rank-based Sorting
""")

# --- Hardcoded Selections (Keep exactly same as chatbot.py) ---
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
st.sidebar.header("📋 Personal Information")
name = st.sidebar.text_input("Enter your Name")
phone = st.sidebar.text_input("Enter your Phone Number")

st.sidebar.header("🎯 Your Preferences")

gender = st.sidebar.selectbox("Select your Gender", gender_options)
category = st.sidebar.selectbox("Select your Category", category_options)
state = st.sidebar.selectbox("Select your Home State", state_options)

degrees = st.sidebar.multiselect("Select Preferred Degree(s)", degree_options)
branches = st.sidebar.multiselect("Select Preferred Branch(es)", branch_options)

rank = st.sidebar.number_input("Enter your JEE Mains Rank", min_value=1, value=10000)

# Add admin section for downloading master CSV
st.sidebar.markdown("---")
st.sidebar.header("📊 Admin Section")
if st.sidebar.button("📥 Download Master CSV (All Users)"):
    master_csv_content = get_master_csv_download()
    if master_csv_content:
        st.sidebar.download_button(
            label="💾 Download Master Data",
            data=master_csv_content,
            file_name=f"master_user_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        st.sidebar.success("✅ Master CSV ready for download!")
    else:
        st.sidebar.warning("⚠️ No master data available yet.")

if st.sidebar.button("🔍 Get Recommendations"):
    if not name or not phone:
        st.error("❌ Please enter your Name and Phone Number.")
    elif not degrees or not branches:
        st.error("❌ Please select at least one Degree and one Branch.")
    else:
        with st.spinner("📥 Loading and filtering colleges..."):
            try:
                sheets = load_sheets()
                
                # --- NITs with State & Quota prioritization (SAME AS CHATBOT.PY) ---
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

                # --- IIITs without state sorting (SAME AS CHATBOT.PY) ---
                iiits_df = filter_colleges(
                    sheets["iiits round 5"],
                    gender,
                    category,
                    rank,
                    degrees,
                    branches,
                    state=None,  # Explicitly set to None for IIITs
                    is_nit=False
                )

                st.success("✅ Recommendations generated successfully!")
                
                # Display results with enhanced information
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🟢 NITs")
                    if nits_df.empty:
                        st.warning("No NITs found matching your criteria.")
                        st.info("💡 Try adjusting your preferences or rank range.")
                    else:
                        # Add rank difference column for better insight
                        nits_display = nits_df.copy()
                        nits_display['Rank Difference'] = nits_display['close rank'] - rank
                        nits_display['Close Rank'] = nits_display['close rank'].astype(int)
                        nits_display = nits_display[['college name', 'Close Rank', 'Rank Difference']]
                        nits_display.columns = ['College Name', 'Close Rank', 'Rank Difference']
                        
                        st.dataframe(nits_display, use_container_width=True, hide_index=True)
                        st.info(f"Found {len(nits_df)} NIT options")
                        
                        # Show state-based filtering info
                        st.caption(f"🏠 Showing colleges with appropriate quota (HS for {state}, OS for other states)")

                with col2:
                    st.subheader("🟣 IIITs")
                    if iiits_df.empty:
                        st.warning("No IIITs found matching your criteria.")
                        st.info("💡 Try adjusting your preferences or rank range.")
                    else:
                        # Add rank difference column for better insight
                        iiits_display = iiits_df.copy()
                        iiits_display['Rank Difference'] = iiits_display['close rank'] - rank
                        iiits_display['Close Rank'] = iiits_display['close rank'].astype(int)
                        iiits_display = iiits_display[['college name', 'Close Rank', 'Rank Difference']]
                        iiits_display.columns = ['College Name', 'Close Rank', 'Rank Difference']
                        
                        st.dataframe(iiits_display, use_container_width=True, hide_index=True)
                        st.info(f"Found {len(iiits_df)} IIIT options")

                # Prepare user data (SAME AS CHATBOT.PY)
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
                
                # Create CSV reports and update master CSV (SAME AS CHATBOT.PY)
                with st.spinner("📄 Creating your personalized CSV reports..."):
                    try:
                        user_info_df, recommendations_df, report_name = create_user_csv_report(user_data, nits_df, iiits_df)
                        
                        # Save to master CSV and get the updated data (AUTO-UPDATE FEATURE)
                        master_df, master_csv_path = save_user_data_to_master_csv(user_data)
                        
                        st.success("✅ Your personalized reports are ready for download!")
                        
                        if master_df is not None:
                            st.info(f"📊 Your data has been automatically added to the master database (Total users: {len(master_df)})")
                        
                        # Create download buttons
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            # User Information CSV
                            user_csv = user_info_df.to_csv(index=False)
                            st.download_button(
                                label="📋 Download Personal Info",
                                data=user_csv,
                                file_name=f"{report_name}_PersonalInfo.csv",
                                mime="text/csv"
                            )
                        
                        with col2:
                            # Recommendations CSV
                            if not recommendations_df.empty:
                                recommendations_csv = recommendations_df.to_csv(index=False)
                                st.download_button(
                                    label="🏛️ Download Recommendations",
                                    data=recommendations_csv,
                                    file_name=f"{report_name}_Recommendations.csv",
                                    mime="text/csv"
                                )
                            else:
                                st.info("No recommendations to download")
                        
                        with col3:
                            # Combined Report (Excel-like format)
                            if not recommendations_df.empty:
                                # Create a combined CSV with sections
                                combined_data = []
                                combined_data.append("=== PERSONAL INFORMATION ===")
                                combined_data.append(user_info_df.to_csv(index=False))
                                combined_data.append("\n=== COLLEGE RECOMMENDATIONS ===")
                                combined_data.append(recommendations_df.to_csv(index=False))
                                
                                combined_csv = "\n".join(combined_data)
                                st.download_button(
                                    label="📊 Download Complete Report",
                                    data=combined_csv,
                                    file_name=f"{report_name}_CompleteReport.csv",
                                    mime="text/csv"
                                )
                        
                        # Enhanced information section
                        st.markdown(f"""
                        **📊 Your Session Summary:**
                        - 👤 **Name:** {name}
                        - 📱 **Phone:** {phone}
                        - 🎯 **JEE Rank:** {rank:,}
                        - 🟢 **NITs Found:** {len(nits_df)}
                        - 🟣 **IIITs Found:** {len(iiits_df)}
                        - 🏠 **Home State:** {state}
                        - 📅 **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        
                        **📋 Your CSV reports include:**
                        - 📋 **Personal Information:** Your details and preferences
                        - 🏛️ **College Recommendations:** NIT and IIIT suggestions with ranks
                        - 📊 **Complete Report:** Combined file with all information
                        
                        **🔄 Auto-Features:**
                        - ✅ Your data is automatically saved to our master database
                        - ✅ State-based quota filtering applied (HS/OS)
                        - ✅ Results sorted by closing rank (ascending)
                        
                        **💡 Tip:** Open CSV files in Excel or Google Sheets for better formatting!
                        """)
                        
                    except Exception as e:
                        st.error(f"❌ Could not create CSV reports: {e}")
                        st.info("Your recommendations are still available above, but downloads could not be generated.")
                        
            except Exception as e:
                st.error(f"❌ Error occurred: {str(e)}")
                st.error("Please check your data connection and try again.")

# Add enhanced footer information
st.markdown("---")
st.markdown("""
### 📞 Need Help?
Download your CSV reports above and keep them for reference. 
Your data is automatically saved in our system for follow-up support.

**🔧 Technical Features:**
- ✅ **Smart State-based Filtering**: For NITs, we show only relevant quota seats
  - 🏠 **Same State as yours**: Only HS (Home State) quota seats
  - 🌍 **Different States**: Only OS (Other State) quota seats
- ✅ **Auto-updating Master Database**: All user data is automatically saved
- ✅ **Individual Download Reports**: Each user gets personalized CSV files
- ✅ **Intelligent Sorting**: Results sorted by closing rank (best opportunities first)
- ✅ **Rank Difference Analysis**: See how close you are to each college's cutoff

**🎯 Compatibility:**
- ✅ Works perfectly with command-line `chatbot.py`
- ✅ Uses same backend functions and data sources
- ✅ Maintains consistency across both interfaces

**Powered by JEE College Recommendation System v2.0**
""")

# Enhanced debug information
if st.checkbox("🔧 Show Debug Info"):
    st.markdown("### 🔍 Debug Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**User Selections:**")
        st.write("🏠 Selected State:", state)
        st.write("👤 Selected Gender:", gender)
        st.write("🏷️ Selected Category:", category)
        st.write("🎓 Selected Degrees:", degrees)
        st.write("🔬 Selected Branches:", branches)
        st.write("📊 JEE Rank:", rank)
    
    with col2:
        st.write("**System Info:**")
        st.write("📅 Current Time:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        st.write("🔄 Master CSV Auto-update:", "✅ Enabled")
        st.write("🎯 State-based Filtering:", "✅ Enabled")
        st.write("📈 Rank-based Sorting:", "✅ Enabled")
        
    st.write("**Available Options Count:**")
    st.write(f"- Gender Options: {len(gender_options)}")
    st.write(f"- Category Options: {len(category_options)}")
    st.write(f"- State Options: {len(state_options)}")
    st.write(f"- Degree Options: {len(degree_options)}")
    st.write(f"- Branch Options: {len(branch_options)}")