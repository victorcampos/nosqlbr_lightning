import pymongo
from bson.code import Code
from datetime import datetime


class MongoLogger:
    connection = None
    db = None
    collection = None


    def __init__(self, connection=None, db=None, collection=None):
        self.connection = connection

        if db != None and collection != None:
            self.db = self.connection[db]
            self.collection = self.db[collection]

            self.collection.create_index("id")
            self.collection.create_index(
                [("id", pymongo.ASCENDING), ("date", pymongo.DESCENDING), ("hour", pymongo.DESCENDING)])


    def log(self, id=None, data=None):
        if id and data:
            now = datetime.now()
            entry = {"id": id, "date": now.date().isoformat(), "hour": now.hour}
            update_data = { "$inc": { "actions.%s" % data : 1 }}

            self.collection.update(entry, update_data, upsert=True)



class MongoFetcher:
    connection = None
    db = None
    collection = None

    def __init__(self, connection=None, db=None, collection=None):
        self.connection = connection

        if db != None and collection != None:
            self.db = self.connection[db]
            self.collection = self.db[collection]


    def fetch(self, id=None, start_date=None, end_date=None, total=False):
        if id != None and start_date != None and end_date != None:
            map = self.get_map_function(total=total)
            reduce = self.get_reduce_function()

            query = self.get_query(id=id, start_date=start_date, end_date=end_date)

            result = self.collection.map_reduce(map, reduce, out="results", query=query)

            summary_data = { "action_types" : [], "summary" : None }
            result_arr = []

            if total == False:
                for doc in result.find():
                    for action in doc["value"]:
                        if not action in summary_data["action_types"]:
                            summary_data["action_types"].append(action)

                    result_arr.append({"date": doc["_id"], "total": doc["value"]})
            else:
                doc = result.find_one()

                for action in doc["value"]:
                    if not action in summary_data["action_types"]:
                        summary_data["action_types"].append(action)

                result_arr.append({"total": doc["value"]})

            result.drop()

            summary_data["summary"] = result_arr

            return summary_data


    def get_map_function(self, total=False):
        key_var = "this.date"

        if total:
            key_var = "1"

        map = Code(
            "function() {"
            "   for(i in this.actions) {"
            "       var action = {};"
            "       action[i] = this.actions[i];"
            "       emit(%s, action);"
            "   }"
            "}" % key_var)

        return map


    def get_reduce_function(self):
        reduce = Code(
                "function(k, vals) {"
                "    total = {};"
                "    for (i in vals) {"
                "        for (n in vals[i]) {"
                "            if(!total[n]) {"
                "                total[n] = 0;"
                "            }"
                "            total[n] += vals[i][n];"
                "        }"
                "    }"
                "    return total;"
                "}")

        return reduce


    def get_query(self, id=None, start_date=None, end_date=None):
        query = { "id": "%s"%id, "date": { "$gte": start_date.isoformat(), "$lte": end_date.isoformat() } }

        return query
