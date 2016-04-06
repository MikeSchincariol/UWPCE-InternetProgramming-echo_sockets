import socket
import sys
import select


def server(log_buffer=sys.stderr):
    # set an address for our server
    address = ('127.0.0.1', 20000)  # Changed to 20000 as I already have webmin on 10000

    # TODO: Replace the following line with your code which will instantiate
    #       a TCP socket with IPv4 Addressing, call the socket you make 'sock'
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_STREAM,
                         socket.IPPROTO_TCP)

    # TODO: You may find that if you repeatedly run the server script it fails,
    #       claiming that the port is already used.  You can set an option on
    #       your socket that will fix this problem. We DID NOT talk about this
    #       in class. Find the correct option by reading the very end of the
    #       socket library documentation:
    #       http://docs.python.org/3/library/socket.html#example
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # log that we are building a server
    print("making a server on {0}:{1}".format(*address), file=log_buffer)

    # TODO: bind your new sock 'sock' to the address above and begin to listen
    #       for incoming connections
    sock.bind(address)
    sock.listen(1)

    # Make up lists of sockets (file descriptors) to watch. Then,
    # have the select module IO mux between them.
    readers = [sock]
    writers = []
    errored = []

    # Create a dictionary, keyed by the sockets file-descritor number,
    # to hold the chunk caches for each connection.
    data_cache = {}

    try:
        print('waiting for a connection', file=log_buffer)
        while True:

            #Wait indefinitely for something to happen. To quit,
            #the user will have to issue a keyboard interrupt.
            readers_rdy, writers_rdy, errored_rdy = select.select(readers, writers, errored)
            print('Found some work to do...')


            # Examine the readers list to identify when new connections are possible
            # or when it is possible to read data.
            for item in readers_rdy:
                # If the socket is our server socket, then, we have a new
                # connection ready to accept. In this case, add the newly
                # connected socket to the list of items that can read
                # and make a entry in the cache for it to use to buffer the
                # characters being echoed.
                # Otherwise, the item is a previously established connection
                # that has data that needs to be read out into its cache.
                if item == sock:
                    conn, addr = sock.accept()
                    print('connection - {0}:{1}'.format(*addr), file=log_buffer)
                    readers.append(conn)
                    data_cache[conn.fileno()] = ""
                else:
                    # Receive 16 bytes of data from the client. Store
                    # the data received in the data cache entry for the
                    # socket.
                    data_cache[item.fileno()] = conn.recv(16)
                    print('From: {0}  Received "{1}"'.format(item.getpeername(),
                                                             data_cache[item.fileno()].decode('utf8')))
                    if data_cache[item.fileno()] == b'':
                        # If no data was received, then, this socket is closing.
                        # In this case, remove the socket from the list of sockets
                        # to watch for reading and don't add it to the list of
                        # sockets to watch for writing. Shutdown our end.
                        print(
                            'Echo complete. Closing client connection to {0}'.format(item.getpeername()), file=log_buffer
                        )
                        readers.remove(item)
                        del data_cache[item.fileno()]
                        item.shutdown(socket.SHUT_RDWR)
                        item.close()
                    else:
                        # Remove the socket from the list of sockets to check
                        # for reading until the data just received is echo'd back
                        # out.
                        readers.remove(item)
                        writers.append(item)

            # Examine the writers list to identify when it is possible to send data
            for item in writers_rdy:
                # TODO: Send the data you received back to the client, log
                # the fact using the print statement here.  It will help in
                # debugging problems.
                item.send(data_cache[item.fileno()])
                print('To: {0}  Sent "{1}"'.format(item.getpeername(),
                                                   data_cache[item.fileno()].decode('utf8')))
                # Remove the socket from the writers list and go back to waiting
                # for more data to echo.
                readers.append(item)
                writers.remove(item)

            # Examine the errored list to identify when...
            for item in errored_rdy:
                pass

    except KeyboardInterrupt:
        # TODO: Use the python KeyboardInterrupt exception as a signal to
        #       close the server socket and exit from the server function.
        #       Replace the call to `pass` below, which is only there to
        #       prevent syntax problems

        # Close down the server socket and any client sockets that haven't
        # completed yet.
        for item in readers[:]:
            item.shutdown(socket.SHUT_RDWR)
            item.close()
            print(
                'echo complete, client connection to {0} closed'.format(item.getpeername()), file=log_buffer
            )
        for item in writers[:]:
            item.shutdown(socket.SHUT_RDWR)
            item.close()
            print(
                'echo complete, client connection to {0} closed'.format(item.getpeername()), file=log_buffer
            )
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        print('quitting echo server', file=log_buffer)


if __name__ == '__main__':
    server()
    sys.exit(0)
