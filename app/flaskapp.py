import flask
import numpy as np
import pymongo
from datetime import datetime
import time
import pickle
import random
import csv

#---------- Database ----------------#

client = pymongo.MongoClient()
db = client.sa_structured_v2
docs = db.collections
final_docs = [doc for doc in docs.find() if doc['keep']==1]

with open('doc_topic_mat_15.pkl', 'rb') as f:
    W_tfidf = pickle.load(f)


#---------- URLS AND WEB PAGES -------------#
app = flask.Flask(__name__)

@app.route('/')
def home_page():
    with open("/Users/samfunk/ds/metis/project_fletcher/app/nlp_page.html",'r') as viz_file:
        return viz_file.read()

@app.route('/d3_week', methods=['GET', 'POST'])
def d3_week_page():
    with open("/Users/samfunk/ds/metis/project_fletcher/app/d3_line_chart.html", 'r') as d3_file:
        return d3_file.read()

@app.route('/week_records.csv')
def wee_data():
    with open("week_records.csv", 'r') as week_datafile:
        return week_datafile.read()


def string_to_timestamp(datestring, add_one=False):
    dt = datetime.strptime(datestring, '%m/%d/%Y')
    t_tuple = dt.timetuple()
    ts = int(time.mktime(t_tuple))
    if add_one:
        ts += 86400
    return ts

@app.route("/api", methods=["POST"])
def trend(final_docs=final_docs, W_tfidf=W_tfidf):

    topic_list = ["Valuation", "IPO/SEO", "Recommendations", "Biotechnology", "Capital Markets", "Energy", "Management", "Earnings", "Federal Reserve", "Retail", "Technology", "Mergers & Acquisitions", "Debt Offerings", "Corporate Strategy", "Job Market"]

    data = flask.request.json
    start = string_to_timestamp(data["startDate"])
    end = string_to_timestamp(data["endDate"], add_one=True)
    topic = int(data["topic"])

    subset_indexes = [idx for idx, doc in enumerate(final_docs) if doc['timestamp'] >= start and doc['timestamp'] < end]

    doc_mat_subset = W_tfidf[subset_indexes[0]:(subset_indexes[-1]+1)]

    if topic == -1:

        rand_index = random.choice(subset_indexes)
        title = final_docs[rand_index]['title']
        text = final_docs[rand_index]['text']
        top3 = [topic_list[i] for i in W_tfidf[rand_index].argsort()[-3:][::-1]]

    else:

        ranks = [[i for i in doc.argsort()[-3:][::-1]] for doc in doc_mat_subset]
        rand_index = random.choice([(i,x) for i,x in zip(subset_indexes,ranks) if x[0] == topic])
        title = final_docs[rand_index[0]]['title']
        text = final_docs[rand_index[0]]['text']
        top3 = [topic_list[i] for i in rand_index[1]]

    results = {"title": title, "text": text, "top3": top3}

    print(results)
    return flask.jsonify(results)


if __name__ == '__main__':
    app.run()
