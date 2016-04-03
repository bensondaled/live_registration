from mp285 import MP285
import pylab as pl

# ask for animal name (cross reference with C:\Data available animals)

# ask for session to align to, with default being most recent

# load target file
target_filename = tk.askFileDialog()
target = np.load(target_filename)

# ask user to move manually to approximate location
pl.imshow(target)

# do the alignment

# report ailgnment outcome, possible manual interventions

# zero the sutter

# close sutter stuff such that scanimage can run
# display animal, image of alignment, and a list of the positions that have been imaged relative to this zero
# (will require caching these b/c data is sent off computer every night)

# (possibly interact with matlab using ongoing local tcpip, to allow double clicking a location and seeing it live with 2p, or do that all from matlab)
