# Parallel in Python -- practical multiprocessing

[Official website](https://docs.python.org/zh-cn/3/library/multiprocessing.html)

# 概述部分

## 在进程之间交换对象

`multiprocessing` 支持进程之间的两种通信通道：

### 队列

Queue 类是一个近似 queue.Queue 的克隆。 官网给了个我感觉没什么用的例子:

```Python
from multiprocessing import Process, Queue

def f(q):
    q.put([42, None, 'hello'])

if __name__ == '__main__':
    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    print(q.get())    # prints "[42, None, 'hello']"
    p.join()
```
队列是线程和进程安全的。

### 管道

Pipe() 函数返回一个由管道连接的连接对象，默认情况下是双工（双向）。例如:

```Python
from multiprocessing import Process, Pipe

def f(conn):
    conn.send([42, None, 'hello'])
    conn.close()

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p = Process(target=f, args=(child_conn,))
    p.start()
    print(parent_conn.recv())   # prints "[42, None, 'hello']"
    p.join()
```

返回的两个连接对象 `Pipe()` 表示管道的两端。每个连接对象都有 `send()` 和 `recv()` 方法（相互之间的）。请注意，如果两个进程（或线程）同时尝试读取或写入管道的同一端，则管道中的数据可能会损坏。当然，在不同进程中同时使用管道的不同端的情况下不存在损坏的风险。

## 进程间同步
`multiprocessing` 可以使用锁 `Lock` 来确保一次只有一个进程打印到标准输出:

```python
from multiprocessing import Process, Lock
def f(l, i):
    l.acquire()
    try:
        print('hello world', i)
    finally:
        l.release()

if __name__ == '__main__':
    lock = Lock()

    for num in range(10):
        Process(target=f, args=(lock, num)).start()


""" 
Output:
-------------
hello world 0
hello world 1
hello world 2
hello world 3
hello world 4
hello world 5
hello world 6
hello world 7
hello world 8
hello world 9
"""
```
**不使用锁的情况下，来自于多进程的输出很容易产生混淆。**
```python
from multiprocessing import Process, Lock
import time

def f(i):
    try:
        print('hello world', i)
    except:
        print("not work")


if __name__ == '__main__':
    for num in range(10):
        Process(target=f, args=(num,)).start()


"""
Output:
------------------------------------
hello world hello world0 hello world
1
 2hello world
 3hello world
 4hello world
 5hello world
 hello world6 
7hello world
 8hello world
 9
"""
```

## 使用工作进程 Pool
`Pool` 类表示一个工作进程池，它具有允许以不同方式将任务分配到工作进程的方法。例如

```python

from multiprocessing import Pool, TimeoutError
import time
import os

def f(x):
    return x*x

if __name__ == '__main__':
    # start 4 worker processes
    with Pool(processes=4) as pool:

        # print "[0, 1, 4,..., 81]"
        print(pool.map(f, range(10)))

        # print same numbers in arbitrary order
        for i in pool.imap_unordered(f, range(10)):
            print(i)

        # evaluate "f(20)" asynchronously
        res = pool.apply_async(f, (20,))      # runs in *only* one process
        print(res.get(timeout=1))             # prints "400"

        # evaluate "os.getpid()" asynchronously
        res = pool.apply_async(os.getpid, ()) # runs in *only* one process
        print(res.get(timeout=1))             # prints the PID of that process

        # launching multiple evaluations asynchronously *may* use more processes
        multiple_results = [pool.apply_async(os.getpid, ()) for i in range(4)]
        print([res.get(timeout=1) for res in multiple_results])

        # make a single worker sleep for 10 secs
        res = pool.apply_async(time.sleep, (10,))
        try:
            print(res.get(timeout=1))
        except TimeoutError:
            print("We lacked patience and got a multiprocessing.TimeoutError")

        print("For the moment, the pool remains available for more work")

    # exiting the 'with'-block has stopped the pool
    print("Now the pool is closed and no longer available")

"""
Output:
------------------------------------
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
0
1
4
16
9
36
25
49
64
81
400
11090
[11091, 11088, 11089, 11090]
We lacked patience and got a multiprocessing.TimeoutError
For the moment, the pool remains available for more work
Now the pool is closed and no longer available
"""
```
## 小结
靠谱的还是用 `pool.apply_async` 应对 `for loop`, 如果是直接对一个数组的话，可以考虑用 `pool.map()` 

**请注意，进程池的方法只能由创建它的进程使用。**  
<font color=#F17B44 size=2> 注解：这个包中的功能要求子进程可以导入`__main__`模块。具体请参考[编程指导](https://docs.python.org/zh-cn/3/library/multiprocessing.html#multiprocessing-programming)。这意味着一些示例在交互式解释器中不起作用 比如: </font>
```python
>>> from multiprocessing import Pool
>>> p = Pool(5)
>>> def f(x):
...     return x*x
...
>>> with p:
...   p.map(f, [1,2,3])
Process PoolWorker-1:
Process PoolWorker-2:
Process PoolWorker-3:
Traceback (most recent call last):
AttributeError: 'module' object has no attribute 'f'
AttributeError: 'module' object has no attribute 'f'
AttributeError: 'module' object has no attribute 'f'
````

# 参考
## Process 和异常

**run()**
- 表示进程活动的方法。

- 你可以在子类中重载此方法。标准 run() 方法调用传递给对象构造函数的可调用对象作为目标参数（如果有），分别从 args 和 kwargs 参数中获取顺序和关键字参数。

**start()**
- 启动进程活动。

- 这个方法每个进程对象最多只能调用一次。它会将对象的 run() 方法安排在一个单独的进程中调用。

**join([timeout])**
- 如果可选参数 `timeout` 是 `None` (默认值)，则该方法将阻塞，直到调用 `join()` 方法的进程终止。如果 `timeout` 是一个正数，它最多会阻塞 `timeout` 秒。请注意，如果进程终止或方法超时，则该方法返回 `None`。检查进程的 `exitcode` 以确定它是否终止。

- 一个进程可以被 `join` 多次。

- 进程无法`join`自身，因为这会导致死锁。尝试在启动进程之前join进程是错误的。

**terminate()**
- 终止进程。 在Unix上，这是使用 SIGTERM 信号完成的；在Windows上使用 TerminateProcess() 。 请注意，不会执行退出处理程序和finally子句等。

- 请注意，进程的后代进程将不会被终止 —— 它们将简单地变成孤立的。

- <font color="FF5733">警告 如果在关联进程使用管道或队列时使用此方法，则管道或队列可能会损坏，并可能无法被其他进程使用。类似地，如果进程已获得锁或信号量等，则终止它可能导致其他进程死锁。</font>

**kill()**
- 与 terminate() 相同，但在Unix上使用 SIGKILL 信号。*3.7 新版功能.*

**close()**
- 关闭 Process 对象，释放与之关联的所有资源。如果底层进程仍在运行，则会引发 ValueError 。一旦 close() 成功返回， Process 对象的大多数其他方法和属性将引发 ValueError 。*3.7 新版功能.*

注意 `start()` 、 `join()` 、 `is_alive()` 、 `terminate()` 和 `exitcode` 方法只能由创建进程对象的进程调用。

```Python
 >>> import multiprocessing, time, signal
 >>> p = multiprocessing.Process(target=time.sleep, args=(1000,))
 >>> print(p, p.is_alive())
 <Process ... initial> False
 >>> p.start()
 >>> print(p, p.is_alive())
 <Process ... started> True
 >>> p.terminate()
 >>> time.sleep(0.1)
 >>> print(p, p.is_alive())
 <Process ... stopped exitcode=-SIGTERM> False
 >>> p.exitcode == -signal.SIGTERM
 True
```
## 管道和队列
使用多进程时，一般使用<font color="FF5733">消息机制</font>实现进程间通信，尽可能避免使用同步原语，例如锁。

消息机制包含：`Pipe()` (可以用于2个进程间传递消息)，以及 **队列** （能够在多个生产者和消费者之间通信）

如果你使用了 `JoinableQueue` ，那么你 **必须** 对每个已经移出队列的任务调用 `JoinableQueue.task_done()` 。不然的话用于统计未完成任务的信号量最终会溢出并抛出异常。

另外还可以通过使用一个 **管理器** 对象创建一个共享队列。

`queue` 示例

```Python
import threading, queue

q = queue.Queue()

def worker():
    while True:
        item = q.get()
        print(f'Working on {item}')
        print(f'Finished {item}')
        q.task_done()

# turn-on the worker thread
threading.Thread(target=worker, daemon=True).start()

# send ten task requests to the worker
for item in range(10):
    q.put(item)
print('All task requests sent\n', end='')

# block until all tasks are done
q.join()
print('All work completed')

"""
Output
----------------------
All task requests sent
Working on 0
Finished 0
Working on 1
Finished 1
Working on 2
Finished 2
Working on 3
Finished 3
Working on 4
Finished 4
Working on 5
Finished 5
Working on 6
Finished 6
Working on 7
Finished 7
Working on 8
Finished 8
Working on 9
Finished 9
All work completed
"""
```

# 杂项

**multiprocessing.active_children()**
- 返回当前进程存活的子进程的列表。
- 调用该方法有“等待”已经结束的进程的副作用。

**multiprocessing.cpu_count()**
- 返回系统的CPU数量
- 该数量不同于当前进程可以使用的CPU数量.可用的CPU数量可以由 `len(os.sched_getaffinity(0))` 方法获得。


**multiprocessing.current_process()**
- 返回与当前进程相对应的 Process 对象。
- 和 threading.current_thread() 相同。

**multiprocessing.parent_process()**
- 返回父进程 `Process` 对象，和父进程调用 `current_process()` 返回的对象一样。如果一个进程已经是主进程，`parent_process` 会返回 `None`.(3.8 新版功能.)

**multiprocessing.freeze_support()**
- 为使用了 multiprocessing  的程序，提供冻结以产生 Windows 可执行文件的支持。(在 **py2exe**, **PyInstaller** 和 **cx_Freeze** 上测试通过)

- 需要在 main 模块的 if __name__ == '__main__' 该行之后马上调用该函数。例如：
```Python
from multiprocessing import Process, freeze_support

def f():
    print('hello world!')

if __name__ == '__main__':
    freeze_support()
    Process(target=f).start()
```
如果没有调用 freeze_support() 在尝试运行被冻结的可执行文件时会抛出 RuntimeError 异常。

对 freeze_support() 的调用在非 Windows 平台上是无效的。如果该模块在 Windows 平台的 Python 解释器中正常运行 (该程序没有被冻结)， 调用`freeze_support()` 也是无效的。


## 共享 ctypes 对象

## 管理器

## 进程池

## 监听器及客户端

# 例子