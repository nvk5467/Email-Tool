import streamlit as st
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from openai import OpenAI

# -----------------------------
# Load API Keys
# -----------------------------
def load_keys():
    load_dotenv()

    # Get keys
    openai_key = os.getenv("OPENAI_API_KEY")
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    return openai_key, sendgrid_key

# -----------------------------
# Helper: Get OpenAI Response
# -----------------------------
def get_openai_response(messages):
    """Fetches a response from OpenAI using the API key from .env."""
    # Load keys from your helper
    openai_key, _ = load_keys()

    if not openai_key:
        st.sidebar.error("Missing OPENAI_API_KEY in .env file.")
        return "Error: No OpenAI API key found."

    # Create a client with the key
    client = OpenAI(api_key=openai_key)

    # Send chat completion request
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        st.sidebar.error(f"OpenAI request failed: {e}")
        return "Error: Failed to contact OpenAI."

# -----------------------------
# Core Email Tool
# -----------------------------
def email_tool(crm_df: pd.DataFrame):
    company_select = st.selectbox("Select a Company to send", crm_df["Company Name"])
    current_company = crm_df[crm_df["Company Name"] == company_select].iloc[0]
    company_name = current_company["Company Name"]
    email_select = current_company["Email"]
    investment_interests = current_company["Investment Interests"]

    if st.button("Generate Email"):
        with st.spinner("Generating AI email..."):
            prompt = (
                f"Write a short, friendly, and professional cold email introducing our company to {company_name}. "
                f"The company is interested in {investment_interests}. "
                f"Address the recipient as their team. "
                f"Keep it under 150 words, tone warm but professional, and focus on potential collaboration."
            )

            messages = [
                {"role": "system", "content": "You are a skilled business email writer."},
                {"role": "user", "content": prompt}
            ]

            email_text = get_openai_response(messages)

            # Store generated email
            st.session_state.generated_email = email_text
    
    if "generated_email" in st.session_state:
            st.write("### ✉️ Generated Email Draft: ", st.session_state.generated_email)
    if st.button("Send Email"):
        st.write(f"Sending email to {email_select}")

    return

    

    if st.button("Send Email"):
        st.write(f"Sending email to {email_select}")

    return


# -----------------------------
# Streamlit App Entry
# -----------------------------
def main():
    st.title("📨 AI Email Generator Test App")

    # Try to load CRM
    try:
        crm_df = pd.read_csv("crm_data.csv")
    except Exception as e:
        st.warning(f"⚠️ Could not read crm_data.csv ({e}). Creating a sample one...")
        sample_data = {
            "Company Name": [
                "Asymmetrica Ventures",
                "Blue Horizon Capital",
                "InnovateX Labs",
                "SummitPoint Partners",
                "Orion Edge Group"
            ],
            "Email": [
                "nikhilkhattar2004@gmail.com",
                "founder@bluehorizoncap.com",
                "ceo@innovatex.com",
                "contact@summitpoint.com",
                "info@orionedgegroup.com"
            ],
            "Investment Interests": [
                "FinTech and AI",
                "ClimateTech and Sustainability",
                "HealthTech and AI",
                "Clean Energy and Infrastructure",
                "Blockchain and Web3"
            ],
            "Contact Names": [
                "Nikhil Khattar",
                "Emily Parker",
                "Robert Lane",
                "Ava Chen",
                "Ethan Reed"
            ],
            "Page Type": [
                "Company Website",
                "LinkedIn Page",
                "Company Website",
                "Portfolio Page",
                "Company Website"
            ],
        }
        crm_df = pd.DataFrame(sample_data)
        crm_df.to_csv("crm_data.csv", index=False)
        st.success("✅ Created new sample crm_data.csv file.")

    st.write("### CRM Data Preview")
    st.dataframe(crm_df)

    if st.button("🚀 Launch Email Tool"):
        # Store state flag so UI doesn’t disappear on rerun
        st.session_state.launch_tool = True

    # --- Keep tool visible after launch ---
    if "launch_tool" in st.session_state and st.session_state.launch_tool:
        email_tool(crm_df)
    else:
        st.info("Click the button above to open the AI Email Generator & Sender.")


if __name__ == "__main__":
    main()
