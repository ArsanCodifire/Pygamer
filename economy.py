import pyairtable as py

api="patjuceu8KPXSyY7d.ceb191e382784d9710beba9337e52506dff6a08df7e81959f51fac86b1ac20bf"
clnt=py.Api(api)
table=clnt.table("apppfyBVPqqW8yELE", "tblSbAtHfGeQLo5pa")

def insert(id):
    dt={
        "user_id" : id,
        "Pycoin" : 100,
        "Status" : "mid"
        }
    table.create(dt)

def update(id,coin,sts):
    records = table.all(formula=f"{{user_id}} = '{id}'")
    if records:
        rec_id, cn=records[0]['id'], records[0]["fields"]["Pycoin"]
        table.update(rec_id, {"user_id" : id, "Pycoin" : cn+coin, "Status" : "mid"})
        return "acc"
    else:
        return "You need an account! Use /account to create one."

def delete(id):
    records = table.all(formula=f"{{user_id}} = '{id}'")
    if records:
        table.delete(records[0]['id'])
    else:
         return "No Record"

def get_coin(id):
    records = table.all(formula=f"{{user_id}} = '{id}'")
    if records:
        rc=records[0]["id"]
        coin=records[0]["fields"]["Pycoin"]
        return coin, "acc"
    else:
        insert(id)
        return 100, "You created an account! You have <:pycoin:1309160887587831949> 100 Pycoin!"