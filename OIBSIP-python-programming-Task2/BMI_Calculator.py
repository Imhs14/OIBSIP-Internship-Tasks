def bmi_calculator(weight,Height):
    Height = Height/100
    bmi = (weight)/(Height*Height) 
    return bmi
    
if __name__ == '__main__':
    weight  = float(input("Enter your Weight: "))
    Height = float(input("Enter your Height: "))
    bmi_res = bmi_calculator(weight,Height)
    print(f"Your BMI is :{round(bmi_res, 1)}")

if bmi_res < 18.5:
        print('Need to gain weight (Underweight)')
elif bmi_res < 25.0:
    print("Normal Weight")
elif bmi_res < 30.0:
    print("Overweight")
elif bmi_res < 35.0:
    print("Obese (Class I)")
elif bmi_res < 40.0:
    print("Obese (Class II)")
else:
    print("Obese (Class III/Severe)")