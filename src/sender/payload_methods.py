file_invoker = lambda folder_path, common_name, suffixes: [
    ('files', open(f"{folder_path}/{common_name}{suffix}", "rb"))
    for suffix in suffixes
]
