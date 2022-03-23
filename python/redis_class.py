import redis
import datetime
import json

class RedisClient(object):
    def __init__(self, host, port, password, database=0):
        self.db = redis.Redis(host=host, port=port, password=password, db=database)
        self.host = host
        self.port = port
        self.password = password

    def get(self, key, start_index=0, end_index=0):
      try:
        value = self.db.get(key).decode()
        if value.isalpha():
            pass
        elif "." in value and not ":" in value:
            value = float(value)
        elif value.count("-") > 1 and ":" in value:
          value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f").timestamp()
        elif value.count("-") >= 3:
          pass
        elif value.count("-") == 1 and value[1:].isnumeric():
          value = int(value)
        elif value.isnumeric():
            value = int(value)
        else:
            pass
      except Exception as e:
        decoded_list = []
        value = self.db.lrange(key, start_index, end_index)
        for i in range(len(value)):
          if '{' in value[i].decode():
            value[i] = json.loads(value[i].decode())
            decoded_list.append(value[i])
          else:
            decoded_list.append(value[i].decode())
        value = decoded_list
      return value
    
    def get_all_keys(self):
      keys = self.db.keys()
      for i in range(len(keys)):
        keys[i] = keys[i].decode()
      return keys
    
    def get_all_keys_and_values(self):
      key_value_dict = {}
      keys = self.get_all_keys()
      for i in range(len(keys)):
        value = self.get(keys[i])
        key_value_dict[keys[i]] = value
      return key_value_dict

    def set(self, key, value):
        self.db.set(key, value)
        
    def set_multiple(self, key_value_dict):
        pipe = self.db.pipeline()
        for key, value in key_value_dict.items():
          pipe.set(key, value)
        pipe.execute()

    def delete(self, key):
        self.db.delete(key)

    def exists(self, key):
      return self.db.exists(key)
    
if __name__ == '__main__':
  redis = RedisClient(host='192.168.0.150', port=6379, password="Redis2019!")
  print(redis.get_all_keys_and_values())