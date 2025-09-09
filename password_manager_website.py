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

def stored_password():

    name = st.text_input("please enter app or website name:")
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
            else:
                st.info("click 'generate password' to generate new password")
        else:
            password = st.text_input("please enter app password:",type="password").replace(" ", "")
            if password:
                store_data(table_name,"app",name,password)
                st.success("password saved")

    else:
        st.write("password already exists.if you want to change it please choose option change password")

def check_password():
    name=st.text_input("please enter the app or website name:")
    value=read_data("password",table_name,"app",name)
    if value:
        st.text_input(f"The password of {name} is: {value[0]}",type="password")
    else:
        st.write(f"The password of {name} have not save yet")

def change_password():

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

st.write("welcome to use password manager")
register=st.radio("",["already have account,sign in","haven't register as a password manager user,sign up"])


if register.startswith("in"):
    username = st.text_input("please enter username:")
    lock=read_data("password",lock_table,"username",username)
    if lock:
        lock_password=st.text_input("please enter password:").replace(" ", "")
        if lock_password== lock[0]:
            st.write("you are already logged in")
        else :
            st.write("your password is wrong.please try again")
            st.stop()
    else:
        st.write("you have not sign up yet.please sign up first")
        st.stop()
else:
    st.write("please enter username and password for sign up")
    username = st.text_input("please enter username:")
    lock=read_data("password",lock_table,"username",username)
    if lock:
        lock_password = st.text_input("please enter password:").replace(" ", "")
        store_data(lock_table,"username",username,lock_password)
        st.write("your account has been created successfully.please sign in again")
        st.stop()
    else:
        st.write("this username already exists")
        st.stop()

table_name=f"password_{username}"

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
    stored_password()
elif st.session_state.mode == "check password":
    check_password()
elif st.session_state.mode == "change password":
    change_password()
elif st.session_state.mode == "exit":
    st.write("Thank you for using this program")
    st.stop()

# Navigation
if st.session_state.mode != "exit":
    if st.button("Next step"):
        st.session_state.mode = "menu"
conn.close()