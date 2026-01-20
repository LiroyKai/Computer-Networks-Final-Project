import socket
import threading
import sys

# הגדרות חיבור
HOST = '127.0.0.1'
PORT = 12345

def receive_messages(sock):
    """פונקציה שרק מקשיבה להודעות מהשרת ומדפיסה אותן"""
    while True:
        try:
            # קבלת מידע
            data = sock.recv(4096).decode('utf-8')
            if not data:
                print("\n[!] Disconnected from server.")
                sock.close()
                sys.exit()

            # פירוק הודעות דבוקות 
            messages = data.split('\n')
            
            for msg in messages:
                if not msg.strip(): continue
                
                # טיפול מיוחד ברשימת משתמשים
                if msg.startswith("USERS_LIST:"):
                    users = msg.replace("USERS_LIST:", "")
                    print(f"\n[👥 Online Users]: {users}")
                else:
                    # הדפסת הודעה רגילה
                    print(msg)
                    
        except Exception as e:
            print(f"\n[!] Error: {e}")
            sock.close()
            break

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except:
        print(f"Cannot connect to server at {HOST}:{PORT}")
        return

    # שלב 1: הרשמה
    username = input("Enter your username: ")
    client.send(username.encode('utf-8'))

    # הפעלת תהליכון להאזנה
    thread = threading.Thread(target=receive_messages, args=(client,), daemon=True)
    thread.start()

    print(f"--- Welcome {username}! ---")
    print("To send message use format: Target:Message")
    print("Example: All:Hello OR Danny:How are you?")
    print("Type 'quit' to exit.")
    print("---------------------------")

    # שלב 2: שליחת הודעות
    while True:
        try:
            msg = input() # מחכה שהמשתמש יקליד משהו
            
            if msg.lower() == 'quit':
                break
            
            # בדיקה שהפורמט נכון
            if ":" in msg:
                client.send(msg.encode('utf-8'))
            else:
                # ברירת מחדל: שולח לכולם אם לא ציינת למי
                client.send(f"All:{msg}".encode('utf-8'))
                
        except:
            break

    client.close()

if __name__ == "__main__":
    start_client()