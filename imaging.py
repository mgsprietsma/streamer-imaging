# script to image GW Ori data using tclean
# Maria Galloway-Sprietsma 08/26/2024

import sys
sys.path.insert(0,'/blue/jbae/mgallowayspriets/casa-6.5.4-9-pipeline-2023.1.0.124/lib/py/lib/python3.8/site-packages/')
import casatools
import casatasks
import os
import glob as glob
from casatools import synthesisutils

# list data directories
data_dir = '/blue/jbae/mgallowayspriets/GW_Ori/data/2022.1.01108.S/'
offset_dir = data_dir+'science_goal.uid___A001_X2d20_X17b4/group.uid___A001_X2d20_X17b5/'
center_dir = data_dir + 'science_goal.uid___A001_X2d20_X17bc/group.uid___A001_X2d20_X17bd/'
archival_dir = '/blue/jbae/mgallowayspriets/GW_Ori/data/2017.1.00286.S/' 
working_directory = '/blue/jbae/mgallowayspriets/GW_Ori/data/working_all/'
imaging_dir = '/blue/jbae/mgallowayspriets/GW_Ori/data/working_all/imaging_output/'

# numbers corresponding to molecules
co = 0
_13co = 1
c18o = 2
so3 = 3
cont = 4

# spws for each pointing in order (co, 13co, c18o, so3, cont)
tm1_spws = ['31','25','29','27','33']
seven_m_spws = ['22','16','20','18','24']
tp_spws = ['23','17','21','19','25']
archival_spws = ['','','','','']

mols = ['co', '13co', 'c18o', 'so', 'cont']
run = ['12m_combine', '12m_offset', '7m_combine', '7m_center','7m_offset']
freqs = ['230.538GHz','220.398GHz','219.560GHz','219.949GHz','233.000GHz']

# TM1 offset
tm1_off = offset_dir+'member.uid___A001_X2d20_X17b6/calibrated/working/uid___A002_X1015532_X1a81_targets_line.ms'

# 7m offset
seven_m_off = offset_dir+'member.uid___A001_X2d20_X17b8/calibrated/working/uid___A002_X107649f_X432c_targets_line.ms'

# TP offset (3 files) (will need to feather in)
tp_off_arr = ['uid___A002_X106f040_X69b.ms.atmcor.atmtype1_bl','uid___A002_X106f040_X6f48.ms.atmcor.atmtype1_bl','uid___A002_X106f040_X7776.ms.atmcor.atmtype1_bl','uid___A002_X106f040_Xfa2b.ms.atmcor.atmtype1_bl']

tp_off = offset_dir+'/member.uid___A001_X2d20_X17ba/calibrated/working/new/'+tp_off_arr[0]

# 7m center
seven_m_center = center_dir+'member.uid___A001_X2d20_X17be/calibrated/working/uid___A002_X10275c0_X15adf_targets_line.ms'

# TP center (will need to feather in)
tp_center_arr = ['uid___A002_X106ccd1_X11884.ms.atmcor.atmtype1_bl','uid___A002_X106f040_X36e.ms.atmcor.atmtype1_bl']
tp_center = center_dir+'member.uid___A001_X2d20_X17c0/new/'+tp_center_arr[0]

# Archival data:

# 12CO
arch_12co_arr = ['uid___A002_Xc7bfc7_X814.ms.split.cal.co.contsub','uid___A002_Xc7bfc7_Xb26.ms.split.cal.co.contsub','uid___A002_Xcb8a93_X7acc.ms.split.cal.co.contsub']

# 13CO
arch_13co_arr = ['uid___A002_Xc7bfc7_X814.ms.split.cal.13co.contsub','uid___A002_Xc7bfc7_Xb26.ms.split.cal.13co.contsub','uid___A002_Xcb8a93_X7acc.ms.split.cal.13co.contsub']

# C18O
arch_c18o_arr = ['uid___A002_Xc7bfc7_X814.ms.split.cal.c18o.contsub','uid___A002_Xc7bfc7_Xb26.ms.split.cal.c18o.contsub','uid___A002_Xcb8a93_X7acc.ms.split.cal.c18o.contsub']


# function to run tclean
def tclean(disk, line,image, robust=None, start=None, width=None, nchan=None,  cyclefactor=None, uvtaper=None, mol=None, mosweight=True):
        
        start = start
        width = width
        nchan = nchan

        start_value = float(start.replace('km/s', ''))
        width_value = float(width.replace('km/s', ''))
        end_channel = (nchan*width_value)+start_value
        print('End channel will be ', end_channel,'km/s')

        robust = robust
        cyclefactor = cyclefactor
        uvtaper=uvtaper

        if line == 'co':
            imol = 0
        elif line == '13co':
            imol = 1
        elif line == 'c18o':
            imol = 2
        elif line == 'so':
            imol = 3
        elif line == 'cont':
            imol = 4
        else:
            print('Molecule you selected is not available. Please select one of the following: co, 13co, c18o,so, or cont')
        
        if image == '12m_archival':
            vis = [archival_dir+arch_12co_arr[0], archival_dir+arch_12co_arr[1],archival_dir+arch_12co_arr[2]]
            spw = [archival_spws[imol],archival_spws[imol], archival_spws[imol]]
        elif image == '12m_combine':
            vis = [tm1_off, archival_dir+arch_12co_arr[0], archival_dir+arch_12co_arr[1],archival_dir+arch_12co_arr[2]]
            spw = [tm1_spws[imol],archival_spws[imol],archival_spws[imol],archival_spws[imol]] 
        elif image == '7m_combine':
            vis = [seven_m_off, seven_m_center]
            spw = [seven_m_spws[imol],seven_m_spws[imol]]
        elif image == 'combine_all':
            vis = [tm1_off, archival_dir+arch_12co_arr[0], archival_dir+arch_12co_arr[1],archival_dir+arch_12co_arr[2],seven_m_off, seven_m_center]
            spw = [tm1_spws[imol],archival_spws[imol],archival_spws[imol],archival_spws[imol], seven_m_spws[imol],seven_m_spws[imol]]
        else:
            print('The imaging task you selected is not available. Please select 12m_archival, 12m_combine, 7m_combine, or combine_all.')

        # to rename the file with another iteration # if it already exists
        iter_count = 1
        base_filename = f'GW_Ori_{line}_nchans{nchan}_robust{robust}_{image}'
        #print(base_filename)
        output_filename = imaging_dir+base_filename
        #print(output_filename)
        while True:
            pattern = f"{output_filename}_iter{iter_count}*"
            matching_files = glob.glob(pattern)
            #print(matching_files)
            if not matching_files:
                break
            iter_count += 1

        output_filename_iter = imaging_dir+f'{base_filename}_iter{iter_count}'
        print(output_filename_iter)

        print('Starting dirty clean on ', disk,' for ',line, ' line.')
        # 'dirty' tclean command with zero iterations to get base rms
        casatasks.tclean(vis=vis,field=disk, spw=spw, intent='OBSERVE_TARGET#ON_SOURCE', datacolumn='data', imagename=output_filename_iter+'.dirty', imsize=[1080,1080], cell=['0.1arcsec'], stokes='I', specmode='cube', nchan=nchan, start=start, width=width, restfreq=freqs[imol], outframe='LSRK',perchanweightdensity=True, gridder='mosaic', mosweight=True, usepointing=False, deconvolver='hogbom', restoration=True, restoringbeam='common', pbcor=True, weighting='briggsbwtaper', robust=robust, npixels=0, niter=0, interactive=False, usemask='auto-multithresh', growiterations=50, dogrowprune=True, minpercentchange=1.0, fastnoise=False, restart=True, uvtaper=[uvtaper])
        
        ia = casatools.image()
        ia.open(output_filename_iter+'.dirty.image')
        h
        if nchan > 11:
            nchan_last = nchan-5
        else:
            nchan_last= nchan-2
        nchan_end = nchan-1
        # calculates the rms using the first and last five channels
        print(nchan_last)
        print(nchan)
        rms = casatasks.imstat(imagename=output_filename_iter+'.dirty.image',chans=f'1~6;{nchan_last}~{nchan_end}')['rms'][0]
        print_rms = rms if rms > 1e-2 else rms * 1e3
        print_unit = 'Jy' if rms > 1e-2 else 'mJy'
        print("# Estimated RMS of unmasked regions: " +
              "{:.2f} {}/beam".format(print_rms, print_unit))
        print('Starting tclean with calculated rms as threshold')
        # real tclean that uses calculated rms 
        if mosweight==True:
            mosweight=True
        else:
            mosweight=False
        casatasks.tclean(vis=vis,field=disk, spw=spw, intent='OBSERVE_TARGET#ON_SOURCE', datacolumn='data', imagename=output_filename_iter+'.clean', imsize=[1080,1080], cell=['0.1arcsec'], stokes='I', specmode='cube', nchan=nchan, start=start, width=width, restfreq=freqs[imol], outframe='LSRK',perchanweightdensity=True, gridder='mosaic', usepointing=False, deconvolver='hogbom', restoration=True, restoringbeam='common', pbcor=True, weighting='briggsbwtaper',robust=robust, npixels=0, niter=100000, threshold=str(4*rms*1.e3) + 'mJy', nsigma=0.0, interactive=False,usemask='auto-multithresh', sidelobethreshold=2.0, noisethreshold=4.25, lownoisethreshold=1.5,negativethreshold=15.0, minbeamfrac=0.3, growiterations=50, dogrowprune=True, minpercentchange=1.0, fastnoise=False, restart=True, savemodel='none', cyclefactor=cyclefactor, uvtaper=[uvtaper], mosweight=mosweight)
        return                

# call the function
tclean(disk='GW_Ori', line='co', image='12m_archival',  robust=0.2,  start='13.4km/s', width='0.1km/s', nchan=11,  cyclefactor=0, uvtaper='1.0arcsec',mosweight=True)

