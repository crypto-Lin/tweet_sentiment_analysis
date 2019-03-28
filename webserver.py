from flask_restful import Resource, Api
from flask_cors import CORS
from flask import Flask, jsonify

import subprocess
import json

from get_news import get_top_news, get_next_news, update_news
from get_twitter_hist_score import get_hist_score
from get_twitter_hist_score_2 import get_hist_score_2

from get_sharpe_ratio import get_sharpe_ratio
from get_price import get_price
from get_bubble import get_bubble

app = Flask(__name__)
CORS(app)
api = Api(app)

class GetVote(Resource):
    def get(self, address):
        vote_info = subprocess.check_output(['docker exec nodeos cleos system listproducers -j -l 300'], shell=True)
        data = json.loads(vote_info)
        return jsonify(data)
api.add_resource(GetVote, '/api/getvote')

class LastedNews(Resource):
    def get(self, skiped, nums):
        data = get_top_news(skiped, nums)
        #data_jso = json.dumps(data)
        return jsonify(data)
api.add_resource(LastedNews, '/api/lastednews/<int:skiped>/<int:nums>')

class NextNews(Resource):
    def get(self, nextid, nums):
        data = get_next_news(nextid, nums)
        #data_json = json.dumps(data)
        return jsonify(data)
api.add_resource(NextNews, '/api/nextnews/<int:nextid>/<int:nums>')

class GetBubble(Resource):
    def get(self, coin):
        data = get_bubble(coin)
        return jsonify(data)
api.add_resource(GetBubble, '/api/getbubble/<string:coin>/')

class UpdateNews(Resource):
    def get(self, currentid):
        data = update_news(currentid)
        return jsonify(data)
api.add_resource(UpdateNews, '/api/updatenews/<int:currentid>')

class GetHistScore(Resource):
    def get(self):
        data = get_hist_score()
        return jsonify(data)
api.add_resource(GetHistScore, '/api/gethistsentiment')

class GetSharpeRatio(Resource):
    def get(self):
        data = get_sharpe_ratio()
        return jsonify(data)
api.add_resource(GetSharpeRatio, '/api/getsharperatio')


class GetPrice(Resource):
    def get(self):
        data = get_price()
        return jsonify(data)
api.add_resource(GetPrice, '/api/getprice')

class GetHistScore2(Resource):
    def get(self):
        data = get_hist_score_2()
        return jsonify(data)
api.add_resource(GetHistScore, '/api/gethistsentiment_2')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=18880, debug=False, threaded=True)

