import subprocess
import traceback
import smtplib
import sys
import os
from email.message import EmailMessage


def send_email(message, node, from_addr, to_addr, password):
    """ Sends email """

    msg = EmailMessage()
    msg['Subject'] = 'Wifi stat failure'
    msg['From'] = from_addr
    msg['To'] = to_addr

    msg.set_content('Wifi stat failure on node: {0}\n\n'
                    'Error msg: {1}'.format(node, message))

    with smtplib.SMTP('smtp.office365.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(from_addr, password)
        smtp.send_message(msg)
    return None


def run_iwconfig(interface):
    """ Gathers interface stats using iwconfig command """

    return subprocess.run(['iwconfig', '{0}'.find(interface)], capture_output=True, text=True).stdout


def get_rx_signal(interface):
    """ Gets rssi from rx_signal file """

    file_path = os.path.join('proc', 'net', 'rtl88x2bu', interface, 'rx_signal')
    return subprocess.run(['cat', file_path], capture_output=True, text=True).stdout

if __name__ == '__main__':
    # sys args: first arg: interface, second arg: name to assign to this node

    try:
        if len(sys.argv) < 3:
            raise ValueError('Please pass wifi interface name and node name')

        iface_stats = run_iwconfig(sys.argv[1])
        rx_signal_stats = get_rx_signal(sys.argv[1])

        # Parse the output
        freq = iface_stats[iface_stats.find('Frequency'): iface_stats.find('GHz', iface_stats.find('Frequency'))].split(':')[-1]
        print('wifi_frequency{node="{0}",device="{1}"} {2}'.format(sys.argv[2], sys.argv[1], freq))

        link_quality = iface_stats[iface_stats.find('Link Quality'): iface_stats.find('Signal', iface_stats.find('Link Quality'))].split('=')[-1]
        print('wifi_link_quality{node="{0}",device="{1}"} {2}'.format(sys.argv[2], sys.argv[1], link_quality))

        signal_level = iface_stats[iface_stats.find('Signal level'): iface_stats.find('Noise', iface_stats.find('Signal level'))].split('=')[-1]
        print('wifi_signal_level{node="{0}",device="{1}"} {2}'.format(sys.argv[2], sys.argv[1], signal_level))

        noise_level = iface_stats[iface_stats.find('Noise level'): iface_stats.find('\n', iface_stats.find('Noise level'))].split('=')[-1]
        print('wifi_noise_level{node="{0}",device="{1}"} {2}'.format(sys.argv[2], sys.argv[1], noise_level))

        rssi = rx_signal_stats[rx_signal_stats.find('rssi'): rx_signal_stats.find('\n', rx_signal_stats.find('rssi'))].split(':')[-1]
        print('wifi_rssi_level{node="{0}",device="{1}"} {2}'.format(sys.argv[2], sys.argv[1], rssi))
    except Exception as err:
        print('Unexpected error')
        print(traceback.format_exc())
        print('sending email notification')
        send_email(str(traceback.format_exc()), sys.argv[2],
                   os.environ.get('EMAIL_ADDRESS'), os.environ.get('EMAIL_ADDRESS'), os.environ.get('EMAIL_PASSWORD'))


