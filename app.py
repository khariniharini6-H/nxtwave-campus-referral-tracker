import sqlite3
import secrets
import string
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title='NxtWave Campus Referral Tracker', page_icon='🚀', layout='wide')
DB = Path(__file__).with_name('tracker.db')
TARGET = 500
BUDGET = 2000
CHANNELS = ['Campus ambassador', 'WhatsApp community', 'College club / LinkedIn', 'Student referral', 'Other']

def connect():
    conn = sqlite3.connect(DB)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('CREATE TABLE IF NOT EXISTS ambassadors (code TEXT PRIMARY KEY, name TEXT NOT NULL, college TEXT NOT NULL)')
    conn.execute('''CREATE TABLE IF NOT EXISTS registrations (
      id INTEGER PRIMARY KEY AUTOINCREMENT, student_key TEXT NOT NULL UNIQUE,
      college TEXT NOT NULL, channel TEXT NOT NULL, referral_code TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(referral_code) REFERENCES ambassadors(code))''')
    conn.commit()
    return conn

def new_code(conn):
    for _ in range(20):
        code = 'CAMP-' + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        if not conn.execute('SELECT 1 FROM ambassadors WHERE code=?', (code,)).fetchone():
            return code
    raise RuntimeError('Could not generate a unique code')

conn = connect()
st.title('🚀 NxtWave Campus Referral Tracker')
st.caption('Growth Challenge prototype • Simulated registrations only • Not an official NxtWave registration system')

amb = pd.read_sql_query('SELECT * FROM ambassadors ORDER BY name', conn)
regs = pd.read_sql_query('SELECT * FROM registrations ORDER BY id DESC', conn)
count = len(regs)
col1, col2, col3, col4 = st.columns(4)
col1.metric('Registration goal', f'{TARGET:,}')
col2.metric('Demo registrations', count)
col3.metric('Progress', f'{count / TARGET * 100:.1f}%')
col4.metric('Budget ceiling', f'₹{BUDGET:,}')
st.progress(min(count / TARGET, 1.0))

page = st.sidebar.radio('Explore', ['Dashboard', 'Add ambassador', 'Simulate registration', 'Leaderboard', 'Campaign plan'])

if page == 'Dashboard':
    st.subheader('Registration sources')
    if regs.empty:
        st.info('No demo registrations yet. Add an ambassador and simulate a registration to get started.')
    else:
        counts = regs.groupby('channel').size().rename('Registrations')
        st.bar_chart(counts)
        st.dataframe(regs[['id','college','channel','referral_code','created_at']].rename(columns={'id':'Registration ID'}), hide_index=True, use_container_width=True)
        st.download_button('Download demo registrations (CSV)', regs.to_csv(index=False), 'demo_registrations.csv', 'text/csv')

elif page == 'Add ambassador':
    st.subheader('Create a unique ambassador referral code')
    with st.form('ambassador_form'):
        name = st.text_input('Ambassador display name', max_chars=70)
        college = st.text_input('College', max_chars=100)
        submitted = st.form_submit_button('Generate code')
    if submitted:
        if not name.strip() or not college.strip():
            st.error('Please enter a name and college.')
        else:
            code = new_code(conn)
            conn.execute('INSERT INTO ambassadors(code,name,college) VALUES (?,?,?)', (code, name.strip(), college.strip()))
            conn.commit()
            st.success(f'Referral code generated: {code}')
            st.code(code)
    st.dataframe(pd.read_sql_query('SELECT name,college,code FROM ambassadors ORDER BY name',conn), hide_index=True, use_container_width=True)

elif page == 'Simulate registration':
    st.subheader('Simulate a student registration')
    st.info('Use fictional student IDs only (for example, DEMO-001). Do not enter real personal information.')
    codes = ['No referral code'] + amb['code'].tolist()
    with st.form('registration_form'):
        student_key = st.text_input('Fictional student ID', placeholder='DEMO-001', max_chars=50)
        college = st.text_input('College', placeholder='Demo Engineering College', max_chars=100)
        channel = st.selectbox('Acquisition channel', CHANNELS)
        referral = st.selectbox('Ambassador referral code', codes)
        submitted = st.form_submit_button('Record demo registration')
    if submitted:
        key = student_key.strip().upper()
        if not key or not college.strip():
            st.error('Student ID and college are required.')
        elif not key.startswith('DEMO-'):
            st.error('Please use a fictional ID beginning with DEMO-.')
        else:
            try:
                conn.execute('INSERT INTO registrations(student_key,college,channel,referral_code) VALUES (?,?,?,?)', (key,college.strip(),channel,None if referral == 'No referral code' else referral))
                conn.commit()
                st.success('Demo registration recorded. Visit Dashboard to see the updated count.')
            except sqlite3.IntegrityError:
                st.warning('Duplicate fictional student ID. This registration was not counted again.')

elif page == 'Leaderboard':
    st.subheader('Campus ambassador leaderboard')
    leaderboard = pd.read_sql_query('''SELECT a.name AS Ambassador, a.college AS College, a.code AS Code,
      COUNT(r.id) AS Registrations FROM ambassadors a
      LEFT JOIN registrations r ON r.referral_code=a.code
      GROUP BY a.code ORDER BY Registrations DESC, Ambassador ASC''',conn)
    if leaderboard.empty:
        st.info('Add ambassadors to start the leaderboard.')
    else:
        leaderboard.insert(0, 'Rank', range(1, len(leaderboard)+1))
        st.dataframe(leaderboard, hide_index=True, use_container_width=True)
        st.bar_chart(leaderboard.set_index('Ambassador')['Registrations'])

elif page == 'Campaign plan':
    st.subheader('Seven-day campaign targets')
    daily = pd.DataFrame({'Day':[1,2,3,4,5,6,7], 'Target':[20,50,80,90,100,100,60]})
    daily['Cumulative target'] = daily['Target'].cumsum()
    st.dataframe(daily, hide_index=True, use_container_width=True)
    st.line_chart(daily.set_index('Day')['Cumulative target'])
    st.subheader('Budget allocation')
    budget = pd.DataFrame({'Category':['Ambassador recognition','Creative assets','Referral rewards','Paid promotion test','Contingency'], 'Budget (₹)':[800,200,500,300,200]})
    st.dataframe(budget, hide_index=True, use_container_width=True)
    st.caption('All channel and daily targets are planning assumptions, not measured forecasts.')

conn.close()
