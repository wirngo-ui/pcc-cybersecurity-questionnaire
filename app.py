import os, sqlite3, json, csv, io
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, flash, send_file, session

BASE=os.path.dirname(os.path.abspath(__file__))
DB=os.path.join(BASE,"responses.db")
app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","change-this-secret-key")
ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD","change-me-now")

LIKERT=["1 - Strongly Disagree","2 - Disagree","3 - Neutral / Unsure","4 - Agree","5 - Strongly Agree"]
SECTIONS=[("A","Respondent Profile"),("B","Leadership, Digital Governance and Cybersecurity"),("C","Sector-Specific Cybersecurity Vulnerabilities"),("D","Security of Central Executive and Administrative Files"),("E","Cybersecurity Preparedness, Awareness and Incident Response"),("F","Follow-up Interview / Key Informant Participation")]

Q=[
("role","A","select","What best describes your current role in the PCC or a PCC-related institution?",["PCC Synod committee / senior leadership","Executive Secretary / senior administrative officer","Regional / Presbytery administrator","IT / ICT / cybersecurity personnel","Finance officer / financial controller","Health institution manager / health data handler","School principal / education administrator / education data handler","Other operational staff","Other (please specify)"],1),
("sector","A","select","Which operational sector is most relevant to your work?",["Executive administration","Finance / banking / microfinance","Health / mission hospital / health centre","Education / school / college","Entrepreneurial or social project","IT / ICT","Other"],1),
("digital_experience","A","select","How would you describe your level of experience with digital systems used in your work?",["Very limited","Limited","Moderate","High","Very high"],1),
("years_role","A","select","How long have you worked in your current PCC-related role?",["Less than 1 year","1–3 years","4–6 years","7–10 years","More than 10 years"],1),
("role_other","A","text","If you selected an Other role, please specify.",[],0),
]
b=["Senior leadership treats cybersecurity as an institutional governance responsibility, not only an IT responsibility.","PCC leadership clearly distinguishes ordinary IT operations from cybersecurity and data protection.","Senior leaders receive adequate information about major cyber risks affecting the institution.","Cybersecurity responsibilities are clearly assigned to specific leaders, offices or personnel.","Cybersecurity considerations influence decisions about budgets, technology procurement and digital services.","There are clear institutional rules governing access to sensitive electronic information.","Leadership communicates the importance of protecting confidential institutional and personal data.","The institution has sufficient leadership-level oversight of cybersecurity risks across its different sectors."]
for i,x in enumerate(b,1): Q.append((f"b{i}","B","likert",x,[],1))
c=["The digital systems used in my area contain information that would cause serious harm if exposed, altered or lost.","User access to important systems is reviewed and removed promptly when responsibilities change.","Important data are backed up regularly and backups can be restored when needed.","Cloud-based systems used by my area are configured and managed with appropriate security controls.","Financial transactions and financial databases receive adequate cybersecurity protection.","Health and patient information receives adequate confidentiality and access protection.","Student, teacher and education records receive adequate cybersecurity protection.","There is adequate separation between public-facing digital services and sensitive internal systems."]
for i,x in enumerate(c,1): Q.append((f"c{i}","C","likert",x,[],1))
d=["Sensitive files managed by central executive offices are stored in controlled locations or systems.","Access to sensitive executive files is limited according to job responsibilities.","Sensitive executive files are protected against unauthorized copying, downloading or sharing.","There is an identifiable record or audit trail showing who accesses sensitive electronic files.","Confidential information exchanged by email, messaging or cloud services is appropriately protected.","There is a defined process for handling confidential files when staff leave, transfer or change responsibilities."]
for i,x in enumerate(d,1): Q.append((f"d{i}","D","likert",x,[],1))
e=["Staff receive regular training on passwords, phishing, social engineering and other cyber threats.","Staff know how to recognize and report suspicious emails, links, messages or system activity.","Strong password practices are consistently followed in my work area.","Multi-factor authentication is used where appropriate for important systems and accounts.","The institution has a documented process for reporting and responding to suspected data breaches.","Roles and responsibilities during a cyber incident are known before an incident occurs.","The institution tests or reviews its incident-response and business-continuity arrangements.","Cybersecurity preparedness is adequate to support continuity of PCC operations after a serious cyber incident."]
for i,x in enumerate(e,1): Q.append((f"e{i}","E","likert",x,[],1))
Q += [
("e9","E","textarea","What is the most significant cybersecurity weakness you have observed in your area of work?",[],0),
("e10","E","textarea","What cybersecurity measure should PCC leadership prioritize most urgently?",[],0),
("f1","F","radio","Would you be willing to participate in a follow-up interview as a key informant for this research?",["Yes","No","Maybe / I would like more information"],1),
("f2","F","checkbox","Which areas could you speak about in a follow-up interview? Select all that apply.",["Strategic leadership and cybersecurity governance","IT / ICT operations and cybersecurity","Finance and financial data systems","Health information and patient data","Education and student/teacher data","Executive administrative files and records","Incident response / business continuity","Staff cybersecurity awareness and training"],0),
("f3","F","text","Name (only if you consent to being contacted for the follow-up interview).",[],0),
("f4","F","email","Email address or preferred contact detail (only if you consent to being contacted).",[],0),
("f5","F","select","Preferred interview mode, if selected for follow-up.",["Online video call","Telephone call","In-person interview","No preference"],0),
("f6","F","textarea","Any additional comment or issue you believe the researcher should investigate?",[],0)
]

def init_db():
    con=sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS responses(id INTEGER PRIMARY KEY AUTOINCREMENT,submitted_at TEXT,role TEXT,sector TEXT,interview_interest TEXT,data_json TEXT)")
    con.commit(); con.close()

def admin_required(fn):
    @wraps(fn)
    def w(*a,**k):
        if not session.get("admin"): return redirect(url_for("admin_login"))
        return fn(*a,**k)
    return w

@app.route("/",methods=["GET","POST"])
def questionnaire():
    if request.method=="POST":
        data={}; errors=[]
        for key,sec,typ,label,opts,req in Q:
            val=request.form.getlist(key) if typ=="checkbox" else request.form.get(key,"").strip()
            data[key]=val
            if req and (not val if isinstance(val,str) else not val): errors.append(label)
        if errors:
            for x in errors[:5]: flash("Please answer: "+x,"error")
            return render_template("questionnaire.html",Q=Q,SECTIONS=SECTIONS,LIKERT=LIKERT,data=data)
        con=sqlite3.connect(DB)
        con.execute("INSERT INTO responses VALUES(NULL,?,?,?,?,?)",(datetime.now(timezone.utc).isoformat(),data.get("role",""),data.get("sector",""),data.get("f1",""),json.dumps(data,ensure_ascii=False)))
        con.commit(); con.close()
        return render_template("thanks.html")
    return render_template("questionnaire.html",Q=Q,SECTIONS=SECTIONS,LIKERT=LIKERT,data={})

@app.route("/admin/login",methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        if request.form.get("password")==ADMIN_PASSWORD:
            session["admin"]=True; return redirect(url_for("admin"))
        flash("Incorrect password.","error")
    return render_template("login.html")

@app.route("/admin/logout")
def logout(): session.clear(); return redirect(url_for("admin_login"))

@app.route("/admin")
@admin_required
def admin():
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
    rows=con.execute("SELECT id,submitted_at,role,sector,interview_interest FROM responses ORDER BY id DESC").fetchall()
    con.close(); return render_template("admin.html",rows=rows)

@app.route("/admin/export.csv")
@admin_required
def export_csv():
    con=sqlite3.connect(DB); rows=con.execute("SELECT * FROM responses ORDER BY id").fetchall(); con.close()
    keys=[x[0] for x in Q]; out=io.StringIO(); w=csv.writer(out)
    w.writerow(["ID","Submitted UTC","Role","Sector","Interview Interest"]+keys)
    for r in rows:
        d=json.loads(r[5]); w.writerow(list(r[:5])+["; ".join(d.get(k,[])) if isinstance(d.get(k,""),list) else d.get(k,"") for k in keys])
    return send_file(io.BytesIO(out.getvalue().encode("utf-8-sig")),mimetype="text/csv",as_attachment=True,download_name="PCC_cybersecurity_responses.csv")

@app.route("/admin/export.xlsx")
@admin_required
def export_xlsx():
    from openpyxl import Workbook
    con=sqlite3.connect(DB); rows=con.execute("SELECT * FROM responses ORDER BY id").fetchall(); con.close()
    keys=[x[0] for x in Q]; labels={x[0]:x[3] for x in Q}; wb=Workbook(); ws=wb.active; ws.title="Responses"
    ws.append(["ID","Submitted UTC","Role","Sector","Interview Interest"]+[labels[k] for k in keys])
    for r in rows:
        d=json.loads(r[5]); ws.append(list(r[:5])+["; ".join(d.get(k,[])) if isinstance(d.get(k,""),list) else d.get(k,"") for k in keys])
    ws.freeze_panes="A2"; mem=io.BytesIO(); wb.save(mem); mem.seek(0)
    return send_file(mem,mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",as_attachment=True,download_name="PCC_cybersecurity_responses.xlsx")

if __name__=="__main__":
    init_db(); app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
