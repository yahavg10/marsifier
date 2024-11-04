file_invoker = lambda folder_path, common_name, suffixes, file_read_mode: [
    ('files', open(f"{folder_path}/{common_name}{suffix}", file_read_mode))
    for suffix in suffixes
]
