import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 9000))

try:
    menu_prompt = client.recv(1024).decode()
    choice = input(menu_prompt)
    client.send(choice.encode())

    if choice not in ('l', 'r'):
        print("Invalid choice. Exiting.")
        client.close()
        exit()
    
    username_prompt = client.recv(1024).decode()
    username = input(username_prompt)
    client.send(username.encode())
    
    password_prompt = client.recv(1024).decode()
    password = input(password_prompt)
    client.send(password.encode())
    
    while True:
        response = client.recv(1024).decode()
        if not response:
            break
        print("\n"+response)

        for line in response.splitlines():
            if "User ID" in response:
                user_id = int(response.split(":")[1].strip())
                break
        if user_id is not None:
            break
    if user_id is None:
        print("Could not retrieve User ID. Exiting.")
        client.close()
        exit()

    while True:
        add_more = input("Add item to cart? (y/n): ").lower()
        if add_more != 'y':
            break
    
        part_prompt = client.recv(1024).decode()
        part_id = input(part_prompt)
        client.send(part_id.encode())

        quantity_prompt = client.recv(1024).decode()
        quantity = input(quantity_prompt)
        client.send(quantity.encode())

        result = client.recv(1024).decode()
        print(result)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    client.close()
