import sqlite3
import string,secrets
import streamlit as st

st.title("Password Manager")

conn=sqlite3.connect("password_manager.db")
c=conn.cursor()
#for the log in system


def read_data(find,table,where,what):
    c.execute(f"SELECT {find} FROM {table} WHERE {where}=?",(what,))
    rows=c.fetchone()
    if rows:
        return rows
    else:
        return False

def store_data(table,service,name,password):
    c.execute(f"""CREATE TABLE IF NOT EXISTS {table}(
    {service}  TEXT PRIMARY KEY ,
    password TEXT)""")
    c.execute(f"""INSERT OR REPLACE INTO {table}({service},password) VALUES (?,?)""",(name,password))
    conn.commit()

def stored_password(table_name):

    name = st.text_input("please enter app or website name:")
    if not name:
        return
    data=read_data("*",table_name,"app",name)
    if not data:
        generate = st.radio("do you want system generate password for you?:",["yes","no"])
        if generate.startswith("y"):
            if st.button("generate password"):
                password = generate_password()
                st.session_state.generated_password = password

        if "generated_password" in st.session_state:
            password=st.session_state.generated_password
            satisfy = st.radio(f"generated password is: {password}.Do you satisfy?",["yes","no"])
            if satisfy.startswith("y"):
                store_data(table_name,"app",name,password)
                st.success("password saved")
                del st.session_state.generated_password
            else:
                st.info("click 'generate password' to generate new password")
        else:
            password = st.text_input("please enter app password:",type="password").replace(" ", "")
            if password:
                store_data(table_name,"app",name,password)
                st.success("password saved")

    else:
        st.warning("password already exists.if you want to change it please choose option change password")

def check_password(table_name):
    name=st.text_input("please enter the app or website name:")
    if not name:
        return
    value=read_data("password",table_name,"app",name)
    if value:
        st.text_input(f"The password of {name} is: {value[0]}",type="password")
    else:
        st.write(f"The password of {name} have not save yet")

def change_password(table_name):

    name=st.text_input("please enter app or website name that you want to change:")
    data=read_data("password",table_name,"app",name)
    if data:
        generate=st.radio("do you want system generate password for you?",["yes","no"])

        if generate.startswith("y"):
            if st.button("generate password"):
                    password = generate_password()
                    st.session_state.generated_password = password

            if "generated_password" in st.session_state:
                password = st.session_state.generated_password
                satisfy = st.radio(f"generated password is: {password}.Do you satisfy?", ["yes", "no"])
                if satisfy.startswith("y"):

                    store_data(table_name,"app",name,password)
                    st.success("password saved")
                    del st.session_state.generated_password
                else:
                    st.info("click 'generate password' to generate new password")
            else:
                password = st.text_input("please enter app password:", type="password").replace(" ", "")
                if password:
                   data[name] = password
                   store_data(table_name,"app",name,password)
                   st.success("password saved")

    else:
        st.write(f"The password of {name} have not save yet")

def generate_password():
    length=st.slider("please enter the length of password:",4,15,8)
    strength=st.radio("please enter the strength of password(weak/medium/strong):",
                      ["digit only (weak)","digit + letter (medium)","digit + letter +symbol (strong)"])
    if strength.startswith("weak"):
        character=string.digits
    elif strength.startswith("medium"):
        character=string.ascii_letters+string.digits
    else:
        character=string.ascii_letters+string.digits+string.punctuation
    return ''.join(secrets.choice(character) for _ in range(int(length)))

lock_table="username_password"

c.execute("""CREATE TABLE IF NOT EXISTS username_password(
username TEXT PRIMARY KEY,
password TEXT)""")

st.write("Welcome to use password manager")

# If already logged in, skip login/signup
if "logged_in" in st.session_state and st.session_state.logged_in:
    st.success(f"Welcome back, {st.session_state.username}!")
else:
    register = st.radio("", ["already have account, sign in", "haven't register as a password manager user, sign up"])

    # --- SIGN IN ---
    if register.startswith("already"):
        username = st.text_input("please enter username:")
        password = st.text_input("please enter password:", type="password")

        if st.button("Sign In"):
            lock = read_data("password", lock_table, "username", username)
                
            if lock and password == lock[0]:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("You are logged in")
                
            else:
                st.error("Your password or username is wrong. Please try again")
                    

    # --- SIGN UP ---
    else:
        username = st.text_input("please enter username for your account:")
        password = st.text_input("please enter password(remember for the future logins):", type="password")

        if st.button("Sign Up"):
            if not username or not password:
                st.error("Username and password cannot be empty")
            else:
                lock = read_data("password", lock_table, "username", username)
                if lock:
                    st.error("This username already exists")
                else:
                    store_data(lock_table, "username", username, password)
                    st.success("Your account has been created successfully. Please sign in again")
                    st.stop()

# ---------------------- PASSWORD TABLE ----------------------

if "logged_in" in st.session_state and st.session_state.logged_in:
    table_name = f"password_{st.session_state.username}"
    c.execute(f"""CREATE TABLE IF NOT EXISTS {table_name}(
    app TEXT PRIMARY KEY,
    password TEXT)""")

#want=want to stored password or no
if "mode" not in st.session_state:
    st.session_state.mode = "menu"

# First menu (after login)
if st.session_state.mode == "menu":
    st.session_state.mode = st.radio(
        "Pick your choice:",
        ["store password", "check password", "change password", "exit"],
        key="main_menu"
    )

# Handle actions
if st.session_state.mode == "store password":
    stored_password(table_name)
elif st.session_state.mode == "check password":
    check_password(table_name)
elif st.session_state.mode == "change password":
    change_password(table_name)
elif st.session_state.mode == "exit":
    st.write("Thank you for using this program")
    st.stop()

# Navigation
if st.session_state.mode != "exit":
    if st.button("Next step"):
        st.session_state.mode = "menu"

conn.close()






