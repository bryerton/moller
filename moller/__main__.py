#!/bin/python

import signal
import argparse
import sys
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from threading import Thread
from . import ctrl as moller_ctrl
from . import util as moller_util
from . import discovery as util_discover
from . import __version__ as __version__

VERSION = __version__

"""
CTRL+C Interrupt Handler
"""
class GracefulExiter():

    def __init__(self):
        self.state = False
        signal.signal(signal.SIGINT, self.change_state)

    def change_state(self, signum, frame):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.state = True

    def exit(self):
        return self.state

flag = GracefulExiter()

def arg_write(args):
    socket = moller_ctrl.ctrl_init(args.ip)
    resp = moller_ctrl.write_msg(socket, int(args.addr, 0), int(args.data, 0))
    print(hex(resp))
    print(str(int(resp)))

def arg_read(args):
    socket = moller_ctrl.ctrl_init(args.ip)
    resp = moller_ctrl.read_msg(socket, int(args.addr, 0))
    print('0x{0:08X}'.format(int(resp)) + " [" + str(int(resp)) + "]")

def arg_status(args):
    socket = moller_ctrl.ctrl_init(args.ip)

    resp = moller_ctrl.read_msg(socket, 0x40)
    print('Register Revision: ' + str(int(resp)))

    resp = moller_ctrl.read_msg(socket, 0x4C)
    print('Frequency TD: ' + str(int(resp)))

    resp = moller_ctrl.read_msg(socket, 0x50)
    print('Frequency Oscillator: ' + str(int(resp)))

    resp = moller_ctrl.read_msg(socket, 0x54)
    print('Frequency SOM0: ' + str(int(resp)))

    resp = moller_ctrl.read_msg(socket, 0x58)
    print('Frequency SOM1: ' + str(int(resp)))

    resp = moller_ctrl.read_msg(socket, 0x5C)
    print("Clock Status: ", end="")
    if resp & 0x1:
        print("PLL1 & PLL2 locked")
    else:
        print("PLL1 & PLL2 not locked")

    print("Clock Status: ", end="")
    if resp & 0x2:
        print("Holdover")
    else:
        print("Not in holdover")
    print('Clock Status: ' + str(int(resp)))

    print("ADC Error Counter Results")
    for n in range(16):
        resp = moller_ctrl.read_msg(socket, 0x0 + (n*4))
        dco_errors = int(resp & 0xFFFF0000) >> 16
        print('   ' + str(n) + '\tDCO: 0x{0:04X}'.format(dco_errors) + " [" + str(dco_errors) + "]", end='')
        pat_errors = int(resp & 0x0000FFFF)
        print('\tPattern: 0x{0:04X}'.format(pat_errors) + "[" + str(pat_errors) + "]")

    print("ADC Delay In")
    for n in range(16):
        resp = moller_ctrl.read_msg(socket, 0x60 + (n*4))
        print('   ' + str(n) + '\t0x{0:08X}'.format(int(resp)) + " [" + str(int(resp)) + "]")

    print("ADC Delay Out")
    for n in range(16):
        resp = moller_ctrl.read_msg(socket, 0xA0 + (n*4))
        print('   ' + str(n) + '\t0x{0:08X}'.format(int(resp)) + " [" + str(int(resp)) + "]")

    resp = moller_ctrl.read_msg(socket, 0xE0)
    print('ADC FIFO Count: ' + str(int(resp)))

    resp = moller_ctrl.read_msg(socket, 0xE4)
    print('RUN FIFO Count: ' + str(int(resp)))

    resp = moller_ctrl.read_msg(socket, 0xE8)
    print('TI FIFO Count: ' + str(int(resp)))


def arg_data(args):
    ctrl_socket = moller_ctrl.ctrl_init(args.ip)

    moller_ctrl.write_msg(ctrl_socket, 0x44, 0x80002000)
    moller_ctrl.write_msg(ctrl_socket, 0x48, 0x80000000)

    # The streamer always returns at least 2, if you give it 1, it will return zero, so bump upwards
    args.samples = int(args.samples)
    if args.samples % 2 != 0:
        args.samples = args.samples + 1

    data_socket = moller_ctrl.data_init(args.ip)
    resp = moller_ctrl.read_samples(data_socket, num_samples_to_read=int(args.samples), convert_time=int(args.rate))
    if(resp is not None):
        print("Timestamp(ns),Channel,Data")
        for line in resp:
            print(str(line[0]) + "," + str(line[1]) + "," + str(line[2]))
    else:
        print("Timeout attempting to get data")

def arg_plot(args):

    graph_data = []
    for n in range(16):
        graph_data.append({"ts": [], "x": []})

    lines = []

    if(args.channel != "all"):
        args.channel = int(args.channel)
        if args.channel < 1:
            args.channel = 1

        elif args.channel > 16:
            args.channel = 16

    ctrl_socket = moller_ctrl.ctrl_init(args.ip)

    def get_data(graph_data):

        data = {'time': [], 'samples': []}

        ch = 0
        if(args.channel != "all"):
            ch = args.channel - 1
            ch = 0

        moller_ctrl.write_msg(ctrl_socket, 0x44, 0x80000000 | (ch << 16) | (ch << 20) | moller_ctrl.ADC_PACKET_SIZE)
        moller_ctrl.write_msg(ctrl_socket, 0x48, 0x80000000)

        while not flag.exit():

            data_socket = moller_ctrl.data_init(args.ip)

            resp = moller_ctrl.read_samples(data_socket, moller_ctrl.ADC_SAMPLES_SIZE, moller_ctrl.ADC_CONVERT_TIME, moller_ctrl.ADC_PACKET_SIZE, True)
            if(resp == None):
                break

            sample_data = []
            for sample in resp:
                sample_data.append(sample[2])

            graph_data[ch]['x'] = np.array(sample_data) * moller_ctrl.ADC_RESOLUTION

            if(args.channel == "all"):
                ch = ch + 1
                if ch == 16:
                    ch = 0

                moller_ctrl.write_msg(ctrl_socket, 0x44, 0x80000000 | (ch << 16) | (ch << 20) | moller_ctrl.ADC_PACKET_SIZE)

            data_socket.close()

            time.sleep(0.001)

    # This function is called periodically from FuncAnimation
    def animate(i, graph_data):
        # Draw x and y lists
        if args.channel == "all":
            for i in range(16):
                lines[i].set_ydata(graph_data[i]["x"])
        else:
            lines[0].set_ydata(graph_data[0]["x"])
        return lines

    def init_plot():
        max_samples = moller_ctrl.ADC_SAMPLES_SIZE
        for idx, a in enumerate(ax):
            if args.channel == "all":
                a.set_title(str(idx + 1), x=0.1, y=0.9)
                a.set_xticks([max_samples / 2, max_samples])
            else:
                a.set_title("Channel " + str(args.channel))

            a.set_yticks([moller_ctrl.VOLT_MIN, moller_ctrl.VOLT_MIN/2, 0, moller_ctrl.VOLT_MAX/2, moller_ctrl.VOLT_MAX])
            a.set_xlim([0, max_samples])
            a.set_ylim(moller_ctrl.VOLT_MIN, moller_ctrl.VOLT_MAX)
            a.grid(True)

        return lines

    max_samples = moller_ctrl.ADC_SAMPLES_SIZE

    fig = plt.figure(figsize=(160, 90))

    if args.channel == "all":
        gs = fig.add_gridspec(2, 8, wspace=0.0, hspace=0.05)
        px = gs.subplots(sharex=True)
        ax = [
            px[0, 0],
            px[0, 1],
            px[0, 2],
            px[0, 3],
            px[0, 4],
            px[0, 5],
            px[0, 6],
            px[0, 7],
            px[1, 0],
            px[1, 1],
            px[1, 2],
            px[1, 3],
            px[1, 4],
            px[1, 5],
            px[1, 6],
            px[1, 7],
        ]
        fig.canvas.manager.set_window_title("All Channels")
        fig.text(0.5, 0.04, "Sample #", ha="center", va="center")
        fig.text(
            0.06, 0.5, "Voltage (V)", ha="center", va="center", rotation="vertical"
        )
    else:
        gs = fig.add_gridspec(1, hspace=0)
        ax = [gs.subplots(sharex=True)]
        fig.canvas.manager.set_window_title("Channel #" + str(args.channel + 1))
        plt.ylabel("Voltage (V)")
        plt.xlabel("Sample #")

    plt.ioff()

    for i in range(16):
        for n in range(max_samples):
            graph_data[i]["ts"].append(n)
            graph_data[i]["x"].append(None)

    # Draw x and y lists
    if args.channel == "all":
        for i in range(16):
            (line0,) = ax[i].plot(graph_data[i]["ts"], graph_data[i]["x"], label="X")

            lines.append(line0)

            # Format plot
            for axs in ax:
                axs.label_outer()

    else:
        (line0,) = ax[0].plot(
            graph_data[0]["ts"], graph_data[0]["x"], label="X"
        )

        lines.append(line0)

        # Format plot
        plt.xlim([0, max_samples])
        plt.grid(True)

    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(
        fig,
        animate,
        init_func=init_plot,
        fargs=(graph_data,),
        interval=200,
        blit=True,
        cache_frame_data=False,
    )

    t = Thread(target=get_data, args=(graph_data,))
    t.start()

    # Blocks until closed
    plt.show()

    # Tell thread to end
    flag.change_state(0, 0)


def arg_align(args):
    ctrl_socket = moller_ctrl.ctrl_init(args.ip)

    pat_map = []
    dco_map = []
    combined_map =[]

    for ch in range(16):
        pat_map.append([])
        dco_map.append([])
        combined_map.append([])


    print("Initial values")
    for ch in range(16):
        result = moller_ctrl.read_msg(ctrl_socket, 0x60 + (ch*4))
        print(hex(result))

    for n in range(moller_ctrl.MAX_DELAY_VALUE+1):

        print("Tap position: " + str(n) + " / " + str(moller_ctrl.MAX_DELAY_VALUE),end='\r')

        # Update delay for each channel
        for ch in range(16):
            moller_ctrl.write_msg(ctrl_socket, 0x60 + (ch*4), n)

        # Clear counters and set to Test Mode
        moller_ctrl.write_msg(ctrl_socket, 0x48, 0xD0000000)
        time.sleep(0.01)
        moller_ctrl.write_msg(ctrl_socket, 0x48, 0xC0000000)

        time.sleep(0.01)

        for ch in range(16):
            result = moller_ctrl.read_msg(ctrl_socket, 0x0 + (ch*4))
            pat_map[ch].append(result & 0xFFFF)
            dco_map[ch].append((result >> 16) & 0xFFFF)
            if(result > 0):
                combined_map[ch].append(1)
            else:
                combined_map[ch].append(0)


    print("                                                                ")

    # Calculate best position for each channel
    print("Calculated values")
    for ch in range(16):
        mid = moller_util.find_mid_of_longest_run(combined_map[ch], 0)
        combined_map[ch] = np.roll(combined_map[ch], -mid)
        moller_ctrl.write_msg(ctrl_socket, 0x60 + (ch*4), mid)
        print(hex(mid))

    # Reset the counters and take it out of test mode
    moller_ctrl.write_msg(ctrl_socket, 0x48, 0x90000000)
    time.sleep(0.01)
    moller_ctrl.write_msg(ctrl_socket, 0x48, 0x80000000)

    # plot
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True)

    ax1.set_title("Test Pattern Errors")
    ax1.set_ylabel("ADC Channel")
    ax1.set_xlabel("Delay Value (tap)")
    ax1.set_yticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16'])
    ax1.grid(visible=True, axis='y')
    im_pat = ax1.imshow(pat_map, interpolation='None', aspect='auto', extent=[0, 512, 0, 16])

    ax2.set_title("DCO Misalignments")
    ax2.set_ylabel("Channel")
    ax2.set_xlabel("Delay Value")
    ax2.set_yticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16'])
    ax2.grid(visible=True, axis='y')
    im_dco = ax2.imshow(dco_map, interpolation='None', aspect='auto', extent=[0, 512, 0, 16])

    ax3.set_title("Combined Errors")
    ax3.set_ylabel("Channel")
    ax3.set_xlabel("Delay Value")
    ax3.set_yticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16'])
    ax3.grid(visible=True, axis='y')
    im_comb = ax3.imshow(combined_map, interpolation='None', aspect='auto', extent=[0, 512, 0, 16])

    # fig.colorbar(im_pat, ax=ax1)
    fig.colorbar(im_comb, ax=ax3)
    fig.tight_layout()
    plt.show()

def arg_discover(args):
    # Load config
    config = util_discover.DiscoveryConfig()

    # Override config with command line arguments

    controller = util_discover.DiscoveryController(config)
    controller.start()

    # while(1):
    #    if flag.exit() or not controller.is_alive():
    #        break
    time.sleep(2)

    controller.stop()

def main():
    prog='moller_ctl'
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument('--version', action='version', version='%(prog)s ' + str(VERSION))
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Increase logging verbosity, can be repeated')
    parser.add_argument('-l', '--log', metavar='file', help='Log to output file')
    parser.add_argument("ip", help="IP address of Moller Integrating ADC")

    cmd_parser = parser.add_subparsers(dest="command", description="Valid subcommands", help=" ")

    read_parser = cmd_parser.add_parser("read")
    read_parser.add_argument("addr")
    read_parser.set_defaults(func=arg_read)

    write_parser = cmd_parser.add_parser("write")
    write_parser.set_defaults(func=arg_write)
    write_parser.add_argument("addr")
    write_parser.add_argument("data")

    data_parser = cmd_parser.add_parser("data")
    data_parser.set_defaults(func=arg_data)
    data_parser.add_argument("samples", default=0, nargs="?")
    data_parser.add_argument("-r", "--rate", default="0")

    status_parser = cmd_parser.add_parser("status")
    status_parser.set_defaults(func=arg_status)

    align_parser = cmd_parser.add_parser("align")
    align_parser.set_defaults(func=arg_align)

    plot_parser = cmd_parser.add_parser("plot")
    plot_parser.set_defaults(func=arg_plot)
    plot_parser.add_argument("channel", default="all", nargs="?")

    args = parser.parse_args()

    if args.ip.lower() == "discover":
        args.func = arg_discover
    elif(args.command == None):
        parser.print_usage()
        sys.exit(0)

    args.func(args)

if __name__ == "__main__":
    main()
