import os
import shutil
import gzip
import multiprocessing

root_path = '/home/yanpeng/GCP_gem5/prism/GCP_scripts/result/'

workloads = {
    'bench' : ['0.0', '0.5', '0.95', '0.99'],
    # 'kc': ['run_workloadl.dat', 'run_workloadh.dat'],
}
# workloads = {
#     'bench' : ['0.0', ],
# }
# workloads = {
#     'kvs' : ['run_workloadb.dat', 'run_workloadc.dat'],
# }

num_threads_per_nodess = [1, ]
# num_threads_per_nodess = [8, ]

# num_nodess = [16, ]
num_nodess = [16, 8, 4, 2]
# num_nodess = [4, ]

num_lockss = [1, ]

# lock_types = [
#             'pthread_rwlock_prefer_w',
#               'percpu',
#               'cohort_rw_spin_mutex',
#               'mcs',
#             #   'pthread_mutex'
#               ]
# lock_types = ['pthread_mutex', ]
from_lock_type = 'pthread_rwlock_prefer_w'
# lock_types = ['mcs', ]
# lock_types = ['cohort_rw_spin_mutex', ]

def process_directory(directory):
    # Backup the directory
    # parent_dir = os.path.dirname(directory)
    # backup_dir = parent_dir + '/' + os.path.basename(directory) + "_backup"
    # if os.path.exists(backup_dir):
    #     print(f"Backup directory {backup_dir} already exists. Consider removing it or renaming.")
    #     # return
    # else:
    #     shutil.copytree(directory, backup_dir)
    #     print(f"Backup of '{directory}' created at '{backup_dir}'")
    
    # Process .gz files in the directory
    os.system('mkdir -p %s' % directory)
    
    from_directory = directory.replace('gcp', from_lock_type)
    # print(from_directory)
    # return
    lock_base_addr = 0
    hot_bucket_begin_addr = 0
    hot_bucket_end_addr = 0
    with open(from_directory + '/mem_meta.txt', 'r') as file:
        for line in file:
            if 'locks' in line:
                parts = line.strip().split()
                if len(parts) == 3:
                    lock_base_addr_str, _, _ = parts
                    lock_base_addr = int(lock_base_addr_str, 16)
            elif 'test_mem' in line:
                parts = line.strip().split()
                hot_bucket_begin_addr = parts[0]
                hot_bucket_begin_addr = int(hot_bucket_begin_addr, 16)
                hot_bucket_end_addr = parts[1]
                hot_bucket_end_addr = int(hot_bucket_end_addr, 16)
                        
    for root, dirs, files in os.walk(from_directory):
        for file in files:
            if file.endswith('.gz'):
                from_gz_file_path = os.path.join(root, file)
                gz_file_path = from_gz_file_path.replace(from_lock_type, 'gcp')
                # print(from_gz_file_path, gz_file_path)
                process_gz_file(from_gz_file_path, gz_file_path, lock_base_addr, hot_bucket_begin_addr, hot_bucket_end_addr)
            elif file.endswith('.out'):
                from_out_file_path = os.path.join(root, file)
                out_file_path = from_out_file_path.replace(from_lock_type, 'gcp')
                os.system('cp %s %s' % (from_out_file_path, out_file_path))

def process_gz_file(from_gz_file_path, gz_file_path, lock_base_addr, hot_bucket_begin_addr, hot_bucket_end_addr):
    in_lock_op = False
    with gzip.open(from_gz_file_path, 'rt') as from_gz_file, gzip.open(gz_file_path, 'wt') as gz_file:
        for line in from_gz_file:
            modified_line = line
            if '!' in line and '4096' not in line:
                rwlock_code = line[-3]
                if rwlock_code == '0':
                    in_lock_op = True
                elif rwlock_code == '1':
                    in_lock_op = False
                    modified_line = line[:-3] + '2' + line[-2:]
                    rwlock_code = int(modified_line[2:])
                    rwlock_indicator = rwlock_code % 100
                    modified_line = '! ' + str(lock_base_addr * 100 + rwlock_indicator) + '\n'
                else:
                    assert False
            if in_lock_op == True:
                modified_line = None
            elif '@' in line:
                parts = line.strip().split()
                mem_acc_addr = int(parts[3][2:], 16)
                if mem_acc_addr >= hot_bucket_begin_addr \
                    and mem_acc_addr < hot_bucket_end_addr:
                    modified_line = '! 9999\n'
            if modified_line is not None:
                gz_file.write(modified_line)
        
    # Replace the original file with the modified temp file
    print(f"Generated '{gz_file_path}'")

def main(directories):
    # print(directories)
    # return
    ps = []
    for directory in directories:
        p = multiprocessing.Process(target=process_directory, args=(directory,))
        ps.append(p)
        p.start()
    for p in ps:
        p.join()
        # process_directory(directory)
        # print(f"Finished processing directory: {directory}")

if __name__ == "__main__":
    directories = []  # Update this list with your directories
    for app in workloads:
        for workload in workloads[app]:
            for num_nodes in num_nodess:
                for num_threads_per_nodes in num_threads_per_nodess:
                    directories.append(root_path + '_'.join((app, workload,
                                    'gcp',
                                    str(num_nodes),
                                    str(num_threads_per_nodes))))
    main(directories)
