# cdc-placement-website-backend-NotificationsApi

## setup

```
git clone <url to repo>
cd cdc-placement-website-backend-NotificationsApi
python3 -m venv venv
cd NotificationsApi
./build.sh
```
This Will setup things for you.....
### To run The server 
``` python3 manage.py runserver```
### To create SuperUser
```python3 manage.py createsuperuser```

## Functionalities 
* Send Notifications to the user before 1 day, 6hrs, 3hrs, 1 hrs, 30 mins before deadline
* can also send custom notifications using ```send/``` endpoint

## Usage
* Trigger ```addopening/``` endpoint with corresponding request while a opening is listed to students and  next things will be taken care . It will send notifications before the deadlines
* To  send custom notifications use ```send/``` endpoint
## how to encode token 
```jwt.encode(payload=<payload here>,key='secret',algorithm="HS256")```

##  addtoken/ 
request_type: ```post```

> Headers <br>
> Authorization: "Bearer {tokenID}"

request_format:
```
{
"fcm_token":"<your fcm token here>"
}
```

* This will automatically add the token to the corresponding user and also adds the token to corresponding topics based on the role 

##  send/  
request_type:```post```\
request_format:
```
{
"token":"<your encoded JWT token here>"
}
```

your encoded token's payload must be either
### a)
```
{
  "topic":"students",(can be students or admins or s_admins)
  "title":"<title>",
  "body":"<body>",
  "url":"<url>"  //leaving url empty("") will keep the url to default(i.e portal) 
 }
```
* This sends the message to students or admins or super admins based on the topic
### b)
```
 {
  email:"<email>" , sends the notifications to specific person only
  "title":"<title>",
  "body":"<body>",
  "url":"<url>"  //leaving url empty("") will keep the url to default(portal) 
 }
```
##   addopening/ 
request_type:```post``` \
request_format: 
```
{ 
"token":"<your encoded JWT token here>" 
} 
```
your encoded token's payload must be  

```
{ 
  "id":"<id>",
  "company":"<name>", 
  "role":"<role>", 
  "deadline":"%Y-%m-%d %H:%M:%S"   
 } 
```
 * resending same id will update the details existed which can be used to update deadline 


