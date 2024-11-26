import os
import gzip
import shutil
import time
import argparse
import logging
from multiprocessing import Process, Manager, Queue
from Bio.PDB import PDBParser
from Bio.PDB.PDBExceptions import PDBException

def setup_logging(log_file):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def decompress_pdb_file(file_path):
    with gzip.open(file_path, 'rb') as f_in:
        with open(file_path[:-3], 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    logging.info(f"Decompressed {file_path}")
    return file_path[:-3]

def check_ca(file_path):
    parser = PDBParser()
    try:
        structure = parser.get_structure('X', file_path)
        for model in structure:
            for chain in model:
                for residue in chain:
                    if 'CA' in residue:
                        logging.info(f"Kept {file_path} (CA atom exists)")
                        return file_path
    except PDBException:
        os.remove(file_path)
        logging.info(f"Removed {file_path} (PDBException)")
        return file_path
    os.remove(file_path)
    logging.info(f"Removed {file_path} (no CA atom)")
    return file_path

def remove_folder(folder_path):
    shutil.rmtree(folder_path)
    logging.info(f"Removed folder {folder_path}")
    return folder_path

def worker_decompression(input_queue, checker_queue):
    while True:
        folder_path = input_queue.get()
        if folder_path is None:
            checker_queue.put(None)
            break
        pdb_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.gz')]
        for file_path in pdb_files:
            decompress_pdb_file(file_path)
        checker_queue.put(folder_path)

def worker_checker(checker_queue, deletion_queue):
    while True:
        folder_path = checker_queue.get()
        if folder_path is None:
            deletion_queue.put(None)
            break
        decompressed_files = [os.path.join(folder_path, f[:-3]) for f in os.listdir(folder_path) if f.endswith('.gz')]
        kept_files = []
        for file_path in decompressed_files:
            result = check_ca(file_path)
            if os.path.exists(result):
                kept_files.append(result)
        deletion_queue.put((folder_path, kept_files))

def worker_deletion(deletion_queue, moving_queue):
    while True:
        item = deletion_queue.get()
        if item is None:
            moving_queue.put(None)
            break
        folder_path, kept_files = item
        gz_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.gz')]
        for file_path in gz_files:
            os.remove(file_path)
            logging.info(f"Removed compressed file {file_path}")
        moving_queue.put((folder_path, kept_files))

def worker_moving(moving_queue, removal_queue, processed_dir):
    while True:
        item = moving_queue.get()
        if item is None:
            removal_queue.put(None)
            break
        folder_path, kept_files = item
        os.makedirs(processed_dir, exist_ok=True)
        for file_path in kept_files:
            shutil.move(file_path, processed_dir)
            logging.info(f"Moved {file_path} to {processed_dir}")
        removal_queue.put(folder_path)

def worker_removal(removal_queue):
    while True:
        folder_path = removal_queue.get()
        if folder_path is None:
            break
        remove_folder(folder_path)

def main(main_folder, processed_dir):
    start = time.time()
    folders = [os.path.join(main_folder, f) for f in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, f))]
    
    manager = Manager()
    input_queue = manager.Queue()
    checker_queue = manager.Queue()
    deletion_queue = manager.Queue()
    moving_queue = manager.Queue()
    removal_queue = manager.Queue()

    decompression_process = Process(target=worker_decompression, args=(input_queue, checker_queue))
    checker_process = Process(target=worker_checker, args=(checker_queue, deletion_queue))
    deletion_process = Process(target=worker_deletion, args=(deletion_queue, moving_queue))
    moving_process = Process(target=worker_moving, args=(moving_queue, removal_queue, processed_dir))
    removal_process = Process(target=worker_removal, args=(removal_queue,))

    decompression_process.start()
    checker_process.start()
    deletion_process.start()
    moving_process.start()
    removal_process.start()

    for folder in folders:
        input_queue.put(folder)

    input_queue.put(None)

    decompression_process.join()
    checker_process.join()
    deletion_process.join()
    moving_process.join()
    removal_process.join()

    logging.info(f'Time: {time.time() - start}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decompress and process PDB files.')
    parser.add_argument('folder', type=str, help='Path to the folder containing PDB folders')
    parser.add_argument('processed_folder', type=str, help='Path to the folder where processed data will be')
    parser.add_argument('--log_file', type=str, default='process.log', help='Path to the log file')
    args = parser.parse_args()

    setup_logging(args.log_file)
    main(args.folder, args.processed_folder)

# python3 preprocess_pdb.py data/pdb_test data/processed --log_file process.log