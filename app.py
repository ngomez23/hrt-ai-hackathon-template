import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date, time
import os
import json
import streamlit.components.v1 as components

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

    /* ── Management tabs (7-tab list) ── */
    .stTabs [data-baseweb="tab-list"]:has([data-baseweb="tab"]:nth-child(7)) [data-baseweb="tab"]:nth-child(2)::before {
        content: " ";
        display: inline-block; width: 14px; height: 14px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 2C8.1 2 5 5.1 5 9c0 5.2 7 13 7 13s7-7.8 7-13c0-3.9-3.1-7-7-7zm0 9.5c-1.4 0-2.5-1.1-2.5-2.5S10.6 6.5 12 6.5s2.5 1.1 2.5 2.5S13.4 11.5 12 11.5z' fill='%2322C55E'/%3E%3C/svg%3E");
        background-size: contain; background-repeat: no-repeat; background-position: center;
        margin-right: 5px; vertical-align: middle;
    }
    .stTabs [data-baseweb="tab-list"]:has([data-baseweb="tab"]:nth-child(7)) [data-baseweb="tab"]:nth-child(5)::before {
        content: " ";
        display: inline-block; width: 20px; height: 13px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 16'%3E%3Cline x1='1' y1='4' x2='13' y2='4' stroke='%23F5A623' stroke-width='2.5' stroke-linecap='round'/%3E%3Cpolyline points='10%2C1 13%2C4 10%2C7' fill='none' stroke='%23F5A623' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3Cline x1='19' y1='12' x2='7' y2='12' stroke='%231E88E5' stroke-width='2.5' stroke-linecap='round'/%3E%3Cpolyline points='10%2C9 7%2C12 10%2C15' fill='none' stroke='%231E88E5' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
        background-size: contain; background-repeat: no-repeat; background-position: center;
        margin-right: 5px; vertical-align: middle;
    }
    .stTabs [data-baseweb="tab-list"]:has([data-baseweb="tab"]:nth-child(7)) [data-baseweb="tab"]:nth-child(6)::before {
        content: " ";
        display: inline-block; width: 15px; height: 15px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpolygon points='12,0.5 14.94,2.97 18.76,2.70 19.69,6.41 22.94,8.45 21.5,12 22.94,15.55 19.69,17.59 18.76,21.30 14.94,21.03 12,23.5 9.06,21.03 5.24,21.30 4.31,17.59 1.06,15.55 2.5,12 1.06,8.45 4.31,6.41 5.24,2.70 9.06,2.97' fill='%23D4A017'/%3E%3Cpolyline points='8.5,12 10.8,14.8 15.5,9' fill='none' stroke='%230F2D52' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
        background-size: contain; background-repeat: no-repeat; background-position: center;
        margin-right: 5px; vertical-align: middle;
    }
    /* ── Employee tabs (3-tab list): swap arrows + cert seal ── */
    .stTabs [data-baseweb="tab-list"]:has([data-baseweb="tab"]:nth-child(3)):not(:has([data-baseweb="tab"]:nth-child(4))) [data-baseweb="tab"]:nth-child(2)::before {
        content: " ";
        display: inline-block; width: 20px; height: 13px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 16'%3E%3Cline x1='1' y1='4' x2='13' y2='4' stroke='%23F5A623' stroke-width='2.5' stroke-linecap='round'/%3E%3Cpolyline points='10%2C1 13%2C4 10%2C7' fill='none' stroke='%23F5A623' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3Cline x1='19' y1='12' x2='7' y2='12' stroke='%231E88E5' stroke-width='2.5' stroke-linecap='round'/%3E%3Cpolyline points='10%2C9 7%2C12 10%2C15' fill='none' stroke='%231E88E5' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
        background-size: contain; background-repeat: no-repeat; background-position: center;
        margin-right: 5px; vertical-align: middle;
    }
    .stTabs [data-baseweb="tab-list"]:has([data-baseweb="tab"]:nth-child(3)):not(:has([data-baseweb="tab"]:nth-child(4))) [data-baseweb="tab"]:nth-child(3)::before {
        content: " ";
        display: inline-block; width: 15px; height: 15px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpolygon points='12,0.5 14.94,2.97 18.76,2.70 19.69,6.41 22.94,8.45 21.5,12 22.94,15.55 19.69,17.59 18.76,21.30 14.94,21.03 12,23.5 9.06,21.03 5.24,21.30 4.31,17.59 1.06,15.55 2.5,12 1.06,8.45 4.31,6.41 5.24,2.70 9.06,2.97' fill='%23D4A017'/%3E%3Cpolyline points='8.5,12 10.8,14.8 15.5,9' fill='none' stroke='%230F2D52' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
        background-size: contain; background-repeat: no-repeat; background-position: center;
        margin-right: 5px; vertical-align: middle;
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
    /* ── Hide JS injection iframe ── */
    [data-testid="stCustomComponentV1"] {
        display: none !important;
        height: 0 !important;
    }
    /* ── Sidebar alert buttons (clickable warnings) ── */
    [data-testid="stSidebar"] .stButton button {
        background-color: rgba(245,166,35,0.15) !important;
        border: 1px solid rgba(245,166,35,0.45) !important;
        border-left: 3px solid #F5A623 !important;
        color: white !important;
        text-align: left !important;
        font-size: 0.83em !important;
        border-radius: 5px !important;
        margin: 2px 0 !important;
        padding: 5px 10px !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: rgba(245,166,35,0.28) !important;
        border-color: #F5A623 !important;
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

ROLES = ["Host/Hostess", "Busser", "Server", "Bartender", "Expeditor", "Cook", "Supervisor", "Manager"]

ROLE_COLORS = {
    # Front of House — cool primaries/secondaries
    "Host/Hostess": "#1A9E6E",   # green (secondary)
    "Busser":       "#00AEEF",   # bright sky blue
    "Server":       "#1E5FA8",   # blue (primary)
    "Bartender":    "#6A3499",   # violet (secondary)
    # Back of House — warm primaries/secondaries
    "Expeditor":    "#D4680A",   # orange (secondary)
    "Cook":         "#B02820",   # red (primary)
    # Management — black scale
    "Supervisor":   "#3A3A3A",   # dark charcoal
    "Manager":      "#111111",   # near black
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
        for col in ["resolved_at", "manager_notes", "requester_note", "status"]:
            if col in df.columns:
                df[col] = df[col].astype(object)
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
    if streak >= BURNOUT_DANGER:  return "danger",  "🔥🔥🔥"
    if streak >= BURNOUT_WARNING: return "warning",  "🔥🔥"
    if streak >= BURNOUT_CAUTION: return "caution",  "🔥"
    return "ok", ""


# ── Cert helpers ──────────────────────────────────────────────────────────────
def cert_badge(expiry_date):
    today = date.today()
    if expiry_date < today:
        return '<span style="color:#DC2626;font-weight:700">Expired</span>', "red"
    days_left = (expiry_date - today).days
    if days_left <= ALERT_DAYS:
        return f'<span style="color:#D97706;font-weight:700">Expiring Soon — {days_left} days left</span>', "orange"
    return '<span style="color:#16A34A;font-weight:700">Valid</span>', "green"

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
    ("vis_move_shift_id", None),
    ("vis_move_confirm", None),
    ("vis_dnd_ts", 0),
    ("vis_dnd_emp_id", None),
    ("vis_dnd_start", None),
    ("training_mode", False),
    ("jump_to_tab", None),
    ("mgr_tab", "Employees"),
]:
    if key not in st.session_state:
        st.session_state[key] = default


inject_theme()

DEMO_MODE = os.path.exists("data_ai/.demo_mode")

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
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "Manager"

    is_mgr = st.session_state.view_mode == "Manager"

    def _dot(active):
        if active:
            return ('<circle cx="7.5" cy="7.5" r="6.5" fill="#F5A623"/>'
                    '<circle cx="7.5" cy="7.5" r="2.6" fill="white"/>')
        return '<circle cx="7.5" cy="7.5" r="6" fill="none" stroke="rgba(255,255,255,0.55)" stroke-width="1.8"/>'

    st.markdown('<p style="font-weight:600;color:white;margin:0 0 4px 0;font-size:0.9rem;">View as</p>',
                unsafe_allow_html=True)

    _vcols = st.columns(2)
    if _vcols[0].button("Manager", type="primary" if is_mgr else "secondary",
                        use_container_width=True, key="vbtn_mgr"):
        st.session_state.view_mode = "Manager"
        st.rerun()
    if _vcols[1].button("Employee", type="primary" if not is_mgr else "secondary",
                        use_container_width=True, key="vbtn_emp"):
        st.session_state.view_mode = "Employee"
        st.rerun()

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
            if st.button(f"⚠️ {total_issues} certification issue(s)", key="sb_certs", use_container_width=True):
                st.session_state.jump_to_tab = "Certifications"
                st.rerun()

    n_pending = len(swaps[swaps["status"] == "pending"]) if len(swaps) > 0 else 0
    if n_pending:
        if st.button(f"🔄 {n_pending} swap request(s) pending", key="sb_swaps", use_container_width=True):
            st.session_state.jump_to_tab = "Swap Requests"
            st.rerun()

    if len(employees) > 0 and len(shifts) > 0:
        burnout_risks = [
            get_consecutive_streak(int(r["id"]), shifts)[0]
            for _, r in employees.iterrows()
        ]
        at_risk = sum(1 for s in burnout_risks if s >= BURNOUT_CAUTION)
        if at_risk:
            if st.button(f"🔥 {at_risk} employee(s) at burnout risk", key="sb_burn", use_container_width=True):
                st.session_state.jump_to_tab = "Burnout Monitor"
                st.rerun()

is_manager = mode == "Manager"

st.markdown(logo_html(width="340px"), unsafe_allow_html=True)
st.caption("Schedule staff · enforce labor law · manage swaps · track certifications · monitor burnout")

if DEMO_MODE:
    st.markdown(
        '<div style="background:#0F2D52;color:#F5A623;padding:12px 20px;border-radius:10px;'
        'margin:8px 0;display:flex;align-items:center;gap:12px">'
        '<span style="font-size:1.3em">▶</span>'
        '<span style="font-weight:800;font-size:1.05em;letter-spacing:0.5px">DEMO MODE</span>'
        '</div>',
        unsafe_allow_html=True,
    )

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
    if n_pending > 0:
        st.markdown(f"""<style>
        .stTabs [data-baseweb="tab-list"] [data-baseweb="tab"]:nth-child(5)::after {{
            content: "{n_pending}";
            background-color: #EF4444;
            color: white;
            font-size: 0.62em;
            font-weight: 800;
            border-radius: 10px;
            padding: 1px 5px;
            margin-left: 5px;
            vertical-align: middle;
            display: inline-block;
            line-height: 1.4;
        }}
        </style>""", unsafe_allow_html=True)

    tabs = st.tabs([
        "👥 Employees",
        "Venues",
        "📅 Visual Scheduler",
        "🗒️ Weekly View",
        "Swap Requests",
        "Certifications",
        "🔥 Burnout Monitor",
    ])
    tab_emp, tab_venues, tab_vis, tab_week, tab_swaps, tab_certs, tab_burn = tabs

    # Jump to tab if triggered from sidebar alert
    if st.session_state.get("jump_to_tab"):
        target = st.session_state.jump_to_tab
        st.session_state.jump_to_tab = None
        import streamlit.components.v1 as components
        components.html(f"""<script>
        setTimeout(function() {{
            var tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
            for (var i = 0; i < tabs.length; i++) {{
                if (tabs[i].textContent.indexOf('{target}') >= 0) {{
                    tabs[i].click(); break;
                }}
            }}
        }}, 300);
        </script>""", height=0, scrolling=False)

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
            week_start  = st.date_input("Week (Monday)", value=default_mon, key="vis_wk")
            st.session_state.vis_week_start = week_start

            # Day selector pills
            _day_labels = [(week_start + timedelta(days=i)).strftime("%a %-m/%-d") for i in range(7)]
            _day_dates  = [week_start + timedelta(days=i) for i in range(7)]
            _sel_day_idx = st.session_state.get("vis_day_idx", 0)
            # Scroll to today if it falls in this week
            for _di, _dd in enumerate(_day_dates):
                if _dd == today:
                    _sel_day_idx = _di
                    st.session_state.vis_day_idx = _di
                    break
            _pill_cols = st.columns(7)
            for _pi, _pl in enumerate(_day_labels):
                _is_today = (_day_dates[_pi] == today)
                _is_sel   = (_pi == _sel_day_idx)
                _pill_style = (
                    "primary" if _is_sel else "secondary"
                )
                if _pill_cols[_pi].button(
                    ("📅 " if _is_today else "") + _pl,
                    key=f"vis_day_pill_{_pi}",
                    type=_pill_style,
                    use_container_width=True,
                ):
                    st.session_state.vis_day_idx = _pi
                    st.session_state.vis_schedule_day = None
                    st.rerun()
            _sel_day_idx = st.session_state.get("vis_day_idx", 0)
            _view_date   = _day_dates[_sel_day_idx]

            # Gather shifts for this day
            _training = st.session_state.get("training_mode", False)
            _day_shifts_raw = shifts.copy()
            _day_shifts_raw["shift_date"] = _day_shifts_raw["start_datetime"].dt.date
            _day_shifts_raw = _day_shifts_raw[_day_shifts_raw["shift_date"] == _view_date]
            if len(_day_shifts_raw) > 0:
                _day_shifts_raw = _day_shifts_raw.merge(
                    employees[["id","name","role"]], left_on="employee_id", right_on="id", suffixes=("","_e"))

            # Build employee list
            _emp_list = []
            for _, _e in employees.iterrows():
                _can, _ = check_employee_schedulable(int(_e["id"]), _e["role"], certs)
                _emp_list.append({
                    "id": int(_e["id"]), "name": _e["name"], "role": _e["role"],
                    "color": ROLE_COLORS.get(_e["role"], "#888"),
                    "locked": not _training and not _can,
                })

            _TSTART, _TEND = 6, 24
            _TSPAN = _TEND - _TSTART
            _is_past_day = (_view_date < today)

            # ── Two-column layout: roster | timeline ──────────────────────
            _vis_left, _vis_right = st.columns([1, 4], gap="small")

            _sel_roster_id = st.session_state.get("vis_dnd_emp_id")

            with _vis_left:
                st.markdown(
                    '<p style="font-size:.75em;font-weight:700;color:#64748b;'
                    'letter-spacing:.5px;margin-bottom:4px">STAFF ROSTER</p>',
                    unsafe_allow_html=True,
                )
                _cur_role_r = None
                _sorted_roster = sorted(
                    _emp_list,
                    key=lambda e: (ROLES.index(e["role"]) if e["role"] in ROLES else 99, e["name"])
                )
                for _er in _sorted_roster:
                    if _er["role"] != _cur_role_r:
                        _cur_role_r = _er["role"]
                        st.markdown(
                            f'<div style="background:{_er["color"]};color:#fff;font-size:.63em;'
                            f'font-weight:700;padding:2px 7px;border-radius:4px;'
                            f'margin:8px 0 3px;letter-spacing:.3px">{_cur_role_r}</div>',
                            unsafe_allow_html=True,
                        )
                    _is_sel  = (_sel_roster_id == _er["id"])
                    _is_lock = _er["locked"]
                    _label   = ("🔒 " if _is_lock else "") + _er["name"]
                    if _is_lock:
                        st.markdown(
                            f'<div style="font-size:.77em;color:#9ca3af;padding:4px 6px;'
                            f'margin-bottom:3px;border:1px solid #fee2e2;border-radius:5px;'
                            f'background:#fff1f2">{_label}</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        _btn_type = "primary" if _is_sel else "secondary"
                        if st.button(
                            _label,
                            key=f"vis_roster_{_er['id']}",
                            type=_btn_type,
                            use_container_width=True,
                        ):
                            if _is_sel:
                                # Deselect
                                st.session_state.vis_dnd_emp_id   = None
                                st.session_state.vis_schedule_day = None
                            else:
                                st.session_state.vis_dnd_emp_id   = _er["id"]
                                st.session_state.vis_schedule_day = None
                            st.session_state.vis_dnd_start = None
                            st.rerun()

            with _vis_right:
                # ── Timeline display ──────────────────────────────────────
                def _hour_lbl(hh):
                    if hh == 12: return "12pm"
                    if hh == 24: return "12am"
                    return f"{hh % 12 or 12}{'am' if hh < 12 else 'pm'}"

                def _pct(h): return (h - _TSTART) / _TSPAN * 100

                _hdr_divs = "".join(
                    f'<div style="position:absolute;left:{_pct(hh):.2f}%;'
                    f'transform:translateX(-50%);font-size:.62em;color:#6b7280;font-weight:500;white-space:nowrap">'
                    f'{_hour_lbl(hh)}</div>'
                    for hh in range(_TSTART, _TEND + 1, 2)
                )

                _now_line_html = ""
                if _view_date == today:
                    _n = datetime.now()
                    _nh = _n.hour + _n.minute / 60
                    if _TSTART <= _nh <= _TEND:
                        _np = _pct(_nh)
                        _now_line_html = (
                            f'<div style="position:absolute;top:0;bottom:0;left:{_np:.2f}%;'
                            f'width:2px;background:#ef4444;opacity:.7;z-index:4;pointer-events:none">'
                            f'<div style="position:absolute;top:-17px;left:50%;transform:translateX(-50%);'
                            f'background:#ef4444;color:#fff;font-size:.58em;font-weight:700;'
                            f'padding:1px 4px;border-radius:3px;white-space:nowrap">'
                            f'{_n.strftime("%-I:%M %p")}</div></div>'
                        )

                _rows_html = ""
                _cur_role_t = None
                _row_idx = 0
                for _et in sorted(
                    _emp_list,
                    key=lambda e: (ROLES.index(e["role"]) if e["role"] in ROLES else 99, e["name"])
                ):
                    if _et["role"] != _cur_role_t:
                        _cur_role_t = _et["role"]
                        _rc = ROLE_COLORS.get(_cur_role_t, "#888")
                        _rows_html += (
                            f'<div style="display:flex;align-items:center;margin:7px 0 2px">'
                            f'<div style="background:{_rc};color:#fff;font-size:.63em;font-weight:700;'
                            f'letter-spacing:.3px;padding:2px 7px;border-radius:4px;white-space:nowrap;'
                            f'margin-right:6px">{_cur_role_t}</div>'
                            f'<div style="flex:1;height:1px;background:#e5e7eb"></div></div>'
                        )

                    _row_bg = "#f8fafc" if _row_idx % 2 == 0 else "#ffffff"
                    _row_idx += 1
                    _lock_html = '<span style="color:#ef4444;font-size:.75em"> 🔒</span>' if _et["locked"] else ""

                    _blks = ""
                    if len(_day_shifts_raw) > 0:
                        _es = _day_shifts_raw[_day_shifts_raw["employee_id"] == _et["id"]]
                        for _, _sr in _es.iterrows():
                            _vn = None
                            if pd.notna(_sr.get("venue_id")) and len(venues) > 0:
                                _vr = venues[venues["id"] == int(_sr["venue_id"])]
                                _vn = _vr.iloc[0]["name"] if len(_vr) else None
                            _sdt = pd.Timestamp(_sr["start_datetime"])
                            _edt = pd.Timestamp(_sr["end_datetime"])
                            _sh = _sdt.hour + _sdt.minute / 60
                            _eh = _edt.hour + _edt.minute / 60
                            if _eh <= _sh: _eh = _TEND
                            _l = max(_TSTART, _sh); _r = min(_TEND, _eh)
                            if _r > _l:
                                _lbl = f"{_sdt.strftime('%-I:%M %p')}–{_edt.strftime('%-I:%M %p')}"
                                if _vn: _lbl += f" · {_vn}"
                                _blks += (
                                    f'<div style="position:absolute;top:5px;bottom:5px;'
                                    f'left:{_pct(_l):.2f}%;width:{(_r-_l)/_TSPAN*100:.2f}%;'
                                    f'background:{_et["color"]};border-radius:4px;color:#fff;'
                                    f'font-size:.69em;font-weight:600;padding:2px 5px;overflow:hidden;'
                                    f'white-space:nowrap;text-overflow:ellipsis;'
                                    f'border-left:3px solid rgba(0,0,0,.18)" title="{_lbl}">{_lbl}</div>'
                                )

                    _gridlines = "".join(
                        f'<div style="position:absolute;top:0;bottom:0;left:{_pct(hh):.2f}%;'
                        f'border-left:1px solid {"#e5e7eb" if (hh-_TSTART)%2==0 else "#f3f4f6"}"></div>'
                        for hh in range(_TSTART, _TEND + 1)
                    )

                    _rows_html += (
                        f'<div style="display:flex;align-items:stretch;min-height:40px;background:{_row_bg};'
                        f'border-radius:4px;margin-bottom:2px;border:1px solid #f1f5f9">'
                        f'<div style="width:110px;flex-shrink:0;padding:4px 8px;font-size:.77em;'
                        f'font-weight:600;color:#374151;display:flex;align-items:center;'
                        f'border-right:1px solid #e5e7eb">{_et["name"]}{_lock_html}</div>'
                        f'<div style="flex:1;position:relative">{_gridlines}{_now_line_html}{_blks}</div>'
                        f'</div>'
                    )

                _n_roles_t = len(set(e["role"] for e in _emp_list))
                _tl_height = max(220, 36 + len(_emp_list) * 44 + _n_roles_t * 32)

                _full_html = f"""<style>
body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  background:transparent;overflow:hidden}}
</style>
<div style="padding:4px 0 6px">
  <div style="position:relative;height:22px;margin-left:110px;
    border-bottom:2px solid #e5e7eb;margin-bottom:2px">{_hdr_divs}</div>
  {_rows_html}
</div>"""
                components.html(_full_html, height=_tl_height, scrolling=False)

            # ── Status / caption ──────────────────────────────────────────
            st.caption(
                f"Showing **{_view_date.strftime('%A, %B %d')}** · "
                f"{len(_day_shifts_raw)} shift(s) scheduled"
                + (f" · **Click a staff name** to select them, then pick a start time"
                   if not _is_past_day and _sel_roster_id is None else "")
            )

            # ── Time-slot quick-picker (shown after roster selection) ─────
            _sel_roster_id = st.session_state.get("vis_dnd_emp_id")
            if _sel_roster_id and not _is_past_day:
                _sel_row = employees[employees["id"] == _sel_roster_id]
                _sel_name = _sel_row.iloc[0]["name"] if len(_sel_row) else "?"
                _sel_color = ROLE_COLORS.get(
                    _sel_row.iloc[0]["role"] if len(_sel_row) else "", "#1E88E5"
                )
                st.markdown(
                    f'<div style="background:{_sel_color}18;border:1.5px solid {_sel_color}44;'
                    f'border-radius:8px;padding:8px 12px;margin:6px 0 4px;font-size:.85em;'
                    f'font-weight:600;color:{_sel_color}">'
                    f'▸ {_sel_name} selected — pick a start time to schedule their shift:</div>',
                    unsafe_allow_html=True,
                )
                _slot_hours = list(range(6, 23))  # 6am to 10pm
                _slot_cols = st.columns(len(_slot_hours))
                for _si, _sh in enumerate(_slot_hours):
                    _sl = _hour_lbl(_sh)
                    if _slot_cols[_si].button(_sl, key=f"vis_slot_{_sh}", use_container_width=True):
                        st.session_state.vis_dnd_start    = time(_sh, 0)
                        st.session_state.vis_schedule_day = _view_date
                        st.rerun()

            # ── Manual add button (no selection needed) ───────────────────
            if not _is_past_day:
                _btn_label = "＋ Add Shift on " + _view_date.strftime("%A")
                if st.button(_btn_label, type="primary" if not _sel_roster_id else "secondary",
                             key="vis_open_form"):
                    st.session_state.vis_schedule_day = _view_date
                    st.session_state.vis_dnd_start    = None
                    st.rerun()

            # ── Move-confirm dialog ───────────────────────────────────────
            _mv = st.session_state.get("vis_move_confirm")
            if _mv:
                _mvr = shifts[shifts["id"] == _mv["shift_id"]]
                if len(_mvr):
                    _msr = _mvr.iloc[0]
                    _mve = employees[employees["id"] == _msr["employee_id"]]
                    _mvn = _mve.iloc[0]["name"] if len(_mve) else "?"
                    _old_d, _new_d = pd.Timestamp(_msr["start_datetime"]).date(), _mv["new_day"]
                    st.warning(f"Move **{_mvn}'s** shift from "
                               f"**{_old_d.strftime('%A %b %d')}** → **{_new_d.strftime('%A %b %d')}**?")
                    _ya, _na, _ = st.columns([2, 2, 5])
                    if _ya.button("✅ Yes, move it", type="primary", key="vis_mv_yes"):
                        _delta = (_new_d - _old_d).days
                        _idx   = shifts.index[shifts["id"] == _mv["shift_id"]][0]
                        shifts.at[_idx,"start_datetime"] = pd.Timestamp(_msr["start_datetime"]) + timedelta(days=_delta)
                        shifts.at[_idx,"end_datetime"]   = pd.Timestamp(_msr["end_datetime"])   + timedelta(days=_delta)
                        shifts.at[_idx,"date"]           = _new_d.isoformat()
                        save_shifts(shifts)
                        st.session_state.vis_move_confirm = None
                        st.rerun()
                    if _na.button("Cancel", key="vis_mv_no"):
                        st.session_state.vis_move_confirm = None
                        st.rerun()
                else:
                    st.session_state.vis_move_confirm = None

            # ── Add-shift form ────────────────────────────────────────────
            sel_day = st.session_state.get("vis_schedule_day")
            if sel_day is not None:
                _avail = {e["name"]: e["id"] for e in _emp_list if not e["locked"]}
                if not _avail:
                    st.warning("No employees available to schedule.")
                else:
                    st.divider()
                    _dnd_emp_id   = st.session_state.get("vis_dnd_emp_id")
                    _dnd_start_t  = st.session_state.get("vis_dnd_start")
                    _avail_names  = list(_avail.keys())
                    # Pre-select DnD employee if set
                    _dnd_emp_name = None
                    if _dnd_emp_id:
                        _dnd_row = employees[employees["id"] == _dnd_emp_id]
                        if len(_dnd_row):
                            _dnd_emp_name = _dnd_row.iloc[0]["name"]
                    _default_emp_idx = (
                        _avail_names.index(_dnd_emp_name)
                        if _dnd_emp_name and _dnd_emp_name in _avail_names else 0
                    )
                    st.markdown(f"### Add Shift — {sel_day.strftime('%A, %B %d')}")
                    with st.form("vis_shift_form"):
                        v_emp_label = st.selectbox("Employee", _avail_names, index=_default_emp_idx)
                        sel_id  = _avail[v_emp_label]
                        sel_emp = employees[employees["id"] == sel_id].iloc[0]
                        fc1, fc2 = st.columns(2)
                        _default_start = _dnd_start_t if _dnd_start_t else time(9, 0)
                        # Default end = start + 8h, capped at 23:00
                        _default_end_h = min(23, _default_start.hour + 8)
                        _default_end   = time(_default_end_h, _default_start.minute)
                        v_start = fc1.time_input("Start Time", value=_default_start, step=900)
                        v_end   = fc2.time_input("End Time",   value=_default_end,   step=900)
                        venue_opts = {"— No venue assigned —": None}
                        venue_opts.update({v["name"]: int(v["id"]) for _, v in venues.iterrows()})
                        v_venue_label = st.selectbox("Venue / Station", list(venue_opts.keys()))
                        v_notes = st.text_input("Notes (optional)")
                        sc1, sc2 = st.columns(2)
                        confirm = sc1.form_submit_button("✅ Add Shift", type="primary", use_container_width=True)
                        cancel  = sc2.form_submit_button("Cancel", use_container_width=True)
                        if cancel:
                            st.session_state.vis_schedule_day = None
                            st.session_state.vis_dnd_emp_id   = None
                            st.session_state.vis_dnd_start    = None
                            st.rerun()
                        if confirm:
                            start_dt = datetime.combine(sel_day, v_start)
                            end_dt   = datetime.combine(
                                sel_day + timedelta(days=1) if v_end <= v_start else sel_day, v_end)
                            hours = (end_dt - start_dt).total_seconds() / 3600
                            training = st.session_state.get("training_mode", False)
                            can_sched, cert_issues = check_employee_schedulable(sel_id, sel_emp["role"], certs)
                            if not training and not can_sched:
                                st.error("Cert issue:\n\n" + "\n".join(f"- {i}" for i in cert_issues))
                            elif hours > 16:
                                st.error(f"🚫 {hours:.1f}h exceeds the 16-hour maximum.")
                            else:
                                viol, reason = check_turnaround(sel_id, start_dt, end_dt, shifts)
                                if viol:
                                    st.error(f"🚫 8h turnaround: {reason}")
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
                                    lvl, b_icon   = burnout_level(new_streak)
                                    st.session_state.vis_schedule_day = None
                                    st.session_state.vis_dnd_emp_id   = None
                                    st.session_state.vis_dnd_start    = None
                                    if hours > 8:
                                        st.warning(f"⚠️ Saved — {hours:.1f}h is a long shift.")
                                    if lvl != "ok":
                                        st.warning(f"Shift added. {b_icon} **{sel_emp['name']}** now "
                                                   f"has **{new_streak} consecutive days**.")
                                    st.rerun()

            # ── Move / remove this day's shifts ───────────────────────────
            if len(_day_shifts_raw) > 0:
                with st.expander("Move or remove a shift on this day"):
                    for _, _sr2 in _day_shifts_raw.iterrows():
                        _st2 = pd.Timestamp(_sr2["start_datetime"])
                        _et2 = pd.Timestamp(_sr2["end_datetime"])
                        _lbl2 = f"{_sr2['name']} · {_st2.strftime('%-I:%M %p')}–{_et2.strftime('%-I:%M %p')}"
                        _ec2  = ROLE_COLORS.get(_sr2["role"], "#888")
                        _ra, _rb, _rc3 = st.columns([5, 2, 1])
                        _ra.markdown(
                            f'<div style="background:{_ec2};color:#fff;border-radius:4px;padding:4px 8px;font-size:.82em;font-weight:600">{_lbl2}</div>',
                            unsafe_allow_html=True)
                        if _rb.button("Move to day…", key=f"vis_mv_open_{int(_sr2['id'])}"):
                            st.session_state.vis_move_confirm  = None
                            st.session_state.vis_move_shift_id = int(_sr2["id"])
                            st.rerun()
                        if _rc3.button("✕", key=f"vis_rm_{int(_sr2['id'])}"):
                            shifts = shifts[shifts["id"] != int(_sr2["id"])]
                            save_shifts(shifts)
                            st.rerun()

            _msid = st.session_state.get("vis_move_shift_id")
            if _msid and not st.session_state.get("vis_move_confirm"):
                _mr = shifts[shifts["id"] == _msid]
                if len(_mr):
                    _ms  = _mr.iloc[0]
                    _mse = employees[employees["id"] == _ms["employee_id"]]
                    _mn  = _mse.iloc[0]["name"] if len(_mse) else "?"
                    _od  = pd.Timestamp(_ms["start_datetime"]).date()
                    st.info(f"Moving **{_mn}'s** shift ({_od.strftime('%A, %B %d')}) — pick a new day:")
                    _p1, _p2, _p3 = st.columns([3, 2, 2])
                    _week_start2 = week_start
                    _mvlbls = [(week_start + timedelta(days=i)).strftime("%a %-m/%-d") for i in range(7)]
                    _mvsel  = _p1.selectbox("New day", _mvlbls, key="vis_mv_day_sel")
                    _mvoff  = _mvlbls.index(_mvsel)
                    _mvnd   = week_start + timedelta(days=_mvoff)
                    if _p2.button("Move here →", type="primary", key="vis_mv_submit"):
                        st.session_state.vis_move_confirm  = {"shift_id": _msid, "new_day": _mvnd}
                        st.session_state.vis_move_shift_id = None
                        st.rerun()
                    if _p3.button("Cancel", key="vis_mv_cancel"):
                        st.session_state.vis_move_shift_id = None
                        st.rerun()
                else:
                    st.session_state.vis_move_shift_id = None


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
                    badge_map = {
                        "pending":  '<span style="background:#FEF3C7;color:#92400E;border:1px solid #F5A623;border-radius:4px;padding:2px 8px;font-size:0.78em;font-weight:700">⇄ Pending</span>',
                        "approved": '<span style="background:#D1FAE5;color:#065F46;border:1px solid #34D399;border-radius:4px;padding:2px 8px;font-size:0.78em;font-weight:700">⇄ Approved</span>',
                        "denied":   '<span style="background:#FEE2E2;color:#7F1D1D;border:1px solid #F87171;border-radius:4px;padding:2px 8px;font-size:0.78em;font-weight:700">⇄ Denied</span>',
                    }
                    si = badge_map.get(swap["status"], "")

                    with st.container(border=True):
                        st.markdown(
                            f"{si} **{rn}** wants to swap with **{tn}**  "
                            f"— {pd.to_datetime(swap['requested_at']).strftime('%b %d %I:%M %p')}",
                            unsafe_allow_html=True
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
                                swaps.loc[swaps["id"] == swap["id"], "status"]       = "approved"
                                swaps.loc[swaps["id"] == swap["id"], "resolved_at"]  = datetime.now().isoformat()
                                swaps.loc[swaps["id"] == swap["id"], "manager_notes"] = mgr_note
                                save_swaps(swaps)
                                st.success("Swap approved and schedule updated.")
                                st.rerun()
                            if bc2.button("❌ Deny", key=f"deny_{swap['id']}"):
                                swaps.loc[swaps["id"] == swap["id"], "status"]       = "denied"
                                swaps.loc[swaps["id"] == swap["id"], "resolved_at"]  = datetime.now().isoformat()
                                swaps.loc[swaps["id"] == swap["id"], "manager_notes"] = mgr_note
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
            def cert_status_badge(emp_id, cert_type):
                today = date.today()
                ec = certs[(certs["employee_id"] == emp_id) & (certs["cert_type"] == cert_type)]
                if len(ec) == 0:
                    return ("Not on file", "#f1f5f9", "#374151", True)
                latest = ec.sort_values("expiry_date", ascending=False).iloc[0]
                exp = latest["expiry_date"]
                if exp < today:
                    return (f"Expired · {exp.strftime('%b %d, %Y')}", "#fee2e2", "#7f1d1d", True)
                days_left = (exp - today).days
                if days_left <= ALERT_DAYS:
                    return (f"Expires {exp.strftime('%b %d, %Y')}", "#fef9c3", "#713f12", True)
                return (f"Valid · {exp.strftime('%b %d, %Y')}", "#dcfce7", "#166534", False)

            any_issues = False
            for role_name in ROLES:
                grp = employees[employees["role"] == role_name].sort_values("name")
                if len(grp) == 0:
                    continue
                color   = ROLE_COLORS.get(role_name, "#888")
                req_cts = ROLE_CERTS.get(role_name, [])

                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;margin:20px 0 8px 0">'
                    f'<span style="background:{color};color:#fff;padding:3px 14px;border-radius:20px;'
                    f'font-size:0.82em;font-weight:700">{role_name}s</span></div>',
                    unsafe_allow_html=True,
                )

                cards_html = ""
                for _, emp in grp.iterrows():
                    cert_pills = ""
                    emp_has_issue = False
                    for ct in req_cts:
                        label, bg, fg, is_issue = cert_status_badge(int(emp["id"]), ct)
                        if is_issue:
                            emp_has_issue = True
                            any_issues = True
                        cert_pills += (
                            f'<div style="display:flex;flex-direction:column;gap:2px;min-width:160px">'
                            f'<span style="font-size:0.72em;color:#718096;font-weight:600;text-transform:uppercase;'
                            f'letter-spacing:0.5px">{ct}</span>'
                            f'<span style="background:{bg};color:{fg};font-size:0.78em;font-weight:600;'
                            f'padding:3px 10px;border-radius:6px;display:inline-block">{label}</span>'
                            f'</div>'
                        )
                    border_color = "#FCA5A5" if emp_has_issue else "#e2e8f0"
                    left_bar     = "#EF4444" if emp_has_issue else "#e2e8f0"
                    cards_html += (
                        f'<div style="display:flex;align-items:center;gap:20px;background:#fff;'
                        f'border:1px solid {border_color};border-left:4px solid {left_bar};'
                        f'border-radius:8px;padding:10px 16px;margin-bottom:8px;flex-wrap:wrap">'
                        f'<span style="font-weight:700;font-size:0.95em;color:#0F2D52;min-width:140px">'
                        f'{emp["name"]}</span>'
                        f'<div style="display:flex;gap:16px;flex-wrap:wrap">{cert_pills}</div>'
                        f'</div>'
                    )
                st.markdown(cards_html, unsafe_allow_html=True)

            if any_issues:
                st.markdown(
                    '<div style="background:#fff7ed;border:1px solid #FDBA74;border-radius:8px;'
                    'padding:12px 16px;color:#7c2d12;font-size:0.88em;margin-top:12px">'
                    '⚠️ Some certifications need attention. Prompt staff to upload renewals via the Employee view.</div>',
                    unsafe_allow_html=True,
                )


    # ── Burnout Monitor ────────────────────────────────────────────────────
    with tab_burn:
        st.subheader("Employee Burnout Monitor")

        # Header info + legend bar
        st.markdown("""
        <div style="background:#f7f9fc;border-radius:10px;padding:14px 18px;margin-bottom:16px;border:1px solid #e2e8f0">
            <span style="color:#0F2D52;font-size:0.92em">
            Tracks consecutive working days across weeks. California labor law limits employees to
            <strong>6 consecutive days</strong> before a required day off.
            </span>
            <div style="display:flex;gap:18px;margin-top:10px;flex-wrap:wrap">
                <span style="display:flex;align-items:center;gap:6px;font-size:0.82em">✅ 1–4 days &nbsp;Healthy</span>
                <span style="display:flex;align-items:center;gap:6px;font-size:0.82em">🔥 5 days &nbsp;Caution</span>
                <span style="display:flex;align-items:center;gap:6px;font-size:0.82em">🔥🔥 6 days &nbsp;At Limit</span>
                <span style="display:flex;align-items:center;gap:6px;font-size:0.82em">🔥🔥🔥 7+ days &nbsp;Violation Risk</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if len(employees) == 0:
            st.info("No employees yet.")
        elif len(shifts) == 0:
            st.info("No shifts scheduled yet.")
        else:
            today = date.today()
            any_risk = False

            LEVEL_META = {
                "ok":      {"bar": "#22C55E", "bg": "#ffffff",   "border": "#e2e8f0", "chip_bg": "#dcfce7", "chip_fg": "#166534", "label": "Healthy"},
                "caution": {"bar": "#EAB308", "bg": "#fefce8",   "border": "#FDE047", "chip_bg": "#fef9c3", "chip_fg": "#713f12", "label": "Caution"},
                "warning": {"bar": "#F97316", "bg": "#fff7ed",   "border": "#FDBA74", "chip_bg": "#ffedd5", "chip_fg": "#7c2d12", "label": "At Limit"},
                "danger":  {"bar": "#EF4444", "bg": "#fff5f5",   "border": "#FCA5A5", "chip_bg": "#fee2e2", "chip_fg": "#7f1d1d", "label": "Violation Risk"},
            }

            for role_name in ROLES:
                grp = employees[employees["role"] == role_name].sort_values("name")
                if len(grp) == 0:
                    continue

                role_color = ROLE_COLORS.get(role_name, "#888")
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;margin:20px 0 8px 0">'
                    f'<span style="background:{role_color};color:#fff;padding:3px 14px;border-radius:20px;'
                    f'font-size:0.82em;font-weight:700;letter-spacing:0.3px">{role_name}s</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                cards_html = ""
                for _, emp in grp.iterrows():
                    streak, streak_dates = get_consecutive_streak(int(emp["id"]), shifts)
                    level, _ = burnout_level(streak)
                    if level != "ok":
                        any_risk = True

                    m = LEVEL_META[level]

                    # Date range string
                    if streak_dates:
                        first, last = streak_dates[0], streak_dates[-1]
                        crosses_week = (
                            any(d < today - timedelta(days=today.weekday()) for d in streak_dates) and
                            any(d >= today - timedelta(days=today.weekday()) for d in streak_dates)
                        )
                        date_range = f"{first.strftime('%b %d')} – {last.strftime('%b %d')}"
                        if crosses_week:
                            date_range += " · spans prior week"
                    else:
                        date_range = "No recent shifts"

                    fire_map  = {"ok": "", "caution": "🔥", "warning": "🔥🔥", "danger": "🔥🔥🔥"}
                    fire_size = {"ok": "1em", "caution": "1.1em", "warning": "1.25em", "danger": "1.4em"}

                    # Alert line
                    alert_html = ""
                    if level == "danger":
                        alert_html = (
                            f'<div style="margin-top:8px;font-size:0.78em;color:#7f1d1d;'
                            f'background:#fee2e2;border-radius:6px;padding:5px 10px">'
                            f'Day off required — potential CA labor law violation.</div>'
                        )
                    elif level == "warning":
                        alert_html = (
                            f'<div style="margin-top:8px;font-size:0.78em;color:#7c2d12;'
                            f'background:#ffedd5;border-radius:6px;padding:5px 10px">'
                            f'At the 6-day maximum. Schedule a rest day before adding more shifts.</div>'
                        )
                    elif level == "caution":
                        alert_html = (
                            f'<div style="margin-top:8px;font-size:0.78em;color:#713f12;'
                            f'background:#fef9c3;border-radius:6px;padding:5px 10px">'
                            f'Approaching the limit. Consider scheduling a rest day soon.</div>'
                        )

                    streak_text = f"{streak} day{'s' if streak != 1 else ''}" if streak > 0 else "—"

                    cards_html += (
                        f'<div style="background:{m["bg"]};border:1px solid {m["border"]};border-left:5px solid {m["bar"]};'
                        f'border-radius:10px;padding:12px 16px;margin-bottom:10px">'
                        f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:6px">'
                        f'<span style="font-weight:700;font-size:0.97em;color:#0F2D52">{emp["name"]}</span>'
                        f'<span style="display:flex;align-items:center;gap:8px">'
                        f'<span style="background:{m["chip_bg"]};color:{m["chip_fg"]};font-size:0.75em;font-weight:700;padding:2px 10px;border-radius:20px">{m["label"]}</span>'
                        f'<span style="font-size:0.85em;color:#4A5568;font-weight:600">{streak_text} consecutive</span>'
                        f'</span></div>'
                        f'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">'
                        + (f'<span style="font-size:{fire_size[level]};letter-spacing:2px">{fire_map[level]}</span>' if level != "ok" else '')
                        + f'<span style="font-size:0.8em;color:#718096">{date_range}</span>'
                        f'</div>'
                        + alert_html
                        + '</div>'
                    )

                st.markdown(cards_html, unsafe_allow_html=True)

            if not any_risk:
                st.markdown(
                    '<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;'
                    'padding:16px 20px;color:#166534;font-weight:600;font-size:0.95em;margin-top:12px">'
                    '✓ All employees are within healthy working day limits.</div>',
                    unsafe_allow_html=True,
                )


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
        "📅 My Shifts", "Request Swap", "My Certifications"
    ])

    with tab_my_shifts:
        st.subheader("My Schedule")
        all_my_shifts = shifts[shifts["employee_id"] == emp_id].copy()

        # ── Visual planner: 4-week rolling calendar ────────────────────────
        today_d = date.today()
        cal_start = today_d - timedelta(days=today_d.weekday())  # Monday of current week
        cal_end   = cal_start + timedelta(weeks=4) - timedelta(days=1)

        # Build shift lookup by date
        shift_by_date = {}
        for _, s in all_my_shifts.iterrows():
            sd = pd.Timestamp(s["start_datetime"]).date()
            if cal_start <= sd <= cal_end:
                shift_by_date.setdefault(sd, []).append(s)

        role_color = ROLE_COLORS.get(emp_role, "#0F2D52")

        # Render 4-week grid
        day_headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        header_html = "".join(
            f'<div style="text-align:center;font-weight:700;font-size:0.78em;'
            f'color:#718096;padding:4px 0">{d}</div>' for d in day_headers
        )

        cells_html = ""
        for week in range(4):
            for dow in range(7):
                d = cal_start + timedelta(weeks=week, days=dow)
                is_today = (d == today_d)
                is_past  = (d < today_d)
                day_shifts = shift_by_date.get(d, [])

                border = "2px solid #F5A623" if is_today else "1px solid #e2e8f0"
                bg     = "#fffbeb" if is_today else ("#f8fafc" if is_past else "#ffffff")
                num_style = (
                    f"background:#F5A623;color:#fff;border-radius:50%;width:22px;height:22px;"
                    f"display:inline-flex;align-items:center;justify-content:center;"
                    f"font-size:0.78em;font-weight:700"
                    if is_today else
                    f"font-size:0.78em;font-weight:{'700' if day_shifts else '400'};"
                    f"color:{'#0F2D52' if not is_past else '#adb5bd'}"
                )
                shift_blocks = ""
                for s in day_shifts:
                    t_start = pd.Timestamp(s["start_datetime"]).strftime("%-I:%M%p").lower()
                    t_end   = pd.Timestamp(s["end_datetime"]).strftime("%-I:%M%p").lower()
                    vn = ""
                    if pd.notna(s.get("venue_id")) and len(venues) > 0:
                        vrow = venues[venues["id"] == int(s["venue_id"])]
                        if len(vrow):
                            vn = f'<div style="font-size:0.72em;opacity:0.85;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{vrow.iloc[0]["name"]}</div>'
                    shift_blocks += (
                        f'<div style="background:{role_color};color:#fff;border-radius:4px;'
                        f'padding:2px 5px;margin-top:3px;font-size:0.72em;font-weight:600;line-height:1.3">'
                        f'{t_start}–{t_end}{vn}</div>'
                    )

                cells_html += (
                    f'<div style="border:{border};background:{bg};border-radius:7px;'
                    f'padding:5px 6px;min-height:72px;position:relative">'
                    f'<span style="{num_style}">{d.day}</span>'
                    f'{shift_blocks}'
                    f'</div>'
                )

        planner_html = (
            f'<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:5px;margin-bottom:16px">'
            f'{header_html}{cells_html}</div>'
        )
        st.markdown(planner_html, unsafe_allow_html=True)

        # ── Upcoming shift list ────────────────────────────────────────────
        st.divider()
        st.markdown("**Upcoming Shifts**")
        my_upcoming = all_my_shifts[all_my_shifts["start_datetime"] >= datetime.now()].sort_values("start_datetime")
        if len(my_upcoming) == 0:
            st.info("No upcoming shifts scheduled.")
        else:
            for _, s in my_upcoming.iterrows():
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
                _ibadge = {
                    "pending":  '<span style="background:#FEF3C7;color:#92400E;border:1px solid #F5A623;border-radius:4px;padding:2px 8px;font-size:0.78em;font-weight:700">⇄ Pending</span>',
                    "approved": '<span style="background:#D1FAE5;color:#065F46;border:1px solid #34D399;border-radius:4px;padding:2px 8px;font-size:0.78em;font-weight:700">⇄ Approved</span>',
                    "denied":   '<span style="background:#FEE2E2;color:#7F1D1D;border:1px solid #F87171;border-radius:4px;padding:2px 8px;font-size:0.78em;font-weight:700">⇄ Denied</span>',
                }.get(swap["status"], swap["status"])
                tgt    = employees[employees["id"] == swap["target_id"]]
                tname  = tgt.iloc[0]["name"] if len(tgt) else "Unknown"
                st.markdown(f"{_ibadge} — swap with **{tname}**  ·  {pd.to_datetime(swap['requested_at']).strftime('%b %d')}", unsafe_allow_html=True)
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
                    st.markdown(f"**Status:** {label}", unsafe_allow_html=True)
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
