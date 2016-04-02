from sutterMP285 import sutterMP285
import pylab as pl

# load target file
target_filename = tk.askFileDialog()
target = np.load(target_filename)

# ask user to move manually to approximate location
pl.imshow(target)

