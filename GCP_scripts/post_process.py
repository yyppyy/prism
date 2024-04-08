import os
import shutil
import gzip
import multiprocessing

def in_shmem_ranges(addr, shmem_ranges):
    for (b, e) in shmem_ranges:
        if addr >= b and addr < e:
            return True
    return False

def process_line(line, profile_enabled, shmem_ranges):
    """
    Modify or delete a line.
    Return the modified line, or None to delete the line.
    """
    # Example: simple modification, uncomment and adjust as needed
    # modified_line = line.replace("original", "modified")
    # return modified_line
    
    # Example: conditionally delete lines, uncomment and adjust as needed
    # if "delete_this" in line:
    #     return None  # Line will be deleted
    is_barrier = False
    if '5^' in line:
        is_barrier = True
    if (not '^' in line) and (not '#' in line) and (not profile_enabled):
        line = None
    # elif '#' in line:
        # line = None
    elif ('@' in line):
        parts = line.strip().split()
        if len(parts) <= 3:
            line = None
        else:
            addr = int(parts[3][2:], 16)
            if not in_shmem_ranges(addr, shmem_ranges):
                line = None
    return line, is_barrier  # Return the line unmodified by default

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
    shmem_ranges = []
    with open(directory + '/mem_meta.txt', 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 3:
                start_addr, end_addr, name = parts
                start_addr = int(start_addr, 16)
                end_addr = int(end_addr, 16)
                shmem_ranges.append((start_addr, end_addr))
        
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.gz'):
                gz_file_path = os.path.join(root, file)
                process_gz_file(gz_file_path, shmem_ranges)

def process_gz_file(gz_file_path, shmem_ranges):
    
    profile_enabled = False
    # Temporary file to store modifications
    temp_file_path = gz_file_path + ".tmp"
    
    # Open the original .gz file and a temporary file for output
    with gzip.open(gz_file_path, 'rt') as gz_file, gzip.open(temp_file_path, 'wt') as temp_file:
        for line in gz_file:
            modified_line, is_barrier = process_line(line, profile_enabled, shmem_ranges)
            if is_barrier:
                profile_enabled = not profile_enabled
            # Write the modified line to temp file if not deleted
            if modified_line is not None:
                temp_file.write(modified_line)
    
    # Replace the original file with the modified temp file
    os.replace(temp_file_path, gz_file_path)
    print(f"Processed and updated '{gz_file_path}'")

def main(directories):
    ps = []
    for directory in directories:
        p = multiprocessing.Process(target=process_directory, args=(directory,))
        ps.append(p)
        p.start()
    for p in ps:
        p.join()
        # process_directory(directory)
        # print(f"Finished processing directory: {directory}")

root_path = '/home/yanpeng/GCP_gem5/prism/GCP_scripts/result/'

workloads = {
    'kvs' : ['run_workloada.dat', 'run_workloadb.dat', 'run_workloadc.dat'],
    # 'kc': ['run_workloadl.dat', 'run_workloadh.dat'],
}
# workloads = {
#     'kvs' : ['run_workloada.dat', ],
# }

num_threads_per_nodess = [8, ]
# num_threads_per_nodess = [8, ]

# num_nodess = [12, ]
num_nodess = [16, 8, 4, 2, 1]
# num_nodess = [1, ]

lock_types = [
            'pthread_rwlock_prefer_w',
              'percpu',
              'cohort_rw_spin_mutex',
              'mcs',
              'pthread_mutex'
              ]
# lock_types = ['pthread_mutex', ]
# lock_types = ['pthread_rwlock_prefer_w', ]
# lock_types = ['mcs', ]
# lock_types = ['cohort_rw_spin_mutex', ]

if __name__ == "__main__":
    directories = []  # Update this list with your directories
    for app in workloads:
        for workload in workloads[app]:
            for lock_type in lock_types:
                for num_nodes in num_nodess:
                    for num_threads_per_nodes in num_threads_per_nodess:
                        directories.append(root_path + '_'.join((app, workload,
                                        lock_type,
                                        str(num_nodes),
                                        str(num_threads_per_nodes))))
    main(directories)