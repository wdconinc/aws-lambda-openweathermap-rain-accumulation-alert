# Python program to find weather details of Norfolk, VA, USA
# using OpenWeatherMap API, integrate the predicted rain fall,
# and determine periods of Ghent Dog Park wetness

import boto3, json, smtplib
from botocore.vendored import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# handler method
def lambda_handler(event = None, context = None):

  # Connect to AWS SSM Parameter Store
  ssm = boto3.client('ssm', 'us-east-1')
  def get_ssm_parameters(name):
    response = ssm.get_parameters(Names = [name])
    for parameter in response['Parameters']:
      return parameter['Value']

  # Create a text/plain message
  msg = MIMEMultipart("alternative")
  msg['Subject'] = 'Ghent Dog Park: Rain Forecast Update'
  msg['From'] = get_ssm_parameters("/GhentDogPark/Weather/EmailFrom")
  msg['To'] = get_ssm_parameters("/GhentDogPark/Weather/EmailTo")

  # Accumulated rain
  rain_accumulation = float(get_ssm_parameters("/GhentDogPark/Weather/RainAccumulation"))
  rain_dryingfactor = float(get_ssm_parameters("/GhentDogPark/Weather/RainDryingFactor"))
  rain_maxallowed = float(get_ssm_parameters("/GhentDogPark/Weather/RainMaxAllowed"))

  # Enter your OpenWeatherMap API key here
  api_key = get_ssm_parameters("/GhentDogPark/Weather/APIKey")

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
  text = "The following rain conditions are expected:\n"
  html = "<html>\n<head></head>\n<body>The following rain conditions are expected\n"

  # Now x contains list of nested dictionaries
  # "404" means city is not found
  # "401" means API key is invalid
  if r["cod"] != "404" and r["cod"] != "401":

    for x in r["list"]:

      desc = x["weather"][0]["description"]

      dt = x["dt_txt"]

      if "3h" in x["rain"].keys():
        rain = float(x["rain"]["3h"])
      else:
        rain = 0

      # Accumulate rain
      rain_accumulation += rain

      # Write line of output
      text += "At %s: rain = %.2f mm, accum. %.2f mm (%s)\n" % (str(dt), rain, rain_accumulation, desc)
      html += "<p>At %s: rain = %.2f mm, accum. %.2f mm (%s)</p>\n" % (str(dt), rain, rain_accumulation, desc)

      # Too wet?
      if rain_accumulation > rain_maxallowed:
        text += "TOO WET, over %.2f mm\n" % rain_maxallowed
        html += "<p><b>TOO WET, over %.2f mm</b></p>\n" % rain_maxallowed

      # Drying factor
      rain_accumulation -= rain_dryingfactor
      if rain_accumulation < 0:
        rain_accumulation = 0

  # HTML footer
  html += "</body>\n</html>\n"

  # Record the MIME types of both parts - text/plain and text/html
  part1 = MIMEText(text, 'plain')
  part2 = MIMEText(html, 'html')

  # Attach parts into message container
  msg.attach(part1)
  msg.attach(part2)

  # Add attachments
  attachments = None
  for attachment in attachments or []:
    with open(attachment, 'rb') as f:
      part = MIMEApplication(f.read())
      part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
      msg.attach(part)

  # Print the message
  print(msg)

  # Send the message via AWS SES
  ses = boto3.client('ses', 'us-east-1')
  response = ses.send_raw_email(
      Source = msg['From'],
      Destinations = [msg['To']],
      RawMessage = {'Data': msg.as_string()}
  )

if __name__ == "__main__":
  lambda_handler()
