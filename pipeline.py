# coding=utf-8

import os, sys, glob, re
import presto.sifting as sifting
from subprocess import getoutput
import numpy as np
import time
import random
from operator import itemgetter, attrgetter
from mpi4py import MPI


def dur(op=None, clock=[time.time()]):
    res = ''
    if op != None:
        duration = time.time() - clock[0]
        res = '%-30s === %.6f \n' % (op, duration)
    clock[0] = time.time()
    return res


def go_process(tasks):
    res = []
    for i, ls in enumerate(tasks):
        if i % nprocs != myrank:
            continue
        logs = []
        for it in ls:
            print(add_info + it)
            output = getoutput(it)
            logs.append(output)
        res.append(logs)
    return res


# Tutorial_Mode = True
Tutorial_Mode = False

timeLog = ''

rootname = 'Sband'
maxDM = 80  # max DM to search
Nsub = 32  # 32 subbands
Nint = 64  # 64 sub integration
Tres = 0.5  # ms
zmax = 0

comm = MPI.COMM_WORLD
nprocs = comm.Get_size()
myrank = comm.Get_rank()

add_info = "rank " + str(myrank) + " : "

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
if (myrank == 0):
    print('''
    
    ====================Read Header======================
    
    ''')
comm.Barrier()
print(add_info + "padd barr0")

dur()
tasks = []
readheadercmd = 'readfile %s' % filename
print(add_info + "readheadercmd : \n" + readheadercmd)
output = getoutput(readheadercmd)
print(add_info + "output : \n" + output)
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
if (myrank == 0):
    print('''
    
    ============Generate Dedispersion===============
    
    ''')
comm.Barrier()
print(add_info + "padd barr1")

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
    print(add_info + ddplancmd)
    ddplanout = getoutput(ddplancmd)
    print(add_info + ddplanout)
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
if (myrank == 0):
    print('''
    
    ================Dedisperse Subbands==================
    
    ''')
comm.Barrier()
print(add_info + "padd barr2")

dur()
cwd = os.getcwd()
try:
    if myrank == 0:
        if not os.access('subbands', os.F_OK):
            os.mkdir('subbands')
    comm.Barrier()
    print(add_info + "padd barr2.5")
    os.chdir('subbands')
    if myrank == 0:
        logfile = open('dedisperse.log', 'wt')
    ddplanSize = 0
    # 对于DDplan的输出信息们（其实就一行） 生成一个lowDM-highDM 间隔为dDm的数组 分成calls份
    # 然后每一份 运行prepsubband 先写一些信息到临时文件里 然后读出来 把有用的信息写到Sband_DMxx.xx里面
    # 最后删掉临时文件 并把log信息存在 dedisperse.log 里面
    for line in ddplan:
        # print "ddplanSize : "
        # print ddplanSize
        ddplanSize += 1
        ddpl = line.split()
        lowDM = float(ddpl[0])
        hiDM = float(ddpl[1])
        dDM = float(ddpl[2])
        DownSamp = int(ddpl[3])
        NDMs = int(ddpl[6])
        calls = int(ddpl[7])
        Nout = Nsamp / DownSamp
        Nout -= (Nout % 500)
        dmlist = np.split(np.arange(lowDM, hiDM, dDM), calls)
        # print "dmlist : "
        # print dmlist
        # copy from $PRESTO/python/Dedisp.py
        subdownsamp = DownSamp / 2
        datdownsamp = 2
        if DownSamp < 2: subdownsamp = datdownsamp = 1

        # random.shuffle(dmlist)
        # TODO 这里cpu跑起来只显示用了一个核的10%左右 应该是时间都在频繁的读写文件上 下一步可以找到prepsubband的源代码改一下（现在还没找到）
        # TODO mutithread test
        # TODO 这里的运行结果里面有个error
        print(add_info + "p1 size ", len(dmlist))
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
    res = go_process(tasks)
    if myrank == 0:
        for ls in res:
            for it in ls:
                logfile.write(it)
    if myrank == 0:
        os.system('rm *.sub*')
    if myrank == 0:
        logfile.close()
    os.chdir(cwd)

except:
    print('failed at prepsubband.')
    os.chdir(cwd)
    sys.exit(0)
timeLog += dur("Dedisperse Subbands")

# exit(0)
if (myrank == 0):
    print('''
    
    ================fft-search subbands==================
    
    ''')
comm.Barrier()
print(add_info + "padd barr3")

dur()
try:
    os.chdir('subbands')
    datfiles = glob.glob("*.dat")
    if myrank == 0:
        logfile = open('fft.log', 'wt')
    print(add_info + "p2 size ", len(datfiles))
    tasks.clear()
    for df in datfiles:
        fftcmd = "realfft %s" % df
        ls_task = []
        ls_task.append(fftcmd)
        tasks.append(ls_task)
        # print(fftcmd)
        # output = getoutput(fftcmd)
        # logfile.write(output)
    res = go_process(tasks)
    if myrank == 0:
        for ls in res:
            for it in ls:
                logfile.write(it)
    if myrank == 0:
        logfile.close()
    comm.Barrier()
    if myrank == 0:
        logfile = open('accelsearch.log', 'wt')
    fftfiles = glob.glob("*.fft")
    print(add_info + "p3 size ", len(fftfiles))
    tasks.clear()
    for fftf in fftfiles:
        searchcmd = "accelsearch -zmax %d %s" % (zmax, fftf)
        ls_task = []
        ls_task.append(searchcmd)
        tasks.append(ls_task)
        # print(searchcmd)
        # output = getoutput(searchcmd)
        # logfile.write(output)
    res = go_process(tasks)
    if myrank == 0:
        for ls in res:
            for it in ls:
                logfile.write(it)
    if myrank == 0:
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
    candfiles = glob.glob(globaccel)
    # Check to see if this is from a short search
    if len(re.findall("_[0-9][0-9][0-9]M_", inffiles[0])):
        dmstrs = [x.split("DM")[-1].split("_")[0] for x in candfiles]
    else:
        dmstrs = [x.split("DM")[-1].split(".inf")[0] for x in inffiles]
    dms = list(map(float, dmstrs))
    dms.sort()
    dmstrs = ["%.2f" % x for x in dms]

    # Read in all the candidates
    cands = sifting.read_candidates(candfiles)

    # Remove candidates that are duplicated in other ACCEL files
    if len(cands):
        cands = sifting.remove_duplicate_candidates(cands)

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


if myrank == 0:
    print('''
    
    ================sifting candidates==================
    
    ''')
comm.Barrier()
print(add_info + "barr sifting")
dur()
try:
    cwd = os.getcwd()
    os.chdir('subbands')
    cands = ACCEL_sift(zmax)
    os.chdir(cwd)
except:
    print('failed at sifting candidates.')
    os.chdir(cwd)
    sys.exit(0)

timeLog += dur("sifting candidates")
if myrank == 0:
    print('''
    
    ================folding candidates==================
    
    ''')
comm.Barrier()
print(add_info + "barr folding")

dur()
try:
    cwd = os.getcwd()
    os.chdir('subbands')
    os.system('ln -s ../%s %s' % (filename, filename))
    if myrank == 0:
        logfile = open('folding.log', 'wt')
    print(add_info + "p4 size is ", len(cands))
    tasks.clear()
    for cand in cands:
        ls_task = []
        # foldcmd = "prepfold -dm %(dm)f -accelcand %(candnum)d -accelfile %(accelfile)s %(datfile)s -noxwin " % {
        # 'dm':cand.DM,  'accelfile':cand.filename+'.cand', 'candnum':cand.candnum, 'datfile':('%s_DM%s.dat' % (rootname, cand.DMstr))} #simple plots
        foldcmd = "prepfold -n %(Nint)d -nsub %(Nsub)d -dm %(dm)f -p %(period)f %(filfile)s -o %(outfile)s -noxwin -nodmsearch" % {
            'Nint': Nint, 'Nsub': Nsub, 'dm': cand.DM, 'period': cand.p, 'filfile': filename,
            'outfile': rootname + '_DM' + cand.DMstr}  # full plots
        ls_task.append(foldcmd)
        tasks.append(ls_task)
        # print(foldcmd)
        # os.system(foldcmd)
        # output = getoutput(foldcmd)
        # logfile.write(output)
    res = go_process(tasks)
    if myrank == 0:
        for ls in res:
            for it in ls:
                logfile.write(it)
    if myrank == 0:
        logfile.close()
    os.chdir(cwd)
except:
    print('failed at folding candidates.')
    os.chdir(cwd)
    sys.exit(0)
timeLog += dur("folding candidates")

print(add_info + timeLog)
