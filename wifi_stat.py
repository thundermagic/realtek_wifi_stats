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

    return subprocess.run(['iwconfig', '{0}'.format(interface)], capture_output=True, text=True).stdout


def get_rx_signal(interface):
    """ Gets rssi from rx_signal file """

    file_path = '/' + os.path.join('proc', 'net', 'rtl88x2bu', interface, 'rx_signal')
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
        freq = 'wifi_frequency[node="{0}",device="{1}"] {2}'.format(sys.argv[2].strip(), sys.argv[1].strip(), int(float(freq.strip()) * 1000000000))
        print(freq.replace('[', '{').replace(']', '}'))

        bit_rate = iface_stats[iface_stats.find('Bit Rate'): iface_stats.find('Mb/s', iface_stats.find('Bit Rate'))].split(':')[-1]
        bit_rate = 'wifi_bit_rate[node="{0}",device="{1}"] {2}'.format(sys.argv[2].strip(), sys.argv[1].strip(), bit_rate.strip())
        print(bit_rate.replace('[', '{').replace(']', '}'))

        link_quality = iface_stats[iface_stats.find('Link Quality'): iface_stats.find('Signal', iface_stats.find('Link Quality'))].split('=')[-1]
        link_quality = 'wifi_link_quality[node="{0}",device="{1}"] {2}'.format(sys.argv[2].strip(), sys.argv[1].strip(), link_quality.split('/')[0])
        print(link_quality.replace('[', '{').replace(']', '}'))

        signal_level = iface_stats[iface_stats.find('Signal level'): iface_stats.find('Noise', iface_stats.find('Signal level'))].split('=')[-1]
        signal_level = 'wifi_signal_level[node="{0}",device="{1}"] {2}'.format(sys.argv[2].strip(), sys.argv[1].strip(), signal_level.split('/')[0])
        print(signal_level.replace('[', '{').replace(']', '}'))

        noise_level = iface_stats[iface_stats.find('Noise level'): iface_stats.find('\n', iface_stats.find('Noise level'))].split('=')[-1]
        noise_level = 'wifi_noise_level[node="{0}",device="{1}"] {2}'.format(sys.argv[2].strip(), sys.argv[1].strip(), noise_level.split('/')[0])
        print(noise_level.replace('[', '{').replace(']', '}'))

        rssi = rx_signal_stats[rx_signal_stats.find('rssi'): rx_signal_stats.find('\n', rx_signal_stats.find('rssi'))].split(':')[-1]
        rssi = 'wifi_rssi_level[node="{0}",device="{1}"] {2}'.format(sys.argv[2].strip(), sys.argv[1].strip(), rssi)
        print(rssi.replace('[', '{').replace(']', '}'))
    except Exception as err:
        print('Unexpected error')
        print(traceback.format_exc())
        print('sending email notification')
        send_email(str(traceback.format_exc()), sys.argv[2],
                   os.environ.get('EMAIL_ADDRESS'), os.environ.get('EMAIL_ADDRESS'), os.environ.get('EMAIL_PASSWORD'))


