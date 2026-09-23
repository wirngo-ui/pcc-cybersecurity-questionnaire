# PCC Cybersecurity Online Questionnaire

Built from the uploaded PhD research outline. The outline specifies a mixed-methods design, including semi-structured elite interviews with executive secretaries and IT heads and structured questionnaires for operational staff; the target population includes PCC Synod committee members, executive secretaries, regional/presbytery administrators, IT/ICT personnel, financial controllers, health institution managers, and school principals. fileciteturn1file0L120-L139

The questionnaire covers the research objectives: leadership vs. cybersecurity, sector vulnerabilities, central executive files, preparedness, awareness and incident response. fileciteturn1file0L40-L60 fileciteturn1file0L151-L180

## Automatic saving and analysis
Every submitted response is stored in `responses.db` (SQLite). The administrator can export all responses to Excel or CSV for SPSS, R or Excel analysis. The research outline proposes descriptive statistics and correlation/regression analysis. fileciteturn1file0L140-L145

## Run locally
1. Install Python 3.11+.
2. `pip install -r requirements.txt`
3. Set environment variables `ADMIN_PASSWORD` and `SECRET_KEY`.
4. Run `python app.py`.
5. Open `http://127.0.0.1:5000`.

## Put online
Deploy the folder to a Python host using:
`gunicorn app:app`
Set `ADMIN_PASSWORD` and `SECRET_KEY` in the host's environment settings. A persistent database is required for production; use managed PostgreSQL or persistent disk rather than ephemeral storage.

## Interview participants
Section F asks whether the respondent is willing to participate in a follow-up interview and captures role-relevant areas. Contact information is optional. The uploaded outline identifies executive secretaries and IT heads for elite interviews. fileciteturn1file0L131-L135

## Ethics
The research outline requires institutional clearance/informed consent, anonymity, confidentiality and secure data storage. fileciteturn1file0L146-L150 Obtain the required approvals before public deployment and align the consent/privacy wording with the approved protocol.
