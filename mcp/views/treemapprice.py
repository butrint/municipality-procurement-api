from flask import Response
from flask.views import View
from bson import json_util
from mcp import mongo


class TreemapPrice(View):

    def dispatch_request(self, komuna, viti):
        ''' permes app.route caktojme URL ne te cilen do te kthejme rezultatin
            qe na nevojitet, dhe permes <int:viti> kerkojme qe te caktojme vitin
            ne URL per te kerkuar nga databaza te dhenat perkatese te atij viti
            Shembull : http://127.0.0.1:5000/treemap/2011
        '''
        json = mongo.db.procurements.aggregate([
            {
                "$match": {
                    "komuna": komuna,
                    "viti": viti
                }
            },
            {
                "$group": {
                    "_id": {
                        "kompania": "$kompania.slug",
                        "tipi": "$tipi"
                    },
                    "shuma": {
                        "$sum": "$kontrata.qmimi"
                    },
                    "count": {
                        "$sum": 1
                    }
                }
            },
            {
                "$sort": {
                    "_id.tipi": 1,
                    "_id.kompania": 1
                }
            },
            {
                "$project": {
                    "kompania": "$_id.kompania",
                    "tipi": "$_id.tipi",
                    "shuma": "$shuma",
                    "count": "$count",
                    "_id": 0
                }
            }
        ])
        resp = Response(
            response=json_util.dumps(json['result']),
            mimetype='application/json')
        return resp
