import pyb
import select
import uasyncio.core

POLLIN = 1
POLLOUT = 2


#class MyEventLoop(asyncio.EventLoop):
    #def time(self):
        #return pyb.millis()

    #def wait(self, delay):
        #log = logging.getLogger("asyncio")
        #log.debug("Sleeping for: %s", delay)
        #start = pyb.millis()
        #while pyb.elapsed_millis(start) < delay:
            #gc.collect()
            #pyb.delay(10)

log = uasyncio.core.log


class PollEventLoop(uasyncio.core.EventLoop):

    def __init__(self):
        uasyncio.core.EventLoop.__init__(self)
        self.poller = select.poll()

    def time(self):
        return pyb.millis()

    def wait(self, delay):
        if __debug__:
            log.debug("epoll.wait(%d)", delay)
        if delay == -1:
            res = self.poller.poll(-1)
        else:
            res = self.poller.poll(delay)
        #log.debug("epoll result: %s", res)
        for cb, ev in res:
            if __debug__:
                log.debug("Calling IO callback: %s%s", cb[0], cb[1])
            cb[0](*cb[1])

    def run_forever(self):
        while True:
            if self.q:
                t, cnt, cb, args = heapq.heappop(self.q)
                if __debug__:
                    log.debug("Next coroutine to run: %s", (t, cnt, cb, args))
#                __main__.mem_info()
                tnow = self.time()
                delay = t - tnow
                if delay > 0:
                    self.wait(delay)
            else:
                self.wait(-1)
                # Assuming IO completion scheduled some tasks
                continue
            if callable(cb):
                cb(*args)
            else:
                delay = 0
                try:
                    if args == ():
                        args = (None,)
                    if __debug__:
                        log.debug("Coroutine %s send args: %s", cb, args)
                    ret = cb.send(*args)
                    if __debug__:
                        log.debug("Coroutine %s yield result: %s", cb, ret)
                    if isinstance(ret, SysCall):
                        arg = ret.args[0]
                        if isinstance(ret, Sleep):
                            delay = arg
                        elif isinstance(ret, IORead):
                            self.add_reader(arg, lambda cb, f: self.call_soon(cb, f), cb, arg)
                            continue
                        elif isinstance(ret, IOWrite):
                            self.add_writer(arg, lambda cb, f: self.call_soon(cb, f), cb, arg)
                            continue
                        elif isinstance(ret, IOReadDone):
                            self.remove_reader(arg)
                        elif isinstance(ret, IOWriteDone):
                            self.remove_writer(arg)
                        elif isinstance(ret, StopLoop):
                            return arg
                    elif isinstance(ret, type_gen):
                        self.call_soon(ret)
                    elif ret is None:
                        # Just reschedule
                        pass
                    else:
                        assert False, "Unsupported coroutine yield value: %r (of type %r)" % (ret, type(ret))
                except StopIteration as e:
                    if __debug__:
                        log.debug("Coroutine finished: %s", cb)
                    continue
                self.call_later(delay, cb, *args)

    def add_reader(self, obj, cb, *args):
        if __debug__:
            log.debug("add_reader%s", (obj, cb, args))
        self.poller.register(obj, POLLIN, (cb, args))

    def remove_reader(self, obj):
        if __debug__:
            log.debug("remove_reader(%s)", obj)
        self.poller.unregister(obj)

    def add_writer(self, obj, cb, *args):
        if __debug__:
            log.debug("add_writer%s", (obj, cb, args))
        self.poller.register(obj, POLLOUT, (cb, args))

    def remove_writer(self, obj):
        if __debug__:
            log.debug("remove_writer(%s)", obj)
        try:
            self.poller.unregister(obj)
        except OSError as e:
            # StreamWriter.awrite() first tries to write to an obj,
            # and if that succeeds, yield IOWrite may never be called
            # for that obj, and it will never be added to poller. So,
            # ignore such error.
            if e.args[0] != errno.ENOENT:
                raise

uasyncio.core._event_loop_class = PollEventLoop


class StreamReader:

    def __init__(self, s):
        self.s = s

    def read(self, n=-1):
        s = yield IORead(self.s)
        while True:
            res = self.s.read(n)
            if res is not None:
                break
            log.warn("Empty read")
        if not res:
            yield IOReadDone(self.s)
        return res

    def readline(self):
        if __debug__:
            log.debug("StreamReader.readline()")
        s = yield IORead(self.s)
        if __debug__:
            log.debug("StreamReader.readline(): after IORead: %s", s)
        while True:
            res = self.s.readline()
            if res is not None:
                break
            log.warn("Empty read")
        if not res:
            yield IOReadDone(self.s)
        if __debug__:
            log.debug("StreamReader.readline(): res: %s", res)
        return res

    def close(self):
        yield IOReadDone(self.s)
        self.s.close()

    def __repr__(self):
        return "<StreamReader %r>" % self.s


class StreamWriter:

    def __init__(self, s):
        self.s = s

    def awrite(self, buf):
        # This method is called awrite (async write) to not proliferate
        # incompatibility with original asyncio. Unlike original asyncio
        # whose .write() method is both not a coroutine and guaranteed
        # to return immediately (which means it has to buffer all the
        # data), this method is a coroutine.
        sz = len(buf)
        if __debug__:
            log.debug("StreamWriter.awrite(): spooling %d bytes", sz)
        while True:
            res = self.s.write(buf)
            # If we spooled everything, return immediately
            if res == sz:
                if __debug__:
                    log.debug("StreamWriter.awrite(): completed spooling %d bytes", res)
                return
            if res is None:
                res = 0
            if __debug__:
                log.debug("StreamWriter.awrite(): spooled partial %d bytes", res)
            assert res < sz
            buf = buf[res:]
            sz -= res
            s2 = yield IOWrite(self.s)
            #assert s2 == self.s
            if __debug__:
                log.debug("StreamWriter.awrite(): can write more")

    def close(self):
        yield IOWriteDone(self.s)
        self.s.close()

    def __repr__(self):
        return "<StreamWriter %r>" % self.s


#def open_connection(host, port):
    #if __debug__:
        #log.debug("open_connection(%s, %s)", host, port)
    #s = _socket.socket()
    #s.setblocking(False)
    #ai = _socket.getaddrinfo(host, port)
    #addr = ai[0][4]
    #try:
        #s.connect(addr)
    #except OSError as e:
        #if e.args[0] != errno.EINPROGRESS:
            #raise
    #if __debug__:
        #log.debug("open_connection: After connect")
    #s2 = yield IOWrite(s)
    #if __debug__:
        #assert s2 == s
    #if __debug__:
        #log.debug("open_connection: After iowait: %s", s)
    #return StreamReader(s), StreamWriter(s)


#def start_server(client_coro, host, port, backlog=10):
    #log.debug("start_server(%s, %s)", host, port)
    #s = _socket.socket()
    #s.setblocking(False)

    #ai = _socket.getaddrinfo(host, port)
    #addr = ai[0][4]
    #s.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
    #s.bind(addr)
    #s.listen(backlog)
    #while True:
        #if __debug__:
            #log.debug("start_server: Before accept")
        #yield IORead(s)
        #if __debug__:
            #log.debug("start_server: After iowait")
        #s2, client_addr = s.accept()
        #s2.setblocking(False)
        #if __debug__:
            #log.debug("start_server: After accept: %s", s2)
        #yield client_coro(StreamReader(s2), StreamWriter(s2))

def main():
    uart = pyb.UART(2)
    read = StreamReader(uart)




if __name__ == "__main__":
    main()

