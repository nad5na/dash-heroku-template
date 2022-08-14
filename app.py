import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


%%capture
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])


mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

data = gss_clean.groupby('sex').agg({'income':'mean','job_prestige':'mean','socioeconomic_index':'mean',
                                    'education':'mean'}).reset_index()
data = data.rename({'income':'Average Annual Income','job_prestige':'Average Occupational Prestige','sex':'Sex',
                     'socioeconomic_index':'Average Socioeconomic Index','education':'Average Years of Education'},
                     axis=1)
table = ff.create_table(round(data,2))


bread = gss_clean[['sex','male_breadwinner']]
bread['male_breadwinner'] = bread['male_breadwinner'].astype('category')
bread['male_breadwinner'] = bread['male_breadwinner'].cat.reorder_categories(['strongly agree', 
                                                                'agree', 
                                                                'disagree', 
                                                                'strongly disagree'])
bread = bread.groupby('sex').value_counts().reset_index()
bread = bread.rename({0:'counts'},axis=1)
fig3 = px.bar(bread, x='male_breadwinner', y='counts', color='sex',
        labels={'male_breadwinner':'Response to Male Breadwinner Question', 'counts':'Number of People'},
        barmode = 'group', category_orders={"male_breadwinner": ['strongly agree', 
                                                                'agree', 
                                                                'disagree', 
                                                                'strongly disagree']})
fig3.update_layout(showlegend=True)
fig3.update(layout=dict(title=dict(x=0.5)))


four = gss_clean[['sex','income','job_prestige','education','socioeconomic_index']]
fig4 = px.scatter(four, x='job_prestige', y='income', 
                    color = 'sex', 
                    trendline='ols',
                    height=600, width=600,
                    labels={'job_prestige':'Occupational Prestige', 
                            'income':'Annual Income'},
                    hover_data=['education', 'socioeconomic_index'])
fig4.update(layout=dict(title=dict(x=0.5)))


fig5a = px.box(gss_clean, x='sex', y = 'income', color = 'sex',
                labels={'income':'Annual Income', 'sex':''}, height=600, width=800)
fig5a.update(layout=dict(title=dict(x=0.5)))
fig5a.update_layout(showlegend=False)


fig5b = px.box(gss_clean, x='sex', y = 'job_prestige', color = 'sex',
                labels={'job_prestige':'Occupational Prestige', 'sex':''}, height=600, width=800)
fig5b.update(layout=dict(title=dict(x=0.5)))
fig5b.update_layout(showlegend=False)


df = gss_clean[['income','sex','job_prestige']]
df['prestige_bins'] = pd.cut(df['job_prestige'], bins=6)
df = df.dropna()
df = df.sort_values(by='prestige_bins')
fig6 = px.box(df, y='sex', x='income', color='sex',
            labels={'job_prestige':'Occupational Prestige', 'sex':''}, height=600, width=800,
            facet_col='prestige_bins', facet_col_wrap=2, color_discrete_map = {'male':'blue', 'female':'red'})


app.layout = html.Div([
    html.H1('2019 General Social Survey Comparisons between Sex'),
    dcc.Markdown('While the exact metrics and effects of the gender wage gap in America vary, there is one consistent conclusion: Women make less than men in the US. In 2018, women made only 82 cents for every dollar that a male made, and this gap was generally larger for women of color or from more diverse backgrounds. The main causes for the pay gap are differences in industries worked in, differences in years of experience, differences in hours worked, and plain old discrimination. \nThe GSS is a nationally representative survey that covers adults across the US, monitoring trends in things like attitudes, opinions, and behaviors. The GSS surveys contain a "standard core of demographic, behavioral, and attitudinal questions, plus topics of special interest" in order to accomplish this. Questions have been adapted over the years so that trends can be detected and analyzed throughout up to 80 years. The GSS lets researchers examine "the structure and functioning of society in general" as well as compare US societal attitudes to other nations.'),
    html.H1("Barplot of responses to the 'Breadwinner' Question by Men and Women"),
    dcc.Graph(figure=fig3),
    html.H2("Income, Job Prestige, Socioeconomic Index, & Years of Education between Men and Women"),
    dcc.Graph(figure=table),
    html.H3("Job Prestige vs. Income for Men and Women"),
    dcc.Graph(figure=fig4),
    html.H4("Income Boxplots between Men and Women by Prestige Level"),
    dcc.Graph(figure=fig6),
    html.Div([html.H5("Distribution of Income between Men and Women"), dcc.Graph(figure=fig5a)], style={'width':'10%', 'float':'right'}),
    html.Div([html.H6("Distribution of Job Prestige between Men and Women"), dcc.Graph(figure=fig5b)], style={'width':'10%', 'float':'left'})
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
