import math 
import numpy as np
import nmrglue as ng
import sys
from nmrglue.process.proc_base import roll

class OneD(object):
     
    def __init__(self, data, ppmscale):
        self.data=data
        self.ppmscale=ppmscale
        #self.ppm1=ppm1
        #self.ppm2=ppm2

    def _bracket_with_zeros(self):
        '''Pad data with zeros for rolling '''
        length_data = len(self.data)
        result = np.zeros(length_data * 3)
        result[length_data:length_data * 2] = self.data
        return result

    def extract(self, ppm1, ppm2):
        '''Extract a region of interest roi '''
        extracted_data, indexes=[], []
        if ppm2<ppm1: ppm1, ppm2=ppm2, ppm1
        for i, j in enumerate(self.ppmscale):
            if j>ppm1 and j<ppm2:
                extracted_data.append((j,self.data[i]))  
                indexes.append(i)
        extracted_data=np.array(extracted_data)
        extracted_ppmscale, extracted_data=extracted_data[:,0], extracted_data[:,1]
        return extracted_ppmscale, extracted_data, indexes


class Roller(object):
     
    def __init__(self,   data_1, data_2, ppmscale1, ppmscale2, roiPPM=(11, 0.0)):
         self.data_1 = data_1
         self.data_2 = data_2
         self.ppmscale1=ppmscale1
         self.ppmscale2=ppmscale2
         self.roiPPM=roiPPM 
    
    def roller(self):
        '''Rol one dataset around an axis so a specified region so it matches a reference dataset region'''
        OneD_1=OneD(self.data_1, self.ppmscale1)
        OneD_2=OneD(self.data_2, self.ppmscale2)
        
        roi1ppm, roi1data, ind=OneD_1.extract(self.roiPPM[0], self.roiPPM[1] )
        roi2ppm, roi2data, ind=OneD_2.extract(self.roiPPM[0], self.roiPPM[1])
        
        bracketed_data1=OneD_1._bracket_with_zeros()
        bracketed_data2=OneD_2._bracket_with_zeros()
    
        ind_roi1=(np.where(bracketed_data1 == roi1data[0])[0][0], np.where(bracketed_data1 == roi1data[-1])[0][0])
        ind_roi2=(np.where(bracketed_data2 == roi2data[0])[0][0], np.where(bracketed_data2 == roi2data[-1])[0][0])
        #print(ind_roi1, ind_roi2)
    
        bracketed_data1=np.zeros(len(bracketed_data1))
        bracketed_data2=np.zeros(len(bracketed_data2))

        bracketed_data1[ind_roi1[0]:ind_roi1[-1]+1]=roi1data
        bracketed_data2[ind_roi2[0]:ind_roi2[-1]+1]=roi2data
 
        result = []
        for i in range(len(bracketed_data1)):
            rolled = roll(bracketed_data1,i)
            dot_value = np.dot(rolled, bracketed_data2)
            result.append(dot_value)

        max_offset  =  max(result)
        offset=abs(result.index(max_offset) - len(bracketed_data1)) - len(bracketed_data1)
        rolleddata1=roll(self.data_1, -offset)
        print('The offset for the  %.3f to %.3f region is: %i' %(self.roiPPM[0], self.roiPPM[1], offset))
        return rolleddata1, offset
 

class Scaler(object):
     
    def __init__(self,   data_1, data_2, ppmscale1, ppmscale2, roiPPM=(11, 0.0)):
        self.data_1 = data_1
        self.data_2 = data_2
        self.ppmscale1=ppmscale1
        self.ppmscale2=ppmscale2
        self.roiPPM=roiPPM
    
    def scale(self, method='sum' ):
        '''Scale one dataset around a specified region so it matches a reference dataset, scalling data1 always '''  

        roi1ppm, roi1data, ind=OneD(self.data_1, self.ppmscale1).extract(self.roiPPM[0], self.roiPPM[1])
        roi2ppm, roi2data, ind=OneD(self.data_2, self.ppmscale2).extract(self.roiPPM[0], self.roiPPM[1])
    
        if method == 'sum' : 
            sum1, sum2=sum(roi1data), sum(roi2data)
            scaling_factor=sum2/sum1 
    
        if method == 'max' : 
            max1, max2=max(roi1data), max(roi2data)
            scaling_factor=max2/max1

        print('The scaling factor for the %.3f to %.3f region is: %.3f'%(self.roiPPM[0], self.roiPPM[1], scaling_factor))
        return self.data_1*scaling_factor, self.data_2, scaling_factor



class Subtract_ROI(object):
    '''This class will subtract peaks for spectra even the dataset are not collected with 
       the same number of points and sw. be aware that in such cases the results are not exact! '''
     
    def __init__(self,   data_1, data_2, ppmscale1, ppmscale2, roiPPM=(11, 0.0)):
         self.data_1 = data_1
         self.data_2 = data_2
         self.ppmscale1=ppmscale1
         self.ppmscale2=ppmscale2
         self.roiPPM=roiPPM


    def calc(self, scaling_method='max' ):
        '''subtract data1 from data2, if ROIppm='full' check if the offset is 0 ie the spectra were collected with the sam
         SW and NP and subtract the''' 
        
        roller=Roller(self.data_1, self.data_2, self.ppmscale1, self.ppmscale2, self.roiPPM)        
        scaler=Scaler(self.data_1, self.data_2, self.ppmscale1, self.ppmscale2, self.roiPPM)
        
        if self.roiPPM=='full':
            roiPPM=(self.ppmscale1[0], self.ppmscale1[-1])
            rolled_data1, off  = roller.roller()    
            scalled_data1, test, sc_factor      = scaler.scale( method=scaling_method )
 
            if int(off) == 0:
                print('Spectra dont need to be rolled, substracting everything after scaling')
                subtracted_data2=self.data2-data1*sc_factor
                return subtracted_data2
        else:
            rolled_data1, off  = roller.roller()    
            scalled_data1, test, sc_factor      = scaler.scale( method='max' )
       
            roi1ppm, roi1data, inds  = OneD(scalled_data1, self.ppmscale1).extract(self.roiPPM[0], self.roiPPM[1])
            tosubtract =np.zeros(len(self.data_1))
            tosubtract[inds[0]:inds[-1]+1]=roi1data
            tosubtract=roll(tosubtract,-off)
    
            subtracted_data2=self.data_2-tosubtract
            return subtracted_data2


