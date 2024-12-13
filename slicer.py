import os
import struct
import sys
from datetime import datetime


def log_message(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    log.write(timestamp + msg + "\n")


def create_archive(directory, extensions, archive_path):
    try:
        if extensions == ['ALL']:
            extensions = []
        else:
            extensions = [ext.lstrip('.') for ext in extensions]

        if not os.path.isdir(directory):
            log_message(f"Error: The directory '{directory}' is not a directory.")
            raise FileNotFoundError(f"Error: The directory '{directory}' is not a directory.")

        if not extensions:
            dict_extensions = {}
        else:
            dict_extensions = {ext: 0 for ext in extensions}

        for root, _, files in os.walk(directory):
            for file in files:
                if file.split('.')[-1] in dict_extensions.keys():
                    dict_extensions[file.split('.')[-1]] += 1
                elif not extensions:
                    file_extension = file.split('.')[-1]
                    if file_extension not in dict_extensions:
                        dict_extensions[file_extension] = 1
                    else:
                        dict_extensions[file_extension] += 1

        for key, value in list(dict_extensions.items()):
            if value == 0:
                dict_extensions.pop(key)

        if len(dict_extensions) == 0:
            log_message(f"Error: No files with the specified extensions found in the directory '{directory}'.")
            raise FileNotFoundError(f"No files with the specified extensions found in the directory '{directory}'.")

        with open(archive_path, 'wb') as archive:
            archive.write(b'PERSONAL_ARCHIVE')
            archive.write(struct.pack('I', len(dict_extensions)))

            for ext in dict_extensions.keys():
                archive.write(struct.pack('I', len(ext)))
                archive.write(ext.encode('utf-8'))
                archive.write(struct.pack('I', dict_extensions[ext]))

            for root, _, files in os.walk(directory):
                for file in files:
                    if file.split('.')[-1] in dict_extensions.keys():
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, directory)
                        try:
                            with open(file_path, 'rb') as f:
                                file_data = f.read()

                            archive.write(struct.pack('I', len(relative_path)))
                            archive.write(relative_path.encode('utf-8'))
                            archive.write(struct.pack('I', len(file_data)))
                            archive.write(file_data)
                        except IOError as e:
                            log_message(f"Failed to read file '{file_path}': {e}")
                            print(f"Failed to read file '{file_path}': {e}")
                            sys.exit(1)

        log_message(f"Archive created successfully: {archive_path}")
        print(f"Archive created successfully: {archive_path}")
    except FileNotFoundError as e:
        log_message(f"File error: {e}")
        print(f"File error: {e}")
        sys.exit(1)

    except struct.error as e:
        log_message(f"Struct error while packing data: {e}")
        print(f"Struct error while packing data: {e}")
        sys.exit(1)

    except Exception as e:
        log_message(f"Unexpected error occurred: {e}")
        print(f"Unexpected error occurred: {e}")
        sys.exit(1)


def slice_archive(archive_path, output_directory, number_of_slices=5):
    try:
        if not os.path.isfile(archive_path):
            raise FileNotFoundError(f"Archive file '{archive_path}' not found.")

        if not os.path.isdir(output_directory):
            os.makedirs(output_directory, exist_ok=True)

        archive_size = os.path.getsize(archive_path)
        if archive_size == 0:
            raise ValueError(f"The archive file '{archive_path}' is empty.")

        slice_size = archive_size // number_of_slices
        remaining_bytes = archive_size % number_of_slices

        with open(archive_path, 'rb') as archive:
            for i in range(number_of_slices):

                if i == number_of_slices - 1:
                    slice_size += remaining_bytes

                slice_data = archive.read(int(slice_size))

                if not slice_data:
                    raise ValueError(f"Failed to read data from the archive '{archive_path}'.")

                slice_hash = hash(slice_data)
                slice_filename = f"{i:05d}_{slice_hash}"
                slice_path = os.path.join(output_directory, slice_filename)

                try:
                    with open(slice_path, 'wb') as slice_file:
                        slice_file.write(slice_data)
                except IOError as e:
                    raise IOError(f"Failed to write slice '{slice_filename}': {e}")

        log_message(f"Slicing completed successfully. Output directory: {output_directory}")
        print(f"Slicing completed successfully. Output directory: {output_directory}")

    except FileNotFoundError as e:
        log_message(f"File error: {e}")
        print(f"File error: {e}")
        sys.exit(1)

    except ValueError as e:
        log_message(f"Value error: {e}")
        print(f"Value error: {e}")
        sys.exit(1)

    except IOError as e:
        log_message(f"IO error: {e}")
        print(f"IO error: {e}")
        sys.exit(1)

    except Exception as e:
        log_message(f"Unexpected error occurred: {e}")
        print(f"Unexpected error occurred: {e}")
        sys.exit(1)


def restore_archive(slices_path, archive_output_path):
    try:
        if not os.path.isdir(slices_path):
            raise FileNotFoundError(f"Directory with slices '{slices_path}' not found.")

        slices = os.listdir(slices_path)
        if len(slices) == 0:
            raise FileNotFoundError(f"No slices found in the directory '{slices_path}'.")

        slices.sort()

        for slice_file in slices:
            slice_path = os.path.join(slices_path, slice_file)
            if not os.access(slice_path, os.R_OK):
                raise PermissionError(f"Read permission denied for slice '{slice_path}'.")

        archive_data = b''
        for i, slice_file in enumerate(slices):
            slice_path = os.path.join(slices_path, slice_file)
            try:
                with open(slice_path, 'rb') as sf:
                    slice_data = sf.read()
                    if not slice_data:
                        raise ValueError(f"Slice '{slice_file}' is empty.")
                    archive_data += slice_data
            except IOError as e:
                raise IOError(f"Failed to read slice '{slice_file}': {e}")

        try:
            with open(archive_output_path, 'wb') as archive:
                archive.write(archive_data)
        except IOError as e:
            raise IOError(f"Failed to write archive '{archive_output_path}': {e}")

        log_message(f"Archive restored successfully. Output path: {archive_output_path}")
        print(f"Archive restored successfully. Output path: {archive_output_path}")

    except FileNotFoundError as e:
        log_message(f"File error: {e}")
        print(f"File error: {e}")
        sys.exit(1)

    except PermissionError as e:
        log_message(f"Permission error: {e}")
        print(f"Permission error: {e}")
        sys.exit(1)

    except ValueError as e:
        log_message(f"Value error: {e}")
        print(f"Value error: {e}")
        sys.exit(1)

    except IOError as e:
        log_message(f"IO error: {e}")
        print(f"IO error: {e}")
        sys.exit(1)

    except Exception as e:
        log_message(f"Unexpected error occurred: {e}")
        print(f"Unexpected error occurred: {e}")
        sys.exit(1)


log_file = "log.txt"
log = None

if not os.path.exists(log_file):
    with open(log_file, "w") as f:
        f.write("Log started:\n")
else:
    with open(log_file, "a") as f:
        f.write("\nLog started:\n")

try:
    log = open(log_file, "a")

    if len(sys.argv) < 2:
        log_message('Usage: python slicer.py <command> [args]\nAvailable commands: create, slice, restore')
        raise ValueError('Usage: python slicer.py <command> [args]')

    if sys.argv[1] == 'create':
        if len(sys.argv) != 5:
            log_message(
                'FAILURE in create!! Usage: python slicer.py create: directory with files, extension list .txt, '
                '.jpg ... [optional ALL for all the extensions],archive path')
            raise ValueError('Usage: python slicer.py create: directory with files, extension list, archive path')
        create_archive(sys.argv[2], sys.argv[3].split(','), sys.argv[4])

    elif sys.argv[1] == 'slice':
        if len(sys.argv) == 5:
            slice_archive(sys.argv[2], sys.argv[3], int(sys.argv[4]))
        elif len(sys.argv) != 4:
            log_message('FAILURE in slice!! Usage: python slicer.py slice: archive path, output directory path, ['
                        'optional number of slices]')
            raise ValueError('Usage: python slicer.py slice: archive path, output directory path')
        else:
            slice_archive(sys.argv[2], sys.argv[3])

    elif sys.argv[1] == 'restore':
        if len(sys.argv) != 4:
            log_message('FAILURE in restore!! Usage: python slicer.py restore: folder path with slices of archive, '
                        'archive output path')
            raise ValueError('Usage: python slicer.py restore: folder path with slices of archive, archive output path')
        restore_archive(sys.argv[2], sys.argv[3])

    else:
        log_message(f'Unknown command: {sys.argv[1]}')
        raise ValueError(f'Unknown command: {sys.argv[1]}')

except IOError as e:
    log_message(f"IO error: {e}")
    print(f"IO error: {e}")
    sys.exit(1)

except ValueError as e:
    log_message(f"Value error: {e}")
    print(f"Value error: {e}")
    sys.exit(1)

except Exception as e:
    log_message(f"Unexpected error occurred in the main program: {e}")
    print(f"Unexpected error occurred in the main program: {e}")
    sys.exit(1)

finally:
    if log:
        log_message("Log ended.")
        log.close()
