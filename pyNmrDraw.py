import nmrglue as ng
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm
from matplotlib.widgets import Slider, RangeSlider
import sys
from optparse import OptionParser
import warnings
warnings.filterwarnings("ignore")


'author: @theok'

# read in the data from a NMRPipe file
if len(sys.argv)<2  :
    print("\n Run as python pyNmrDraw.py [path to 1D/2D spectrum]\n")
    sys.exit(-1)
else:
    spectrum=sys.argv[1]


parser = OptionParser(usage = """\n python %prog [path to 1D/2D spectrum] [options] \n
   Script to plot and save 1D or 2D nmrdata
   requires nmrglue 0.8 or later
""")

parser.add_option("-w", "--whiteBackground", dest="wb", action="store_true",
                  help="option to have a white background",
                  default=False)
                  
               
(options, args) = parser.parse_args()
wb=options.wb

if not wb :
    plt.style.use('dark_background')


dic, data = ng.pipe.read(spectrum)

# plot parameters
cmap = matplotlib.cm.Blues_r    # contour map (colors to use for contours)
cmap_neg = matplotlib.cm.Reds    # contour map (colors to use for contours)
contour_start = 500000           # contour level start value
contour_num = 20                # number of contour levels
contour_factor = 1.20          # scaling factor between contour levels

# calculate contour levels
cl = contour_start * contour_factor ** np.arange(contour_num) 
cl_neg = -cl[::-1]

# create the figure
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111)
    

ax.set_ylabel("f1 (points)")
ax.set_xlabel("f2 (points)")
ax.xaxis.label.set_color('white')
ax.xaxis.label.set_color('white')

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


if (data.shape[0]!=1):
    f_d=ax.contour(data, cl, cmap=cmap, extent=(0, data.shape[1] - 1, 0, data.shape[0] - 1))
    ax.contour(data, cl_neg, cmap=cmap_neg, extent=(0, data.shape[1] - 1, 0, data.shape[0] - 1))
    
    s_Cont = Slider(ax=ax_Cont, label='2D cont', valmin=1000, valmax=np.max(data)*0.2,
              valinit=contour_start, valfmt=' %i ', facecolor='#cc7000')
              
else:
    ax.plot(range(data.shape[1]), data[0])
    ax.set_ylim( min(data[0])*1.2 ,max(ax.get_ylim()))
    s_Cont = RangeSlider(ax_Cont, 'Int', np.min(data)*1.5, np.max(data)*1.5, facecolor='#cc7000')


s_h = Slider(ax=ax_h, label='h ', valmin=0, valmax=data.shape[0] - 1,
              valinit=0, valfmt=' %i pnts', facecolor='#cc7000')

s_v = Slider(ax=ax_v, label='v ', valmin=0, valmax=data.shape[1] - 1,
              valinit=0, valfmt=' %i pnts', facecolor='#cc7000')


s_P0h = Slider(ax=ax_P0h, label='P0', valmin=-180, valmax=180,
              valinit=0, valfmt=' %.1f deg', facecolor='#cc7000')

s_P1h = Slider(ax=ax_P1h, label='P1', valmin=-180, valmax=180,
              valinit=0, valfmt=' %.1f deg', facecolor='#cc7000')

s_P0v = Slider(ax=ax_P0v, label='P0', valmin=-180, valmax=180,
              valinit=0, valfmt=' %.1f deg', facecolor='#cc7000')

s_P1v = Slider(ax=ax_P1v, label='P1', valmin=-180, valmax=180,
              valinit=0, valfmt=' %.1f deg', facecolor='#cc7000')


def animate(val):  
    
    h=s_h.val
    v=s_v.val
    p0h=s_P0h.val
    p1h=s_P1h.val
    p0v=s_P0v.val
    p1v=s_P1v.val
    
    p0h = p0h * np.pi / 180.
    p1h = p1h * np.pi / 180.

    p0v = p0v * np.pi / 180. 
    p1v = p1v * np.pi / 180.

    ax.cla()
    
    if (data.shape[0]!=1):
        contour_start = s_Cont.val
        cl = contour_start * contour_factor ** np.arange(contour_num) 
        cl_neg = -cl[::-1]
         
        ax.contour(data, cl, cmap=cmap, extent=(0, data.shape[1] - 1, 0, data.shape[0] - 1))
        ax.contour(data, cl_neg, cmap=cmap_neg, extent=(0, data.shape[1] - 1, 0, data.shape[0] - 1))


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
    
    else:
        min_Int, max_Int=s_Cont.val[0], s_Cont.val[1]
        ht=ng.proc_base.ht(data[0], N=data.shape[-1])  #hilbelt transform to reconstruct imaginaries
        apodx = np.exp(1.0j * (p0h + (p1h * np.arange(data.shape[1]) / data.shape[1])))
        phasedx=ht*apodx
        
        ax.plot(range(data.shape[1]),  phasedx ) 
        ax.set_ylim(min_Int, max_Int)
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
