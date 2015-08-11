#import dns.zones
# log_path, zone_path
import sys, os, config, logging, datetime, errno, re

#initialize the logs
logging.basicConfig(filename=config.log_path, level=logging.INFO)

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
      return self.zone_contents

    def get_records_type(self,record_type):
      zone_file = open(self.file)
      record_data = [zone_file.read().split('\n')]
      results = []
      for record in record_data:
        if record.split() == record_type:
          results.append(record)
      return results


    def delete(self):
      os.remove(self.file)
      
        
if __name__ == "__main__":
  logging.info("\n[%s] called from command line" % datetime.datetime.now())
  if len(sys.argv) > 2:
    command = sys.argv[1]
    args = sys.argv[1:len(sys.argv)]
    print("nn %s %s" % (command, args))
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
      
