from data_loader import load_sheets
from recommender import filter_colleges

def run_bot():
    print("👋 Hello! I can recommend colleges based on your JEE rank.")
    print("Which exam would you like suggestions for?")
    print("1. JEE Mains")
    print("2. JEE Advanced")
    
    mode = input("Enter 1 or 2: ").strip()

    if mode != "1":
        print("Currently, only JEE Mains-based recommendations are supported.")
        return

    # --- Hardcoded Options ---
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

    # --- User Inputs ---
    print("\nSelect your Gender:")
    for i, g in enumerate(gender_options, 1):
        print(f"{i}. {g}")
    try:
        gender_choice = int(input("Enter choice (1 or 2): "))
        gender = gender_options[gender_choice - 1]
    except (ValueError, IndexError):
        print("Invalid choice. Please restart.")
        return

    print("\nSelect your Category:")
    for i, c in enumerate(category_options, 1):
        print(f"{i}. {c}")
    try:
        category_choice = int(input(f"Enter choice (1 to {len(category_options)}): "))
        category = category_options[category_choice - 1]
    except (ValueError, IndexError):
        print("Invalid choice. Please restart.")
        return

    print("\nSelect your Home State:")
    for i, s in enumerate(state_options, 1):
        print(f"{i}. {s}")
    try:
        state_choice = int(input(f"Enter choice (1 to {len(state_options)}): "))
        state = state_options[state_choice - 1]
    except (ValueError, IndexError):
        print("Invalid choice. Please restart.")
        return

    print("\nSelect one or more Degrees (comma-separated index):")
    for i, d in enumerate(degree_options, 1):
        print(f"{i}. {d}")
    try:
        degree_indices = input("Enter choices (e.g. 1,3): ").split(",")
        degrees = [degree_options[int(i.strip()) - 1] for i in degree_indices]
    except (ValueError, IndexError):
        print("Invalid degree selection. Please restart.")
        return

    print("\nSelect one or more Branches (comma-separated index):")
    for i, b in enumerate(branch_options, 1):
        print(f"{i}. {b}")
    try:
        branch_indices = input("Enter choices (e.g. 1,4): ").split(",")
        branches = [branch_options[int(i.strip()) - 1] for i in branch_indices]
    except (ValueError, IndexError):
        print("Invalid branch selection. Please restart.")
        return

    try:
        rank = int(input("\nEnter your JEE Mains rank: "))
    except ValueError:
        print("Invalid rank. Please enter a valid number.")
        return

    print("\n📥 Loading college data...")
    try:
        sheets = load_sheets()
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    print("\n🔍 Filtering colleges based on your preferences...")
    
    # Filter NITs
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

    # Filter IIITs
    iiits_df = filter_colleges(
        sheets["iiits round 5"], 
        gender, 
        category, 
        rank, 
        degrees, 
        branches
    )

    print("\n🎯 College Recommendations Based on JEE Mains Rank:\n")

    print("🟢 NITs ===")
    if nits_df.empty:
        print("No NITs found matching your criteria.")
    else:
        print(nits_df.to_string(index=False))

    print("\n🟣 IIITs ===")
    if iiits_df.empty:
        print("No IIITs found matching your criteria.")
    else:
        print(iiits_df.to_string(index=False))

if __name__ == "__main__":
    run_bot()