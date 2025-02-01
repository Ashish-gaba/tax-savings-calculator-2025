import streamlit as st
import pandas as pd
import time
import plotly.express as px

# App title
st.title("💰 Tax Savings Calculator (Budget 2024-25 vs. Budget 2025-26)")
st.subheader("Find out how much tax you save under the new budget for FY 2025-26! 🚀")

# Custom CSS for button styling (outline buttons)
st.markdown(
    """
    <style>
        div.stButton > button {
            border-radius: 10px !important;
            font-size: 18px !important;
            font-weight: bold !important;
            padding: 10px 24px !important;
            border: 2px solid !important;
            background-color: transparent !important;
            transition: background-color 0.3s ease, color 0.3s ease;
        }

        /* Target the first button in a row (Calculate Tax Savings) */
        div.stButton button:has-text("📊 Calculate Tax Savings") {
            border-color: #4CAF50 !important;
            color: #4CAF50 !important;
        }
        div.stButton button:has-text("📊 Calculate Tax Savings"):hover {
            background-color: #4CAF50 !important;
            color: white !important;
        }

        /* Target the second button in a row (Reset) */
        div.stButton button:has-text("🔄 Reset") {
            border-color: #FF5733 !important;
            color: #FF5733 !important;
        }
        div.stButton button:has-text("🔄 Reset"):hover {
            background-color: #FF5733 !important;
            color: white !important;
        }

        .stDataFrame {
            border-radius: 10px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# Function to format numbers with Indian commas dynamically
def format_indian_currency(value):
    try:
        # Convert value to float and round to 2 decimal places
        value = round(float(value), 2)
        value_int = int(value)
        decimal_part = f"{value:.2f}".split(".")[1]  # Extract two decimal places

        # Convert integer part to string for manual formatting
        value_str = str(value_int)
        
        # If the number is less than 1000, return it as is
        if len(value_str) <= 3:
            formatted_value = value_str
        else:
            # Split last 3 digits (hundreds)
            last_three = value_str[-3:]
            remaining = value_str[:-3]

            # Insert commas every two digits from the right in the remaining part
            formatted_remaining = ""
            while len(remaining) > 2:
                formatted_remaining = "," + remaining[-2:] + formatted_remaining
                remaining = remaining[:-2]

            # Combine formatted parts
            formatted_value = remaining + formatted_remaining + "," + last_three if remaining else last_three

        # Append decimal part only if it's non-zero
        if int(decimal_part) > 0:
            formatted_value += "." + decimal_part

        return f"₹{formatted_value}"
    except ValueError:
        return "Invalid Input"




# def format_indian_currency(value):
#     return f"₹{value:,.0f}".replace(",", "X").replace("X", ",")

# Function to calculate tax based on slabs
def calculate_tax_2024_25(income):
    tax = 0
    slabs = [
        (300000, 0.00),
        (100000, 0.05),
        (300000, 0.05),
        (100000, 0.10),
        (200000, 0.10),
        (200000, 0.15),
        (300000, 0.20),
        (100000, 0.30),
        (400000, 0.30),
        (400000, 0.30),
        (float("inf"), 0.30),
    ]
    tax_free_limit = 700000  # After standard deduction

    if income <= tax_free_limit:
        return 0

    taxable_income = income - 50000  # Standard deduction
    for slab, rate in slabs:
        if taxable_income > slab:
            tax += slab * rate
            taxable_income -= slab
        else:
            tax += taxable_income * rate
            break

    return round(tax, 2)


def calculate_tax_2025_26(income):
    tax = 0
    slabs = [
        (400000, 0.00),
        (400000, 0.05),
        (400000, 0.10),
        (400000, 0.15),
        (400000, 0.20),
        (400000, 0.25),
        (float("inf"), 0.30),
    ]
    tax_free_limit = 1200000  # After standard deduction

    if income <= tax_free_limit:
        return 0

    taxable_income = income - 75000  # Standard deduction
    for slab, rate in slabs:
        if taxable_income > slab:
            tax += slab * rate
            taxable_income -= slab
        else:
            tax += taxable_income * rate
            break

    return round(tax, 2)

# Initialize session state for income input
if "formatted_income" not in st.session_state:
    st.session_state["formatted_income"] = "0"

# Function to update formatted income dynamically
def update_income():
    try:
        raw_value = st.session_state["income_input"].replace(",", "").replace("₹", "")
        if raw_value.isdigit():
            st.session_state["formatted_income"] = format_indian_currency(int(raw_value))
        else:
            st.session_state["formatted_income"] = "0"
    except ValueError:
        st.session_state["formatted_income"] = "0"

# User input for annual income (Live formatted input)
st.text_input(
    "Enter Your Annual Income (₹):",
    key="income_input",
    on_change=update_income,
)

st.markdown(f"**Annual Income: {st.session_state['formatted_income']}**")

# Convert formatted income back to integer for calculation
income = int(st.session_state["formatted_income"].replace("₹", "").replace(",", ""))

# Calculate and display results
col1, col2 = st.columns([1, 1])
with col1:
    calculate = st.button("📊 Calculate Tax Savings")
with col2:
    reset = st.button("🔄 Reset")

def get_tax_bracket_2024_25(income):
    brackets = [
        (0, 300000, "₹0 - ₹3 lakh (Nil)"),
        (300000, 500000, "₹3 - ₹5 lakh (5%)"),
        (500000, 1000000, "₹5 - ₹10 lakh (10%)"),
        (1000000, 1250000, "₹10 - ₹12.5 lakh (15%)"),
        (1250000, 1500000, "₹12.5 - ₹15 lakh (20%)"),
        (1500000, float("inf"), "Above ₹15 lakh (30%)"),
    ]
    for lower, upper, label in brackets:
        if lower <= income <= upper:
            return label
    return "Unknown"

def get_tax_bracket_2025_26(income):
    brackets = [
        (0, 400000, "₹0 - ₹4 lakh (Nil)"),
        (400000, 800000, "₹4 - ₹8 lakh (5%)"),
        (800000, 1200000, "₹8 - ₹12 lakh (10%)"),
        (1200000, 1600000, "₹12 - ₹16 lakh (15%)"),
        (1600000, 2000000, "₹16 - ₹20 lakh (20%)"),
        (2000000, 2400000, "₹20 - ₹24 lakh (25%)"),
        (2400000, float("inf"), "Above ₹24 lakh (30%)"),
    ]
    for lower, upper, label in brackets:
        if lower <= income <= upper:
            return label
    return "Unknown"
    

if calculate:
    tax_2024 = calculate_tax_2024_25(income)
    tax_2025 = calculate_tax_2025_26(income)
    savings = tax_2024 - tax_2025
    bracket_2024 = get_tax_bracket_2024_25(income)
    bracket_2025 = get_tax_bracket_2025_26(income)

    # Create a DataFrame for the comparison table
       # **Create DataFrame for Comparison Table**
    df = pd.DataFrame({
        "Category": ["Annual Income", "Tax Bracket", "Tax Under Budget 2024-25", "Tax Under Budget 2025-26", "Tax Savings"],
        "Budget 2024-25 (₹)": [
            format_indian_currency(income),
            bracket_2024,
            format_indian_currency(tax_2024),
            "-",
            "-"
        ],
        "Budget 2025-26 (₹)": [
            format_indian_currency(income),
            bracket_2025,
            "-",
            format_indian_currency(tax_2025),
            format_indian_currency(savings)
        ],
    })

    # Display Comparison Table
    st.write("### 📊 Tax Comparison Table")
    st.dataframe(df)

    
    # Display result message
    if savings > 0:
        st.balloons()
        # **Bar Chart (Tax Comparison)**
        df_plot = pd.DataFrame({
            "Category": ["Tax Under 2024-25", "Tax Under 2025-26", "Tax Savings"],
            "Amount": [tax_2024, tax_2025, savings]
        })

        fig1 = px.bar(
            df_plot, x="Category", y="Amount",
            text="Amount",
            labels={"Amount": "Tax Amount (₹)"},
            title="Tax Comparison: Budget 2024-25 vs. Budget 2025-26",
            color="Category",
            color_discrete_map={"Tax Under 2024-25": "#FF5733", "Tax Under 2025-26": "#4CAF50", "Tax Savings": "#FFD700"}
        )
        fig1.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig1.update_layout(yaxis=dict(title="Tax Amount (₹)"))

        st.plotly_chart(fig1, use_container_width=True)

        # **Pie Chart (Tax Savings)**
        pie_data = pd.DataFrame({
            "Category": ["Tax Under 2024-25", "Tax Savings"],
            "Amount": [tax_2024, savings]
        })
        fig2 = px.pie(
            pie_data, names="Category", values="Amount",
            title="Tax Savings Proportion",
            hole=0.4,
            color="Category",
            color_discrete_map={"Tax Under 2024-25": "#FF5733", "Tax Savings": "#4CAF50"}
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.write("### 💸 Summary")

        st.success(f"📊 Tax under Budget 2024-25 : {format_indian_currency(tax_2024)}")
        st.success(f"📊 Tax under Budget 2025-26: {format_indian_currency(tax_2025)}")
        st.success(f"🎉 YAYY!! You Save: {format_indian_currency(savings)}  🎉😍")

        # Simulate a delay before showing the funny GIF
        time.sleep(1)

        col1, col2 = st.columns(2)
        with col1:
            st.image("https://media1.tenor.com/m/gr5jdQC2CDkAAAAd/nirmala-sitharaman-shy-woman.gif", width=300)
        with col2:
            st.image("https://media1.tenor.com/m/UHTTVFbzDb4AAAAd/modiji-bhangra.gif", width=300)
    else:
        st.write("### 💸 Summary")

        st.success(f"📊 Tax under Budget 2024-25 : {format_indian_currency(tax_2024)}")
        st.success(f"📊 Tax under Budget 2025-26: {format_indian_currency(tax_2025)}")
        
        st.warning("⚠️ AWW Shucks!!! No tax savings for you under the new regime 😓")
    
        # Simulate a delay before showing the funny GIF
        time.sleep(1)

        # Display a funny GIF instead of a sad one
        st.image("https://media1.tenor.com/m/QOkWoZH3PbIAAAAC/vicky-kaushal-masaan.gif", width=300)

if reset:
    for key in st.session_state.keys():
        del st.session_state[key]  # Delete all session state variables
    st.rerun()  # Rerun the script to apply changes

# Educational Section
# Expanding with tax slab comparison

# Tax Slab Comparison
with st.expander("⚖️ Tax Slab Comparison: New Regime"):
    st.markdown("""
    ### Income Tax Slabs for FY 2025-26 vs FY 2024-25

    | **Income Range (₹)** | **FY 2025-26 Tax Rate** | **FY 2024-25 Tax Rate** |
    |--------------------|---------------------|-----------------------|
    | 0 - 4 lakh         | **Nil**             | Nil (up to 3L)        |
    | 4 - 8 lakh         | **5%**              | 5% (3L - 7L)          |
    | 8 - 12 lakh        | **10%**             | 10% (7L - 10L)        |
    | 12 - 16 lakh       | **15%**             | 15% (10L - 12L)       |
    | 16 - 20 lakh       | **20%**             | 20% (12L - 15L)       |
    | 20 - 24 lakh       | **25%**             | 30% (above 15L)       |
    | Above 24 lakh      | **30%**             | 30%                   |
    """)

# Key Budget Changes
with st.expander("📢 Key Changes in Budget 2025 vs 2024"):
    st.markdown("""
    ### 🔹 Major Tax Reforms:
    - **No Income Tax for incomes upto ₹12 lakh** after rebates! 💸
    - **Basic Tax Exemption Increased:** ₹4 lakh (vs ₹3 lakh earlier)  
    - **Lower Tax for Middle Class:**
      - **5% tax up to ₹8 lakh** (vs ₹7 lakh earlier)  
      - **New 10% slab for ₹8-12 lakh** (previously 20-30%)  
      - **Progressive slabs:** 15%, 20%, 25% for ₹12-24 lakh  

    ### 💰 Additional Benefits:
    - **Rebate Limit Increased:** ₹12 lakh (vs ₹7 lakh earlier)  
    - **Standard Deduction:** Now part of the new tax regime  
    - **Middle-Class Boost:** Higher savings & simplified tax filing  

    ### 📈 Economic Impact:
    - **More Disposable Income → Higher Spending**  
    - **Govt Revenue Considerations → Fiscal Deficit Watch**  
    """)


# Footer
st.markdown(
    """
    *Developed with ❤️ using [Streamlit](https://streamlit.io/)*
    """
)