from flask import Flask, render_template
import requests as r
import os

app = Flask(__name__)
#set the ip address of the inverter on your local network
app.config['inverter_address'] = os.environ.get('INVERTER_ADDRESS')


class InverterRequest(object):

    def __init__(self, ip_address, endpoint, extension, **kwargs):
        self.s = r.session()
        self.payload = dict(**kwargs)
        self.inverter_endpoint = '/solar_api/v1/'
        self.inverter_request = r.Request('GET', 'http://{}{}{}.{}'.format(ip_address, self.inverter_endpoint, endpoint,
                                                                           extension),
                                          params=self.payload).prepare()
        self.my_url = self.inverter_request.url

    def print_url(self):
        return print(self.my_url)

    def make_request(self):
        self.response = self.s.send(self.inverter_request)

    def print_response_body(self):
        self.make_request()
        self.body = self.response.text
        return print(self.body)

    def get_data(self):
        self.print_url()
        self.print_response_body()

    def return_data_json(self):
        self.make_request()
        return self.response.json()


class TempertatureRequest(InverterRequest):

    def __init__(self, domain, endpoint, ):
        super(TempertatureRequest, self).__init__(domain, endpoint, '')
        self.temperature_endpoint = ''
        self.temperature_request = r.Request('GET', 'http://{}/{}'.format(domain, endpoint)).prepare()

    def make_request(self):
        self.response = self.s.send(self.temperature_request)


def scale_number(value, field_info):
    """Function takes a value to scale and the map of fields which has a key called "divisor" which defines how ot scale the value"""
    if "divisor" in field_info:
        #Don't divide by zero!
        if value == 0:
            pass
        else:
            value /= field_info["divisor"]
    return value

@app.route('/')
def hello_world():
    return "hello world"


@app.route('/get-power-flow')
def get_latest_power_data():
    x = InverterRequest(app.config['inverter_address'], 'GetPowerFlowRealtimeData', 'fcgi')
    return x.return_data_json()


@app.route('/get-meter-flow')
def get_latest_meter_data():
    x = InverterRequest(app.config['inverter_address'], 'GetMeterRealtimeData', 'cgi', Scope='System')
    return x.return_data_json()


@app.route('/get-inverter-data')
def get_lastest_inverter_data():
    x = InverterRequest(app.config['inverter_address'], 'GetInverterRealtimeData', 'cgi', Scope='System')
    return x.return_data_json()


@app.route("/get-meter-readings")
def get_meter_readings():
    x = InverterRequest(app.config['inverter_address'], 'GetPowerFlowRealtimeData', 'fcgi')
    response = x.return_data_json()
    inverter_data = response['Body']['Data']['Site']
    field_map = {"P_PV": {"name": "Current Solar Production (kilowatts)", "format": "{:.1f}kW", "divisor": 1000,
                          "color": "green"},
                 "P_Load": {"name": "Current Household Consumption (kilowatts)", "format": "{:.1f}kW", "divisor": 1000,
                            "color": "blue"},
                 "P_Grid": {"name": "Current Power Draw from Grid (kilowatts)", "format": "{:.1f}kW", "divisor": 1000},
                 "color": "red",
                 "E_Day": {"name": "Total Solar Production Today (kilowatt hours)", "format": "{:.1f}kWhr",
                           "divisor": 1000},
                 "E_Total": {"name": "Total Solar Production Since Installation (kilowatt hours)",
                             "format": "{:.1f}kWhr",
                             "divisor": 1000},
                 "E_Year": {"name": "Total Solar Production This Year (kilowatt hours)", "format": "{:.1f}kWhr",
                            "divisor": 1000},
                 "rel_Autonomy": {"name": "Percentage of Household Consumption Supplied From Solar",
                                  "format": "{:.2f}%"},
                 "rel_SelfConsumption": {"name": "Percentage of Solar Production Consumed", "format": "{:.2f}%"},
                 "P_Akku": {"name": "Battery Accumulation (watts)", "format": "{}"}}

    formatted_data = {}
    for key, value in inverter_data.items():
        field_info = field_map.get(key, {"name": key, "format": "{}"})
        scaled_value = scale_number(value, field_info)
        format_option = field_info["format"]
        formatted_value = format_option.format(scaled_value)
        formatted_data[field_info["name"]] = formatted_value
    return render_template('template.html', data=formatted_data)


# TODO add colours to the template

@app.route('/get-temp-data')
def get_latest_temp_data():
    x = TempertatureRequest('raspberrypi.local', 'users')
    return x.return_data_json()


@app.route("/get-all-readings")
def get_all_readings():
    inverter_response = InverterRequest(app.config['inverter_address'], 'GetPowerFlowRealtimeData', 'fcgi')
    inverter_data = inverter_response.return_data_json()
    temp_response = TempertatureRequest('raspberrypi.local', 'users')
    temp_data = temp_response.return_data_json()
    return render_template('template.html',
                           inverter_data=inverter_data['Body']['Data']['Site'], temperature_data=temp_data['feeds'])
