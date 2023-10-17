# cdc-placement-website-backend-NotificationsApi
## Functionalities 
* Send Notifications to the user before 1 day,6hrs,3hrs,1 hrs,30 mins before deadline..\
* can also send custom notifications using send endpoint\

## Usage
* Trigger add opening endpoint with corresponding request while a opening is listed to students next things will be taken care . It will send notifications before the deadlines
* To  send custom notifications use ```/send/``` endpoint
## how to encode token 
```jwt.encode(payload={},key='secret',algorithm="HS256")```

##  /addtoken/ endpoint
request_type:```post```\
This request should have http authorisation header similar to our backend. \
request_format:
```
{
"fcm_token":"<your fcm token here>"
}
```

This will automatically add the token to the corresponding user and also adds the token to corresponding groups........ based on the role 

##  /send/ endpoint 
request_type:```post```\
request_format:
```
{
"token":"<your encoded token here>"
}
```

your encoded token's payload must be either
### a)
```
{
  "topic":"students",(can be students or admins or s_admins)
  "title":"<title>",
  "body":"<body>",
  "url":"<url>"  //leaving url empty("") will keep the url to default(portal) 
 }
```
 this sends the message to students or admins or super admins based on the topic
### b)
```
 {
  email:"<email>" , sends the notifications to specific person only
  "title":"<title>",
  "body":"<body>",
  "url":"<url>"  //leaving url empty("") will keep the url to default(portal) 
 }
```
##   /addopening/ endpoint 
request_type:```post``` \
request_format: 
```
{ 
"token":"<your encoded token here>" 
} 
```
your encoded token's payload must be  

```
{ 
  "id":"<id>",(can be students or admins or s_admins) 
  "company":"<name>", 
  "role":"<role>", 
  "deadline":"%Y-%m-%d %H:%M:%S"   
 } 
```
 resending same id will update the details existed 


