import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title='Amika+ Benefits Calculator', page_icon='🩺', layout='wide')
BASE = Path(__file__).parent
st.title('Amika+ | Intermittent Feeding Benefits Calculator')
st.caption('Illustrative operational model based on the supplied Excel workbook. Not a clinical decision tool.')
with st.sidebar:
    st.header('Facility assumptions')
    boluses = st.number_input('Boluses per day', min_value=1, max_value=100, value=4, step=1)
    volume = st.number_input('Volume per bolus (ml)', min_value=1, value=200, step=10)
    manual_minutes = st.number_input('Manual nursing minutes per bolus', min_value=0.0, value=4.0, step=0.5)
    setup_minutes = st.number_input('Amika+ setup minutes per day', min_value=0.0, value=3.0, step=0.5)
    walking = st.number_input('Walking distance per round trip (m)', min_value=0.0, value=15.0, step=1.0)
    days = st.number_input('Days per year', min_value=1, max_value=366, value=365)

nursing_saved = boluses * manual_minutes - setup_minutes
touches_saved = boluses - 1
walk_saved = (boluses - 1) * walking
cols = st.columns(4)
for col, label, value in zip(cols,
    ['Daily feeding volume', 'Nursing hours saved/year', 'Touches avoided/year', 'Walking km saved/year'],
    [f'{boluses*volume:,.0f} ml', f'{nursing_saved*days/60:,.1f}', f'{touches_saved*days:,.0f}', f'{walk_saved*days/1000:,.1f}']):
    col.metric(label, value)

tab1, tab2, tab3 = st.tabs(['Workload comparison', 'Sample feed accuracy', 'Clinical risks & references'])
with tab1:
    metrics = pd.DataFrame({
        'Metric':['Nursing touches (count/day)','Nursing time (min/day)','Walking distance (m/day)'],
        'Manual':[boluses,boluses*manual_minutes,boluses*walking],
        'Amika+':[1,setup_minutes,walking],
        'Saved/day':[touches_saved,nursing_saved,walk_saved],
        'Saved/year':[touches_saved*days,round(nursing_saved*days/60),round(walk_saved*days/1000,1)],
        'Yearly unit':['touches','hours','km']})
    st.dataframe(metrics, hide_index=True, use_container_width=True)
    st.subheader('Daily nursing time')
    st.bar_chart(pd.DataFrame({'Minutes':[boluses*manual_minutes,setup_minutes]}, index=['Manual','Amika+']))
    if nursing_saved < 0:
        st.warning('Under these assumptions, Amika+ requires more nursing time than manual feeding.')
with tab2:
    st.info('Sample variances below are illustrative values copied from the workbook, not measured device performance.')
    manual_variances=[.12,-.08,.18,-.15,.05,-.22,.09,-.11]
    amika_variances=[.02,-.01,.03,-.02,.01,-.03,.02,-.01]
    if boluses > 8:
        st.warning('The original workbook contains only eight sample bolus accuracy scenarios. Showing the first eight.')
    rows=[]
    for i in range(min(boluses,8)):
        m=int(volume*(1+manual_variances[i])+0.5)
        a=int(volume*(1+amika_variances[i])+0.5)
        rows.append({'Bolus':i+1,'Target (ml)':volume,'Manual delivered (ml)':m,'Amika+ delivered (ml)':a,'Manual Δ%':(m-volume)/volume*100,'Amika+ Δ%':(a-volume)/volume*100})
    st.dataframe(pd.DataFrame(rows).style.format({'Manual Δ%':'{:+.1f}%','Amika+ Δ%':'{:+.1f}%'}),hide_index=True,use_container_width=True)
with tab3:
    risks=pd.read_json(BASE/'risks.json')
    refs=pd.read_json(BASE/'references.json')
    st.subheader('Clinical risks listed in the workbook')
    st.dataframe(risks,hide_index=True,use_container_width=True)
    st.subheader('Workbook references')
    st.dataframe(refs,hide_index=True,use_container_width=True,column_config={'DOI / Source':st.column_config.LinkColumn('DOI / Source')})
    st.caption('Clinical claims and citations are reproduced from the provided workbook and have not been independently validated. Review against current guidance before external or clinical use.')
