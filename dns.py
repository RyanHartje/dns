#import dns.zones
# log_path, zone_path
import sys, os, config, logging, datetime, errno

#initialize the logs
logging.basicConfig(filename=config.log_path, level=logging.INFO)

def command_line():
  if len(sys.argv) > 2:
    command = sys.argv[1]
    args = sys.argv[1:len(sys.argv)]
    print("nn %s %s" % (command, args))
  else:
    print('nn_dns [command] <domains>\nNinjanode DNS\nexample: nn_dns create domain.com')


class Zone():
    def __init__(self,domain):
        # We need to set the domain, and create a file for the zone if it doesn't exist.
        # This will allow us to import zones because they will be in our zone file path.
        logging.info('[%s] creating zone for %s' % domain)
    	self.domain = domain
        self.file = config.zone_path + domain + '.db'
        # We need to set up flags to open our file with:
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY

        # Let's try opening the file to see if it exists.
        # If it doesn't, we'll create it, and set up the zone.
        try:
          file_handle = os.open(self.file)
        except OSError as e:
          if e.errno == errno.EEXIST:
            logging.info('[%s] Zone for %s exists' % (datetime.datetime.now(),self.domain)) 
        else:
          logging.info('[%s] Attempting to create zone file for %s' % (datetime.datetime.now())))
         
          # To create a new zone, we'll copy a template, then sed replace example.com
          # with our domain, and create a new serial.
          try:
            template_file = os.fdopen('./template.db', 'r')
            zone_contents = template_file.read()
            template_file.close()
          except:
            logging.error("[%s] ERROR - failed to find template file at ./template.db" % datetime.datetime.now()
          
          # Get Serial Data
          Y = datetime.datetime.now().year
          M = "%02d" % datetime.datetime.now().month
          D = "%02d" % datetime.datetime.now().day
          # Let's create our serial object
          # YYYYMMDD00
          # 2002022401
          serial = "%s%s%s00"

          # Add in our regex here to replace example.com and the current serial to our examples
         
          
          # Now write our zone to disk
          with os.fdopen(file_handle, 'w') as file_obj:
            file_obj.write(zone_contents)
            file_obj.close()
          
        

    #def get_domain(domain):
        

# Create Zone or Zones
for zone in 
my_zone = Zone()
#print(my_zone.domain)
