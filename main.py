import streamlit as st
import pandas as pd
import hashlib
import pickle
import os
import base64
from PIL import Image
import matplotlib.pyplot as plt
import PyPDF2

# ----------- SETTINGS: YOU CAN CHANGE THESE COLORS ----------- #
PRIMARY_COLOR = "#245bff"
BG_GRAD = "linear-gradient(120deg, #eaf6fb 0%, #b0e4fd 100%)"
CARD_BG = "#fff"
HEADER_COLOR = "#245bff"
SUBHEADER_COLOR = "#1567a7"
SUCCESS_COLOR = "#2fc47e"
BORDER_COLOR = "#e3ecf8"
ACCENT_COLOR = "#ffd700"

# ----------- UTILITY FUNCTIONS ----------- #
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_users(users):
    with open("USERS.pkl", "wb") as f:
        pickle.dump(users, f)

def load_users():
    if os.path.exists("USERS.pkl"):
        with open("USERS.pkl", "rb") as f:
            users = pickle.load(f)
            return users if users else {}
    return {}

def save_roles_responsibilities(responsibilities, roles_map):
    with open("roles_user.pkl", "wb") as f:
        pickle.dump({
            "RESPONSIBILITIES": responsibilities,
            "ROLES_MAP": roles_map
        }, f)

def load_roles_responsibilities():
    if os.path.exists("roles_user.pkl"):
        with open("roles_user.pkl", "rb") as f:
            data = pickle.load(f)
            return data.get("RESPONSIBILITIES", set()), data.get("ROLES_MAP", {})
    return set(), {}

def image_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        b64 = base64.b64encode(img_file.read()).decode()
    return b64

def show_logo(max_width=120):
    logo_path = "images/inlogo.png"
    if os.path.exists(logo_path):
        logo_b64 = image_to_base64(logo_path)
        st.markdown(
            f"""
            <div style='text-align:center;'>
                <img src='data:image/png;base64,{logo_b64}' width='{max_width}' style='margin-bottom:1rem;'/>
            </div>
            """,
            unsafe_allow_html=True
        )

# ----------- GLOBAL SESSION INITIALIZATION ----------- #
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = ""
if "role" not in st.session_state: st.session_state.role = ""
if "USERS" not in st.session_state: st.session_state.USERS = load_users()
if "show_create_user_form" not in st.session_state: st.session_state.show_create_user_form = False
if "RESPONSIBILITIES" not in st.session_state or "ROLES_MAP" not in st.session_state:
    resp, rmap = load_roles_responsibilities()
    st.session_state.RESPONSIBILITIES = resp
    st.session_state.ROLES_MAP = rmap

# ----------- CUSTOM PAGE-WIDE CSS ----------- #
st.markdown(f"""
<style>
.stApp {{ background: {BG_GRAD} !important; }}
.infoway-login-bg {{
    height: 100vh; min-height: 540px; width: 100vw;
    display: flex; flex-direction:column; align-items:center; justify-content:center;
}}
.infoway-card {{
    background: {CARD_BG}; border-radius: 24px;
    box-shadow: 0 8px 32px 0 #4c6b9c18; padding:44px 32px 32px 32px;
    width:350px; max-width:96vw; margin: 0 auto; position:relative; display:flex; flex-direction:column; align-items:center;
    animation: fade-in 1s;
}}
.infoway-logo-circle {{
    position: absolute; top: -48px; left: 50%; transform: translateX(-50%);
    width: 96px; height: 96px; border-radius: 50%;
    background: #fff; box-shadow: 0 2px 16px #4c6b9c22;
    display: flex; align-items: center; justify-content: center; z-index: 10;
}}
.infoway-logo-circle img {{ width: 82px; height: 82px; border-radius: 50%; background: #fff; object-fit: contain; border: 1px solid #f3f3f3; }}
.infoway-title {{ margin-top:60px; margin-bottom:28px; font-size:1.44rem; font-weight:800; letter-spacing:.5px; color:{HEADER_COLOR}; text-align:center; }}
.infoway-form input {{ width:100%; padding:12px 10px; margin-bottom:16px; border-radius:9px; border: 1.4px solid #d5e2f4; font-size:1.09rem; background:#f3f7fa; color:#27354a; outline:none; transition: border .18s; }}
.infoway-form input:focus {{ border:1.5px solid {PRIMARY_COLOR}; }}
.infoway-form button {{
    width: 100%; padding: 12px 0; background: {PRIMARY_COLOR};
    color: #fff; font-weight:600; border:none; border-radius:9px; font-size:1.1rem; margin-top:8px;
    box-shadow:0 2px 10px #1567a74b; cursor:pointer; transition: background .18s;
}}
.infoway-form button:hover {{ background: #1567a7; }}
.infoway-error {{ color:#e04a34; background:#fff3f3; border-radius:7px; padding:7px 13px; margin-bottom:10px; font-size:1rem; text-align:center; }}
.infoway-header {{
    display:flex; align-items:center; justify-content:space-between; margin-bottom:30px; padding:16px 0 5px 0;
    background:rgba(255,255,255,0.95); border-bottom:2.4px solid {BORDER_COLOR}; border-radius:0 0 13px 13px; box-shadow: 0 2px 8px 0 #2c4e7e12;
}}
.infoway-header .logo {{ height:44px; width:auto; margin-left:16px; }}
.infoway-header .userinfo {{ margin-right:26px; color:#123355; font-weight:700; font-size:1.11rem; }}
.infoway-section {{
    background: #fff; border-radius:18px; box-shadow:0 2px 12px #e2e6f6; padding:32px 22px 22px 22px; margin-bottom:30px; animation: fade-in 0.7s;
}}
.infoway-section h3 {{ color:{SUBHEADER_COLOR}; font-weight:800; margin-top:0; margin-bottom:17px; font-size:1.22rem; letter-spacing:.2px; }}
.infoway-badge {{
    background:{ACCENT_COLOR}; color:#173e7d; border-radius:8px; padding:4px 13px; margin-left:7px; font-weight:700; font-size:0.97rem;
}}
@keyframes fade-in {{ from {{opacity:0; transform:translateY(18px);}} to {{opacity:1; transform:translateY(0);}} }}
</style>
""", unsafe_allow_html=True)

# ----------- MAIN CLASS ----------- #
class InfowayDashboard:
    def run(self):
        if not st.session_state.USERS:
            self.initial_admin_setup()
            return
        if not st.session_state.logged_in:
            self.login_page()
            return
        self.render_header()
        if st.session_state.role == "admin":
            self.admin_panel()
        else:
            self.user_panel()

    def initial_admin_setup(self):
        show_logo(96)
        st.markdown('<div class="infoway-login-bg">', unsafe_allow_html=True)
        st.markdown('<div class="infoway-card">', unsafe_allow_html=True)
        st.markdown('<div class="infoway-title">Infoway Admin Setup</div>', unsafe_allow_html=True)
        st.info("No users found. Create your initial admin account.")
        admin_username = st.text_input("Admin Username")
        admin_email = st.text_input("Admin Email")
        admin_password = st.text_input("Admin Password", type="password")
        if st.button("Create Admin"):
            if admin_username and admin_email and admin_password:
                users = {admin_username: [hash_password(admin_password), ["admin"], admin_email]}
                save_users(users)
                st.session_state.USERS = users
                st.success("Admin user created. Please login.")
                st.rerun()
            else:
                st.warning("Fill all fields to continue.")
        st.markdown('</div></div>', unsafe_allow_html=True)

    def login_page(self):
        # Remove any top Streamlit padding
        st.markdown("""
            <style>
            .block-container, .main .block-container {padding-top: 0 !important;}
            [data-testid="stHeader"] {height: 0; visibility: hidden;}
            .stApp {background: linear-gradient(120deg,#eaf6fb 0%,#b0e4fd 100%) !important;}
            </style>
            """, unsafe_allow_html=True)

        # Use st.empty() to center vertically
        for _ in range(6):
            st.write("")

        # Center logo and login fields with Streamlit only
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            logo_path = "images/inlogo.png"
            if os.path.exists(logo_path):
                st.markdown(
                    f"<div style='text-align:center;'><img src='data:image/png;base64,{image_to_base64(logo_path)}' width='100'/></div>",
                    unsafe_allow_html=True
                )
            st.markdown(
                "<h2 style='text-align:center; color:#245bff; font-weight:800; margin-bottom: 30px;'>Infoway Dashboard</h2>",
                unsafe_allow_html=True)
            username = st.text_input("Username", key="login_user", placeholder="Username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Password")
            login_btn = st.button("Login", use_container_width=True)
            if login_btn:
                users = st.session_state.USERS
                if username in users and hash_password(password) == users[username][0]:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = users[username][1][0] if isinstance(users[username][1], list) else \
                    users[username][1]
                    st.success(f"Welcome, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    def render_header(self):
        logo_path = "images/inlogo.png"
        logo_b64 = image_to_base64(logo_path) if os.path.exists(logo_path) else ""
        st.markdown(f"""
        <div class="infoway-header">
            <img src="data:image/png;base64,{logo_b64}" class="logo">
            <div class="userinfo">👤 {st.session_state.username} <span class="infoway-badge">{st.session_state.role.title()}</span></div>
        </div>
        """, unsafe_allow_html=True)

    def admin_panel(self):
        menu = st.sidebar.radio("Menu", [
            "Dashboard", "Users", "Roles & Responsibilities", "Sales", "Purchase", "Budgeting", "File Upload"
        ], help="Select what you want to manage.")
        st.sidebar.success("Role: Admin")
        st.sidebar.button("Logout", on_click=self.logout)

        if menu == "Dashboard":
            st.markdown(f"""<div class="infoway-section"><h3>Welcome Admin 🎉</h3>
                <p style="color:{SUCCESS_COLOR};font-weight:700;">All systems running smoothly.</p>
            </div>""", unsafe_allow_html=True)
        elif menu == "Users": self.user_management()
        elif menu == "Roles & Responsibilities": self.roles_responsibilities()
        elif menu == "Sales": self.sales_module()
        elif menu == "Purchase": self.purchase_module()
        elif menu == "Budgeting": self.budgeting_module()
        elif menu == "File Upload": self.file_uploads()

    def user_panel(self):
        menu = st.sidebar.radio("Menu", [
            "Home", "Profile", "Sales", "Purchase", "Budgeting", "File Upload"
        ])
        st.sidebar.info(f"Role: {st.session_state.role.title()}")
        st.sidebar.button("Logout", on_click=self.logout)

        if menu == "Home":
            st.markdown(f"""<div class="infoway-section"><h3>Welcome 🎊</h3>
                <p style="font-size:1.1rem;">Enjoy your Infoway Dashboard, {st.session_state.username}.</p>
            </div>""", unsafe_allow_html=True)
        elif menu == "Profile": self.edit_my_profile()
        elif menu == "Sales": self.sales_module()
        elif menu == "Purchase": self.purchase_module()
        elif menu == "Budgeting": self.budgeting_module()
        elif menu == "File Upload": self.file_uploads()

    def user_management(self):
        st.markdown('<div class="infoway-section"><h3>User Management</h3>', unsafe_allow_html=True)
        if st.button("➕ Create New User"): st.session_state.show_create_user_form = True
        if st.session_state.show_create_user_form: self.create_user_form()
        st.subheader("Registered Users")
        for uname, details in st.session_state.USERS.items():
            role = details[1][0] if isinstance(details[1], list) else details[1]
            email = details[2] if len(details) > 2 else ""
            st.markdown(f"**{uname}** | Role: {role} | Email: {email}")
            new_email = st.text_input(f"Edit email for {uname}", value=email, key=f"editemail_{uname}")
            if st.button(f"Update Email for {uname}", key=f"btn_{uname}"):
                details[2] = new_email
                st.session_state.USERS[uname] = details
                save_users(st.session_state.USERS)
                st.success(f"Email for '{uname}' updated!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    def create_user_form(self):
        st.markdown("---")
        st.subheader("Create New User")
        with st.form("create_user_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            roles = st.multiselect("Assign Roles", list(st.session_state.ROLES_MAP.keys()), key="role_select")
            submit_btn = st.form_submit_button("Add User")
        if submit_btn:
            if not username or not email or not password:
                st.error("Please fill in all fields.")
            elif username in st.session_state.USERS:
                st.error("Username already exists.")
            else:
                st.session_state.USERS[username] = [hash_password(password), roles, email]
                save_users(st.session_state.USERS)
                st.success(f"User {username} added.")
                st.session_state.show_create_user_form = False
                st.rerun()

    def roles_responsibilities(self):
        st.markdown('<div class="infoway-section"><h3>Roles & Responsibilities</h3>', unsafe_allow_html=True)
        new_resp = st.text_input("Add New Responsibility")
        if st.button("Add Responsibility"):
            if new_resp:
                st.session_state.RESPONSIBILITIES.add(new_resp)
                save_roles_responsibilities(st.session_state.RESPONSIBILITIES, st.session_state.ROLES_MAP)
                st.success(f"Responsibility '{new_resp}' added.")
            else:
                st.warning("Enter a valid responsibility.")
        st.markdown("#### Current Responsibilities:")
        st.write(list(st.session_state.RESPONSIBILITIES))
        st.markdown("---")
        new_role = st.text_input("New Role")
        selected_resps = st.multiselect("Select Responsibilities", list(st.session_state.RESPONSIBILITIES), key="add_role_resps")
        if st.button("Add Role"):
            if new_role and selected_resps:
                st.session_state.ROLES_MAP[new_role] = selected_resps
                save_roles_responsibilities(st.session_state.RESPONSIBILITIES, st.session_state.ROLES_MAP)
                st.success(f"Role '{new_role}' created with assigned responsibilities.")
            else:
                st.warning("Fill in role and select responsibilities.")
        st.markdown("#### Current Roles & Mappings:")
        st.write(st.session_state.ROLES_MAP)
        st.markdown('</div>', unsafe_allow_html=True)

    def edit_my_profile(self):
        users = st.session_state.USERS
        uname = st.session_state.username
        details = users[uname]
        st.markdown(f"""<div class="infoway-section"><h3>Profile</h3>
            <b>Username:</b> {uname} <br>
            <b>Role:</b> {details[1][0] if isinstance(details[1], list) else details[1]}
        """, unsafe_allow_html=True)
        email = details[2]
        new_email = st.text_input("Your Email", value=email, key="user_myemail")
        if st.button("Update My Email"):
            details[2] = new_email
            users[uname] = details
            save_users(users)
            st.success("Your email updated!")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    def sales_module(self):
        st.markdown('<div class="infoway-section"><h3>Sales Dashboard 📈</h3>', unsafe_allow_html=True)
        file_name = "sales_data.csv"
        if not os.path.exists(file_name):
            st.warning("Please upload 'sales_data.csv' (with columns: City,Total)")
            return
        df = pd.read_csv(file_name)
        st.dataframe(df)
        if "City" in df.columns and "Total" in df.columns:
            st.bar_chart(df.set_index("City")["Total"])
        st.markdown("#### Sales by Person (Sample)")
        data = {'Name': ['Omkar', 'Lakshman', 'Ajay'],'Sales': [24, 25, 23]}
        fig, ax = plt.subplots()
        ax.bar(data['Name'], data['Sales'], color=PRIMARY_COLOR)
        ax.set_title("Sales by Person")
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)

    def purchase_module(self):
        st.markdown('<div class="infoway-section"><h3>Purchase Dashboard 🛒</h3>', unsafe_allow_html=True)
        file_name = "purchase.csv"
        if not os.path.exists(file_name):
            st.warning("Please upload 'purchase.csv' (with columns: Date,Amount)")
            return
        df = pd.read_csv(file_name)
        st.dataframe(df)
        if "Date" in df.columns and "Amount" in df.columns:
            st.line_chart(df.set_index("Date")["Amount"])
        st.markdown('</div>', unsafe_allow_html=True)

    def budgeting_module(self):
        st.markdown('<div class="infoway-section"><h3>Budgeting Section 💰</h3>', unsafe_allow_html=True)
        file_name = "budget.csv"
        if not os.path.exists(file_name):
            st.warning("Please upload 'budget.csv' (columns: Department,Budget)")
            return
        df = pd.read_csv(file_name)
        st.dataframe(df)
        if "Department" in df.columns and "Budget" in df.columns:
            st.bar_chart(df.set_index("Department")["Budget"])
        st.markdown('</div>', unsafe_allow_html=True)

    def file_uploads(self):
        st.markdown('<div class="infoway-section"><h3>File Uploads 📁</h3>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload CSV, Excel, or PDF", type=["csv", "xlsx", "xls", "pdf"])
        if uploaded_file:
            ext = uploaded_file.name.split(".")[-1].lower()
            if ext == "csv":
                df = pd.read_csv(uploaded_file)
                st.success("CSV uploaded!")
                st.dataframe(df)
            elif ext in ["xlsx", "xls"]:
                df = pd.read_excel(uploaded_file)
                st.success("Excel uploaded!")
                st.dataframe(df)
            elif ext == "pdf":
                st.success("PDF uploaded!")
                try:
                    reader = PyPDF2.PdfReader(uploaded_file)
                    st.subheader("PDF Preview:")
                    for i, page in enumerate(reader.pages):
                        text = page.extract_text()
                        st.text_area(f"Page {i+1}", text, height=180)
                except Exception as e:
                    st.error(f"Error reading PDF: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    def logout(self):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.success("Logged out.")
        st.rerun()

if __name__ == "__main__":
    st.set_page_config(page_title="Infoway Dashboard", layout="centered")
    dashboard = InfowayDashboard()
    dashboard.run()
