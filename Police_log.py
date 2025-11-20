import streamlit as st
import pandas as pd
import mysql.connector as mysqlcon
import plotly.express as px

#connect to database
def create_connection():
   try:
      connection = mysqlcon.connect(
        host="localhost",
        user="root",
        password="kans",
        database="police_db"
      )
      return connection
   except Exception as e:
      st.error(f"data base connection error :{e}")
      return None

#Fetch data from the database
def fetch_data(query):
   connection=create_connection()
   if connection:
      try:
         with connection.cursor() as cursor:
          cursor.execute(query)
          result=cursor.fetchall()
          df=pd.DataFrame(result)
          return df
      finally:
        connection.close()
   else:
      return pd.DataFrame()
   
st.title("Secure check : A Python-SQL Digital Ledger for Police Post Logs")
st.divider()
st.text("Real-time monitoring and insight for law enforcement")

st.header("Police Logs Overview")

df = pd.read_csv(r"C:\Users\Admin\Desktop\Police_check\traffic.csv")
st.write (df)

st.header("Violation")

if not df.empty and 'violation' in df.columns:
    violation_data = df['violation'].value_counts().reset_index()
    violation_data.columns = ['violation', 'count']
    fig = px.scatter(violation_data, x='violation', y='count', title='Violation Type', color='violation')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available")

st.header("Advanced Insights")

select_query = st.selectbox("Queries",["What are the top 10 vehicle_Number involved in drug-related stops?",
 "Which vehicles were most frequently searched?",
 "Which driver age group had the highest arrest rate?",
 "What is the gender distribution of drivers stopped in each country?",
 "Which race and gender combination has the highest search rate?",
 "What time of day sees the most traffic stops?",
 "What is the average stop duration for different violations?",
 "Are stops during the night more likely to lead to arrests?",
 "Which violations are most associated with searches or arrests",
 "Which violations are most common among younger drivers (<25)?",
 "Which countries report the highest rate of drug-related stops?",
 "What is the arrest rate by country and violation",
 "Which country has the most stops with search conducted?",
 "Top 5 Violations with Highest Arrest Rates"
])

query_map = {"What are the top 10 vehicle_Number involved in drug-related stops?": "select vehicle_number, count(*) as stop_count from log where drugs_related_stop = True group by vehicle_number order by stop_count asc limit 10",
"Which vehicles were most frequently searched?" : "select vehicle_number, count(*) as most_searched from log where search_conducted = True group by vehicle_number order by most_searched desc limit 10",
"Which driver age group had the highest arrest rate?" : "select driver_age, count(*) as arrested from log where is_arrested = True group by driver_age order by arrested desc limit 10",
"What is the gender distribution of drivers stopped in each country?" : "select country_name , driver_gender, count(*) as count from log group by country_name, driver_gender",
"Which race and gender combination has the highest search rate?" : "select driver_race, driver_gender, count(*) as search from log where search_conducted = True group by driver_race, driver_gender order by search desc",
"What time of day sees the most traffic stops?" : "select stop_date, stop_time , count(*) as count_stop from log group by stop_date, stop_time",
"What is the average stop duration for different violations?" : "select violation, avg(stop_duration) as avg_stp_dur from log group by violation",
"Are stops during the night more likely to lead to arrests?" : "select case when stop_time between '6:00:00' and '18:00:00' then 'day' else 'night' end as shift, count(is_arrested) as arrest from log where is_arrested = True group by shift",
"Which violations are most associated with searches or arrests" : "select violation, count(*) as arrest from log where is_arrested = True group by violation order by violation desc",
"Which violations are most common among younger drivers (<25)?" : "select violation, driver_age, count(*) as tot_case from log where driver_age<25 group by violation,driver_age order by tot_case desc",
"Which countries report the highest rate of drug-related stops?" : "select country_name, count(*) as drug_stop from log where drugs_related_stop = True group by country_name",
"What is the arrest rate by country and violation" : "select country_name, violation ,count(*) as arr_rate from log where is_arrested = True group by country_name,violation order by arr_rate desc",
"Which country has the most stops with search conducted?" : "select country_name, count(*) as most_stop from log where search_conducted = True group by country_name",
"Top 5 Violations with Highest Arrest Rates" :"select violation, count(*) as arr_rate from log where is_arrested = True group by violation order by arr_rate desc"
}

if st.button("Run query"):
   result = fetch_data(query_map[select_query])
   if not result.empty:
      st.write(result)
   else:
      st.warning("No results are found")

st.divider()

st.header("Display the predict outcome")

#Input form for all fields 
with st.form("new_log_form"):
   stop_date = st.date_input("Stop Date")
   stop_time = st.time_input("Stop Time")
   country_name = st.text_input("Country Name")
   driver_gender = st.selectbox("Driver Gender",['Male','Female'])
   driver_age = st.number_input("Driver Age", min_value = 18, max_value = 100, value = 27)
   driver_race = st.text_input("Driver Race")
   search_conducted = st.selectbox("Was a Search Conducted?", ["0","1"])
   search_type = st.selectbox("Search Type",['Vehicle Search','Frisk','None'])
   violation = st.selectbox("violation",['DUI','Speeding','Seatbelt','Signal','Other'])
   drugs_related_stop = st.selectbox("Was it Drugs Related", ["0","1"])
   stop_outcome = st.selectbox("stop_outcome", ['Ticket','Arrest','Warning'])
   stop_duration = st.selectbox("Stop Duration", df['stop_duration'].dropna().unique())
   vehicle_number = st.text_input("Vehicle Number")
   timestamp = pd.Timestamp.now()
   
   submitted = st.form_submit_button("Predict Stop Outcome and Violation")

# Filter data for prediction
if submitted:
    filter_data = df[
        (df['driver_gender'] == driver_gender) &
        (df['driver_age'] == driver_age) &
        (df['search_conducted'] == search_conducted) &
        (df['stop_duration'] == stop_duration) &
        (df['violation'] == violation) &
        (df['stop_outcome'] == stop_outcome) &
        (df['drugs_related_stop'] == int(drugs_related_stop))
    ]

# Predict stop outcome
    if not filter_data.empty:
        predicted_outcome = filter_data['stop_outcome'].mode()[0]
        predicted_violation = filter_data['violation'].mode()[0]
    else:
        predicted_outcome = stop_outcome
        predicted_violation = violation
# Natural Language Summary
    Search_text = "A Search was Conducted" if int(search_conducted) else "No search was conducted"
    drug_text = "was drug_related" if int(drugs_related_stop) else "was not 💊 drug_related"

    st.markdown(f"""
                **Prediction Summary**
                - **Predicted Violation:** {predicted_violation}
                - **Predicted Stop Outcome:** {predicted_outcome}
                    
                🚓 A  **{driver_age}**-year-old 🧍‍♂️ **{driver_gender}** driver in 🌎 **{ country_name}** was stopped at 🕒**{stop_time.strftime('%I:%M%p')}** on 📅**{stop_date}**. 
                {Search_text}, and the stop {drug_text}.
                stop duration: **{stop_duration}**.
                Vehicle Number: **{vehicle_number}**.
                """)