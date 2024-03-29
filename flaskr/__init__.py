import os
from flask import Flask, request, abort
from flask_cors import CORS
from pymongo.collection import Collection
from pymongo import ReturnDocument, MongoClient
from flask_pymongo import PyMongo
from models import *
from errors import *
from auth import requires_auth

"""
   .oooooo.                          .o88o.  o8o             
   d8P'  `Y8b                         888 `"  `"'             
  888           .ooooo.  ooo. .oo.   o888oo  oooo   .oooooooo 
  888          d88' `88b `888P"Y88b   888    `888  888' `88b  
  888          888   888  888   888   888     888  888   888  
  `88b    ooo  888   888  888   888   888     888  `88bod8P'  
   `Y8bood8P'  `Y8bod8P' o888o o888o o888o   o888o `8oooooo.  
                                                   d"     YD  
                                                   "Y88888P'
"""
MONGO_DB_USER = os.getenv('MONGO_DB_USER')
MONGO_DB_PASSWORD = os.getenv('MONGO_DB_PASSWORD')

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['MONGO_URI'] = 'mongodb+srv://'+ MONGO_DB_USER + ':' + MONGO_DB_PASSWORD + '@cluster0.fl3oghq.mongodb.net/snow?retryWrites=true&w=majority'
    pymongo = PyMongo(app)
    resorts: Collection = pymongo.db.resorts

    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(res):
        res.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization'
            )
        res.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, DELETE, PATCH, PUT'
            )

        return res


    """
  ooooooooo.                             .                      
  `888   `Y88.                         .o8                      
   888   .d88'  .ooooo.  oooo  oooo  .o888oo  .ooooo.   .oooo.o 
   888ooo88P'  d88' `88b `888  `888    888   d88' `88b d88(  "8 
   888`88b.    888   888  888   888    888   888ooo888 `"Y88b.  
   888  `88b.  888   888  888   888    888 . 888    .o o.  )88b 
  o888o  o888o `Y8bod8P'  `V88V"V8P'   "888" `Y8bod8P' 8""888P'  
    """

#   	88""Yb 888888 .dP"Y8  dP"Yb  88""Yb 888888 .dP"Y8 
#       88__dP 88__   `Ybo." dP   Yb 88__dP   88   `Ybo." 
#       88"Yb  88""   o.`Y8b Yb   dP 88"Yb    88   o.`Y8b 
#       88  Yb 888888 8bodP'  YbodP  88  Yb   88   8bodP'

    @app.route("/<string:resort>", methods=["POST"])
    def create_resort(resort):
        raw_resort = request.get_json()

        if not raw_resort:
            abort(422)
        
        # looking up if the name of these lifts already exists
        all_resorts = resorts.find_one({'name': resort})
        print(all_resorts)
        if all_resorts:
            print('Resort with the name ' + raw_resort['name'] + ' already exists!')
            abort(409)

        resort_data = Resort(
            user = raw_resort['user'],
            name = raw_resort['name'],
            country = raw_resort['country'], 
            lifts = [],
            working_hours = {'mon': {}, 'tue': {}, 'wed': {}, 'thu': {}, 'fri': {}, 'sat': {}, 'sun': {}},
            temporarily_closed = {'working': False}
            )
        try:
            insert_result = resorts.insert_one(resort_data.to_bson())
            return jsonify({
                'success': True,
                'added': resort
            })
        except:
            abort(500)

    @app.route("/<string:resort>", methods=["GET"])
    def get_resort(resort):
        resort_data = resorts.find_one_or_404({'name': resort})
        return jsonify({
                "name": resort_data["name"],
                "closed_until": resort_data["closed_until"],
                "opened_until": resort_data["opened_until"],
                "temporarily_closed": resort_data["temporarily_closed"],
                "notes": resort_data["notes"],
                "notes_count": resort_data["notes_count"],
                "working": resort_data["working"],
                "working_hours": resort_data["working_hours"]
        })
    
    @app.route("/<string:resort>", methods={"PATCH"})
    @requires_auth('patch:resort')
    def update_resort(payload, resort):
        resort_data = request.get_json()

        if not resort_data:
            abort(422)

        try:
            updated = resorts.find_one_and_update(
                {"name": resort}, 
                {'$set': {
                    "closed_until": resort_data["closed_until"],
                    "opened_until": resort_data["opened_until"],
                    "temporarily_closed": resort_data["temporarily_closed"],
                    "notes": resort_data["notes"],
                    "notes_count": resort_data["notes_count"],
                    "working": resort_data["working"],
                    "working_hours": resort_data["working_hours"]
                }},
                return_document=ReturnDocument.AFTER,
            )
            if updated:
                return jsonify({
                    'updated_resort': Resort(**updated).to_json(),
                    'success': True
                })
            else:
                abort(404)
        except:
            abort(500)

    @app.route("/<string:resort>", methods=["DELETE"])
    @requires_auth('delete:resort')
    def delete_resort(payload, resort):
        try:
            resorts.delete_one({"name": resort})
            return jsonify({
                    "deleted": resort,
                    'success': True
                })
        except:
            abort(500)


#       88     88 888888 888888 .dP"Y8 
#       88     88 88__     88   `Ybo." 
#       88  .o 88 88""     88   o.`Y8b 
#       88ood8 88 88       88   8bodP'

    # Route for adding new lifts for a specified resort
    @app.route("/<string:resort>/lifts", methods=["POST"])
    @requires_auth('post:lift')
    def new_lift(payload, resort):
        raw_lift = request.get_json()
        raw_lift['working_hours'] = {'mon': {}, 'tue': {}, 'wed': {}, 'thu': {}, 'fri': {}, 'sat': {}, 'sun': {}}
        print(resort)
        if not raw_lift:
            abort(422)
        
        # looking up if the resort exists and has lifts array storing into variable
        all_lifts = resorts.find_one_or_404({'name': resort})['lifts']
        
        # looking up if the name of these lifts already exists
        exists = [l for l in all_lifts if l['name'] == raw_lift['name']]
        if exists:
            print('Lift with the name ' + raw_lift['name'] + ' already exists!')
            abort(409)

        try:
            lift = Lift(**raw_lift)
            
            resorts.find_one_and_update(
                {'name': resort}, 
                {'$push': {'lifts': 
                    {'$each': [lift.to_json()],
                    '$sort': {'id': 1}}}})
            return ({
                'success': True,
                'new_lift': lift.to_json()
            })
        except:
            abort(500)

    # Route for modifying working hours, notes ...
    @app.route("/<string:resort>/lifts", methods=['PUT'])
    @requires_auth('put:lift')
    def update_working_hours(payload, resort):
        raw_lifts = request.get_json()

        if not raw_lifts:
            abort(422)

        all_lifts = resorts.find_one_or_404({'name': resort})['lifts']
        
        try:
            for l in raw_lifts:
                for m in all_lifts:
                    if l['name'] == m['name']:

                        resorts.update_one({'name': resort, 'lifts.name': l['name']}, {
                            '$set': {
                                'lifts.$.notes': l['notes'],
                                'lifts.$.notes_count': l['notes_count'],
                                'lifts.$.working': l['working'],
                                'lifts.$.working_hours': l['working_hours']
                            }
                        })
            
            updated_lifts = resorts.find_one({'name': resort})['lifts']
            updated_lifts.sort(key = lambda x : int(x["id"]))
            
            return jsonify({
                    'lifts': updated_lifts,
                    "resort": resort,
                    'success': True
                })
        except:
            abort(500)

    # Route for changing name, type and capacity
    @app.route("/<string:resort>/lifts", methods=["PATCH"])
    @requires_auth('patch:lift')
    def update_lift(payload, resort):
        raw_lift = request.get_json()

        if not raw_lift:
            abort(422)

        # looking up if the resort exists and has lifts array
        all_lifts = resorts.find_one_or_404({'name': resort})['lifts']
        # looking up if the name of these lifts already exists
        exists = [l for l in all_lifts if l['name'] == raw_lift['name']]
        
        if not exists:
            print('Lift with the name ' + raw_lift['name'] + ' does not exists!')
            abort(404)

        try:
            for l in all_lifts:
                if l['name'] == raw_lift['name']:
                   updated = resorts.update_one({'name': resort, 'lifts.name': raw_lift['name']}, {
                        '$set': {
                            'lifts.$.id': raw_lift['id'],
                            'lifts.$.name': raw_lift['newName'],
                            'lifts.$.type': raw_lift['type'],
                            'lifts.$.capacity': raw_lift['capacity']
                        }}) 

            return jsonify({
                'success': True
            })

        except:
            abort(500)

    # route for getting the data of lifts
    @app.route("/<string:resort>/lifts", methods=["GET"])
    def get_lifts(resort):
        lifts = resorts.find_one_or_404({'name': resort})['lifts']
        
        lifts.sort(key = lambda x : int(x["id"]))

        lift_count = len(lifts)

        if lift_count == 0:
            abort(404)

        return jsonify({
            "success": True,
            "resort": resort,
            "lifts":  lifts,
            "number_of_lifts": lift_count
        }) 


#       .dP"Y8 88      dP"Yb  88""Yb 888888 .dP"Y8 
#       `Ybo." 88     dP   Yb 88__dP 88__   `Ybo." 
#       o.`Y8b 88  .o Yb   dP 88"""  88""   o.`Y8b 
#       8bodP' 88ood8  YbodP  88     888888 8bodP' 

    @app.route("/<string:resort>/slopes", methods=["POST"])
    @requires_auth('post:slope')
    def new_slope(payload, resort):
        new_slope = request.get_json()

        if not new_slope:
            abort(422)

        all_slopes = resorts.find_one_or_404({'name': resort})['slopes']

        exists = [l for l in all_slopes if l['name'] == new_slope['name']]
        if exists:
            print('Slope with the name ' + new_slope['name'] + ' already exists!')
            abort(409)
        try:
            slope = Slope(**new_slope)
            resorts.find_one_and_update(
                {'name': resort}, 
                {'$push': {'slopes': 
                    {'$each': [slope.to_json()],
                    '$sort': {'id': 1}}}})
            return ({
                'success': True,
                'new_slope': slope.to_json()
            })
        except:
            abort(500)

    @app.route("/<string:resort>/slopes", methods=["GET"])
    def get_slopes(resort):
        slopes = resorts.find_one_or_404({"name": resort})["slopes"]

        slopes.sort(key = lambda x : int(x["id"]))
        slopes_count = len(slopes)
        if slopes_count == 0:
            abort(404)

        return jsonify({
            "success": True,
            "resort": resort,
            "slopes": slopes,
            "number_of_slopes": slopes_count
        })

    @app.route("/<string:resort>/slopes", methods=['PUT'])
    @requires_auth('put:slope')
    def update_slopes(payload, resort):
        raw_slopes = request.get_json()

        if not raw_slopes:
            abort(422)

        all_slopes = resorts.find_one_or_404({'name': resort})['slopes']
        try:
            for l in raw_slopes:
                for m in all_slopes:
                    if l['name'] == m['name']:

                        resorts.update_one({'name': resort, 'slopes.name': l['name']}, {
                            '$set': {
                                'slopes.$.working': l['working'],
                                'slopes.$.notes': l['notes'],
                                'slopes.$.notes_count': l['notes_count'],
                                'slopes.$.snowmaking': l['snowmaking']
                            }
                        })
            
            updated_slopes = resorts.find_one({'name': resort})['slopes']
            updated_slopes.sort(key = lambda x : int(x["id"]))
            
            return jsonify({
                    'slopes': updated_slopes,
                    "resort": resort,
                    'success': True
                })
        except:
            abort(500)

    @app.route("/<string:resort>/slopes", methods=["PATCH"])
    @requires_auth('patch:slope')
    def update_slope(payload, resort):
        updated_slope = request.get_json()
        if not updated_slope:
            abort(422)

        all_slopes = resorts.find_one_or_404({"name": resort})["slopes"]
        exists = [s for s in all_slopes if s["name"] == updated_slope["name"]]
        if not exists:
            print('Slope with the name ' + updated_slope['name'] + ' does not exist!')
            abort(404)
        try:
            for s in all_slopes:
                if s["name"] == updated_slope["name"]:
                    updated = resorts.update_one({"name": resort, "slopes.name": updated_slope["name"]}, {
                        '$set': {
                            'slopes.$.name': updated_slope['newName'],
                            'slopes.$.difficulty': updated_slope['difficulty'],
                            'slopes.$.id': updated_slope['id']
                        }})
            return jsonify({
                'success': True
            })
        except:
            abort(500)

# # # # # # #

    # PUT vreme
    # GET vreme

    errors(app)

    return app

app = create_app()
application = app

if __name__ == '__main__':
    app.run()