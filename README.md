# NxtWave Campus Referral Tracker — Growth Challenge Prototype

A simulated registration and referral attribution prototype supporting a seven-day campaign goal of 500 registrations with a ₹2,000 budget. **Not affiliated with or connected to NxtWave's actual registration system.**

## Features
- Create unique ambassador referral codes
- Record simulated student registrations (fictional `DEMO-` IDs only)
- Prevent duplicate fictional student IDs
- View a leaderboard, channel breakdown and progress to 500
- Review campaign targets and budget allocation
- Export simulated registration data to CSV

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Demo
1. Open **Add ambassador** and create 2 ambassadors.
2. Open **Simulate registration** and add fictional students `DEMO-001`, `DEMO-002`, etc. Assign their referral codes.
3. Re-submit `DEMO-001` to demonstrate duplicate protection.
4. Open **Leaderboard** and **Dashboard** to show the counts.
5. Open **Campaign plan** to explain how the tool supports the growth strategy.

Data is stored locally in `tracker.db` (created automatically). To reset the demo, stop the app and delete that file. Public hosting would require persistent storage and authentication before real use; this prototype is for simulation only.
