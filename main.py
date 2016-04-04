from mp285 import MP285
from controllers import Controller
import pylab as pl

c = Controller()
# each animal has a template, and every time it is put on rig, a new image is taken and stored
# then most recent one is shown on next day
# after alignment:
# zero the sutter
# close sutter stuff such that scanimage can run
# display animal, image of alignment, and a list of the positions that have been imaged relative to this zero
# (will require caching these b/c data is sent off computer every night)

# (possibly interact with matlab using ongoing local tcpip, to allow double clicking a location and seeing it live with 2p, or do that all from matlab)
