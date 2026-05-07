/demo will preload the schedule with employee and scheduling data so the viewer can understand how the app works.

Steps:
1. Run this Python script to generate demo data and create the demo flag:
```
python3 << 'EOF'
import pandas as pd, os
from datetime import datetime

os.makedirs("data_ai", exist_ok=True)
open("data_ai/.demo_mode", "w").close()

employees = pd.DataFrame([
    {"id":1,  "name":"Maria Santos",     "role":"Server",       "email":"maria@example.com",   "phone":"555-0101"},
    {"id":2,  "name":"James Kim",        "role":"Server",       "email":"james@example.com",   "phone":"555-0102"},
    {"id":3,  "name":"Ashley Torres",    "role":"Server",       "email":"ashley@example.com",  "phone":"555-0103"},
    {"id":4,  "name":"Carlos Rivera",    "role":"Bartender",    "email":"carlos@example.com",  "phone":"555-0104"},
    {"id":5,  "name":"Priya Patel",      "role":"Bartender",    "email":"priya@example.com",   "phone":"555-0105"},
    {"id":6,  "name":"Derek Washington", "role":"Host/Hostess", "email":"derek@example.com",   "phone":"555-0106"},
    {"id":7,  "name":"Sofia Chen",       "role":"Cook",         "email":"sofia@example.com",   "phone":"555-0107"},
    {"id":8,  "name":"Marcus Johnson",   "role":"Cook",         "email":"marcus@example.com",  "phone":"555-0108"},
    {"id":9,  "name":"Tyler Rodriguez",  "role":"Busser",       "email":"tyler@example.com",   "phone":"555-0109"},
    {"id":10, "name":"Aisha Thompson",   "role":"Expeditor",    "email":"aisha@example.com",   "phone":"555-0110"},
    {"id":11, "name":"Rachel Lee",       "role":"Supervisor",   "email":"rachel@example.com",  "phone":"555-0111"},
    {"id":12, "name":"David Park",       "role":"Manager",      "email":"david@example.com",   "phone":"555-0112"},
])
employees.to_csv("data_ai/employees.csv", index=False)

venues = pd.DataFrame([
    {"id":1, "name":"Main Dining Room", "type":"Restaurant",   "description":"Ground floor, seats 120"},
    {"id":2, "name":"Rooftop Bar",      "type":"Rooftop Bar",  "description":"Level 12, open-air, seats 40"},
    {"id":3, "name":"Pool Bar",         "type":"Pool Bar",     "description":"Poolside, casual service"},
    {"id":4, "name":"Banquet Hall A",   "type":"Banquet Hall", "description":"Seats 200, events & private dining"},
])
venues.to_csv("data_ai/venues.csv", index=False)

def s(sid, eid, d, sh, sm, eh, em, venue_id=None, notes=""):
    start = datetime(2026, 5, d, sh, sm)
    end   = datetime(2026, 5, d if eh > sh else d+1, eh, em)
    return {"id":sid,"employee_id":eid,"date":f"2026-05-{d:02d}","start_datetime":start,"end_datetime":end,"notes":notes,"venue_id":venue_id}

shifts = pd.DataFrame([
    s(1,1,4,9,0,17,0,1),s(2,1,5,9,0,17,0,1),s(3,1,6,11,0,19,0,1),s(4,1,7,9,0,17,0,1),s(5,1,8,17,0,23,0,1),s(6,1,9,10,0,18,0,1),
    s(7,4,4,17,0,23,0,2),s(8,4,5,17,0,23,0,2),s(9,4,6,17,0,23,0,2),s(10,4,7,17,0,23,0,2),s(11,4,8,17,0,23,0,2),s(12,4,9,12,0,22,0,2,notes="Long cover shift"),s(13,4,10,15,0,23,0,2),
    s(14,6,4,10,0,18,0,1),s(15,6,5,10,0,18,0,1),s(16,6,6,10,0,18,0,1),s(17,6,7,10,0,18,0,1),s(18,6,8,10,0,18,0,1),
    s(19,2,4,17,0,23,0,1),s(20,2,6,17,0,23,0,1),s(21,2,8,11,0,19,0,4),s(22,2,9,17,0,23,0,1),
    s(23,3,5,11,0,19,0,1),s(24,3,7,11,0,19,0,1),s(25,3,9,11,0,19,0,1),
    s(26,5,5,16,0,23,0,3),s(27,5,7,16,0,23,0,3),s(28,5,9,16,0,23,0,3),
    s(29,7,4,7,0,15,0),s(30,7,5,7,0,15,0),s(31,7,7,7,0,15,0),s(32,7,8,7,0,15,0),s(33,7,9,7,0,15,0),
    s(34,8,6,15,0,23,0),s(35,8,7,15,0,23,0),s(36,8,8,15,0,23,0),s(37,8,10,15,0,23,0),
    s(38,9,8,17,0,23,0,1),s(39,9,9,11,0,19,0,1),s(40,9,10,11,0,19,0,1),
    s(41,10,4,11,0,19,0,1),s(42,10,6,11,0,19,0,4),s(43,10,9,11,0,19,0,1),
    s(44,11,4,9,0,17,0,1),s(45,11,6,9,0,17,0,1),s(46,11,7,14,0,22,0,2),s(47,11,9,14,0,22,0,2),
    s(48,12,4,8,0,16,0),s(49,12,5,8,0,16,0),s(50,12,7,8,0,16,0),s(51,12,8,10,0,18,0),
])
shifts.to_csv("data_ai/shifts.csv", index=False)

certs = pd.DataFrame([
    {"id":1, "employee_id":1, "cert_type":"Food Handler","expiry_date":"2027-03-15","file_name":None,"uploaded_at":"2025-03-10 10:00:00"},
    {"id":2, "employee_id":2, "cert_type":"Food Handler","expiry_date":"2026-05-25","file_name":None,"uploaded_at":"2024-05-20 09:00:00"},
    {"id":3, "employee_id":4, "cert_type":"Food Handler","expiry_date":"2027-01-10","file_name":None,"uploaded_at":"2025-01-05 11:00:00"},
    {"id":4, "employee_id":4, "cert_type":"RBS",         "expiry_date":"2026-12-01","file_name":None,"uploaded_at":"2025-12-01 11:00:00"},
    {"id":5, "employee_id":5, "cert_type":"Food Handler","expiry_date":"2027-02-20","file_name":None,"uploaded_at":"2025-02-15 14:00:00"},
    {"id":6, "employee_id":5, "cert_type":"RBS",         "expiry_date":"2026-04-01","file_name":None,"uploaded_at":"2024-04-01 14:00:00"},
    {"id":7, "employee_id":6, "cert_type":"Food Handler","expiry_date":"2027-06-15","file_name":None,"uploaded_at":"2025-06-10 09:00:00"},
    {"id":8, "employee_id":7, "cert_type":"Food Handler","expiry_date":"2027-08-20","file_name":None,"uploaded_at":"2025-08-15 10:00:00"},
    {"id":9, "employee_id":8, "cert_type":"Food Handler","expiry_date":"2026-03-15","file_name":None,"uploaded_at":"2024-03-10 08:00:00"},
    {"id":10,"employee_id":9, "cert_type":"Food Handler","expiry_date":"2027-04-10","file_name":None,"uploaded_at":"2025-04-05 09:00:00"},
    {"id":11,"employee_id":10,"cert_type":"Food Handler","expiry_date":"2026-11-30","file_name":None,"uploaded_at":"2025-11-25 10:00:00"},
    {"id":12,"employee_id":11,"cert_type":"Food Handler","expiry_date":"2027-01-25","file_name":None,"uploaded_at":"2025-01-20 11:00:00"},
    {"id":13,"employee_id":11,"cert_type":"RBS",         "expiry_date":"2026-05-30","file_name":None,"uploaded_at":"2024-05-25 11:00:00"},
    {"id":14,"employee_id":12,"cert_type":"Food Handler","expiry_date":"2027-03-01","file_name":None,"uploaded_at":"2025-02-25 08:00:00"},
    {"id":15,"employee_id":12,"cert_type":"RBS",         "expiry_date":"2026-10-15","file_name":None,"uploaded_at":"2025-10-10 08:00:00"},
    {"id":16,"employee_id":12,"cert_type":"Food Service Manager","expiry_date":"2027-05-20","file_name":None,"uploaded_at":"2025-05-15 08:00:00"},
])
certs.to_csv("data_ai/certifications.csv", index=False)

swaps = pd.DataFrame([{
    "id":1,"requester_id":11,"requester_shift_id":46,"target_id":6,"target_shift_id":17,
    "status":"pending","requester_note":"I have a family commitment Thursday evening — can we swap?",
    "requested_at":"2026-05-06 18:30:00","resolved_at":None,"manager_notes":None,
}])
swaps.to_csv("data_ai/swap_requests.csv", index=False)
print("Demo data ready.")
EOF
```

2. Kill any existing streamlit processes: `pkill -f "streamlit run" 2>/dev/null; sleep 1`

3. Start the demo app on port 8501 (with demo data):
```
streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true --server.enableCORS false --server.enableXsrfProtection false > /tmp/streamlit_demo.log 2>&1 &
```

4. Start the regular app on port 8502 (clean, no data) from a separate temp directory:
```
mkdir -p /tmp/clean_app/data_ai/cert_uploads
cp app.py /tmp/clean_app/app.py
cd /tmp/clean_app && streamlit run app.py --server.address 0.0.0.0 --server.port 8502 --server.headless true --server.enableCORS false --server.enableXsrfProtection false > /tmp/streamlit_clean.log 2>&1 &
```

5. Wait for both to be ready:
```
for i in {1..20}; do curl -s http://localhost:8501 >/dev/null && curl -s http://localhost:8502 >/dev/null && break; sleep 1; done
```

6. Determine the base URL:
   - If `$CODESPACE_NAME` is set: base = `https://${CODESPACE_NAME}`
   - Otherwise: base = `http://localhost`

7. Tell the user:
```
✅ Demo is live. Here are your two links:

**Demo Version** (preloaded data + DEMO MODE banner):
<base>-8501.app.github.dev

**Regular Version** (blank, start fresh):
<base>-8502.app.github.dev
```
