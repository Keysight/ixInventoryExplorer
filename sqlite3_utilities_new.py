import sqlite3
import json

def _get_db_connection():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn


def write_performace_metrics():
    conn = _get_db_connection()
    cur = conn.cursor()



def write_data_to_database(table_name=None, records=None, ip_tags_dict=None):
    tags = ""
    conn = _get_db_connection()
    cur = conn.cursor()
    
    # Clear of old records from database
    cur.execute(f"DELETE FROM {table_name}")
    
    for record in records:
        if table_name == "chassis_summary_details":
            if ip_tags_dict:
                tags = ip_tags_dict.get(record["chassisIp"]) #This is a list
                if tags:
                    tags = ",".join(tags)
                else:
                    tags = ""
            else:
                tags = ""
                
            record.update({"tags": tags })
            
            cur.execute(f"""INSERT INTO {table_name} (ip, chassisSN, controllerSN, type_of_chassis, 
                        physicalCards, status_status, ixOS, ixNetwork_Protocols, ixOS_REST, tags, lastUpdatedAt_UTC, 
                        mem_bytes, mem_bytes_total, cpu_pert_usage, os) VALUES 
                        ('{record["chassisIp"]}', '{record['chassisSerial#']}',
                        '{record['controllerSerial#']}','{record['chassisType']}','{record['physicalCards#']}',
                        '{record['chassisStatus']}',
                        '{record['IxOS']}','{record['IxNetwork Protocols']}','{record['IxOS REST']}','{record['tags']}', 
                        datetime('now'), '{record['mem_bytes']}','{record['mem_bytes_total']}','{record['cpu_pert_usage']}',
                        '{record['os']}')""")
        
        if table_name == "license_details_records":
            for rcd in record:
                cur.execute(f"""INSERT INTO {table_name} (chassisIp, typeOfChassis, hostId, partNumber, 
                            activationCode, quantity, description, maintenanceDate, expiryDate, isExpired, lastUpdatedAt_UTC) VALUES 
                            ('{rcd["chassisIp"]}', '{rcd["typeOfChassis"]}',
                            '{rcd["hostId"]}','{rcd["partNumber"]}',
                            '{rcd["activationCode"]}','{str(rcd["quantity"])}','{rcd["description"]}',
                            '{rcd["maintenanceDate"]}','{rcd["expiryDate"]}','{str(rcd["isExpired"])}', datetime('now'))""")
                
        if table_name == "chassis_card_details":
            for rcd in record:
                
                if ip_tags_dict:
                    tags = ip_tags_dict.get(record["chassisIp"]) #This is a list
                    if tags:
                        tags = ",".join(tags)
                    else:
                        tags = ""
                else:
                    tags = ""    
                rcd.update({"tags": tags })
                cur.execute(f"""INSERT INTO {table_name} (chassisIp,typeOfChassis,cardNumber,serialNumber,cardType,numberOfPorts,tags,
                            lastUpdatedAt_UTC) VALUES 
                            ('{rcd["chassisIp"]}', '{rcd["chassisType"]}', '{rcd["cardNumber"]}','{rcd["serialNumber"]}',
                            '{rcd["cardType"]}','{rcd["numberOfPorts"]}', '{rcd['tags']}', datetime('now'))""")
            
        if table_name == "chassis_port_details":
            for rcd in record:
                cur.execute(f"""INSERT INTO {table_name} (chassisIp,typeOfChassis,cardNumber,portNumber,phyMode,transceiverModel,
                            transceiverManufacturer,owner,totalPorts,ownedPorts,freePorts, lastUpdatedAt_UTC) VALUES 
                                ('{rcd["chassisIp"]}', '{rcd["typeOfChassis"]}', '{rcd["cardNumber"]}','{rcd["portNumber"]}',
                                '{rcd.get("phyMode","NA")}','{rcd["transceiverModel"]}', '{rcd["transceiverManufacturer"]}','{rcd["owner"]}',
                                '{rcd["totalPorts"]}','{rcd["ownedPorts"]}', '{rcd["freePorts"]}',datetime('now'))""")
                
        if table_name == "chassis_sensor_details":
            for rcd in record:
                unit = rcd["unit"]
                if {rcd["unit"]} ==  "CELSIUS": unit = f'{rcd["value"]} {chr(176)}C'
                if {rcd["unit"]} ==  "AMPERSEND": unit = "AMP"
                cur.execute(f"""INSERT INTO {table_name} (chassisIp,typeOfChassis,sensorType,sensorName,sensorValue,unit,lastUpdatedAt_UTC) VALUES 
                                ('{rcd["chassisIp"]}', '{rcd["typeOfChassis"]}', '{rcd["type"]}','{rcd["name"]}',
                                 '{rcd["value"]}','{unit}', datetime('now'))""")
            
    cur.close()
    conn.commit()
    conn.close()

def read_data_from_database(table_name=None):
    conn = _get_db_connection()
    cur = conn.cursor()
    records = cur.execute(f"SELECT * FROM {table_name}").fetchall()
    cur.close()
    conn.close()
    return records


def writeTags(ip, tags, type_of_update=None, operation=None):
    updated_tags = ""
    if type_of_update == "chassis":
        table = 'user_ip_tags'
        field = 'ip'
            
            
    if type_of_update == "card":
        table = 'user_card_tags'
        field = 'serialNumber'
        
    conn = _get_db_connection()
    cur = conn.cursor()
    
    # Get Present Tags from DB
    ip_tags_dict = getTagsFromCurrentDatabase(type_of_update)
    currenttags = ip_tags_dict.get(ip) # This is a list    
    new_tags = tags.split(",")
    
   # There is a record present
    if currenttags: 
        if operation == "add":
            updated_tags = ",".join(currenttags + new_tags)
        elif operation == "remove":
            for t in new_tags:
                currenttags.remove(t)
            updated_tags = ",".join(currenttags)
            
        cur.execute(f"UPDATE {table} SET tags = '{updated_tags}' where {field} = '{ip}'")
        cur.execute(f"UPDATE chassis_summary_details SET tags = '{updated_tags}' where ip = '{ip}'")
    else: # New Record
        cur.execute(f"INSERT INTO {table} ({field}, tags) VALUES ('{ip}', '{tags}')")
        
        
    conn.commit()
    cur.close()
    conn.close()
    return "Records successfully updated"
        
def getTagsFromCurrentDatabase(type_of_update=None):
    ip_tags_dict = {}
    if type_of_update == "chassis":
        table = "user_ip_tags"
        field = "ip"
        
    if type_of_update == "card":
        table = "user_card_tags"
        field = "serialNumber"
    
    conn = _get_db_connection()
    cur = conn.cursor()

    query = f"SELECT * FROM {table};"
    posts = cur.execute(query).fetchall()
    cur.close()
    conn.close()
    for post in posts:
        ip_tags_dict.update({post[field]: post["tags"].split(",")})
    return ip_tags_dict


def getChassistypeFromIp(chassisIp):
    conn = _get_db_connection()
    cur = conn.cursor()
    
    query = f"SELECT type_of_chassis FROM chassis_summary_details where ip = '{chassisIp}';"
    posts = cur.execute(query).fetchone()
    cur.close()
    conn.close()
    if posts:
        return  posts['type_of_chassis']
    return "NA"
    

def write_username_password_to_database(list_of_un_pw):
    conn = _get_db_connection()
    cur = conn.cursor()
    user_pw_dict = []
    cur.execute("DELETE from user_db")
    user_pw_dict = creat_config_dict(list_of_un_pw)
    print(user_pw_dict)
    if user_pw_dict:
        json_str_data = json.dumps(user_pw_dict)
        for item in user_pw_dict:
            q = f"""INSERT INTO user_db (ip, username, password, api_key) VALUES  
            ('{item.get("ip")}','{item.get("username")}','{item.get("password")}','{item.get("api_key", json_str_data)}')"""
            cur.execute(q)
        cur.close()
        conn.commit()
        conn.close()

def read_username_password_from_database():
    conn = _get_db_connection()
    cur = conn.cursor()
    query = f"SELECT api_key FROM user_db;"
    posts = cur.execute(query).fetchone()
    cur.close()
    conn.close()
    if posts:
        return  posts['api_key']
    return []


def creat_config_dict(list_of_un_pw):
    user_pw_dict = []
    print(list_of_un_pw)
    for entry in list_of_un_pw.split("\n"):
        user_pw_dict.append({
        "ip": entry.split(",")[0].strip(),
        "username": entry.split(",")[1].strip(),
        "password": entry.split(",")[2].strip(),
        })
    return user_pw_dict