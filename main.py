from secrets import SSCreds

if __name__ == "__main__":
    cred = SSCreds(secret_id=int(input("Enter secret_id to retrieve: ")))

    print(f"id: {cred.secret_id} ident: {cred.ident} secret: {cred.secret}")