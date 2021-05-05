
#include <cstdio>
#include <cstring>
#include <iostream>
#include <fstream>
#include <cmath>

using namespace std;

int main() {

    string fn[1] = {"subbands/Sband_DM83.00_ACCEL_0.cand"};
    string fr[1] = {"../../node2ANS/subbands/Sband_DM30.00_ACCEL_0.cand"};

    fstream out, in, inn;

    auto tlen = 528 / 32;
    for (int tt = 0; tt < 1; tt++) {
        float *f1 = new float[tlen];
        float *f2 = new float[tlen];

        cout << fn[tt] << " " << fr[tt] << endl;

        in.open(fn[tt].c_str(), ios::in | ios::binary);
        inn.open(fr[tt].c_str(), ios::in | ios::binary);
        if (!in) {
            printf("Can't open file \"%s\"\n", fn[tt].c_str());
        } else if (!inn) {
            printf("Can't open file \"%s\"\n", fr[tt].c_str());
        } else {
            in.seekg(0, ios::beg);
            in.read(reinterpret_cast<char *>(f1), tlen * sizeof(float));
            inn.seekg(0, ios::beg);
            inn.read(reinterpret_cast<char *>(f2), tlen * sizeof(float));
            printf("=================================================\n");
            for (int i = 0; i < tlen; i++) {
//                if (fabs(f1[i] - f2[i]) > 1e-3) {
                    printf("GG on test %d  %f %f\n", i, f1[i], f2[i]);
//                    break;
//                }
            }
            printf("=================================================\n");
        }
        in.close();
        inn.close();
    }
    return 0;
}