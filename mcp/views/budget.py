from flask import Response
from flask.views import View
from bson import json_util
from mcp import mongo


class BudgetType(View):
#@app.route("/<string:komuna>/budget-type/<int:year>")
    def dispatch_request(self, komuna, year):
        ''' Ruajme rezultatin qe na kthehet nga databaza permes ekzekutimit
            te kerkeses(Query) ne json.
        '''
        json = mongo.db.procurements.aggregate([
            {
                "$match": {
                    "city": komuna,
                    "viti": year
                }
            },
            {
                "$group": {
                    "_id": {
                        "tipi": "$tipiBugjetit"
                    },
                    "shuma": {
                        "$sum": "$kontrata.vlera"}
                }
            },
            {
                "$sort": {
                    "_id.tipi": 1
                }
            },
            {
                "$project": {
                    "tipi": "$_id.tipi",
                    "shuma": "$shuma",
                    "_id": 0
                }
            }
        ])
        # pergjigjen e kthyer dhe te konvertuar ne JSON ne baze te json_util.dumps() e ruajme ne resp
        resp = Response(
            response=json_util.dumps(json['result']),
            mimetype='application/json')

        # ne momentin kur hapim  sh.: http://127.0.0.1:5000/piechart/2011 duhet te kthejme JSON, ne rastin tone resp.
        return resp
