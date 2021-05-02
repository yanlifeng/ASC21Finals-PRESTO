import hashlib
import os


def listdir(path, list_name):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            listdir(file_path, list_name)
        else:
            list_name.append(file_path)


# ls1 = []
# ls11 = []
# listdir("./subbands/", ls11)
# for it in ls11:
#     if "pfd" not in it:
#         ls1.append(it)
# ls1.sort()
# ls2 = []
# ls22 = []
# listdir("../../STD1/subbands/", ls22)
# for it in ls22:
#     if "pfd" not in it:
#         ls2.append(it)
# ls2.sort()


ls1 = []
listdir("./subbands/", ls1)
ls1.sort()
ls2 = []
listdir("../../ANS1/subbands/", ls2)
ls2.sort()

print(len(ls1), len(ls2))
assert (len(ls1) == len(ls2))
ok = 1
for i in range(len(ls1)):
    try:
        if "_ACCEL_0.cand" in ls1[i]:
            # print("jump this test because cand")
            continue
        if ".png" in ls1[i]:
            # print("jump this test because cand")
            continue
        if "_ACCEL_0" in ls1[i]:
            # print("jump this test because cand")
            continue
        if "txtcand" in ls1[i]:
            # print("jump this test because cand")
            continue

        f1 = ls1[i]
        with open(f1, 'rb') as fp:
            data = fp.read()
            if ".pfd.ps" in f1:
                data = str(data).split("\n")[10:]
                data = bytes(data)
        m1 = hashlib.md5(data).hexdigest()
        # print(m1)
        f2 = ls2[i]
        with open(f2, 'rb') as fp:
            data = fp.read()
            if ".pfd.ps" in f2:
                data = str(data).split("\n")[10:]
                data = bytes(data)
        m2 = hashlib.md5(data).hexdigest()
        if m1 != m2:
            print("GG on check ", f1, f2)
            ok = 0
        else:
            print("pass on test ", f1)
    except:
        print("some errors occur when open ", f1, f2)
        continue

f1 = "../../ANS1/DDplan.ps"
with open(f1, 'rb') as fp:
    data = fp.read()
    data = str(data).split("\n")[10:]
    data = bytes(data)
m1 = hashlib.md5(data).hexdigest()
f2 = "./DDplan.ps"
with open(f2, 'rb') as fp:
    data = fp.read()
    data = str(data).split("\n")[10:]
    data = bytes(data)
m2 = hashlib.md5(data).hexdigest()
if m1 != m2:
    print("GG on file " + f2)
    ok = 0
else:
    print("pass on test DD")
if ok:
    print("Accepted !")
else:
    print("GG !")
