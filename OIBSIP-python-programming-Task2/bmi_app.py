import streamlit as st

# 1. Page Title
st.title("⚖️ Interactive BMI Calculator")
st.write("Enter your details below to see where you stand on the BMI scale.")

# 2. Get User Inputs
# We set min values so the app doesn't crash from dividing by zero!
weight = st.number_input("Enter your Weight (in kg):", min_value=1.0, value=70.0)
height = st.number_input("Enter your Height (in cm):", min_value=50.0, value=170.0)

# 3. The Calculate Button
if st.button("Calculate My BMI"):
    # The math for converting we already know
    height_m = height / 100 
    bmi = weight / (height_m * height_m)
    
    st.write(f"### Your BMI is: {round(bmi, 1)}")
    
    # 4. Logic & Color Coding
    if bmi < 18.5:
        category = "Need to gain weight (Underweight)"
        color = "blue"
    elif bmi < 25.0:
        category = "Normal Weight"
        color = "green"
    elif bmi < 30.0:
        category = "Overweight"
        color = "orange"
    elif bmi < 35.0:
        category = "Obese (Class I)"
        color = "red"
    elif bmi < 40.0:
        category = "Obese (Class II)"
        color = "red"
    else:
        category = "Obese (Class III/Severe)"
        color = "red"
        
    # Display the colored category
    st.subheader(f"Category: :{color}[{category}]")
    
    # 5. The Visual Meter
    # Streamlit progress bars need a value between 0.0 and 1.0.
    # If we assume 50 is the "max" normal end of the BMI scale, we divide bmi by 50.
    # We use min() to ensure if someone's BMI is over 50, it caps at 1.0 so the app doesn't crash.
    progress_value = min(bmi / 50.0, 1.0)
    
    st.write("Visual Scale (0 to 50+):")
    st.progress(progress_value)

    # To Run the program : streamlit run OIBSIP-python-programming-Task2/bmi_app.py , if you fork this Repo then same as this command else " streamlit run bmi_app.py" 