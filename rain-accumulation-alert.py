# Python program to find weather details of Norfolk, VA, USA
# using OpenWeatherMap API, integrate the predicted rain fall,
# and determine periods of Ghent Dog Park wetness

import boto3, requests, json, smtplib, email

# Connect to AWS SSM Parameter Store
ssm = boto3.client('ssm', 'us-east-1')
def get_parameters(name):
  response = ssm.get_parameters(Names = [name])
  for parameter in response['Parameters']:
    return parameter['Value']

# Create a text/plain message
msg = email.message.EmailMessage()
msg['Subject'] = 'Ghent Dog Park: Rain Forecast Update'
msg['From'] = get_parameters("/GhentDogPark/Weather/EmailFrom")
msg['To'] = get_parameters("/GhentDogPark/Weather/EmailTo")

# Enter your OpenWeatherMap API key here
api_key = get_parameters("/GhentDogPark/Weather/APIKey")

# base_url variable to store url
base_url = "http://api.openweathermap.org/data/2.5/forecast?"

# Give city name
city_name = "Norfolk"

# complete_url variable to store complete url address
complete_url = base_url + "appid=" + api_key + "&q=" + city_name

# get method of requests module return response object
response = requests.get(complete_url)

# json method of response object convert json format data into python format data
r = response.json()

# Start with empty email message
message = ""

# Now x contains list of nested dictionaries
# Check the value of "cod" key is equal to "404",
# means city is found otherwise, city is not found
# Check the value of "cod" key is equal to "401",
# means API key is invalid.
if r["cod"] != "404" and r["cod"] != "401":

  for x in r["list"]:

    description = x["weather"][0]["description"]

    dt = x["dt_txt"]

    if "3h" in x["rain"].keys():
      rain = x["rain"]["3h"]
    else:
      rain = 0

    message += (
      "\nTime = " + str(dt) + "\n" +
      "rain (in mm) = " + str(rain) +
      ", " + str(description) + "\n"
    )

# Set the message content
msg.set_content(message)

# Print the message
print(msg)

# Send the message via our own SMTP server
#s = smtplib.SMTP('localhost')
#s.send_message(msg)
#s.quit()
