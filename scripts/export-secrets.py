# Export secrets to an encrypted file
#
# Usage: python ./export-secrets.py <output-file> <encryption-key>
#
import sys
from tempfile import TemporaryDirectory

def encrypt_secrets_to_directory(encryption_key: str, directory: str) -> None:
    print("Encrypting secrets to directory ...")
    files_to_encrypt = ["ansible-vault-password.txt"]
    for filename in files_to_encrypt:
        encrypt_secret(filename, encryption_key, directory)

def encrypt_secret(filename: str, encryption_key: str, directory: str) -> None:
    print(f"  Encrypting {filename} ...")

def create_archive_from_directory(directory: str, output_file: str) -> None:
    print("Creating archive from directory ...")


if __name__ == "__main__":
    (output_file, encryption_key) = sys.argv[1:3]

    with TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory \"{temp_dir}\"")
        encrypt_secrets_to_directory(encryption_key, temp_dir)
        create_archive_from_directory(temp_dir, output_file)
