from data_loader import load_sheets, save_user_data_to_master_csv
from recommender import filter_colleges
import pandas as pd
from datetime import datetime

def get_user_input(prompt, options=None):
    """Helper function to get user input with validation"""
    while True:
        if options:
            print("\nOptions:")
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            
            try:
                choice = input(f"{prompt} (Enter number): ").strip()
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(options):
                    return options[choice_idx]
                else:
                    print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("Please enter a valid number")
        else:
            result = input(f"{prompt}: ").strip()
            if result:
                return result
            print("This field cannot be empty. Please try again.")

def get_multiple_choice(prompt, options):
    """Helper function to get multiple selections from user"""
    print(f"\n{prompt}")
    print("Options:")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    while True:
        try:
            choices = input("\nEnter your choices (comma-separated numbers, e.g., 1,3,5): ").strip()
            if not choices:
                print("Please select at least one option.")
                continue
                
            choice_indices = [int(x.strip()) - 1 for x in choices.split(',')]
            selected_options = []
            
            for idx in choice_indices:
                if 0 <= idx < len(options):
                    selected_options.append(options[idx])
                else:
                    print(f"Invalid choice: {idx + 1}. Please try again.")
                    break
            else:
                return selected_options
                
        except ValueError:
            print("Please enter valid numbers separated by commas.")

def display_results(nits_df, iiits_df, user_data):
    """Display the filtered results"""
    print("\n" + "="*80)
    print("🎯 COLLEGE RECOMMENDATIONS")
    print("="*80)
    
    # Display NITs
    print("\n🟢 NITs (National Institutes of Technology)")
    print("-" * 50)
    if nits_df.empty:
        print("❌ No NITs found matching your criteria.")
    else:
        print(f"✅ Found {len(nits_df)} NIT options:")
        print(f"{'S.No.':<5} {'College Name':<50} {'Close Rank':<10}")
        print("-" * 70)
        for idx, (_, row) in enumerate(nits_df.iterrows(), 1):
            print(f"{idx:<5} {row['college name'][:47]:<50} {int(row['close rank']):<10}")
    
    # Display IIITs
    print("\n🟣 IIITs (Indian Institutes of Information Technology)")
    print("-" * 50)
    if iiits_df.empty:
        print("❌ No IIITs found matching your criteria.")
    else:
        print(f"✅ Found {len(iiits_df)} IIIT options:")
        print(f"{'S.No.':<5} {'College Name':<50} {'Close Rank':<10}")
        print("-" * 70)
        for idx, (_, row) in enumerate(iiits_df.iterrows(), 1):
            print(f"{idx:<5} {row['college name'][:47]:<50} {int(row['close rank']):<10}")

def run_bot():
    print("="*80)
    print("🎓 JEE COLLEGE RECOMMENDATION BOT")
    print("="*80)
    print("👋 Hello! I can recommend colleges based on your JEE rank.")
    print("\nWhich exam would you like suggestions for?")
    print("1. JEE Mains")
    print("2. JEE Advanced")
    
    mode = input("\nEnter 1 or 2: ").strip()

    if mode != "1":
        print("\n❌ Currently, only JEE Mains-based recommendations are supported.")
        print("🔜 JEE Advanced recommendations coming soon!")
        return

    print("\n✅ JEE Mains mode selected!")
    
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

    # Collect user information
    print("\n📋 PERSONAL INFORMATION")
    print("-" * 30)
    name = get_user_input("Enter your Name")
    phone = get_user_input("Enter your Phone Number")
    
    print("\n🎯 PREFERENCES")
    print("-" * 20)
    gender = get_user_input("Select your Gender", gender_options)
    category = get_user_input("Select your Category", category_options)
    state = get_user_input("Select your Home State", state_options)
    
    degrees = get_multiple_choice("Select your Preferred Degree(s)", degree_options)
    branches = get_multiple_choice("Select your Preferred Branch(es)", branch_options)
    
    # Get JEE rank
    while True:
        try:
            rank = int(input("\nEnter your JEE Mains Rank: ").strip())
            if rank > 0:
                break
            else:
                print("Rank must be a positive number.")
        except ValueError:
            print("Please enter a valid number for rank.")

    # Load data and get recommendations
    print("\n🔄 Loading college data...")
    try:
        sheets = load_sheets()
        print("✅ Data loaded successfully!")
        
        print("\n🔍 Filtering colleges based on your preferences...")
        
        # Filter NITs with state-based quota filtering
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

        # Filter IIITs (no state-based filtering)
        iiits_df = filter_colleges(
            sheets["iiits round 5"],
            gender,
            category,
            rank,
            degrees,
            branches,
            state=None,
            is_nit=False
        )

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

        # Display results
        display_results(nits_df, iiits_df, user_data)
        
        # Silently save to master CSV (no user notification)
        try:
            save_user_data_to_master_csv(user_data)
        except Exception:
            pass  # Silently ignore errors in data saving
        
        # Summary
        print("\n" + "="*80)
        print("📊 SUMMARY")
        print("="*80)
        print(f"👤 Name: {name}")
        print(f"🎯 JEE Mains Rank: {rank}")
        print(f"🟢 NITs Found: {len(nits_df)}")
        print(f"🟣 IIITs Found: {len(iiits_df)}")
        print(f"📅 Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n✅ Recommendation process completed!")
        print("Thank you for using our recommendation system!")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print("Please check your data connection and try again.")

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n\n👋 Thank you for using JEE College Recommendation Bot!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("Please restart the application.")