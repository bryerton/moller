import zmq
import struct

MAX_DELAY_VALUE = 511

CLOCKS_TO_NANOSECONDS = 4  # There are 4ns per clock

MIN_CONVERT_CLOCKS = 17
MAX_CONVERT_CLOCKS = 255

ADC_DIVISOR = 1
ADC_CONVERT_CLOCKS = int(MIN_CONVERT_CLOCKS*2)
ADC_CONVERT_TIME = (ADC_CONVERT_CLOCKS * CLOCKS_TO_NANOSECONDS)
ADC_SAMPLE_RATE = ((1.0/(ADC_CONVERT_TIME / 1000000000)) / ADC_DIVISOR) # Dividing the sample rate by 2 to prevent errors in transmission
ADC_PACKET_SIZE = (0x2004)
ADC_SAMPLES_SIZE = ADC_PACKET_SIZE - 4

ADC_MAX_VOLTAGEpp = 4.096
ADC_RESOLUTION = ADC_MAX_VOLTAGEpp / pow(2, 18)
VOLT_MAX = (ADC_MAX_VOLTAGEpp / 2)
VOLT_MIN = -(ADC_MAX_VOLTAGEpp / 2)

def ctrl_init(ip, port=5555):
    try:
        context = zmq.Context()
        url = "tcp://" + str(ip) + ":" + str(port)
        #  Socket to talk to server
        socket = context.socket(zmq.REQ)
        socket.connect(url)
    except zmq.ZMQError:
        # No message received, keep looping
        socket = None

    return socket

def data_init(ip, port=5556):
    try:
        context = zmq.Context()
        url = "tcp://" + str(ip) + ":" + str(port)
        #  Socket to talk to server
        socket = context.socket(zmq.SUB)
        socket.setsockopt_string( zmq.SUBSCRIBE, "ADC")
        socket.connect(url)

    except zmq.ZMQError:
        # No message received, keep looping
        socket = None

    return socket

def write_msg(socket, addr, data):
    msg = struct.pack("<III", ord('w'), int(addr / 4), data)
    socket.send(msg, 0)
    resp = socket.recv()
    msg = struct.unpack_from("<I", resp, 0)
    if(msg[0] == 114):
        msg = struct.unpack_from("<I", resp, 4)
        return msg[0]
    else:
        raise("Write Error")

def read_msg(socket, addr):
    msg = struct.pack("<III", ord('r'), int(addr / 4), 0)
    socket.send(msg, 0)
    resp = socket.recv()
    msg = struct.unpack_from("<I", resp, 0)
    if(msg[0] == 114):
        return struct.unpack_from("<I", resp, 4)[0]
    else:
        raise("Read Error")

def read_samples(socket, num_samples_to_read, convert_time, packet_size = 0x4000, zero_ts = False):
    samples = []
    sample_count = 0
    ts = 0

    buffer = bytearray()

    prev_pkt = None

    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    if convert_time < MIN_CONVERT_CLOCKS:
        convert_time = MIN_CONVERT_CLOCKS

    if convert_time > MAX_CONVERT_CLOCKS:
        convert_time = MAX_CONVERT_CLOCKS

    while(sample_count < num_samples_to_read):
        res = poller.poll(timeout=5000)
        if(res):
            msg = socket.recv_multipart(zmq.NOBLOCK)
            num_words, num_pkt, id, pkt_ts = struct.unpack_from("<HIxBQ", msg[1], 0)
            buffer = buffer + msg[1][16:]
            sample_count = sample_count + (packet_size - 4)
            if(not zero_ts and prev_pkt == None):
                # Unpack message
                ts = pkt_ts

            prev_pkt = num_pkt
        else:
            return None


    for n in range(int(num_samples_to_read/2)):
        ch1, ch2 = struct.unpack_from("<ii", buffer, (n * 8))

        ch1_data = ch1 >> 14
        ch1_sel = ch1 & 0xF

        ch2_data = ch2 >> 14
        ch2_sel = ch2 & 0xF

        stream_div = ((ch1 >> 4) & 0x7F) + 1

        samples.append([ts, ch2_sel, ch2_data * ADC_RESOLUTION])
        ts = ts + (convert_time * CLOCKS_TO_NANOSECONDS * stream_div)

        samples.append([ts, ch1_sel, ch1_data * ADC_RESOLUTION])
        ts = ts + (convert_time * CLOCKS_TO_NANOSECONDS * stream_div)

    return samples
