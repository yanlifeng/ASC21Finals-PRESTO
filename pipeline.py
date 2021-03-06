# coding=utf-8

import os, sys, glob, re
import presto.sifting as sifting
from subprocess import getoutput
import numpy as np
import time
import random
from operator import itemgetter, attrgetter

from math import ceil
from mpi4py import MPI


def dur(op=None, clock=[time.time()]):
    res = ''
    if op != None:
        duration = time.time() - clock[0]
        res = '%-30s === %.6f \n' % (op, duration)
    clock[0] = time.time()
    return res


# tasks 是每个host拿到的任务
def go_process(tasks):
    n = len(tasks)
    numPreProce = ceil(n / procPreHost)
    l = myRank * numPreProce
    r = min(n, (myRank + 1) * numPreProce)
    res = []
    newTasks = tasks[l:r]
    # print("new tasks:")
    # print(new_tasks)
    for ls in newTasks:
        logs = []
        for it in ls:
            # print(add_info + it)
            output = getoutput(it)
            logs.append(output)
        res.append(logs)
    return res


# Tutorial_Mode = True
Tutorial_Mode = False

timeLog = ''
# load automatic

rootname = 'Sband'
maxDM = 80  # max DM to search
Nsub = 32  # 32 subbands
Nint = 64  # 64 sub integration
Tres = 0.5  # ms
zmax = 0

hostNum = 2

comm = MPI.COMM_WORLD
totNum = comm.Get_size()
totRank = comm.Get_rank()
assert (totNum % hostNum == 0)
procPreHost = totNum // hostNum
hostRank = totRank // procPreHost
myRank = totRank % procPreHost

filename = sys.argv[1]
if len(sys.argv) > 2:
    maskfile = sys.argv[2]
else:
    maskfile = None


def query(question, answer, input_type):
    print("Based on output of the last step, answer the following questions:")
    Ntry = 3
    while not input_type(input("%s:" % question)) == answer and Ntry > 0:
        Ntry -= 1
        print("try again...")
    if Ntry == 0: print("The correct answer is:", answer)


# """
if (totRank == 0):
    print('''
    
    ====================Read Header======================
    
    ''')
comm.Barrier()

dur()
tasks = []
readheadercmd = 'readfile %s' % filename
if (totRank == 0):
    print(readheadercmd)
output = getoutput(readheadercmd)
if (totRank == 0):
    print(output)
header = {}
size = 0
for line in output.split('\n'):
    size += 1
    items = line.split("=")
    if len(items) > 1:
        header[items[0].strip()] = items[1].strip()
# print header
# except:
# print 'failed at reading file %s.' % filename
# sys.exit(0)
timeLog += dur("Read Header")
if (totRank == 0):
    print('''
    
    ============Generate Dedispersion===============
    
    ''')
comm.Barrier()

dur()
try:
    Nchan = int(header['Number of channels'])
    tsamp = float(header['Sample time (us)']) * 1.e-6
    BandWidth = float(header['Total Bandwidth (MHz)'])
    fcenter = float(header['Central freq (MHz)'])
    Nsamp = int(header['Spectra per file'])

    if Tutorial_Mode:
        query("Input file has how many frequency channel?", Nchan, int)
        query("what is the total bandwidth?", BandWidth, float)
        query("what is the size of each time sample in us?", tsamp * 1.e6, float)
        query("what's the center frequency?", fcenter, float)
        print('see how these numbers are used in the next step.')
        print('')
    # 利用读取出来的参数 运行DDplan.py 然后收集到输出中的最后一行参数
    ddplancmd = 'DDplan.py -d %(maxDM)s -n %(Nchan)d -b %(BandWidth)s -t %(tsamp)f -f %(fcenter)f -s %(Nsub)s -o DDplan.ps' % {
        'maxDM': maxDM, 'Nchan': Nchan, 'tsamp': tsamp, 'BandWidth': BandWidth, 'fcenter': fcenter, 'Nsub': Nsub}
    if (totRank == 0):
        print(ddplancmd)
    ddplanout = getoutput(ddplancmd)
    if (totRank == 0):
        print(ddplanout)
    planlist = ddplanout.split('\n')
    ddplan = []
    planlist.reverse()
    for plan in planlist:
        if plan == '':
            continue
        elif plan.strip().startswith('Low DM'):
            break
        else:
            ddplan.append(plan)
    ddplan.reverse()
except:
    print('failed at generating DDplan.')
    sys.exit(0)

if Tutorial_Mode:
    calls = 0
    for line in ddplan:
        ddpl = line.split()
        calls += int(ddpl[7])
    query("According to the DDplan, how many times in total do we have to call prepsubband?", calls, int)
    print('see how these numbers are used in the next step.')
    print('')
timeLog += dur("Generate Dedispersion")
if (totRank == 0):
    print('''
    
    ================Dedisperse Subbands==================
    
    ''')
comm.Barrier()
dur()
cwd = os.getcwd()
try:
    if myRank == 0:
        if not os.access('subbands', os.F_OK):
            os.mkdir('subbands')
    comm.Barrier()
    os.chdir('subbands')
    if totRank == 0:
        logfile = open('dedisperse.log', 'wt')
    ddplanSize = 0
    for line in ddplan:
        # print "ddplanSize : "
        # print ddplanSize
        ddplanSize += 1
        ddpl = line.split()
        # ['0.000', '84.000', '0.50', '1', '12.00', '168', '24', '7', '1']
        lowDM = float(ddpl[0])
        hiDM = float(ddpl[1])
        dDM = float(ddpl[2])  # 0.5
        DownSamp = int(ddpl[3])  # 1
        NDMs = int(ddpl[6])  # 24 --->
        calls = int(ddpl[7])  # 7
        Nout = Nsamp / DownSamp
        Nout -= (Nout % 500)
        dmlist = np.split(np.arange(lowDM, hiDM, dDM), calls)
        # copy from $PRESTO/python/Dedisp.py
        subdownsamp = DownSamp / 2
        datdownsamp = 2
        if DownSamp < 2: subdownsamp = datdownsamp = 1
        tasks.clear()
        for i, dml in enumerate(dmlist):
            ls_task = []
            lodm = dml[0]
            subDM = np.mean(dml)
            if maskfile:
                # print "maskfile has open"
                prepsubband = "prepsubband -sub -subdm %.2f -nsub %d -downsamp %d -mask ../%s -o %s %s" % (
                    subDM, Nsub, subdownsamp, maskfile, rootname, '../' + filename)
            else:
                prepsubband = "prepsubband -sub -subdm %.2f -nsub %d -downsamp %d -o %s %s" % (
                    subDM, Nsub, subdownsamp, rootname, '../' + filename)
            # print("prepsubband : " + prepsubband)
            ls_task.append(prepsubband)
            # output = getoutput(prepsubband)
            # logfile.write(output)
            # print output
            # print "========================================================================"
            subnames = rootname + "_DM%.2f.sub[0-9]*" % subDM
            # prepsubcmd = "prepsubband -nsub %(Nsub)d -lodm %(lowdm)f -dmstep %(dDM)f -numdms %(NDMs)d -numout %(Nout)d -downsamp %(DownSamp)d -o %(root)s ../%(filfile)s" % {
            # 'Nsub':Nsub, 'lowdm':lodm, 'dDM':dDM, 'NDMs':NDMs, 'Nout':Nout, 'DownSamp':datdownsamp, 'root':rootname, 'filfile':filename}
            prepsubcmd = "prepsubband -nsub %(Nsub)d -lodm %(lowdm)f -dmstep %(dDM)f -numdms %(NDMs)d -numout %(Nout)d -downsamp %(DownSamp)d -o %(root)s %(subfile)s" % {
                'Nsub': Nsub, 'lowdm': lodm, 'dDM': dDM, 'NDMs': NDMs, 'Nout': Nout, 'DownSamp': datdownsamp,
                'root': rootname, 'subfile': subnames}
            # print("prepsubcmd : " + prepsubcmd)
            ls_task.append(prepsubcmd)
            # output = getoutput(prepsubcmd)
            # logfile.write(output)
            # print output
            # print "========================================================================"
            tasks.append(ls_task)
    n = len(tasks)
    numPreHost = ceil(n / hostNum)
    L = hostRank * numPreHost
    R = min(n, (hostRank + 1) * numPreHost)
    depRes = go_process(tasks[L:R])
    if myRank == 0:
        os.system('rm *.sub*')
    totDepRes = comm.gather(depRes, root=0)
    comm.Barrier()
    if totRank == 0:
        for ls in totDepRes:
            for it in ls:
                for item in it:
                    logfile.write(item)
        logfile.close()
    os.chdir(cwd)

except:
    print('failed at prepsubband.')
    os.chdir(cwd)
    sys.exit(0)
timeLog += dur("Dedisperse Subbands")

# exit(0)
if (totRank == 0):
    print('''
    
    ================fft-search subbands==================
    
    ''')
comm.Barrier()

dur()
try:
    os.chdir('subbands')
    datfiles = glob.glob("*.dat")
    if totRank == 0:
        logfile = open('fft.log', 'wt')
    tasks.clear()
    for df in datfiles:
        fftcmd = "realfft %s" % df
        ls_task = []
        ls_task.append(fftcmd)
        tasks.append(ls_task)
        print(fftcmd)
        # output = getoutput(fftcmd)
        # logfile.write(output)
    fftRes = go_process(tasks)
    totFftRes = comm.gather(fftRes, root=0)
    comm.Barrier()
    if totRank == 0:
        for ls in totFftRes:
            for it in ls:
                for item in it:
                    logfile.write(item)
        logfile.close()
    comm.Barrier()
    if totRank == 0:
        logfile = open('accelsearch.log', 'wt')
    fftfiles = glob.glob("*.fft")
    tasks.clear()
    for fftf in fftfiles:
        searchcmd = "accelsearch -zmax %d %s" % (zmax, fftf)
        ls_task = []
        ls_task.append(searchcmd)
        tasks.append(ls_task)
        print(searchcmd)
        # output = getoutput(searchcmd)
        # logfile.write(output)
    accRes = go_process(tasks)
    totAccRes = comm.gather(accRes, root=0)
    comm.Barrier()
    if totRank == 0:
        for ls in totAccRes:
            for it in ls:
                for item in it:
                    logfile.write(item)
        logfile.close()
    os.chdir(cwd)
except:
    print('failed at fft search.')
    os.chdir(cwd)
    sys.exit(0)

timeLog += dur("fft-search subbands")


# """


def ACCEL_sift(zmax):
    '''
    The following code come from PRESTO's ACCEL_sift.py
    '''

    p1 = []
    p2 = []
    if myRank == 0:
        globaccel = "*ACCEL_%d" % zmax
        globinf = "*DM*.inf"
        # In how many DMs must a candidate be detected to be considered "good"
        min_num_DMs = 2
        # Lowest DM to consider as a "real" pulsar
        low_DM_cutoff = 2.0
        # Ignore candidates with a sigma (from incoherent power summation) less than this
        sifting.sigma_threshold = 4.0
        # Ignore candidates with a coherent power less than this
        sifting.c_pow_threshold = 100.0

        # If the birds file works well, the following shouldn't
        # be needed at all...  If they are, add tuples with the bad
        # values and their errors.
        #                (ms, err)
        sifting.known_birds_p = []
        #                (Hz, err)
        sifting.known_birds_f = []

        # The following are all defined in the sifting module.
        # But if we want to override them, uncomment and do it here.
        # You shouldn't need to adjust them for most searches, though.

        # How close a candidate has to be to another candidate to
        # consider it the same candidate (in Fourier bins)
        sifting.r_err = 1.1
        # Shortest period candidates to consider (s)
        sifting.short_period = 0.0005
        # Longest period candidates to consider (s)
        sifting.long_period = 15.0
        # Ignore any candidates where at least one harmonic does exceed this power
        sifting.harm_pow_cutoff = 8.0

        # --------------------------------------------------------------

        # Try to read the .inf files first, as _if_ they are present, all of
        # them should be there.  (if no candidates are found by accelsearch
        # we get no ACCEL files...
        inffiles = glob.glob(globinf)
        inffiles.sort()
        # print("inffiles")
        # print(inffiles)
        candfiles = glob.glob(globaccel)
        candfiles.sort()
        # print("candfiles")
        # print(candfiles)
        # Check to see if this is from a short search
        if len(re.findall("_[0-9][0-9][0-9]M_", inffiles[0])):
            dmstrs = [x.split("DM")[-1].split("_")[0] for x in candfiles]
        else:
            dmstrs = [x.split("DM")[-1].split(".inf")[0] for x in inffiles]
        # print("dmstrs")
        # print(dmstrs)
        dms = list(map(float, dmstrs))
        # print("dms")
        # print(dms)
        dms.sort()
        dmstrs = ["%.2f" % x for x in dms]
        cands = sifting.read_candidates(candfiles)
        p1 = dmstrs
        p2 = cands.cands
    totListCands = comm.gather(p2, root=0)
    # comm.Barrier()

    totDmstrs = comm.gather(p1, root=0)
    comm.Barrier()

    cands = []
    dmstrs = []
    if totRank == 0:

        for itt in totListCands:
            for it in itt:
                cands.append(it)

        for itt in totDmstrs:
            for it in itt:
                dmstrs.append(it)

        cands = sifting.Candlist(cands)
        # Remove candidates that are duplicated in other ACCEL files
        if len(cands):
            cands = sifting.remove_duplicate_candidates(cands)

        # for it in cands:
        #     print("cand hits")
        #     print(it.hits)
        # Remove candidates with DM problems
        if len(cands):
            cands = sifting.remove_DM_problems(cands, min_num_DMs, dmstrs, low_DM_cutoff)

        # Remove candidates that are harmonically related to each other
        # Note:  this includes only a small set of harmonics
        if len(cands):
            cands = sifting.remove_harmonics(cands)

        # Write candidates to STDOUT
        if len(cands):
            cands.sort(key=attrgetter('sigma'), reverse=True)
            # cands.sort(sifting.cmp_sigma)
            # for cand in cands[:1]:
            # print cand.filename, cand.candnum, cand.p, cand.DMstr
            # sifting.write_candlist(cands)
    return cands


# exit(0)
if totRank == 0:
    print('''
    
    ================sifting candidates==================
    
    ''')
comm.Barrier()
dur()
try:
    # if myRank == 0:
    cwd = os.getcwd()
    os.chdir('subbands')
    cands = ACCEL_sift(zmax)
    os.chdir(cwd)
except:
    print('failed at sifting candidates.')
    os.chdir(cwd)
    sys.exit(0)

timeLog += dur("sifting candidates")

if totRank == 0:
    print('''
    
    ================folding candidates==================
    
    ''')
comm.Barrier()
tasksCands = []
if totRank == 0:
    n = len(cands)
    preCandsPreProce = ceil(n / totNum)
    for i in range(totNum):
        l = i * preCandsPreProce
        r = min(n, (i + 1) * preCandsPreProce)
        tasksCands.append(cands[l:r])
cands = comm.scatter(tasksCands, root=0)
comm.Barrier()
dur()
try:
    cwd = os.getcwd()
    os.chdir('subbands')
    os.system('ln -s ../%s %s' % (filename, filename))
    if totRank == 0:
        logfile = open('folding.log', 'wt')
    fldRes = []
    for cand in cands:
        # foldcmd = "prepfold -dm %(dm)f -accelcand %(candnum)d -accelfile %(accelfile)s %(datfile)s -noxwin " % {
        # 'dm':cand.DM,  'accelfile':cand.filename+'.cand', 'candnum':cand.candnum, 'datfile':('%s_DM%s.dat' % (rootname, cand.DMstr))} #simple plots
        foldcmd = "prepfold -n %(Nint)d -nsub %(Nsub)d -dm %(dm)f -p %(period)f %(filfile)s -o %(outfile)s -noxwin -nodmsearch" % {
            'Nint': Nint, 'Nsub': Nsub, 'dm': cand.DM, 'period': cand.p, 'filfile': filename,
            'outfile': rootname + '_DM' + cand.DMstr}  # full plots
        print(foldcmd)
        # os.system(foldcmd)
        output = getoutput(foldcmd)
        fldRes.append(output)
        # logfile.write(output)
    totFolRes = comm.gather(fldRes, root=0)
    comm.Barrier()
    if totRank == 0:
        for ls in totFolRes:
            for it in ls:
                logfile.write(it)
        logfile.close()
    os.chdir(cwd)
except:
    print('failed at folding candidates.')
    os.chdir(cwd)
    sys.exit(0)
timeLog += dur("folding candidates")
if totRank == 0:
    print(timeLog)
