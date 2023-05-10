# -*-coding:utf-8-*-
from collections import UserDict
from threading import RLock, Lock
import time
from queue import Queue


class TTLDict(UserDict):
    def __init__(self, ttl_set: set = None, max_broken_length: int = None, *args, **kwargs):
        self._rlock = RLock()
        self._lock = Lock()

        self._set = ttl_set
        self._q_broken = None
        if max_broken_length is not None:
            self._q_broken = Queue(maxsize=max_broken_length)

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '<TTLDict@%#08x; %r;>' % (id(self), self.data)

    def expire(self, key, ttl, now=None):
        if now is None:
            now = time.time()
        with self._rlock:
            _expire, value = self.data[key]
            self.data[key] = (now + ttl, value)

    def ttl(self, key, now=None):
        if now is None:
            now = time.time()
        with self._rlock:
            expire, _value = self.data[key]
            if expire is None:
                # Persistent keys
                return -1
            elif expire <= now:
                # Expired keys
                del self[key]
                return -2
            return expire - now

    def set_expire(self, key, ttl, value):
        with self._rlock:
            expire = time.time() + ttl
            if self.data.get(key, None) is None:
                self.data[key] = (expire, value)
            else:
                self.data[key] = (expire, self.data[key][-1])
            if self._set is not None:
                self._set.add(key)

    def list_set(self):
        self.__len__()
        with self._rlock:
            temp = []
            for i in self._set:
                temp.append(i)
            return temp

    def get_broken_connection(self):
        self.__len__()
        try:
            if self._q_broken is not None:
                return self._q_broken.get(block=False)
            return None
        except Exception:
            return None

    def __len__(self):
        with self._rlock:
            for key in list(self.data.keys()):
                self.ttl(key)
            return len(self.data)

    def __iter__(self):
        with self._rlock:
            for k in self.data.keys():
                ttl = self.ttl(k)
                if ttl != -2:
                    yield k

    def __setitem__(self, key, value):
        with self._lock:
            self.data[key] = (None, value)

    def __delitem__(self, key):
        with self._lock:
            del self.data[key]
            if self._set is not None:
                self._set.remove(key)
                # 存入过期连接
                if self._q_broken is not None:
                    try:
                        self._q_broken.put(key, block=False)
                    except Exception:
                        pass

    def __getitem__(self, key):
        with self._rlock:
            self.ttl(key)
            return self.data[key][1]
