import streamlit as st
import html
from supabase import create_client
from datetime import date, timedelta
from PIL import Image

TIPS = [
    "Pay yourself first. Move some of every paycheck into savings before you spend the rest.",
    "Impulse buys are lowkey traps. Wait 24 hours, and if you still want it, it's a real want.",
    "Selling something? Look up what similar stuff sold for so you don't underprice it.",
    "Doing gigs? Count your time and supplies in your rate so you're actually getting paid.",
    "A job that makes you pay to get hired is a red flag. Walk away.",
    "Anyone asking for gift cards is sus. It's a scam, and the money's gone for good.",
    "Meet in a public place and bring a friend or parent when you buy or sell.",
    "Track where your money goes for one month. You can't fix what you can't see.",
    "Saving a little early beats saving a lot late. Start now and stack it up.",
    "Gig money counts as income at tax time, so keep a record of what you earn.",
]

TYPE_TIPS = {
    "sale": "Check what similar items sold for before you price it, and meet in a public place.",
    "service": "Charge for prep, travel and supplies too, not just the hours you work.",
    "vacancy": "Be upfront about pay, and never charge people a fee to apply.",
    "jobneeded": "Ask about pay and hours first, and never pay to get a job. That's a scam.",
}

TYPE_LABELS = {
    "vacancy": "Hiring",
    "jobneeded": "Looking for work",
    "service": "Service",
    "sale": "For sale",
}

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

if "supabase_connection" not in st.session_state:
    st.session_state.supabase_connection = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase_connection = st.session_state.supabase_connection

st.markdown("""
<style>
div[data-baseweb="tab-list"] { gap: 0; justify-content: space-between; }
button[data-baseweb="tab"] { flex: 1; justify-content: center; font-size: 1.05rem; padding: 10px 0; }
</style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None

def note(text):
    st.markdown(
        '<div style="background:#DCE5CF; border-left:4px solid #2F5233; '
        'padding:10px 14px; border-radius:6px; color:#1F2A1F;">'
        f'{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )

def user_is_minor():
    """True if the logged-in user signed up as 13-17."""
    if st.session_state.user is None:
        return False
    meta = st.session_state.user.user_metadata or {}
    return meta.get("age_group") == "13-17"

def user_guardian_email():
    meta = st.session_state.user.user_metadata or {}
    return meta.get("guardian_email", "")

#Sidebar for account
st.sidebar.subheader("Account")
if st.session_state.user is None:
    mode = st.sidebar.radio("Login or Sign up", ["Login", "Sign up"])
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if mode == "Sign up":
        age_group = st.sidebar.radio("Age group", ["18 or older", "13-17", "Under 13"])
        guardian_email = ""
        agreed = False

        if age_group == "Under 13":
            st.sidebar.error("Sorry, you must be at least 13 to create an account.")
        else:
            if age_group == "13-17":
                guardian_email = st.sidebar.text_input("Parent/guardian email")
                agreed = st.sidebar.checkbox("My parent/guardian knows I'm joining and agrees.")
            else:
                agreed = st.sidebar.checkbox("I'm 18+ and agree to the community guidelines.")

            if st.sidebar.button("Create account"):
                if not agreed:
                    st.sidebar.error("Please tick the agreement box.")
                elif age_group == "13-17" and "@" not in guardian_email:
                    st.sidebar.error("Please enter a valid parent/guardian email.")
                else:
                    try:
                        supabase_connection.auth.sign_up({
                            "email": email,
                            "password": password,
                            "options": {"data": {
                                "age_group": age_group,
                                "guardian_email": guardian_email,
                            }},
                        })
                        st.sidebar.success("Account created! Switch to Login.")
                    except Exception as e:
                        st.sidebar.error(f"Sign up failed: {e}")

    if mode == "Login":
        if st.sidebar.button("Log in"):
            try:
                result = supabase_connection.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )
                st.session_state.user = result.user
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Login failed: {e}")
else:
    st.sidebar.write(f"Logged in as {st.session_state.user.email}")
    if st.sidebar.button("Log out"):
        supabase_connection.auth.sign_out()
        st.session_state.user = None
        st.rerun()

# Sidebar for menu (logged-in users only) 
page = "All listings"

if st.session_state.user is not None:
    if st.session_state.get("go_home"):
        st.session_state.page = "All listings"
        st.session_state.go_home = False

    st.sidebar.divider()
    page = st.sidebar.radio(
        "Menu",
        ["All listings", "Post a listing", "My listings"],
        key="page",
    )

# Header
img = Image.open("header.jpeg")
w, h = img.size
strip_h = w // 6
top = int(h * 0.50)
img = img.crop((0, top, w, min(h, top + strip_h)))
st.image(img, use_container_width=True)
st.title("mountainhouse.localboard")
st.caption("What's up in Mountain House?")

def render_listings(rows):
    if not rows:
        st.info("Nothing here yet. Be the first to post.")
        return

    for listing in rows:
        st.subheader(listing["title"])
        label = TYPE_LABELS.get(listing['type'].strip(), listing['type'])
        category = (listing.get("category") or "").strip()
        st.write(f"**{label}**" + (f" · {category}" if category else ""))
        st.write(listing["description"])
        st.caption(f"Active until {listing['expires_at']}")

        if st.session_state.user is not None:
            contact = listing.get("contact") or "not provided"
            if "@" in contact and not contact.startswith("@") and " " not in contact:
                st.markdown(f"**Contact:** [{contact}](mailto:{contact})")
            else:
                st.write(f"**Contact:** {contact}")
            if listing.get("is_minor"):
                st.caption("Posted by a minor. Contact goes through a parent/guardian.")
        st.divider()

def show_feed():
    st.header("All listings")
    if st.session_state.get("flash"):
        st.success(st.session_state.flash)
        st.session_state.flash = None
    tip = TIPS[date.today().toordinal() % len(TIPS)]
    st.caption(f"Money tip of the day: {tip}")
    
    if st.session_state.user is None:
        note("Log in from the sidebar to see contact info or post a listing. New here? Choose Sign up.")
    if st.session_state.user is None:
        columns = "id,type,title,description,category,created_at,expires_at,is_minor,user_id"
    else:
        columns = "*"
    rows = (
        supabase_connection.table("listings")
        .select(columns)
        .gte("expires_at", str(date.today()))
        .order("created_at", desc=True)
        .execute()
        .data
    )

    def of_type(t):
        return [r for r in rows if r["type"].strip() == t]

    vacancies = of_type("vacancy")
    jobs = of_type("jobneeded")
    services = of_type("service")
    sales = of_type("sale")

    tab_all, tab_vac, tab_job, tab_srv, tab_sale = st.tabs([
        f"All ({len(rows)})",
        f"Hiring ({len(vacancies)})",
        f"Looking for work ({len(jobs)})",
        f"Services ({len(services)})",
        f"For sale ({len(sales)})",
    ])
    with tab_all:
        render_listings(rows)
    with tab_vac:
        render_listings(vacancies)
    with tab_job:
        render_listings(jobs)
    with tab_srv:
        render_listings(services)
    with tab_sale:
        render_listings(sales)

# Create Post
def show_post_form():
    st.header("Post a new listing")
    today = date.today()
    max_date = today + timedelta(days=60)
    is_minor = user_is_minor()
    guardian_email = user_guardian_email() if is_minor else ""

    with st.form("post_form", clear_on_submit=False):
        title = st.text_input("Title")
        type_ = st.selectbox(
            "Type",
            ["vacancy", "jobneeded", "service", "sale"],
            format_func=lambda t: TYPE_LABELS[t],
        )
        category = st.text_input("Category (optional)", placeholder="e.g. Tutoring, Furniture, Events")
        description = st.text_area("Description")

        if is_minor:
            note(f"For safety, people will contact your parent/guardian: {guardian_email}")
            contact = guardian_email
        else:
            contact = st.text_input("How should people reach you? (email, phone, or Instagram)")

        expires_at = st.date_input(
            "Expires on (default is 60 days from today)",
            value=max_date, min_value=today, max_value=max_date,
        )
        submitted = st.form_submit_button("Post listing")

    if submitted:
        if title and description and contact:
            try:
                supabase_connection.table("listings").insert({
                    "title": title,
                    "type": type_,
                    "category": category,
                    "description": description,
                    "contact": contact,
                    "expires_at": str(expires_at),
                    "is_minor": is_minor,
                    "user_id": st.session_state.user.id,
                }).execute()
                #st.session_state.flash = "Listing posted!"
                st.session_state.flash = f"Listing posted! Tip: {TYPE_TIPS[type_]}"
                st.session_state.go_home = True
                st.rerun()
            except Exception as e:
                st.error(f"Could not post: {e}")
        else:
            st.error("Hold up, you still need to fill in the title, description and contact.")

# Update/Delete Post
def show_my_listings():
    st.header("My listings")
    if st.session_state.get("my_flash"):
        st.success(st.session_state.my_flash)
        st.session_state.my_flash = None
    today = date.today()
    max_date = today + timedelta(days=60)
    is_minor = user_is_minor()

    mine = (
        supabase_connection.table("listings")
        .select("*")
        .eq("user_id", st.session_state.user.id)
        .order("created_at", desc=True)
        .execute()
        .data
    )
    if not mine:
        st.info("You haven't posted anything yet. Your first one only takes a moment.")

    for item in mine:
        expired = item["expires_at"] < str(today)
        status = ":red[Expired]" if expired else ":green[Active]"
        with st.expander(f"{item['title']}  ({status})"):    
            st.caption(f"{'Expired on' if expired else 'Active until'} {item['expires_at']}")
            new_title = st.text_input("Title", item["title"], key=f"title_{item['id']}")
            new_desc = st.text_area("Description", item["description"], key=f"desc_{item['id']}")
            new_contact = st.text_input(
                "Contact", item.get("contact") or "",
                key=f"contact_{item['id']}", disabled=is_minor,
            )
            new_expiry = st.date_input(
                "Expires on (pick a new date to reactivate)",
                value=today if expired else date.fromisoformat(item["expires_at"]),
                min_value=today, max_value=max_date,
                key=f"exp_{item['id']}",
            )
            confirm = st.checkbox("Yes, delete this listing", key=f"confirm_{item['id']}")

            col1, col2 = st.columns(2)
            if col1.button("Save changes", key=f"save_{item['id']}"):
                missing = []
                if not new_title.strip():
                    missing.append("title")
                if not new_desc.strip():
                    missing.append("description")
                if not new_contact.strip():
                    missing.append("contact")

                if missing:
                    st.error("Hold up, you still need: " + ", ".join(missing))
                else:
                    supabase_connection.table("listings").update({
                        "title": new_title,
                        "description": new_desc,
                        "contact": new_contact,
                        "expires_at": str(new_expiry),
                    }).eq("id", item["id"]).execute()
                    st.session_state.my_flash = "Changes saved! You're good."
                    st.rerun()
            if col2.button("Delete", key=f"del_{item['id']}"):
                if confirm:
                    supabase_connection.table("listings").delete().eq("id", item["id"]).execute()
                    st.session_state.my_flash = "Gone. Listing deleted."
                    st.rerun()
                else:
                    st.warning("Tick the box first to confirm.")

# Show chosen page
if page == "Post a listing":
    show_post_form()
elif page == "My listings":
    show_my_listings()
else:
    show_feed()