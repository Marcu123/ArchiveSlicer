import os
import struct


def extract_archive(archive_path, extract_to):
    try:
        with open(archive_path, 'rb') as archive:
            magic_signature = archive.read(len(b'PERSONAL_ARCHIVE'))
            if magic_signature != b'PERSONAL_ARCHIVE':
                raise ValueError("Invalid archive format")

            num_extensions = struct.unpack('I', archive.read(4))[0]
            extensions = {}

            for _ in range(num_extensions):
                ext_length = struct.unpack('I', archive.read(4))[0]
                ext = archive.read(ext_length).decode('utf-8')
                file_count = struct.unpack('I', archive.read(4))[0]
                extensions[ext] = file_count

            extracted_counts = {ext: 0 for ext in extensions}

            while True:
                path_length_data = archive.read(4)
                if not path_length_data:
                    break

                path_length = struct.unpack('I', path_length_data)[0]
                relative_path = archive.read(path_length).decode('utf-8')

                file_length = struct.unpack('I', archive.read(4))[0]
                file_data = archive.read(file_length)

                file_extension = os.path.splitext(relative_path)[1].lstrip('.')

                extracted_counts[file_extension] += 1

                output_path = os.path.join(extract_to, relative_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as output_file:
                    output_file.write(file_data)

        for ext, count in extensions.items():
            if extracted_counts[ext] != count:
                print(
                    f"Warning: Mismatch for extension '.{ext}': Expected {count}, but extracted {extracted_counts[ext]}")
            else:
                print(f"Extension '.{ext}' extracted successfully: {count} files")

        print(f"Archive extracted successfully to {extract_to}")

    except FileNotFoundError:
        print(f"Error: Archive '{archive_path}' not found.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


extract_archive('arhiva', 'extr')
