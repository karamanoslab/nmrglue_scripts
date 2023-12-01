import nmrglue as ng
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm
from matplotlib.widgets import Slider
import sys

import warnings
warnings.filterwarnings("ignore")

# read in the data from a NMRPipe file
if len(sys.argv)<2 or sys.argv[1] == '-h' or  sys.argv[1]=='-help' :
    print("\n Run as python pyNmrDraw.py [path to 2D spectrum]\n")
    sys.exit(-1)
else:
    spectrum=sys.argv[1]

dic, data = ng.pipe.read(spectrum)

# plot parameters
cmap = matplotlib.cm.Blues_r    # contour map (colors to use for contours)
contour_start = 500000           # contour level start value
contour_num = 20                # number of contour levels
contour_factor = 1.20          # scaling factor between contour levels

# calculate contour levels
cl = contour_start * contour_factor ** np.arange(contour_num) 

# create the figure
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111)

f_d=ax.contour(data, cl, cmap=cmap, extent=(0, data.shape[1] - 1, 0, data.shape[0] - 1))

ax.set_ylabel("f1 (points)")
ax.set_xlabel("f2 (points)")

ax_Cont = fig.add_axes([0.1, 0.96, 0.2, 0.02])
ax_Cont.spines['top'].set_visible(True)
ax_Cont.spines['right'].set_visible(True)

ax_h = fig.add_axes([0.1, 0.93, 0.2, 0.02])
ax_h.spines['top'].set_visible(True)
ax_h.spines['right'].set_visible(True)

ax_v = fig.add_axes([0.1, 0.90, 0.2, 0.02])
ax_v.spines['top'].set_visible(True)
ax_v.spines['right'].set_visible(True)


ax_P0h = fig.add_axes([0.4, 0.93, 0.2, 0.02])
ax_P0h.spines['top'].set_visible(True)
ax_P0h.spines['right'].set_visible(True)

ax_P1h = fig.add_axes([0.7, 0.93, 0.2, 0.02])
ax_P1h.spines['top'].set_visible(True)
ax_P1h.spines['right'].set_visible(True)


ax_P0v = fig.add_axes([0.4, 0.90, 0.2, 0.02])
ax_P0v.spines['top'].set_visible(True)
ax_P0v.spines['right'].set_visible(True)

ax_P1v = fig.add_axes([0.7, 0.90, 0.2, 0.02])
ax_P1v.spines['top'].set_visible(True)
ax_P1v.spines['right'].set_visible(True)


s_Cont = Slider(ax=ax_Cont, label='2D cont', valmin=100, valmax=np.max(data)*0.2,
              valinit=contour_start, valfmt=' %1.1f ', facecolor='#cc7000')

s_h = Slider(ax=ax_h, label='h ', valmin=0, valmax=data.shape[0] - 1,
              valinit=0, valfmt=' %i pnts', facecolor='#cc7000')

s_v = Slider(ax=ax_v, label='v ', valmin=0, valmax=data.shape[1] - 1,
              valinit=0, valfmt=' %i pnts', facecolor='#cc7000')


s_P0h = Slider(ax=ax_P0h, label='P0', valmin=-180, valmax=180,
              valinit=0, valfmt=' %i deg', facecolor='#cc7000')

s_P1h = Slider(ax=ax_P1h, label='P1', valmin=-180, valmax=180,
              valinit=0, valfmt=' %i deg', facecolor='#cc7000')

s_P0v = Slider(ax=ax_P0v, label='P0', valmin=-180, valmax=180,
              valinit=0, valfmt=' %i deg', facecolor='#cc7000')

s_P1v = Slider(ax=ax_P1v, label='P1', valmin=-180, valmax=180,
              valinit=0, valfmt=' %i deg', facecolor='#cc7000')


def animate(val):  
    contour_start = s_Cont.val
    h=s_h.val
    v=s_v.val
    p0h=s_P0h.val
    p1h=s_P1h.val
    p0v=s_P0v.val
    p1v=s_P1v.val
    
    p0h = p0h * np.pi / 180.  # convert to radians
    p1h = p1h * np.pi / 180.

    p0v = p0v * np.pi / 180. 
    p1v = p1v * np.pi / 180.

    ax.cla()

    cl = contour_start * contour_factor ** np.arange(contour_num) 
    ax.contour(data, cl, cmap=cmap, extent=(0, data.shape[1] - 1, 0, data.shape[0] - 1))

    # plot slices in each direction
    xslice = data[int(h), :]    
    ht=ng.proc_base.ht(xslice, N=xslice.shape[-1])  #hilbelt transform to reconstruct imaginaries
    apodx = np.exp(1.0j * (p0h + (p1h * np.arange(data.shape[1]) / data.shape[1])))
    phasedx=ht*apodx

    ax.plot(range(data.shape[1]), [h]*data.shape[1], '-y' ) 
    ax.plot(range(data.shape[1]), phasedx / (contour_start/10))# + h)


    yslice = data[:, int(v)]
    ht=ng.proc_base.ht(yslice, N=yslice.shape[-1])
    apody = np.exp(1.0j * (p0v + (p1v * np.arange(data.shape[0]) / data.shape[0])))
    phasedy=ht*apody

    ax.plot( [v]*data.shape[0], range(data.shape[0]))
    ax.plot( phasedy / (contour_start/10) + 0, range(data.shape[0]))
    plt.draw()
    #fig.canvas.draw_idle()

        
# Create animation
s_Cont.on_changed(animate)
s_h.on_changed(animate)
s_v.on_changed(animate)
s_P0h.on_changed(animate)
s_P1h.on_changed(animate)
s_P0v.on_changed(animate)
s_P1v.on_changed(animate)

plt.show()