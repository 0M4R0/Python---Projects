# Password generator V2
import secrets
from cryptography.fernet import Fernet
import string
import json
import os


# Generate a key for encryption (do this only once and save the key securely)
def generate_key():
    key = Fernet.generate_key()
    with open('key.key', 'wb') as key_file:
        key_file.write(key)
    print("Encryption key generated and saved.")
    print(f"Key: {key.decode()}")

# Load the encryption key
def load_key():
    if not os.path.exists('key.key'):
        print('Encryption key not found. Generating a new one...')
        generate_key()
    with open('key.key', 'rb') as key_file:
        return key_file.read() # Return the key as bytes

# Encrypt the password
def encrypt_password(password, fernet):
    return fernet.encrypt(password.encode()).decode()

# Decrypt the password
def decrypt_password(encrypted_password, fernet):
    return fernet.decrypt(encrypted_password.encode()).decode()

# Generate the password
def generate_password(length):
    if length < 8:
        print("The minimun length for a strong password is 8 characters.")
        return None
    
    # Define character sets
    upper_case = string.ascii_uppercase
    lower_case = string.ascii_lowercase
    numbers = string.digits
    symbols = string.punctuation

    # Ensure atleast have one character of each type
    password = [
        secrets.choice(upper_case),
        secrets.choice(lower_case),
        secrets.choice(numbers),
        secrets.choice(symbols),
    ]

    # Fill with random characters until reaching the desired length
    all_characters = upper_case + lower_case + numbers + symbols
    password += [secrets.choice(all_characters) for _ in range(length - 4)]

    # Mix the characters a bit more
    secrets.SystemRandom().shuffle(password)

    # Join the list of characters into a string
    return ''.join(password)

# Load the passwords that are saved
def load_password():
    if os.path.exists('password.json'):
        with open('password.json', 'r') as file:
            return json.load(file)
    return {}

# Save the passwords to a file
def save_password(passwords):
    with open('password.json', 'w') as file:
        json.dump(passwords, file, indent=4) # Create the file if it doesn't exist

# Add or update the password
def add_or_update_login(passwords, login, password, fernet):
    if not login or not isinstance(login, str):
        print("Error: the login must be a valid string.")
        return
    encrypted_password = encrypt_password(password, fernet) # Encrypt the password before saving
    passwords[login] = encrypted_password
    save_password(passwords)
    print(f"Saved login: {login}")

# Delete a password
def delete_login_and_password(passwords, login):
    if login in passwords:
        del passwords[login]
        save_password(passwords)
    else:
        print("Login was not found.")

# List all logins and give an option to see the passwords
def list_logins(passwords, fernet):
    if passwords:
        print("\nLogins saved:")
        for index, login in enumerate(passwords):
            print(f"{index+1}. {login}")

        choice = input("\nSelect the number of a login to see the password (Press enter to cancel): ")
        if choice:
            try:
                choice = int(choice) - 1
                login = list(passwords.keys())[choice]
                decrypted_password = decrypt_password(passwords[login], fernet) # Decrypt the password before displaying
                print(f"'{login}': {decrypted_password}")
            except (ValueError, IndexError):
                print("Invalid selection.")
    else:
        print("There aren't any saved logins.")

def menu():
    # Load encryption key and initialize Fernet
    key = load_key()
    fernet = Fernet(key)

    passwords = load_password()

    while True:
        print("\n--- Password Generator ---")
        print("1. Generate password")
        print("2. Save a new password")
        print("3. List logins")
        print("4. Delete a password")
        print("5. Close program")

        try:
            option = int(input("Select an option (1, 2, 3, 4, 5): ").strip())
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 5.")
            continue

        if option == 1:
            length = int(input("How many caracters should the password have?: ").strip())
            new_password = generate_password(length)
            if new_password:
                print(f"\nPassword generated: {new_password}")

        elif option == 2:
            login = input("\nInsert the login (page in which you'll be using the password): ").strip()
            if login in passwords:
                confirm = input(f"A password already exists for '{login}' Overwrite it? (y/n): ").strip().lower()
                if confirm != 'y':
                    print("Operation cancelled.")
                    return

            password = input("Enter password (leave blank to generate one): ").strip()

            if not password: 
                length_input = input("How many caracters should the password have?: ").strip()

                # Verify if the input is blank
                if not length_input:
                    return

                try: 
                    length = int(length_input)
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
                    return

                # Generate password
                password = generate_password(length)

            if password:
                add_or_update_login(passwords, login, password, fernet)
            else:
                print("Password generation failed.")

        elif option == 3:
            list_logins(passwords, fernet)

        elif option == 4:
            login = input("Enter the login to delete: ")
            confirm = input(f"Are you sure you want to delete the login '{login}'? (y/n): ").strip().lower()
            if confirm == 'y':
                delete_login_and_password(passwords, login)
                print('Password deleted')
            else:
                print("Operation cancelled.")

        elif option == 5:
            print("Closing the program...")
            break

        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    menu()
