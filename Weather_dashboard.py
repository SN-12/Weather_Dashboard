import xml.etree.ElementTree as ET
import paho.mqtt.client as paho

def get_CurrentMetrics(XMLFile):
    """
    Extract metrics from "Current Conditions" section

    input: weather.xml
    output: string containing Temperature,Humidity and Pressure
    """
    mytree = ET.parse(XMLFile)
    myroot = mytree.getroot()
    current_metrics = ""
    for x in myroot.findall('{http://www.w3.org/2005/Atom}entry'):
        # faghat tage sumaray ro mikhanad
        for y in x.findall('{http://www.w3.org/2005/Atom}summary'):
            if y.text.find('Temperature') != -1:
                current_metrics = y.text
                return current_metrics
    return current_metrics


def get_StrSlic(str,strFlag1, strFlag2):
    """
    Returns the value between strFlag1 and strFlag2 in str
    """
    start = str.find(strFlag1)
    start += len(strFlag1)
    end = str.find(strFlag2, start)
    return float(str[start:end])


def get_TempPreHum(s):
    """
    input: string containing Temperature,Humidity and Pressure
    output: tuple Temperature,Humidity and Pressure
    """
    Temperature = get_StrSlic(s, r"<b>Temperature:</b>", r"&deg;")
    Pressure = get_StrSlic(s, r"<b>Pressure / Tendency:</b>", r"kPa")
    Humidity= get_StrSlic(s, r"<b>Humidity:</b>", r"%")
    return (Temperature , Pressure, Humidity)


def publishOnMqqr(tph_tuple):
    """
    input:  tuple Temperature,Humidity and Pressure
    output: publish on MQTT
    """
    broker = 'broker.mqttdashboard.com'
    port = 1883
    client1 = paho.Client("control1")
    topic = 'weather-8d82995e-acd3-43cc-8084-c9f516288088'
    client1.connect(broker, port)  # establish connection
    metricToSent = f'T:{tph_tuple[0]:.2f}\nH:{tph_tuple[2]:.2f}\nP:{tph_tuple[1]:.2f}'
    print(metricToSent)
    metricToSent = f'T:{tph_tuple[0]:.2f}'
    ret = client1.publish(topic, metricToSent)  # publish
    metricToSent = f'H:{tph_tuple[2]:.2f}'
    ret = client1.publish(topic, metricToSent)  # publish
    metricToSent = f'P:{tph_tuple[1]:.2f}'
    ret = client1.publish(topic, metricToSent)  # publish


def loadRSS():
    """
    Read the url and save in an xml file

    Input: https://meteo.gc.ca/rss/city/qc-147_e.xml
    Output: weather.xml
    """
    import requests
    url = 'https://meteo.gc.ca/rss/city/qc-147_e.xml'
    resp = requests.get(url)
    XMLFile = 'weather.xml'
    with open(XMLFile, 'wb') as f:
        f.write(resp.content)
    return XMLFile


if __name__ == '__main__':

    XMLFile = loadRSS()
    raw_metrics = get_CurrentMetrics(XMLFile)
    TempPreHum_tuple = get_TempPreHum(raw_metrics)
    publishOnMqqr(TempPreHum_tuple)