import os
import struct
import sys


def create_archive(directory, extensions, archive_path):
    try:
        print('Directory: %s' % directory)
        print('Extensions: %s' % extensions)
        print('Archive path: %s' % archive_path)

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
        print('Slicing archive: %s' % archive_path)
        print('Output directory: %s' % output_directory)

    except FileNotFoundError as e:
        print(f"File error: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")


def restore_archive(folder_path, archive_output_path):
    try:
        print('Restoring archive from folder: %s' % folder_path)
        print('Archive output path: %s' % archive_output_path)

    except FileNotFoundError as e:
        print(f"File error: {e}")
    except Exception as e:
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
            log.write('FAILURE in create!! Usage: python slicer.py create directory with files, extension list, '
                      'archive path')
            raise ValueError('Usage: python slicer.py create directory with files, extension list, archive path')
        create_archive(sys.argv[2], sys.argv[3].split(','), sys.argv[4])

    elif sys.argv[1] == 'slice':
        if len(sys.argv) != 4:
            log.write('FAILURE in slice!! Usage: python slicer.py slice archive path, output directory path')
            raise ValueError('Usage: python slicer.py slice archive path, output directory path')
        slice_archive(sys.argv[2], sys.argv[3])

    elif sys.argv[1] == 'restore':
        if len(sys.argv) != 4:
            log.write('FAILURE in restore!! Usage: python slicer.py restore folder path with slices of archive, '
                      'archive output path')
            raise ValueError('Usage: python slicer.py restore folder path with slices of archive, archive output path')
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
