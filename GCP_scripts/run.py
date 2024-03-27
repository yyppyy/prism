from os import listdir
from os.path import isfile, join
import subprocess
import yaml
import argparse
import shlex
import os

running_procs = []
MAX_PROCS = 1
total_procs = 0

bin_dir = '/home/yanpeng/mind_internal/mind_linux/test_programs/07_lock_micro_benchmark/bin/'
workload_dir = '/home/yanpeng/GCP_gem5/workloads/ycsb_workloads/'
log_dir_dir = 'log/'
result_dir_dir = 'result/'

# workloads = {
#     'kvs' : ['run_workloada.dat', 'run_workloadb.dat', 'run_workloadc.dat'],
#     'kc': ['run_workloadl.dat', 'run_workloadh.dat'],
# }
workloads = {
    'kvs' : ['run_workloada.dat', ],
}

num_threads_per_nodess = [8, ]

# num_nodess = [16, ]
num_nodess = [1, ]

num_lockss = [1000, ]

# lock_types = ['pthread_rwlock_prefer_w', 'percpu', 'cohort_soul_pthread', 'cohort_rw_spin_mutex', 'mcs']
lock_types = ['pthread_mutex', ]

warmup_iters = 0

# num_iters = 10000
num_iters = 100

req_interval = 0
load_file = '/'
rmax = 0
wmax = 0

if __name__ == "__main__":
    for app in workloads:
        for workload in workloads[app]:
            for lock_type in lock_types:
                for num_locks in num_lockss:
                    for num_nodes in num_nodess:
                        for num_threads_per_nodes in num_threads_per_nodess:
                            bin_file = bin_dir + app
                            run_file = workload_dir + workload
                            run_id = '_'.join((app, workload, lock_type, str(num_nodes), str(num_threads_per_nodes)))
                            log_dir = log_dir_dir + run_id
                            result_dir = result_dir_dir + run_id
                            print(result_dir)
                            os.system('mkdir -p %s' % result_dir)
                            # cmd = '../../../build/bin/prism --backend=stgen -ltextv2 --executable='
                            cmd = '../../../build/bin/prism --backend=stgen --executable='
                            gcp_cmd = ' '.join((bin_file, str(num_nodes), str(num_threads_per_nodes), str(num_locks),
                                        lock_type, log_dir, str(warmup_iters), str(num_iters), str(req_interval),
                                        load_file, run_file, str(rmax), str(wmax)))
                            cmd += gcp_cmd
                            print(cmd)
                            cmds = shlex.split(cmd)
                            total_procs += 1
                            running_procs.append(subprocess.Popen(cmds, cwd=result_dir))
                            if len(running_procs) == MAX_PROCS:
                                for p in running_procs:
                                    p.wait()
                            print("total procs finished: %d" % total_procs)
                            running_procs = []