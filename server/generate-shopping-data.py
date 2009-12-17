from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.db import transaction
from server.shopping.models import *

import datetime
import random
import sys
import traceback

NUM_CPU_MANUFACTURERS = 3
NUM_CPUS = 8
NUM_HDD_MANUFACTURERS = 3
NUM_HDDS = 10
NUM_PC_MANUFACTURERS = 5
NUM_PCS = 500
NUM_PRICES = 2
NUM_USAGES = 4

@transaction.commit_manually
def generate_data():
    try:
        cpus = generate_objects(CPU, NUM_CPU_MANUFACTURERS, NUM_CPUS)
        disks = generate_objects(HardDisk, NUM_HDD_MANUFACTURERS, NUM_HDDS)
        generate_pcs(cpus, disks, NUM_PC_MANUFACTURERS, NUM_PCS, NUM_PRICES, NUM_USAGES)
        
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback,
                                  file=sys.stdout)
        transaction.rollback()
    else:
        transaction.commit()

def generate_manufacturers(manufacturer_type, num_manufacturers):
    manufacturers = []
    for i in range(num_manufacturers):
        m = Manufacturer()
        m.name = "%s manufacturer %d" % (manufacturer_type, i)
        m.address = "address %d" % (i)
        m.save()
        manufacturers.append(m)
    return manufacturers
    
def generate_objects(model, num_manufacturers, num_objects):
    manufacturers = generate_manufacturers(model.__name__, num_manufacturers)
    objects = []
    for i in range(num_objects):
        obj = model()
        obj.manufacturer = random.choice(manufacturers)
        obj.model = "%s model %d" % (obj.manufacturer.name, i)
        obj.save()
        objects.append(obj)
    return objects

def generate_pcs(cpus, disks, num_manufacturers, num_pcs, num_prices, num_usages):
    manufacturers = generate_manufacturers("pc", num_manufacturers)
    prices = range(1, num_prices+1)
    usages = []
    for i in range(num_usages):
        usage = Usage(description = "usage %d" % (i))
        usage.save()
        usages.append(usage)
    for i in range(num_pcs):
        pc = DesktopPC()
        pc.model = "pc %d" % (i)
        pc.price = random.choice(prices)
        pc.manufacturer = random.choice(manufacturers)
        pc.usage = random.choice(usages)
        pc.cpu = random.choice(cpus)
        pc.hdd = random.choice(disks)
        pc.save()
        
if __name__ == "__main__":
    generate_data()
