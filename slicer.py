import os
import struct
import sys


def create_archive(directory, extensions, archive_path):
    try:
        extensions = [ext.lstrip('.') for ext in extensions]

        if not os.path.isdir(directory):
            log.write(f"Error: The directory '{directory}' is not a directory.")
            raise FileNotFoundError(f"Error: The directory '{directory}' is not a directory.")

        dict_extensions = {ext: 0 for ext in extensions}

        for root, _, files in os.walk(directory):
            for file in files:
                if file.split('.')[-1] in extensions:
                    dict_extensions[file.split('.')[-1]] += 1

        for key, value in list(dict_extensions.items()):
            if value == 0:
                dict_extensions.pop(key)

        if len(dict_extensions) == 0:
            log.write(f"Error: No files with the specified extensions found in the directory '{directory}'.")
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
                        with open(file_path, 'rb') as f:
                            file_data = f.read()

                        archive.write(struct.pack('I', len(relative_path)))
                        archive.write(relative_path.encode('utf-8'))
                        archive.write(struct.pack('I', len(file_data)))
                        archive.write(file_data)

        log.write(f"Archive created successfully: {archive_path}")
        print(f"Archive created successfully: {archive_path}")
    except FileNotFoundError as e:
        log.write(f"File error: {e}")
        print(f"File error: {e}")
    except struct.error as e:
        log.write(f"Struct error while packing data: {e}")
        print(f"Struct error while packing data: {e}")
    except Exception as e:
        log.write(f"Unexpected error occurred: {e}")
        print(f"Unexpected error occurred: {e}")


def slice_archive(archive_path, output_directory):
    try:
        if not os.path.isfile(archive_path):
            raise FileNotFoundError(f"Archive file '{archive_path}' not found.")

        if not os.path.isdir(output_directory):
            os.makedirs(output_directory, exist_ok=True)

        number_of_slices = 5
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
                slice_filename = f"{i}_{slice_hash}"
                slice_path = os.path.join(output_directory, slice_filename)

                try:
                    with open(slice_path, 'wb') as slice_file:
                        slice_file.write(slice_data)
                except IOError as e:
                    raise IOError(f"Failed to write slice '{slice_filename}': {e}")

        log.write(f"Slicing completed successfully. Output directory: {output_directory}\n")
        print(f"Slicing completed successfully. Output directory: {output_directory}")

    except FileNotFoundError as e:
        log.write(f"File error: {e}\n")
        print(f"File error: {e}")
    except ValueError as e:
        log.write(f"Value error: {e}\n")
        print(f"Value error: {e}")
    except IOError as e:
        log.write(f"IO error: {e}\n")
        print(f"IO error: {e}")
    except Exception as e:
        log.write(f"Unexpected error occurred: {e}\n")
        print(f"Unexpected error occurred: {e}")


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

        log.write(f"Archive restored successfully. Output path: {archive_output_path}\n")
        print(f"Archive restored successfully. Output path: {archive_output_path}")

    except FileNotFoundError as e:
        log.write(f"File error: {e}\n")
        print(f"File error: {e}")
    except PermissionError as e:
        log.write(f"Permission error: {e}\n")
        print(f"Permission error: {e}")
    except ValueError as e:
        log.write(f"Value error: {e}\n")
        print(f"Value error: {e}")
    except IOError as e:
        log.write(f"IO error: {e}\n")
        print(f"IO error: {e}")
    except Exception as e:
        log.write(f"Unexpected error occurred: {e}\n")
        print(f"Unexpected error occurred: {e}")


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
        log.write('Usage: python slicer.py <command> [args]')
        raise ValueError('Usage: python slicer.py <command> [args]')

    if sys.argv[1] == 'create':
        if len(sys.argv) != 5:
            log.write('FAILURE in create!! Usage: python slicer.py create: directory with files, extension list, '
                      'archive path')
            raise ValueError('Usage: python slicer.py create: directory with files, extension list, archive path')
        create_archive(sys.argv[2], sys.argv[3].split(','), sys.argv[4])

    elif sys.argv[1] == 'slice':
        if len(sys.argv) != 4:
            log.write('FAILURE in slice!! Usage: python slicer.py slice: archive path, output directory path')
            raise ValueError('Usage: python slicer.py slice: archive path, output directory path')
        slice_archive(sys.argv[2], sys.argv[3])

    elif sys.argv[1] == 'restore':
        if len(sys.argv) != 4:
            log.write('FAILURE in restore!! Usage: python slicer.py restore: folder path with slices of archive, '
                      'archive output path')
            raise ValueError('Usage: python slicer.py restore: folder path with slices of archive, archive output path')
        restore_archive(sys.argv[2], sys.argv[3])

    else:
        log.write(f'Unknown command: {sys.argv[1]}')
        raise ValueError(f'Unknown command: {sys.argv[1]}')

except IOError as e:
    log.write(f"IO error: {e}")
    print(f"IO error: {e}")
    sys.exit(1)
except ValueError as e:
    log.write(f"Value error: {e}")
    print(f"Value error: {e}")
    sys.exit(1)
except Exception as e:
    log.write(f"Unexpected error occurred in the main program: {e}")
    print(f"Unexpected error occurred in the main program: {e}")
    sys.exit(1)

finally:
    if log:
        log.write("\nLog ended.")
        log.close()
