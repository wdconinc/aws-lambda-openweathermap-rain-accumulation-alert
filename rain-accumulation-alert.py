# Python program to find weather details of Norfolk, VA, USA
# using OpenWeatherMap API, integrate the predicted rain fall,
# and determine periods of Ghent Dog Park wetness

import boto3, json, smtplib
from botocore.vendored import requests
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

import pytz
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# handler method
def lambda_handler(event = None, context = None, email = False):

  # Connect to AWS SSM Parameter Store
  ssm = boto3.client('ssm', 'us-east-1')
  def get_ssm_parameters(name):
    response = ssm.get_parameters(Names = [name])
    for parameter in response['Parameters']:
      return parameter['Value']

  # Create a text/plain message
  msg = MIMEMultipart("related")
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
  tzinfo = pytz.timezone('US/Eastern')

  # complete_url variable to store complete url address
  complete_url = base_url + "appid=" + api_key + "&q=" + city_name

  # get method of requests module return response object
  response = requests.get(complete_url)

  # json method of response object convert json format data into python format data
  r = response.json()

  # Start with empty email message
  text = "The following rain conditions are expected:\n"
  html = "<html>\n<head></head>\n<body><img src=\"cid:rain-accumulation\">\n<p>The following rain conditions are expected:</p>"

  # Now x contains list of nested dictionaries
  # "404" means city is not found
  # "401" means API key is invalid
  if r["cod"] != "404" and r["cod"] != "401" and r["cnt"] > 0:

    # Start with empty series
    cnt = r["cnt"]
    date_array = np.ndarray((cnt,), dtype = 'datetime64[s]')
    rain_interval_array = np.ndarray((cnt,), dtype = float)
    rain_accumulation_array = np.ndarray((cnt,), dtype = float)

    # Loop over forecast
    for i,x in enumerate(r["list"]):

      # Get date time
      dt = 0
      if "dt" in x.keys():
        dt = x["dt"]
      # Store date time
      dt = datetime.fromtimestamp(dt, tzinfo)
      date_array[i] = dt

      # Get rain interval
      rain_interval = 0
      if "rain" in x.keys():
        rain =  x["rain"]
        if "3h" in rain.keys():
          rain_interval = float(rain["3h"])
      # Store rain interval
      rain_interval_array[i] = rain_interval

      # Accumulate rain
      rain_accumulation += rain_interval
      rain_accumulation_array[i] = rain_accumulation

      # Get description
      desc = ""
      if "weather" in x.keys():
        weather =  x["weather"][0]
        if "description" in weather.keys():
          desc = weather["description"]

      # Write line of output
      text += "At %s: rain = %.2f mm, accum. %.2f mm (%s)" % (dt.strftime("%Y-%m-%d %I:%M %p"), rain_interval, rain_accumulation, desc)
      html += "<p>At %s: rain = %.2f mm, accum. %.2f mm (%s)" % (dt.strftime("%Y-%m-%d %I:%M %p"), rain_interval, rain_accumulation, desc)

      # Too wet?
      if rain_accumulation > rain_maxallowed:
        text += " TOO WET, over %.2f mm\n" % rain_maxallowed
        html += " <b>TOO WET, over %.2f mm</b></p>\n" % rain_maxallowed
      else:
        text += "\n"
        html += "</p>\n"

      # Drying factor
      rain_accumulation -= rain_dryingfactor
      if rain_accumulation < 0:
        rain_accumulation = 0

  # HTML footer
  html += "</body>\n</html>\n"

  # Create time graph
  with plt.xkcd():
    fig, ax = plt.subplots(figsize = (6, 4), dpi = 150)
    ax.fill_between(date_array, rain_accumulation_array, color = 'blue')
    ax.plot(date_array, rain_interval_array, 'ob')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.set_ylabel('rainfall in mm')
    ax.set_title('Rain forecast for Ghent Dog Park')

    # Rotate and align the tick labels so they look better
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %b %d'))
    fig.autofmt_xdate()

    #plt.annotate(
    #    'Close park at %s' % (np.datetime_as_string(date_array[20], timezone='local')),
    #    xy = (date_array[20], 1), arrowprops = dict(arrowstyle = '->'), xytext = (date_array[15], +10))

    # Save figure
    fig.savefig('/tmp/rain-accumulation.png')

  # Record the MIME types of both parts - text/plain and text/html
  part1 = MIMEText(text, 'plain')
  part2 = MIMEText(html, 'html')

  # Attach parts into message container
  msg.attach(part1)
  msg.attach(part2)

  # Attach image
  fp = open('/tmp/rain-accumulation.png', 'rb')
  image = MIMEImage(fp.read())
  fp.close()
  image.add_header('Content-ID', '<rain-accumulation>')
  msg.attach(image)

  # Send the message via AWS SES
  if (email):
    ses = boto3.client('ses', 'us-east-1')
    response = ses.send_raw_email(
        Source = msg['From'],
        Destinations = [msg['To']],
        RawMessage = {'Data': msg.as_string()}
    )

if __name__ == "__main__":
  lambda_handler(email = False)
