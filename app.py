import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date, time
import os

st.set_page_config(page_title="SmartSchedules", layout="wide")

# ── Logo ─────────────────────────────────────────────────────────────────────
def logo_html(width="260px"):
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 80" width="{width}">
      <!-- Icon mark: stacked shift bars inside a rounded square -->
      <rect width="80" height="80" rx="16" fill="#0F2D52"/>
      <rect x="12" y="16" width="34" height="9" rx="4" fill="#F5A623"/>
      <rect x="12" y="30" width="56" height="9" rx="4" fill="rgba(245,166,35,0.45)"/>
      <rect x="12" y="44" width="44" height="9" rx="4" fill="#F5A623"/>
      <rect x="12" y="58" width="26" height="9" rx="4" fill="rgba(245,166,35,0.45)"/>
      <!-- Badge: gold circle with a check -->
      <circle cx="62" cy="18" r="11" fill="#F5A623"/>
      <polyline points="56,18 61,23 70,11"
        fill="none" stroke="#0F2D52" stroke-width="2.8"
        stroke-linecap="round" stroke-linejoin="round"/>
      <!-- Wordmark -->
      <text x="94" y="36"
        font-family="'Helvetica Neue',Arial,sans-serif"
        font-weight="800" font-size="24" fill="#0F2D52" letter-spacing="-0.5">Smart</text>
      <text x="94" y="63"
        font-family="'Helvetica Neue',Arial,sans-serif"
        font-weight="300" font-size="24" fill="#F5A623" letter-spacing="1.5">Schedules</text>
    </svg>
    """

# ── Theme ─────────────────────────────────────────────────────────────────────
def inject_theme():
    st.markdown("""
    <style>
    /* ── Sidebar: navy background ── */
    [data-testid="stSidebar"] {
        background-color: #0F2D52 !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stSelectbox div {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.15) !important;
    }
    /* Sidebar alert boxes: use gold tones instead of red */
    [data-testid="stSidebar"] [data-testid="stNotification"] {
        background-color: rgba(245,166,35,0.18) !important;
        border-left-color: #F5A623 !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] [data-testid="stNotification"] p {
        color: #ffffff !important;
    }

    /* ── Tabs: gold active underline, navy text ── */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #F5A623 !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #0F2D52 !important;
        font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #4A5568;
    }

    /* ── Primary buttons: navy ── */
    [data-testid="baseButton-primary"] {
        background-color: #0F2D52 !important;
        border-color: #0F2D52 !important;
        color: #ffffff !important;
    }
    [data-testid="baseButton-primary"]:hover {
        background-color: #1a4278 !important;
        border-color: #1a4278 !important;
    }

    /* ── Page headers ── */
    h1, h2, h3, h4 { color: #0F2D52 !important; }

    /* ── Dividers ── */
    hr { border-color: #dde3ed !important; }

    /* ── DataFrames: header row in navy ── */
    [data-testid="stDataFrame"] th {
        background-color: #0F2D52 !important;
        color: #ffffff !important;
    }

    /* ── Input focus ring in gold ── */
    input:focus, textarea:focus, select:focus {
        border-color: #F5A623 !important;
        box-shadow: 0 0 0 2px rgba(245,166,35,0.25) !important;
    }
    /* ── Sidebar view-selector links ── */
    [data-testid="stSidebar"] a.view-link {
        display: flex !important;
        align-items: center !important;
        gap: 9px !important;
        text-decoration: none !important;
        color: white !important;
        padding: 5px 6px !important;
        border-radius: 4px !important;
        font-size: 0.9rem !important;
        transition: background 0.15s !important;
    }
    [data-testid="stSidebar"] a.view-link:hover {
        background-color: rgba(255,255,255,0.10) !important;
    }
    /* ── Training toggle indented ── */
    [data-testid="stSidebar"] [data-testid="stToggle"] {
        margin-left: 1.6em !important;
        margin-top: 1px !important;
        margin-bottom: 1px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
EMPLOYEES_FILE = "data_ai/employees.csv"
SHIFTS_FILE    = "data_ai/shifts.csv"
SWAPS_FILE     = "data_ai/swap_requests.csv"
CERTS_FILE     = "data_ai/certifications.csv"
VENUES_FILE    = "data_ai/venues.csv"
CERT_DIR       = "data_ai/cert_uploads"

VENUE_TYPES = [
    "Restaurant", "Bar", "Pool Bar", "Lobby Bar", "Rooftop Bar",
    "Banquet Hall", "Café", "Room Service", "Event Space", "Patio/Terrace", "Other",
]

ROLES = ["Server", "Bartender", "Host/Hostess", "Cook", "Busser", "Expeditor", "Supervisor", "Manager"]

ROLE_COLORS = {
    "Server":       "#2878BE",   # sky blue
    "Bartender":    "#6B4FBB",   # indigo
    "Host/Hostess": "#0D9B7D",   # teal
    "Cook":         "#D4870A",   # dark amber
    "Busser":       "#3D7EAA",   # ocean blue
    "Expeditor":    "#2D6A4F",   # forest green
    "Supervisor":   "#4A5E7A",   # slate blue
    "Manager":      "#0F2D52",   # navy  (matches logo)
}

ROLE_CERTS = {
    "Server":       ["Food Handler"],
    "Bartender":    ["Food Handler", "RBS"],
    "Host/Hostess": ["Food Handler"],
    "Cook":         ["Food Handler"],
    "Busser":       ["Food Handler"],
    "Expeditor":    ["Food Handler"],
    "Supervisor":   ["Food Handler", "RBS"],
    "Manager":      ["Food Handler", "RBS", "Food Service Manager"],
}

CERT_DESCRIPTIONS = {
    "Food Handler":          "California Food Handler Card",
    "RBS":                   "Responsible Beverage Service (RBS) Certification",
    "Food Service Manager":  "Food Service Manager Certification (ServSafe or equivalent)",
}

ALERT_DAYS      = 30
BURNOUT_CAUTION = 5   # yellow — approaching limit
BURNOUT_WARNING = 6   # orange — at CA max
BURNOUT_DANGER  = 7   # red — CA labor law violation territory

os.makedirs("data_ai", exist_ok=True)
os.makedirs(CERT_DIR, exist_ok=True)


# ── Data I/O ──────────────────────────────────────────────────────────────────
def load_employees():
    if os.path.exists(EMPLOYEES_FILE):
        df = pd.read_csv(EMPLOYEES_FILE)
        df["id"] = df["id"].astype(int)
        return df
    return pd.DataFrame(columns=["id", "name", "role", "email", "phone"])

def save_employees(df):
    df.to_csv(EMPLOYEES_FILE, index=False)

def load_shifts():
    if os.path.exists(SHIFTS_FILE):
        df = pd.read_csv(SHIFTS_FILE)
        df["id"] = df["id"].astype(int)
        df["employee_id"] = df["employee_id"].astype(int)
        df["start_datetime"] = pd.to_datetime(df["start_datetime"])
        df["end_datetime"]   = pd.to_datetime(df["end_datetime"])
        if "venue_id" not in df.columns:
            df["venue_id"] = None
        return df
    return pd.DataFrame(columns=["id", "employee_id", "date", "start_datetime", "end_datetime", "notes", "venue_id"])

def load_venues():
    if os.path.exists(VENUES_FILE):
        df = pd.read_csv(VENUES_FILE)
        df["id"] = df["id"].astype(int)
        return df
    return pd.DataFrame(columns=["id", "name", "type", "description"])

def save_venues(df):
    df.to_csv(VENUES_FILE, index=False)

def save_shifts(df):
    df.to_csv(SHIFTS_FILE, index=False)

def load_swaps():
    if os.path.exists(SWAPS_FILE):
        df = pd.read_csv(SWAPS_FILE)
        for col in ["id", "requester_id", "target_id", "requester_shift_id", "target_shift_id"]:
            df[col] = df[col].astype(int)
        df["requested_at"] = pd.to_datetime(df["requested_at"])
        return df
    return pd.DataFrame(columns=[
        "id", "requester_id", "requester_shift_id", "target_id", "target_shift_id",
        "status", "requester_note", "requested_at", "resolved_at", "manager_notes",
    ])

def save_swaps(df):
    df.to_csv(SWAPS_FILE, index=False)

def load_certs():
    if os.path.exists(CERTS_FILE):
        df = pd.read_csv(CERTS_FILE)
        df["id"] = df["id"].astype(int)
        df["employee_id"] = df["employee_id"].astype(int)
        df["expiry_date"]  = pd.to_datetime(df["expiry_date"]).dt.date
        return df
    return pd.DataFrame(columns=["id", "employee_id", "cert_type", "expiry_date", "file_name", "uploaded_at"])

def save_certs(df):
    df.to_csv(CERTS_FILE, index=False)

def next_id(df):
    return int(df["id"].max() + 1) if len(df) > 0 else 1


# ── Labor compliance ──────────────────────────────────────────────────────────
def check_turnaround(emp_id, new_start, new_end, shifts_df, exclude_id=None):
    emp_shifts = shifts_df[shifts_df["employee_id"] == emp_id].copy()
    if exclude_id is not None:
        emp_shifts = emp_shifts[emp_shifts["id"] != exclude_id]
    for _, s in emp_shifts.iterrows():
        es, ee = s["start_datetime"], s["end_datetime"]
        if new_start < ee and new_end > es:
            return True, f"Overlaps with {es.strftime('%b %d %I:%M %p')}–{ee.strftime('%I:%M %p')}."
        if ee <= new_start:
            gap = (new_start - ee).total_seconds() / 3600
            if gap < 8:
                return True, f"Only {gap:.1f}h rest after shift ending {ee.strftime('%b %d %I:%M %p')}."
        if new_end <= es:
            gap = (es - new_end).total_seconds() / 3600
            if gap < 8:
                return True, f"Only {gap:.1f}h rest before shift at {es.strftime('%b %d %I:%M %p')}."
    return False, None

def check_shift_duration(start_dt, end_dt):
    """
    Returns (severity, message).
    severity: None = ok, 'warning' = long but allowed (8–16h), 'error' = blocked (>16h).
    """
    hours = (end_dt - start_dt).total_seconds() / 3600
    if hours > 16:
        return "error", (
            f"🚫 Shift is **{hours:.1f} hours** — shifts over 16 hours are not permitted. "
            "Please correct the start or end time."
        )
    if hours > 8:
        return "warning", (
            f"⚠️ Long shift: **{hours:.1f} hours**. Shifts over 8 hours should be reviewed. "
            "10s, 12s, and 16s are allowed — verify this is intentional."
        )
    return None, None

def validate_swap(s1_id, s2_id, shifts_df):
    s1 = shifts_df[shifts_df["id"] == s1_id].iloc[0]
    s2 = shifts_df[shifts_df["id"] == s2_id].iloc[0]
    v, r = check_turnaround(s1["employee_id"], s2["start_datetime"], s2["end_datetime"], shifts_df, exclude_id=s1_id)
    if v:
        return False, f"Requester 8h violation: {r}"
    v, r = check_turnaround(s2["employee_id"], s1["start_datetime"], s1["end_datetime"], shifts_df, exclude_id=s2_id)
    if v:
        return False, f"Target 8h violation: {r}"
    return True, None


# ── Burnout tracking ──────────────────────────────────────────────────────────
def get_consecutive_streak(emp_id, shifts_df):
    """
    Returns (streak_length, list_of_dates_in_streak).
    Finds the active or most-recent streak within a 28-day lookback window,
    including upcoming scheduled shifts so cross-week patterns are caught.
    """
    emp_dates = sorted(set(
        shifts_df[shifts_df["employee_id"] == emp_id]["start_datetime"].dt.date.tolist()
    ))
    if not emp_dates:
        return 0, []

    today = date.today()
    # Only consider dates within a 28-day lookback + 14-day lookahead
    window_start = today - timedelta(days=28)
    window_end   = today + timedelta(days=14)
    emp_dates = [d for d in emp_dates if window_start <= d <= window_end]
    if not emp_dates:
        return 0, []

    # Build all consecutive streaks
    streaks = []
    streak = [emp_dates[0]]
    for i in range(1, len(emp_dates)):
        if (emp_dates[i] - emp_dates[i - 1]).days == 1:
            streak.append(emp_dates[i])
        else:
            streaks.append(streak)
            streak = [emp_dates[i]]
    streaks.append(streak)

    # Prefer a streak that includes today or ends very recently / upcoming
    for s in streaks:
        if today in s:
            return len(s), s
    # Recently ended (yesterday)
    yesterday = today - timedelta(days=1)
    for s in streaks:
        if yesterday == s[-1]:
            return len(s), s
    # Upcoming streak starting soon
    for s in streaks:
        if s[0] >= today:
            return len(s), s
    # Fallback: most recent
    most_recent = max(streaks, key=lambda x: x[-1])
    if (today - most_recent[-1]).days <= 7:
        return len(most_recent), most_recent
    return 0, []

def burnout_level(streak):
    if streak >= BURNOUT_DANGER:  return "danger",  "🔴"
    if streak >= BURNOUT_WARNING: return "warning",  "🟠"
    if streak >= BURNOUT_CAUTION: return "caution",  "🟡"
    return "ok", "🟢"


# ── Cert helpers ──────────────────────────────────────────────────────────────
def cert_badge(expiry_date):
    today = date.today()
    if expiry_date < today:
        return "🔴 Expired", "red"
    days_left = (expiry_date - today).days
    if days_left <= ALERT_DAYS:
        return f"🟡 Expires in {days_left}d", "orange"
    return f"🟢 Valid ({days_left}d left)", "green"

def emp_cert_issues(emp_id, role, certs_df):
    issues = []
    today = date.today()
    for ct in ROLE_CERTS.get(role, []):
        rows = certs_df[(certs_df["employee_id"] == emp_id) & (certs_df["cert_type"] == ct)]
        if len(rows) == 0:
            issues.append((ct, "missing"))
        else:
            latest = rows.sort_values("expiry_date", ascending=False).iloc[0]["expiry_date"]
            if latest < today:
                issues.append((ct, "expired"))
            elif (latest - today).days <= ALERT_DAYS:
                issues.append((ct, "expiring_soon"))
    return issues

def fmt_shift(row):
    return (
        f"{row['start_datetime'].strftime('%a %b %d')}  "
        f"{row['start_datetime'].strftime('%I:%M %p')}–{row['end_datetime'].strftime('%I:%M %p')}"
    )

def role_pill(role, small=False):
    color = ROLE_COLORS.get(role, "#888")
    size  = "0.75em" if small else "0.82em"
    return (
        f'<span style="background:{color};color:#fff;padding:1px 8px;'
        f'border-radius:10px;font-size:{size};font-weight:600">{role}</span>'
    )

def shift_card_html(name, role, start, end, venue_name=None, extra_style=""):
    hours = (end - start).total_seconds() / 3600
    if hours > 8:
        bg    = "#F5A623"
        fg    = "#1a1a1a"
        label = f"⚠️ {name}"
        note  = f"{hours:.1f}h — long shift"
    else:
        bg    = ROLE_COLORS.get(role, "#888")
        fg    = "#fff"
        label = name
        note  = f"{hours:.1f}h"
    venue_line = (
        f'<br><span style="opacity:0.75;font-size:0.9em">📍 {venue_name}</span>'
        if venue_name else ""
    )
    return (
        f'<div style="background:{bg};color:{fg};padding:4px 7px;border-radius:7px;'
        f'margin:3px 0;font-size:0.75em;line-height:1.4;{extra_style}">'
        f'<b>{label}</b><br>'
        f'{start.strftime("%-I:%M%p").lower()}–{end.strftime("%-I:%M%p").lower()}<br>'
        f'<span style="opacity:0.85">{note}</span>{venue_line}'
        f'</div>'
    )


# ── Cert scheduling gate ──────────────────────────────────────────────────────
def check_employee_schedulable(emp_id, role, certs_df):
    """Returns (can_schedule, [blocking_issue_strings]).
    Only hard-blocks on missing or expired certs — expiring-soon is allowed."""
    today  = date.today()
    issues = []
    for ct in ROLE_CERTS.get(role, []):
        rows = certs_df[(certs_df["employee_id"] == emp_id) & (certs_df["cert_type"] == ct)]
        if len(rows) == 0:
            issues.append(f"{CERT_DESCRIPTIONS.get(ct, ct)} — not on file")
        else:
            latest_exp = rows.sort_values("expiry_date", ascending=False).iloc[0]["expiry_date"]
            if latest_exp < today:
                issues.append(
                    f"{CERT_DESCRIPTIONS.get(ct, ct)} — expired {latest_exp.strftime('%b %d, %Y')}"
                )
    return len(issues) == 0, issues


# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("vis_emp_id", None),
    ("vis_week_start", None),
    ("vis_schedule_day", None),
    ("training_mode", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


inject_theme()

# ── Load data ─────────────────────────────────────────────────────────────────
employees = load_employees()
shifts    = load_shifts()
swaps     = load_swaps()
certs     = load_certs()
venues    = load_venues()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(logo_html(width="200px"), unsafe_allow_html=True)
    st.divider()
    # Sync view from URL query param (set when user clicks a view-selector link)
    _qp = st.query_params
    if "view" in _qp and _qp["view"] in ("Manager", "Employee"):
        st.session_state.view_mode = _qp["view"]
    elif "view_mode" not in st.session_state:
        st.session_state.view_mode = "Manager"

    is_mgr = st.session_state.view_mode == "Manager"

    def _dot(active):
        if active:
            return ('<circle cx="7.5" cy="7.5" r="6.5" fill="#F5A623"/>'
                    '<circle cx="7.5" cy="7.5" r="2.6" fill="white"/>')
        return '<circle cx="7.5" cy="7.5" r="6" fill="none" stroke="rgba(255,255,255,0.55)" stroke-width="1.8"/>'

    def _vlink(label, target, active):
        w = "600" if active else "400"
        return (
            f'<a class="view-link" href="?view={target}" '
            f'style="font-weight:{w};">'
            f'<svg width="15" height="15" viewBox="0 0 15 15" style="flex-shrink:0;">'
            f'{_dot(active)}</svg>{label}</a>'
        )

    st.markdown('<p style="font-weight:600;color:white;margin:0 0 4px 0;font-size:0.9rem;">View as</p>',
                unsafe_allow_html=True)
    st.markdown(_vlink("Manager", "Manager", is_mgr), unsafe_allow_html=True)

    if is_mgr:
        training_on = st.toggle(
            "Training Mode",
            value=st.session_state.get("training_mode", False),
            key="sidebar_training_toggle",
            help="Disables certification checks so managers can practice scheduling freely.",
        )
        st.session_state.training_mode = training_on
        if training_on:
            st.markdown(
                '<span style="font-size:0.75em;color:#F5A623;font-weight:600;">'
                '&nbsp;&nbsp;Cert checks disabled</span>',
                unsafe_allow_html=True,
            )

    st.markdown(_vlink("Employee", "Employee", not is_mgr), unsafe_allow_html=True)

    mode = "Manager" if is_mgr else "Employee"

    current_emp = None
    if not is_mgr:
        if len(employees) == 0:
            st.warning("No employees in system yet.")
        else:
            sel_name = st.selectbox("Your name", employees["name"].tolist())
            current_emp = employees[employees["name"] == sel_name].iloc[0]

    st.divider()

    if len(employees) > 0:
        total_issues = sum(
            len(emp_cert_issues(r["id"], r["role"], certs))
            for _, r in employees.iterrows()
        )
        if total_issues:
            st.warning(f"⚠️ {total_issues} certification issue(s)")

    n_pending = len(swaps[swaps["status"] == "pending"]) if len(swaps) > 0 else 0
    if n_pending:
        st.warning(f"🔄 {n_pending} swap request(s) pending")

    if len(employees) > 0 and len(shifts) > 0:
        burnout_risks = [
            get_consecutive_streak(int(r["id"]), shifts)[0]
            for _, r in employees.iterrows()
        ]
        at_risk = sum(1 for s in burnout_risks if s >= BURNOUT_CAUTION)
        if at_risk:
            st.warning(f"🔥 {at_risk} employee(s) at burnout risk")

is_manager = mode == "Manager"

st.markdown(logo_html(width="340px"), unsafe_allow_html=True)
st.caption("Schedule staff · enforce labor law · manage swaps · track certifications · monitor burnout")

if is_manager and st.session_state.get("training_mode"):
    st.markdown(
        '<div style="background:#F5A623;color:#0F2D52;padding:14px 20px;border-radius:10px;'
        'margin:10px 0;border:2px solid #D4870A">'
        '<b style="font-size:1.1em">TRAINING MODE ACTIVE</b><br>'
        'Certification requirements are disabled. You can schedule any employee freely to explore the app. '
        'Go to the Employees tab → Manager Settings to turn it off and restore full compliance enforcement.'
        '</div>',
        unsafe_allow_html=True,
    )

st.divider()


# ════════════════════════════════════════════════════════════════════════════
# MANAGER VIEW
# ════════════════════════════════════════════════════════════════════════════
if is_manager:
    swap_badge  = "  🔴" if n_pending else ""
    tabs = st.tabs([
        "👥 Employees",
        "🏢 Venues",
        "📅 Visual Scheduler",
        "📆 Weekly View",
        f"🔄 Swap Requests{swap_badge}",
        "🎓 Certifications",
        "🔥 Burnout Monitor",
    ])
    tab_emp, tab_venues, tab_vis, tab_week, tab_swaps, tab_certs, tab_burn = tabs


    # ── Employees ──────────────────────────────────────────────────────────
    with tab_emp:
        col_form, col_roster = st.columns([1, 1], gap="large")

        with col_form:
            st.subheader("Add Employee")
            with st.form("add_emp", clear_on_submit=True):
                name  = st.text_input("Full Name *")
                role  = st.selectbox("Role *", ROLES)
                email = st.text_input("Email (optional)")
                phone = st.text_input("Phone (optional)")
                if st.form_submit_button("Add Employee", type="primary", use_container_width=True):
                    if not name.strip():
                        st.error("Name is required.")
                    elif name.strip().lower() in employees["name"].str.lower().values:
                        st.error(f"'{name.strip()}' already exists.")
                    else:
                        new_row = pd.DataFrame([{
                            "id": next_id(employees), "name": name.strip(),
                            "role": role, "email": email.strip(), "phone": phone.strip(),
                        }])
                        employees = pd.concat([employees, new_row], ignore_index=True)
                        save_employees(employees)
                        st.success(f"Added **{name.strip()}** as {role}.")
                        st.rerun()

            st.subheader("Required Certifications by Role")
            for r, cl in ROLE_CERTS.items():
                st.markdown(f"**{r}:** {', '.join(cl)}")

        with col_roster:
            st.subheader("Current Roster")
            if len(employees) == 0:
                st.info("No employees yet.")
            else:
                for role_name in ROLES:
                    grp = employees[employees["role"] == role_name]
                    if len(grp) == 0:
                        continue
                    color = ROLE_COLORS.get(role_name, "#888")
                    st.markdown(
                        f'<span style="background:{color};color:#fff;padding:2px 10px;'
                        f'border-radius:12px;font-size:0.85em;font-weight:600">{role_name}</span>',
                        unsafe_allow_html=True,
                    )
                    for _, emp in grp.iterrows():
                        issues = emp_cert_issues(emp["id"], emp["role"], certs)
                        streak, _ = get_consecutive_streak(int(emp["id"]), shifts)
                        _, burn_icon = burnout_level(streak)
                        cert_badge_str = " ⚠️" if issues else ""
                        burn_str = f" {burn_icon}" if streak >= BURNOUT_CAUTION else ""
                        c1, c2 = st.columns([4, 1])
                        c1.write(f"  • {emp['name']}{cert_badge_str}{burn_str}")
                        if c2.button("Remove", key=f"rm_{emp['id']}"):
                            employees = employees[employees["id"] != emp["id"]]
                            shifts    = shifts[shifts["employee_id"] != emp["id"]]
                            save_employees(employees)
                            save_shifts(shifts)
                            st.rerun()



    # ── Venues ─────────────────────────────────────────────────────────────
    with tab_venues:
        st.subheader("Venue Management")
        st.caption("Add the food outlets, bar stations, and event spaces at your property.")

        col_vadd, col_vlist = st.columns([1, 1], gap="large")

        with col_vadd:
            st.markdown("**Add Venue**")
            with st.form("add_venue", clear_on_submit=True):
                v_name = st.text_input("Venue Name *", placeholder="e.g. Rooftop Bar, Main Dining Room")
                v_type = st.selectbox("Outlet Type", VENUE_TYPES)
                v_desc = st.text_input("Description (optional)", placeholder="e.g. 3rd floor, seats 80")
                if st.form_submit_button("Add Venue", type="primary", use_container_width=True):
                    if not v_name.strip():
                        st.error("Venue name is required.")
                    elif v_name.strip().lower() in venues["name"].str.lower().values:
                        st.error(f"A venue named '{v_name.strip()}' already exists.")
                    else:
                        new_venue = pd.DataFrame([{
                            "id": next_id(venues),
                            "name": v_name.strip(),
                            "type": v_type,
                            "description": v_desc.strip(),
                        }])
                        venues = pd.concat([venues, new_venue], ignore_index=True)
                        save_venues(venues)
                        st.success(f"Added **{v_name.strip()}** ({v_type}).")
                        st.rerun()

        with col_vlist:
            st.markdown("**Property Venues**")
            if len(venues) == 0:
                st.info("No venues added yet. Add your first outlet or station.")
            else:
                for v_type_group in VENUE_TYPES:
                    grp = venues[venues["type"] == v_type_group]
                    if len(grp) == 0:
                        continue
                    st.markdown(f"**{v_type_group}**")
                    for _, v in grp.iterrows():
                        c1, c2, c3 = st.columns([3, 2, 1])
                        c1.write(f"  • {v['name']}")
                        c2.caption(v["description"] if pd.notna(v["description"]) and v["description"] else "—")
                        if c3.button("Remove", key=f"rmv_{v['id']}"):
                            # Clear venue from any shifts using it
                            shifts.loc[shifts["venue_id"] == v["id"], "venue_id"] = None
                            save_shifts(shifts)
                            venues = venues[venues["id"] != v["id"]]
                            save_venues(venues)
                            st.rerun()

    # ── Visual Scheduler ───────────────────────────────────────────────────
    with tab_vis:
        st.subheader("Visual Scheduler")

        if len(employees) == 0:
            st.warning("Add employees first.")
        else:
            today       = datetime.today().date()
            default_mon = today - timedelta(days=today.weekday())

            # Week picker at top
            week_start = st.date_input(
                "Week (Monday)", value=default_mon, key="vis_wk",
                help="Navigate to any week to schedule shifts."
            )
            week_end = week_start + timedelta(days=6)
            st.caption(
                f"Scheduling week: **{week_start.strftime('%B %d')} – {week_end.strftime('%B %d, %Y')}**  ·  "
                "Click an employee on the left, then click a day to schedule."
            )
            st.divider()

            # Save week to session so the form can read it
            st.session_state.vis_week_start = week_start

            # Filter shifts for this week
            ws = shifts.copy()
            ws["shift_date"] = ws["start_datetime"].dt.date
            ws = ws[(ws["shift_date"] >= week_start) & (ws["shift_date"] <= week_end)]
            if len(ws) > 0 and len(employees) > 0:
                ws = ws.merge(employees[["id", "name", "role"]], left_on="employee_id", right_on="id", suffixes=("", "_e"))

            # Layout: employee panel | calendar grid
            left, right = st.columns([2, 7], gap="medium")

            # ── Employee Roster Panel ──────────────────────────────────────
            with left:
                st.markdown("**Click an employee to select them, then click a day to schedule.**")
                st.markdown("")
                sel_id = st.session_state.vis_emp_id

                for role_name in ROLES:
                    grp = employees[employees["role"] == role_name].sort_values("name")
                    if len(grp) == 0:
                        continue
                    color = ROLE_COLORS.get(role_name, "#888")
                    st.markdown(
                        f'<div style="background:{color};color:#fff;padding:2px 8px;'
                        f'border-radius:8px;font-size:0.78em;font-weight:700;margin-bottom:4px">'
                        f'{role_name}</div>',
                        unsafe_allow_html=True,
                    )
                    for _, emp in grp.iterrows():
                        is_sel     = (sel_id == int(emp["id"]))
                        can_sched, _ = check_employee_schedulable(int(emp["id"]), emp["role"], certs)
                        training   = st.session_state.get("training_mode", False)
                        locked     = not training and not can_sched
                        prefix     = "✓ " if is_sel else ("🔒 " if locked else "")
                        label      = f"{prefix}{emp['name']}"
                        btn_type   = "primary" if is_sel else "secondary"
                        if st.button(
                            label, key=f"vis_emp_{emp['id']}",
                            use_container_width=True, type=btn_type,
                            disabled=locked,
                            help="Missing or expired certifications — cannot schedule in Production Mode" if locked else None,
                        ):
                            if is_sel:
                                st.session_state.vis_emp_id       = None
                                st.session_state.vis_schedule_day = None
                            else:
                                st.session_state.vis_emp_id       = int(emp["id"])
                                st.session_state.vis_schedule_day = None
                            st.rerun()
                        if locked:
                            st.markdown(
                                '<span style="color:#F5A623;font-size:0.72em;margin-left:4px">'
                                'Cert issue — see Certifications tab</span>',
                                unsafe_allow_html=True,
                            )

                if sel_id is not None:
                    sel_row = employees[employees["id"] == sel_id]
                    if len(sel_row):
                        sel_name = sel_row.iloc[0]["name"]
                        sel_role = sel_row.iloc[0]["role"]
                        st.divider()
                        st.markdown(
                            f'**Selected:** {sel_name}  \n'
                            f'{role_pill(sel_role)}',
                            unsafe_allow_html=True,
                        )
                        streak, s_dates = get_consecutive_streak(sel_id, shifts)
                        level, icon = burnout_level(streak)
                        if streak >= BURNOUT_CAUTION:
                            st.warning(f"{icon} {streak} consecutive days scheduled")

            # ── Calendar Grid ──────────────────────────────────────────────
            with right:
                days     = [week_start + timedelta(days=i) for i in range(7)]
                day_cols = st.columns(7)

                for col_idx, (day, dcol) in enumerate(zip(days, day_cols)):
                    is_today = (day == today)
                    header_style = (
                        "background:#1E88E5;color:#fff;padding:4px 6px;border-radius:6px;text-align:center"
                        if is_today else
                        "background:#f0f2f6;padding:4px 6px;border-radius:6px;text-align:center"
                    )
                    dcol.markdown(
                        f'<div style="{header_style}"><b>{day.strftime("%a")}</b><br>'
                        f'<span style="font-size:0.85em">{day.strftime("%-m/%-d")}</span></div>',
                        unsafe_allow_html=True,
                    )

                    # Existing shift cards for this day
                    day_ws = ws[ws["shift_date"] == day] if len(ws) > 0 else pd.DataFrame()
                    for _, sr in day_ws.iterrows():
                        v_name = None
                        if pd.notna(sr.get("venue_id")) and len(venues) > 0:
                            v_row = venues[venues["id"] == int(sr["venue_id"])]
                            v_name = v_row.iloc[0]["name"] if len(v_row) else None
                        dcol.markdown(
                            shift_card_html(sr["name"], sr["role"], sr["start_datetime"], sr["end_datetime"], venue_name=v_name),
                            unsafe_allow_html=True,
                        )
                        if dcol.button("🗑", key=f"vis_del_{sr['id']}_{col_idx}", help="Remove shift"):
                            shifts = shifts[shifts["id"] != sr["id"]]
                            save_shifts(shifts)
                            st.rerun()

                    # "+" button — only when an employee is selected
                    if st.session_state.vis_emp_id is not None:
                        if dcol.button("＋", key=f"vis_add_{col_idx}", use_container_width=True, help=f"Schedule on {day.strftime('%b %d')}"):
                            st.session_state.vis_schedule_day = day
                            st.rerun()

                # ── Inline scheduling form (appears below grid) ────────────
                sel_id  = st.session_state.vis_emp_id
                sel_day = st.session_state.vis_schedule_day

                if sel_id is not None and sel_day is not None:
                    sel_row = employees[employees["id"] == sel_id]
                    if len(sel_row):
                        sel_emp = sel_row.iloc[0]
                        st.divider()
                        st.markdown(
                            f"### Schedule **{sel_emp['name']}** on "
                            f"{sel_day.strftime('%A, %B %d')}"
                        )
                        with st.form("vis_shift_form"):
                            fc1, fc2 = st.columns(2)
                            v_start = fc1.time_input("Start Time", value=time(9, 0), step=900)
                            v_end   = fc2.time_input("End Time",   value=time(17, 0), step=900)
                            venue_opts = {"— No venue assigned —": None}
                            venue_opts.update({v["name"]: int(v["id"]) for _, v in venues.iterrows()})
                            v_venue_label = st.selectbox("Venue / Station", list(venue_opts.keys()))
                            v_notes = st.text_input("Notes (optional)")
                            sc1, sc2 = st.columns(2)
                            confirm = sc1.form_submit_button("✅ Add Shift", type="primary", use_container_width=True)
                            cancel  = sc2.form_submit_button("Cancel", use_container_width=True)

                            if cancel:
                                st.session_state.vis_schedule_day = None
                                st.rerun()

                            if confirm:
                                start_dt = datetime.combine(sel_day, v_start)
                                end_dt   = datetime.combine(
                                    sel_day + timedelta(days=1) if v_end <= v_start else sel_day, v_end
                                )
                                hours    = (end_dt - start_dt).total_seconds() / 3600
                                training = st.session_state.get("training_mode", False)

                                # Certification gate (production mode only)
                                can_sched, cert_issues = check_employee_schedulable(
                                    sel_id, sel_emp["role"], certs
                                )
                                if not training and not can_sched:
                                    st.error(
                                        f"**Cannot schedule {sel_emp['name']} — certification required by California law:**\n\n"
                                        + "\n".join(f"- {i}" for i in cert_issues)
                                        + "\n\nEmployee must provide valid documentation before being scheduled. "
                                        "Use the Employee view to upload renewed certifications."
                                    )
                                # Duration gate — checked before anything else
                                elif hours > 16:
                                    st.error(
                                        f"🚫 **Shift Blocked — {hours:.1f} hours is not permitted.**  \n"
                                        "Shifts over 16 hours cannot be scheduled. "
                                        "Please correct the start or end time."
                                    )
                                else:
                                    viol, reason = check_turnaround(sel_id, start_dt, end_dt, shifts)
                                    if viol:
                                        st.error(f"🚫 **Blocked — 8h Turnaround Violation**\n\n{reason}")
                                    else:
                                        new_shift = pd.DataFrame([{
                                            "id": next_id(shifts), "employee_id": sel_id,
                                            "date": sel_day.isoformat(),
                                            "start_datetime": start_dt, "end_datetime": end_dt,
                                            "notes": v_notes.strip(),
                                            "venue_id": venue_opts[v_venue_label],
                                        }])
                                        shifts = pd.concat([shifts, new_shift], ignore_index=True)
                                        save_shifts(shifts)
                                        new_streak, _ = get_consecutive_streak(sel_id, shifts)
                                        lvl, b_icon = burnout_level(new_streak)
                                        st.session_state.vis_schedule_day = None
                                        if hours > 8:
                                            st.warning(
                                                f"⚠️ Shift saved — **{hours:.1f} hours** is a long shift. "
                                                "It appears yellow on the calendar as a reminder."
                                            )
                                        if lvl != "ok":
                                            st.warning(
                                                f"Shift added, but {b_icon} **{sel_emp['name']}** now has "
                                                f"**{new_streak} consecutive days** — review Burnout Monitor."
                                            )
                                        st.rerun()


    # ── Weekly View (read-only grid) ───────────────────────────────────────
    with tab_week:
        st.subheader("Weekly Schedule Grid")
        if len(shifts) == 0 or len(employees) == 0:
            st.info("Add employees and shifts to see the grid.")
        else:
            today       = datetime.today().date()
            default_mon = today - timedelta(days=today.weekday())
            wk_c1, wk_c2 = st.columns([2, 2])
            week_start = wk_c1.date_input("Week starting (Monday)", value=default_mon, key="wk_grid")
            week_end   = week_start + timedelta(days=6)
            venue_filter_opts = ["All Venues"] + venues["name"].tolist() if len(venues) > 0 else ["All Venues"]
            wk_venue = wk_c2.selectbox("Filter by Venue", venue_filter_opts, key="wk_venue")
            st.caption(f"{week_start.strftime('%B %d')} – {week_end.strftime('%B %d, %Y')}")

            ws = shifts.copy()
            ws["shift_date"] = ws["start_datetime"].dt.date
            ws = ws[(ws["shift_date"] >= week_start) & (ws["shift_date"] <= week_end)]
            if wk_venue != "All Venues" and len(venues) > 0:
                v_id = int(venues[venues["name"] == wk_venue].iloc[0]["id"])
                ws = ws[ws["venue_id"] == v_id]

            if len(ws) == 0:
                st.info("No shifts this week.")
            else:
                ws = ws.merge(employees[["id","name","role"]], left_on="employee_id", right_on="id")
                days     = [week_start + timedelta(days=i) for i in range(7)]
                day_cols = [d.strftime("%a %-m/%-d") for d in days]

                for role_name in ROLES:
                    role_emps = employees[employees["role"] == role_name].sort_values("name")
                    role_week = ws[ws["role"] == role_name]
                    if len(role_week) == 0:
                        continue
                    color = ROLE_COLORS.get(role_name, "#888")
                    st.markdown(
                        f'<h4 style="margin-top:1em"><span style="background:{color};color:#fff;'
                        f'padding:3px 14px;border-radius:14px">{role_name}s</span></h4>',
                        unsafe_allow_html=True,
                    )
                    rows, hrs_map = {}, {}
                    for _, emp in role_emps.iterrows():
                        row, total = {}, 0.0
                        for day, label in zip(days, day_cols):
                            ds = role_week[(role_week["employee_id"] == emp["id"]) & (role_week["shift_date"] == day)]
                            if len(ds):
                                s = ds.iloc[0]
                                h = (s["end_datetime"] - s["start_datetime"]).total_seconds() / 3600
                                total += h
                                row[label] = f"{s['start_datetime'].strftime('%-I:%M%p').lower()}–{s['end_datetime'].strftime('%-I:%M%p').lower()}"
                            else:
                                row[label] = ""
                        rows[emp["name"]] = row
                        hrs_map[emp["name"]] = f"{total:.1f}h"
                    gdf = pd.DataFrame(rows).T
                    gdf.columns = day_cols
                    gdf.index.name = "Employee"
                    gdf["Total Hrs"] = gdf.index.map(hrs_map)
                    st.dataframe(gdf, use_container_width=True, height=min(80 + 35 * len(gdf), 400))


    # ── Swap Requests ──────────────────────────────────────────────────────
    with tab_swaps:
        st.subheader("Shift Swap Requests")
        if len(swaps) == 0:
            st.info("No swap requests submitted yet.")
        else:
            swap_filter = st.selectbox("Filter", ["Pending", "All", "Approved", "Denied"], key="swf")
            fmap        = {"Pending": "pending", "Approved": "approved", "Denied": "denied", "All": None}
            disp_swaps  = swaps if fmap[swap_filter] is None else swaps[swaps["status"] == fmap[swap_filter]]

            if len(disp_swaps) == 0:
                st.info(f"No {swap_filter.lower()} requests.")
            else:
                for _, swap in disp_swaps.sort_values("requested_at", ascending=False).iterrows():
                    req_name  = employees.loc[employees["id"] == swap["requester_id"], "name"].values
                    tgt_name  = employees.loc[employees["id"] == swap["target_id"],    "name"].values
                    req_shift = shifts[shifts["id"] == swap["requester_shift_id"]]
                    tgt_shift = shifts[shifts["id"] == swap["target_shift_id"]]

                    rn = req_name[0]  if len(req_name)  else "Unknown"
                    tn = tgt_name[0]  if len(tgt_name)  else "Unknown"
                    rs = fmt_shift(req_shift.iloc[0]) if len(req_shift) else "Deleted shift"
                    ts = fmt_shift(tgt_shift.iloc[0]) if len(tgt_shift) else "Deleted shift"
                    si = {"pending": "🟡", "approved": "🟢", "denied": "🔴"}.get(swap["status"], "")

                    with st.container(border=True):
                        st.markdown(
                            f"{si} **{rn}** wants to swap with **{tn}**  "
                            f"— {pd.to_datetime(swap['requested_at']).strftime('%b %d %I:%M %p')}"
                        )
                        c1, c2 = st.columns(2)
                        c1.markdown(f"**{rn}'s shift:** {rs}")
                        c2.markdown(f"**{tn}'s shift:** {ts}")
                        if pd.notna(swap.get("requester_note")) and swap.get("requester_note"):
                            st.caption(f"Note from {rn}: {swap['requester_note']}")

                        if swap["status"] == "pending":
                            valid, val_reason = True, None
                            if len(req_shift) and len(tgt_shift):
                                valid, val_reason = validate_swap(
                                    int(swap["requester_shift_id"]), int(swap["target_shift_id"]), shifts
                                )
                            if not valid:
                                st.error(f"⚠️ Schedule changed — swap now violates 8h rule: {val_reason}")

                            mgr_note = st.text_input("Manager note (optional)", key=f"mn_{swap['id']}")
                            bc1, bc2 = st.columns(2)
                            if bc1.button("✅ Approve", key=f"app_{swap['id']}", type="primary", disabled=not valid):
                                if len(req_shift) and len(tgt_shift):
                                    shifts.loc[shifts["id"] == int(swap["requester_shift_id"]), "employee_id"] = int(swap["target_id"])
                                    shifts.loc[shifts["id"] == int(swap["target_shift_id"]),    "employee_id"] = int(swap["requester_id"])
                                    save_shifts(shifts)
                                swaps.loc[swaps["id"] == swap["id"], ["status", "resolved_at", "manager_notes"]] = ["approved", datetime.now().isoformat(), mgr_note]
                                save_swaps(swaps)
                                st.success("Swap approved and schedule updated.")
                                st.rerun()
                            if bc2.button("❌ Deny", key=f"deny_{swap['id']}"):
                                swaps.loc[swaps["id"] == swap["id"], ["status", "resolved_at", "manager_notes"]] = ["denied", datetime.now().isoformat(), mgr_note]
                                save_swaps(swaps)
                                st.rerun()
                        else:
                            resolved = pd.to_datetime(swap["resolved_at"]).strftime("%b %d") if pd.notna(swap.get("resolved_at")) else "—"
                            note_str = f" — Manager note: {swap['manager_notes']}" if pd.notna(swap.get("manager_notes")) and swap.get("manager_notes") else ""
                            st.caption(f"Resolved {resolved}{note_str}")


    # ── Certifications ─────────────────────────────────────────────────────
    with tab_certs:
        st.subheader("Certification Tracker")
        if len(employees) == 0:
            st.info("Add employees to track certifications.")
        else:
            any_issues = False
            for role_name in ROLES:
                grp = employees[employees["role"] == role_name]
                if len(grp) == 0:
                    continue
                color    = ROLE_COLORS.get(role_name, "#888")
                req_cts  = ROLE_CERTS.get(role_name, [])
                st.markdown(
                    f'<h4 style="margin-top:1em"><span style="background:{color};color:#fff;'
                    f'padding:3px 14px;border-radius:14px">{role_name}s</span></h4>',
                    unsafe_allow_html=True,
                )
                hcols = st.columns([2] + [1.8] * len(req_cts))
                hcols[0].markdown("**Employee**")
                for i, ct in enumerate(req_cts):
                    hcols[i + 1].markdown(f"**{ct}**")

                for _, emp in grp.iterrows():
                    rcols = st.columns([2] + [1.8] * len(req_cts))
                    rcols[0].write(emp["name"])
                    for i, ct in enumerate(req_cts):
                        ec = certs[(certs["employee_id"] == emp["id"]) & (certs["cert_type"] == ct)]
                        if len(ec) == 0:
                            rcols[i + 1].markdown("🔴 **Missing**")
                            any_issues = True
                        else:
                            latest = ec.sort_values("expiry_date", ascending=False).iloc[0]
                            label, cs = cert_badge(latest["expiry_date"])
                            rcols[i + 1].markdown(f"**{label}**  \n_{latest['expiry_date'].strftime('%b %d, %Y')}_")
                            if cs in ("red", "orange"):
                                any_issues = True

            if any_issues:
                st.warning("⚠️ Some certifications need attention. Prompt staff to upload renewals via the Employee view.")


    # ── Burnout Monitor ────────────────────────────────────────────────────
    with tab_burn:
        st.subheader("Employee Burnout Monitor")
        st.markdown(
            "Tracks consecutive working days across weeks. California labor law generally limits employees "
            "to **6 consecutive days** before requiring a day off."
        )
        st.markdown(
            "**Legend:** 🟢 1–4 days &nbsp;|&nbsp; 🟡 5 days — caution &nbsp;|&nbsp; "
            "🟠 6 days — at limit &nbsp;|&nbsp; 🔴 7+ days — potential violation"
        )
        st.divider()

        if len(employees) == 0:
            st.info("No employees yet.")
        elif len(shifts) == 0:
            st.info("No shifts scheduled yet.")
        else:
            today = date.today()
            any_risk = False

            for role_name in ROLES:
                grp = employees[employees["role"] == role_name].sort_values("name")
                if len(grp) == 0:
                    continue

                color = ROLE_COLORS.get(role_name, "#888")
                st.markdown(
                    f'<h4 style="margin-top:1em"><span style="background:{color};color:#fff;'
                    f'padding:3px 14px;border-radius:14px">{role_name}s</span></h4>',
                    unsafe_allow_html=True,
                )

                for _, emp in grp.iterrows():
                    streak, streak_dates = get_consecutive_streak(int(emp["id"]), shifts)
                    level, icon = burnout_level(streak)
                    if level != "ok":
                        any_risk = True

                    with st.container(border=(level != "ok")):
                        c1, c2, c3 = st.columns([2, 1, 4])
                        c1.markdown(f"**{emp['name']}**")
                        if streak == 0:
                            c2.write("—")
                            c3.write("No recent consecutive days")
                        else:
                            streak_label = f"{icon} **{streak} consecutive day{'s' if streak > 1 else ''}**"
                            c2.markdown(streak_label)

                            # Show the actual date range
                            if streak_dates:
                                first = streak_dates[0]
                                last  = streak_dates[-1]
                                # Highlight if spans previous week
                                crosses_week = any(d < today - timedelta(days=today.weekday()) for d in streak_dates) and \
                                               any(d >= today - timedelta(days=today.weekday()) for d in streak_dates)

                                date_str = f"{first.strftime('%b %d')} – {last.strftime('%b %d')}"
                                if crosses_week:
                                    date_str += " *(spans prior week)*"

                                c3.markdown(date_str)

                                if level == "danger":
                                    c3.error(
                                        f"🚨 **{emp['name']}** has worked {streak} consecutive days. "
                                        "This may violate CA labor law. A day off is required."
                                    )
                                elif level == "warning":
                                    c3.warning(
                                        f"**{emp['name']}** is at the 6-day maximum. "
                                        "Schedule a day off before adding more shifts."
                                    )
                                elif level == "caution":
                                    c3.info(f"Approaching limit. Consider scheduling a rest day soon.")

            if not any_risk:
                st.success("✅ All employees are within healthy working day limits.")


# ════════════════════════════════════════════════════════════════════════════
# EMPLOYEE VIEW
# ════════════════════════════════════════════════════════════════════════════
else:
    if current_emp is None:
        st.info("Select your name in the sidebar.")
        st.stop()

    emp_id   = int(current_emp["id"])
    emp_role = current_emp["role"]
    emp_name = current_emp["name"]

    st.subheader(f"Welcome, {emp_name}")
    st.markdown(role_pill(emp_role), unsafe_allow_html=True)

    issues = emp_cert_issues(emp_id, emp_role, certs)
    for ct, kind in issues:
        msg = {
            "missing":       f"⚠️ **{CERT_DESCRIPTIONS.get(ct, ct)}** is not on file. Please upload below.",
            "expired":       f"⚠️ **{CERT_DESCRIPTIONS.get(ct, ct)}** has expired. Please renew and upload.",
            "expiring_soon": f"🕐 **{CERT_DESCRIPTIONS.get(ct, ct)}** is expiring soon. Please renew and upload.",
        }.get(kind, "")
        if kind in ("missing", "expired"):
            st.error(msg)
        else:
            st.warning(msg)

    streak, _ = get_consecutive_streak(emp_id, shifts)
    level, icon = burnout_level(streak)
    if streak >= BURNOUT_CAUTION:
        st.warning(f"{icon} You have **{streak} consecutive working days** scheduled. Please speak with your manager about scheduling a rest day.")

    st.divider()

    tab_my_shifts, tab_swap_req, tab_my_certs = st.tabs([
        "📅 My Shifts", "🔄 Request Swap", "🎓 My Certifications"
    ])

    with tab_my_shifts:
        st.subheader("My Upcoming Shifts")
        my_shifts = shifts[(shifts["employee_id"] == emp_id) & (shifts["start_datetime"] >= datetime.now())].sort_values("start_datetime")
        if len(my_shifts) == 0:
            st.info("No upcoming shifts scheduled.")
        else:
            for _, s in my_shifts.iterrows():
                dur = (s["end_datetime"] - s["start_datetime"]).total_seconds() / 3600
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    c1.markdown(f"**{s['start_datetime'].strftime('%A, %B %d')}**")
                    c2.write(f"{s['start_datetime'].strftime('%I:%M %p')} → {s['end_datetime'].strftime('%I:%M %p')}")
                    c3.write(f"{dur:.1f}h")
                    if pd.notna(s.get("notes")) and s.get("notes"):
                        st.caption(f"Note: {s['notes']}")

    with tab_swap_req:
        st.subheader("Request a Shift Swap")
        my_future = shifts[(shifts["employee_id"] == emp_id) & (shifts["start_datetime"] >= datetime.now())].sort_values("start_datetime")

        if len(my_future) == 0:
            st.info("You have no upcoming shifts to swap.")
        elif len(employees) <= 1:
            st.info("No other employees to swap with.")
        else:
            with st.form("swap_form"):
                my_opts    = {fmt_shift(r): int(r["id"]) for _, r in my_future.iterrows()}
                my_sel     = st.selectbox("My shift to swap away", list(my_opts.keys()))
                other_emps = employees[employees["id"] != emp_id].sort_values("name")
                other_opts = {f"{r['name']}  ({r['role']})": int(r["id"]) for _, r in other_emps.iterrows()}
                target_sel = st.selectbox("Swap with", list(other_opts.keys()))
                target_id  = other_opts[target_sel]
                their_fut  = shifts[(shifts["employee_id"] == target_id) & (shifts["start_datetime"] >= datetime.now())].sort_values("start_datetime")
                their_opts = {fmt_shift(r): int(r["id"]) for _, r in their_fut.iterrows()} if len(their_fut) else {}
                their_sel  = st.selectbox("Their shift to take", list(their_opts.keys()) if their_opts else ["— none available —"])
                swap_note  = st.text_input("Reason (optional)")
                submitted  = st.form_submit_button("Submit Swap Request", type="primary", use_container_width=True)

                if submitted and their_opts:
                    my_sid    = my_opts[my_sel]
                    their_sid = their_opts[their_sel]
                    dup = swaps[(swaps["status"] == "pending") & (swaps["requester_shift_id"] == my_sid) & (swaps["target_shift_id"] == their_sid)]
                    if len(dup):
                        st.error("A pending swap request already exists for these shifts.")
                    else:
                        valid, reason = validate_swap(my_sid, their_sid, shifts)
                        if not valid:
                            st.error(f"🚫 Swap would violate the 8-hour rest rule.\n\n{reason}")
                        else:
                            new_swap = pd.DataFrame([{
                                "id": next_id(swaps), "requester_id": emp_id,
                                "requester_shift_id": my_sid, "target_id": target_id,
                                "target_shift_id": their_sid, "status": "pending",
                                "requester_note": swap_note.strip(),
                                "requested_at": datetime.now().isoformat(),
                                "resolved_at": None, "manager_notes": None,
                            }])
                            swaps = pd.concat([swaps, new_swap], ignore_index=True)
                            save_swaps(swaps)
                            st.success("✅ Swap request submitted. Awaiting manager approval.")
                            st.rerun()

        st.divider()
        st.subheader("My Swap History")
        my_swaps = swaps[swaps["requester_id"] == emp_id].sort_values("requested_at", ascending=False) if len(swaps) else pd.DataFrame()
        if len(my_swaps) == 0:
            st.info("No swap requests submitted.")
        else:
            for _, swap in my_swaps.iterrows():
                icon   = {"pending": "🟡 Pending", "approved": "🟢 Approved", "denied": "🔴 Denied"}.get(swap["status"], swap["status"])
                tgt    = employees[employees["id"] == swap["target_id"]]
                tname  = tgt.iloc[0]["name"] if len(tgt) else "Unknown"
                st.markdown(f"**{icon}** — swap with **{tname}**  ·  {pd.to_datetime(swap['requested_at']).strftime('%b %d')}")
                if pd.notna(swap.get("manager_notes")) and swap.get("manager_notes"):
                    st.caption(f"Manager note: {swap['manager_notes']}")

    with tab_my_certs:
        st.subheader("My Certifications")
        required = ROLE_CERTS.get(emp_role, [])
        if not required:
            st.info("No certifications required for your role.")
        else:
            for cert_type in required:
                st.markdown(f"### {CERT_DESCRIPTIONS.get(cert_type, cert_type)}")
                my_certs = certs[(certs["employee_id"] == emp_id) & (certs["cert_type"] == cert_type)].sort_values("expiry_date", ascending=False)
                if len(my_certs) == 0:
                    st.error("No certification on file.")
                else:
                    latest = my_certs.iloc[0]
                    label, _ = cert_badge(latest["expiry_date"])
                    st.markdown(f"**Status:** {label}")
                    st.markdown(f"**Expiry:** {latest['expiry_date'].strftime('%B %d, %Y')}")
                    if latest.get("file_name") and pd.notna(latest["file_name"]):
                        fp = os.path.join(CERT_DIR, str(latest["file_name"]))
                        if os.path.exists(fp):
                            with open(fp, "rb") as f:
                                st.download_button(f"Download {cert_type}", data=f, file_name=str(latest["file_name"]), key=f"dl_{emp_id}_{cert_type}")

                with st.expander(f"Upload / Renew {cert_type}"):
                    with st.form(f"cf_{emp_id}_{cert_type}", clear_on_submit=True):
                        new_exp = st.date_input("New expiry date", value=date.today() + timedelta(days=365))
                        upfile  = st.file_uploader("Certificate file (PDF, JPG, PNG)", type=["pdf", "jpg", "jpeg", "png"])
                        if st.form_submit_button("Save Certification", type="primary", use_container_width=True):
                            if new_exp <= date.today():
                                st.error("Expiry date must be in the future.")
                            else:
                                fname = None
                                if upfile:
                                    ext   = upfile.name.rsplit(".", 1)[-1]
                                    ts    = datetime.now().strftime("%Y%m%d%H%M%S")
                                    safe  = cert_type.replace(" ", "_").replace("/", "_")
                                    fname = f"{emp_id}_{safe}_{ts}.{ext}"
                                    with open(os.path.join(CERT_DIR, fname), "wb") as f:
                                        f.write(upfile.read())
                                new_cert = pd.DataFrame([{
                                    "id": next_id(certs), "employee_id": emp_id,
                                    "cert_type": cert_type, "expiry_date": new_exp.isoformat(),
                                    "file_name": fname, "uploaded_at": datetime.now().isoformat(),
                                }])
                                certs = pd.concat([certs, new_cert], ignore_index=True)
                                save_certs(certs)
                                st.success(f"✅ {cert_type} saved. Expires {new_exp.strftime('%B %d, %Y')}.")
                                st.rerun()
                st.divider()
