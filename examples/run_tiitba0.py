import sys
sys.path.append('/home/rdcorona/phD/tiitba_n/code')
from tiitba0 import Load_Pick 

#### 
tmp = Load_Pick('/home/rdcorona/phD/tiitba_n/examples/1928.03.22.GDL.NS.125.jpg')
img, points = tmp.load_image()

print(points)

print('All set ')