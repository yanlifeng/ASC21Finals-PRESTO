#include <cstdio>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <array>
#include <cstring>
#include <vector>
#include "mytimer.hpp"

#ifdef _OPENMP

#include <omp.h>

#endif

#define maxn 2010
using namespace std;
vector<string> c1, c2, c3, c4;

string exec(const char *cmd) {
//    printf("now running %s\n", cmd);
    array<char, 128> buffer;
    string result;
    unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
    if (!pipe) {
        throw runtime_error("popen() failed!");
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    return result;
}

int main() {
    freopen("in.txt", "r", stdin);
    char s[maxn];
    int cnt = 0;
    while (cin.getline(s, 1000)) {
//        printf("%s\n", s);
        if (strcmp("!@#$%^", s) == 0) {
            cnt++;
            continue;
        }
        if (cnt == 0) {
            string str(s);
            c1.push_back(str);
        }
        if (cnt == 1) {
            string str(s);
            c2.push_back(str);
        }
        if (cnt == 2) {
            string str(s);
            c3.push_back(str);
        }
        if (cnt == 3) {
            string str(s);
            c4.push_back(str);
        }
    }
    printf("n1 %d\n", c1.size());
    printf("n2 %d\n", c2.size());
    printf("n3 %d\n", c3.size());
    printf("n4 %d\n", c4.size());
#ifdef _OPENMP
    printf("omp is open\n");
    printf("totle thread is %d\n", omp_get_num_procs());
#endif
    double t0 = get_wall_time();
#ifdef _OPENMP
#pragma omp parallel for
#endif
    for (int i = 0; i < c1.size(); i += 2) {
        exec(c1[i].c_str());
        exec(c1[i + 1].c_str());
    }
    exec("rm *.sub*");

#ifdef _OPENMP
#pragma omp parallel for
#endif
    for (int i = 0; i < c2.size(); i++) {
        exec(c2[i].c_str());
    }

#ifdef _OPENMP
#pragma omp parallel for
#endif
    for (int i = 0; i < c3.size(); i++) {
        exec(c3[i].c_str());
    }

#ifdef _OPENMP
#pragma omp parallel for
#endif
    for (int i = 0; i < c4.size(); i++) {
        exec(c4[i].c_str());
    }
    printf("cost %.4f\n", get_wall_time() - t0);
    return 0;
}