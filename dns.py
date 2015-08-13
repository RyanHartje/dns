#import dns.zones
# log_path, zone_path
import sys, os, config, logging, datetime, errno, re, glob

#initialize the logs
logging.basicConfig(filename=config.log_path, level=logging.INFO)

def list_zones():
  files = []
  #for file in glob.glob('%s*db' % config.zone_path):
  #  files.append(file)
  for file in os.listdir(config.zone_path):
    if file.endswith('.db'):
      files.append(file)
  
  return files

class Zone():
    def __init__(self,domain):
        self.zone_contents=""
        # We need to set the domain, and create a file for the zone if it doesn't exist.
        # This will allow us to import zones because they will be in our zone file path.
        logging.info('[%s] creating zone for %s' % (datetime.datetime.now(), domain))
    	self.domain = domain
        self.file = config.zone_path + domain + '.db'
        # We need to set up flags to open our file with:
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY

        # Let's try opening the file to see if it exists.
        # If it doesn't, we'll create it, and set up the zone.
        # If this works, we should preserve it, and alert the user
        try:
          file_handle = os.open(self.file, flags)
        except OSError as e:
          if e.errno == errno.EEXIST:
            logging.info('[%s] Zone for %s exists' % (datetime.datetime.now(),self.domain)) 
            file_handle = open(self.file)
            self.zone_contents = file_handle.read()
        # This else should only contain the creation of the zone
        else:
          logging.info('[%s] Attempting to create zone file for %s' % (datetime.datetime.now(),domain))
         
          # To create a new zone, we'll copy a template, then sed replace example.com
          # with our domain, and create a new serial.
          try:
            template_file = open('./template.db')
            self.zone_contents = template_file.read()
            logging.info("[%s] Zone contents generated:\n%s\n\n" % (datetime.datetime.now(),self.zone_contents))
            #template_file.close()
          except:
            logging.error("[%s] ERROR - failed to find template file at ./template.db" % datetime.datetime.now())
          # Get Serial Data
          Y = datetime.datetime.now().year
          M = "%02d" % datetime.datetime.now().month
          D = "%02d" % datetime.datetime.now().day
          # Let's create our serial object
          # YYYYMMDD00
          # 2002022401
          serial = "%s%s%s00" % (Y,M,D)
          logging.info("[%s] Generated serial: %s" % (datetime.datetime.now(),serial))

          # Add in our regex here to replace example.com and the current serial to our examples
          self.zone_contents = re.sub("example.com", domain, self.zone_contents)
          self.zone_contents = re.sub("2002022401", serial, self.zone_contents)
          logging.info('[%s] Zone contents after sub:\n%s\n\n' % (datetime.datetime.now(),self.zone_contents))
           
          
          # Now write our zone to disk
          with os.fdopen(file_handle, 'w') as file_obj:
            file_obj.write(self.zone_contents)
            file_obj.close()
          
        

    def get_zone(self):
      self.zone_contents = open(self.file).read()
      return self.zone_contents

    def get_records_type(self,record_type):
      zone_file = open(self.file)
      record_data = zone_file.read().split('\n')
      results = []
      for record in record_data:
        if len(record.split()) > 2:
          if record.split()[2] == record_type:
            results.append(record)
      zone_file.close()
      return results

    def find_record(self,value):
      zone_file = open(self.file)
      record_data = zone_file.read().split('\n')
      results = []
      for record in record_data:
        if len(record.split()) > 0:
          if record.split()[0] == value:
            results.append(record)
      zone_file.close()
      return results

    def add_record(self,name,type,value):
      zone_file = open(self.file,'a')
      zone_file.write("%s IN %s %s \n" % (name,type,value))
      zone_file.close()

    def edit_record(self,old_name,old_type,old_value,new_name,new_type,new_value):
      zone_file = open(self.file,'r+')
      record = "%s IN %s %s \n" % (old_name,old_type,old_value)
      file_content = zone_file.readlines()
      # Set the cursor at the top of the file again
      zone_file.seek(0)
      for line in file_content:
        # When we find the old line, write the new one instead
        # This may seem elaborate, but its a way of ensuring we're editing the right
        #   record and that we don't miss it
        if re.search(old_name,line) and re.search(old_type,line) and re.search(old_value,line):
          zone_file.write("%s IN %s %s \n" % (new_name,new_type,new_value))
        else:
          zone_file.write(line)
      # remove any remaining text after our cursor
      zone_file.truncate()
      
      zone_file.close()

    def delete_record(self,name,type,value):
      # We should really have some sort of backup in effect here
      zone_file = open(self.file,'r+')
      record = "%s IN %s %s \n" % (name,type,value)
      file_content = zone_file.readlines()
      # Let's remove the file before we rewrite it
      self.delete()

      for line in file_content:
        # As long as the record we want to delete isn't here, lets keep writing
        if line != record:
          zone_file.write(line)
      zone_file.close()

    def delete_record_match(self,match_value):
      # We should really have some sort of backup in effect here
      zone_file = open(self.file,'r+')
      for line in zone_file.readlines():
        if line != match_value:
          zone_file.write(line)
      zone_file.close()

     

    def delete(self):
      os.remove(self.file)

def get_records(domain):
  zone_file = open(config.zone_path+domain+".db")
  record_data = zone_file.read().split('\n')
  records = []
  for record in record_data:
    #records.append(record) 
    if len(record.split()) > 1:
      if record.split()[1] == "IN":
        #print(record)
        records.append(record)
  return records

def rndc_reload():
  # First, check the zone syntax. If a syntax check passes, 
  # reload rndc so our zone changes go into effect
  #if
  os.system('rndc reload')
  logging.info('[%s] rndc reloaded' % datetime.datetime.now())
 
      
        
if __name__ == "__main__":
  logging.info("\n[%s] called from command line" % datetime.datetime.now())
  if len(sys.argv) > 1:
    command = sys.argv[1]
    args = sys.argv[2:len(sys.argv)]
  else:
    print('nn_dns [command] <domains>\nNinjanode DNS\nexample: nn_dns create domain.com')



  # Create Zone or Zones
  if command == "create":
    for domain in args: 
      my_zone = Zone(domain)
  elif command == "delete":
    for domain in args:
      my_zone = Zone(domain)
      my_zone.delete()
  elif command == "list":
    if not args:
      print(list_zones())
    else:
      for arg in args:
        if arg:
            print(get_records(arg))
  elif command == "debug":
    print("%s\%s" % (command, args))
      
