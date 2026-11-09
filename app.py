"""
Portfolio Weight Checker
========================
Enter your holdings (or upload a CSV), and the app shows what percentage of
the portfolio is in each asset class.

Weight of an asset class = (value in that class) / (total portfolio value)
"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Portfolio Weight Checker")
st.title("Portfolio Weight Checker")
st.write("Enter each holding's asset class and market value to see how your portfolio is split.")

# ---- 1. Starting example data (users can edit, add, or delete rows) ----
example = pd.DataFrame({
    "Holding": ["VTI", "VXUS", "BND", "VNQ", "Cash"],
    "Asset Class": ["US Stocks", "International Stocks", "Bonds", "Real Estate", "Cash"],
    "Market Value": [50000.0, 20000.0, 20000.0, 5000.0, 5000.0],
})

# ---- 2. Optional CSV upload (columns: Holding, Asset Class, Market Value) ----
uploaded = st.file_uploader("Optional: upload a CSV with columns Holding, Asset Class, Market Value",
                            type="csv")
if uploaded is not None:
    data = pd.read_csv(uploaded)
    missing = [c for c in ["Holding", "Asset Class", "Market Value"] if c not in data.columns]
    if missing:
        st.error(f"Your CSV is missing these columns: {', '.join(missing)}")
        st.stop()
    data = data[["Holding", "Asset Class", "Market Value"]]
else:
    data = example

# ---- 3. Editable table of holdings ----
st.subheader("Holdings")
holdings = st.data_editor(data, num_rows="dynamic", width="stretch")

# ---- 4. Check the inputs ----
holdings = holdings.dropna(how="all")  # ignore fully empty rows
holdings["Market Value"] = pd.to_numeric(holdings["Market Value"], errors="coerce")

if holdings["Market Value"].isna().any():
    st.error("Every holding needs a market value, and it must be a number.")
    st.stop()
if (holdings["Market Value"] < 0).any():
    st.error("Market values can't be negative.")
    st.stop()
if holdings["Asset Class"].isna().any() or (holdings["Asset Class"].astype(str).str.strip() == "").any():
    st.error("Every holding needs an asset class.")
    st.stop()

total = holdings["Market Value"].sum()
if total == 0:
    st.error("The portfolio total is $0. Enter at least one market value.")
    st.stop()

# ---- 5. Calculate weights by asset class ----
holdings["Asset Class"] = holdings["Asset Class"].astype(str).str.strip()
by_class = (
    holdings.groupby("Asset Class", as_index=False)["Market Value"].sum()
    .sort_values("Market Value", ascending=False)
)
by_class["Weight (%)"] = by_class["Market Value"] / total * 100

# ---- 6. Show the results ----
st.subheader("Weight by asset class")
st.metric("Total portfolio value", f"${total:,.2f}")
st.dataframe(
    by_class.style.format({"Market Value": "${:,.2f}", "Weight (%)": "{:.1f}%"}),
    hide_index=True,
    width="stretch",
)
st.bar_chart(by_class, x="Asset Class", y="Weight (%)")

# Check: the weights should always add to 100%
weight_sum = by_class["Weight (%)"].sum()
if abs(weight_sum - 100) < 0.01:
    st.success(f"Check passed: weights add up to {weight_sum:.1f}%.")
else:
    st.error(f"Check failed: weights add up to {weight_sum:.2f}%, not 100%.")
