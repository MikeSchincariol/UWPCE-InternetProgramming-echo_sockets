import sys
import socket

def list_services(*ports):
    """
    :param ports: If no ports are listed, provides services names for ports 0 - 1023.
                  If a single port is provided, only the service on that port will be found.
                  If 2, comma separated ports, are provided, then, all service names for
                  all ports between the 2 ports provided will be discovered.
    :return: A list of service names
    """

    # Determine the start and end of the port range to enumerate over
    start_port = 0
    end_port = 1023
    try:
        start_port = int(ports[0])
        if len(ports) > 1:
            end_port = int(ports[1])
        else:
            end_port = start_port
    except TypeError:
        print("The ports provided must be integer values")

    # Confirm the port ranges provided are valid.
    if start_port < 0 or start_port > 65525 or end_port < 0 or end_port > 65535:
        print("The ports provided must be between 0 and 65525")

    # Find service names. If no service is defined/known for a given port,
    # just return an empty string.
    for port in range(start_port, end_port + 1):
        svc_name = ""
        try:
            svc_name = socket.getservbyport(port)
        except OSError:
            # Will get an OSError if there is no service asscociated with the port.
            # This is not fatal.
            pass
        print("PORT: {0:5}  SERVICE: {1:10}".format(port, svc_name))


if __name__ == "__main__":
    list_services(sys.argv)