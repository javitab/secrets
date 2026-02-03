from delinea import SSCreds

if __name__ == "__main__":
    sec_id = int(input("Enter secret_id to retrieve: "))

    cred = SSCreds(
        secret_id=sec_id,
        slug_ident="username",  # Optional, this shows default
        slug_secret="password",  # Optional, this shows default
    )

    print(f"id: {cred.secret_id} ident: {cred.ident} secret: {cred.secret}")
