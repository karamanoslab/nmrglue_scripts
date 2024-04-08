import math 
import numpy as np
import nmrglue as ng
import sys
from nmrglue.process.proc_base import roll
import matplotlib.pyplot as plt
import matplotlib.cm


class TwoD(object):
     
    def __init__(self, spectrum_path):
        self.spectrum_path=spectrum_path

        self.cmap_p='viridis'
        self.cmap_n='plasma_r'

    def loadpeaks(self, fname):
        peaks={}
        with open(fname) as f:
            lines = filter(None, (line.rstrip() for line in f))
            for line in lines:
                line=line.strip()
                fields=line.split(' ')
                ass=fields[0]
                spec=fields[1]
                peaks[spec]={}
        
                num_peaks=int((len(fields)-2)/3)
                peaks[spec][ass]=[]

                for p in range(num_peaks):
                    H= fields[2+p]
                    N= fields[2+num_peaks+p]
                    Inten= fields[2+num_peaks+num_peaks+p]
                    peaks[spec][ass].append((H,N,Inten ))
        return peaks


    def draw_peaks(self, spectrum, peaks, axis, color='k', compact=False):
        allshifts=[]
        for spec in peaks.keys():
            values=list(peaks[spec].values())[0]
            if values!=[]:
                allshifts.append(values[0])

        allshifts=np.array(allshifts, dtype=float )
        X=allshifts[:,0] 
        Y=allshifts[:,1] 
        
        if self.scale=='ppm':
            lims=[(min(X)-(min(X)*0.02), max(X)+(max(X)*0.02)  ), (min(Y)-(min(Y)*0.01), max(Y)+(max(Y)*0.01)  )] #for all spectra
        if self.scale=='hz':
            lims=[(min(X)-(min(X)*0.008), max(X)+(max(X)*0.008)  ), (min(Y)-(min(Y)*0.003), max(Y)+(max(Y)*0.003)  )] #for all spectra
        
        peaks=peaks[spectrum]
        for ass in peaks.keys():
            if peaks[ass]==[]:
                print('%s s%s contains no peaks'%(ass, spectrum))
            for p, peak in enumerate(peaks[ass]):
                x, y, I =float(peak[0]), float(peak[1]), float(peak[2])
                axis.plot(x, y, 'x', markersize=20, color=color)

                if compact:
                    axis.text(x-(x*0.002), y, 's%s p%i'%( spectrum, p), size=12, color=color )
                else:
                    axis.text(x-(x*0.002), y, '%s s%s p%i'%(ass, spectrum, p), size=12, color=color )
                    #axis.text(0.95, 0.95*(0.05*off ) , '%s s%s p%i'%(ass, spectrum, p), ha='right', va='top', transform=axis.transAxes )

                #lims=[(x-0.2, x+0.2 ), (y-1.0, y+1.0)] #for each spec individually
                print('%s s%s p%i'%(ass, spectrum, p), x, y, I)
        return lims


    def read_spec(self, scale='ppm'):
        spectrum= self.spectrum_path
        self.scale=scale

        dir=spectrum.split('/')[-2]

        dic,data = ng.pipe.read('%s'%(spectrum))

        uc_x1= ng.pipe.make_uc(dic, data, dim=1)    
        uc_y1 = ng.pipe.make_uc(dic, data, dim=0)

        if scale == 'ppm':
            ppm_x1 = uc_x1.ppm_scale()
            ppm_y1 = uc_y1.ppm_scale()
            return dic, data, ppm_x1, ppm_y1, dir
        if scale =='hz':
            hz_x1 = uc_x1.hz_scale()
            hz_y1 = uc_y1.hz_scale()
            return dic, data, hz_x1, hz_y1, dir


    def extract(self,  DATA,  x_ppm=(6, 11), y_ppm=(100, 140) ):
        '''Extract a region of interest roi 
        DATA is a read_spec insace'''

        dic, data, ppm_x1, ppm_y1, dir=DATA
    
        xppm1, xppm2=x_ppm[0], x_ppm[1]
        yppm1, yppm2=y_ppm[0], y_ppm[1]

        indexesx, indexesy=[], []
        #if ppm2<ppm1: ppm1, ppm2=ppm2, ppm1

        for i, x in enumerate(ppm_x1):
            if x>xppm1 and x<xppm2:
                indexesx.append(i)

        for j, y in enumerate(ppm_y1):
            if y>yppm1 and y<yppm2:
                indexesy.append(j)

        x0, x1= indexesx[0], indexesx[-1]
        y0, y1= indexesy[0], indexesy[-1]
        
        extracted_data = data[y0:y1, x0:x1]
        ext_xppm= ppm_x1[x0:x1]
        ext_yppm= ppm_y1[y0:y1]

        return dic, extracted_data, ext_xppm, ext_yppm, dir


    def plot2ds( self, specs=[], peaks=[], countour=4000000,  dir='' ):
        '''peaks is a list of loadpeaks instances
        '''
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111) 

        for i, spec in enumerate(specs):
            
            spectrum=self.read_spec(specs[i])
            
            dic, data, ppm_x1, ppm_y1, dir= spectrum
        
            ppm_x1_0, ppm_x1_1 =  ppm_x1[0],  ppm_x1[-1]
            ppm_y1_0, ppm_y1_1 =  ppm_y1[0],  ppm_y1[-1] 

            cmap_p="%s_r"%self.cmaps[i]
            cmap_n=self.cmaps[len(self.cmaps)-1-i]
            
            contour_start =    countour        # contour level start value
            contour_num = 10                # number of contour levels
            contour_factor = 1.20          # scaling factor between contour levels

            # calculate contour levels
            cl = contour_start * contour_factor ** np.arange(contour_num) 
            cl_neg = -cl[::-1]
            

            ax.contour(data, cl, cmap=cmap_p, extent=(ppm_x1_0, ppm_x1_1, ppm_y1_0, ppm_y1_1) )
            ax.contour(data, cl_neg, cmap=cmap_n, extent=(ppm_x1_0, ppm_x1_1, ppm_y1_0, ppm_y1_1) )

            ax.set_xlim( ppm_x1_0,  ppm_x1_1)
            ax.set_ylim(ppm_y1_0, ppm_y1_1)     
            
            for p in peaks:
                labels=self.draw_peaks(dir, p, ax, color=matplotlib.cm.get_cmap(cmap_p)(0) )
            
        
        plt.show()

