# Zelorain
The Telegram Zelorain Bot is a powerful tool designed to run on your Telegram account, assisting you in managing various aspects of your account, such as keeping it online and changing profiles. This bot runs directly on your account and provides functionalities to enhance your Telegram experience.

# Robot Advantages:
- Ease of use
- High speed
- Optimal use of resources

# Requirements
- Python (3.5, 3.6, 3.7, 3.8, 3.9, 3.10)
- Telethon (1.29.3)

# Installation
```
git clone https://github.com/mahdiashtian/zelorain.git
cd zelorain
pip install -r requirements.txt
```
# Usage
```
touch .env
```
Open the ".env" file and copy the following information into it:
```
api_id=123456
api_hash="35886641ed1bfaa92e7ee30er9888"
master=11111
admin_list=22222,33333,44444
```
You can get the values of **api_id** and **api_hash** from my.telegram.org

The **master** value is equal to your main admin (only one ID) and the **admin_list** value is equal to your auxiliary admins (gets a list of IDs separated by ,) which You can get these two values using [userinfobot](https://telegram.me/userinfobot)


Then enter the following command in the terminal and complete the authentication process:
```
python main.py
```
