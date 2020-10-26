#! https://zhuanlan.zhihu.com/p/259337581
# Parallel in Python -- practical multiprocessing

[Official website](https://docs.python.org/zh-cn/3/library/multiprocessing.html)

# 快速上手

如果你想快速地通过例子去理解、仿写，那么只用看**标有三颗星**的部分（及其子部分）就可以

# 概述 

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
        cc = time.time()
        value = datetime.datetime.fromtimestamp(cc).strftime('%Y-%m-%d %H:%M:%S') + "\n"
        print('hello world', i, value)
        time.sleep(1)
    finally:
        l.release()

if __name__ == '__main__':
    lock = Lock()

    for num in range(10):
        Process(target=f, args=(lock, num)).start()


""" 
Output:
-------------
hello world 0 2020-09-25 15:49:42

hello world 1 2020-09-25 15:49:43

hello world 2 2020-09-25 15:49:44

hello world 3 2020-09-25 15:49:45

hello world 4 2020-09-25 15:49:46

hello world 5 2020-09-25 15:49:47

hello world 6 2020-09-25 15:49:48

hello world 7 2020-09-25 15:49:49

hello world 8 2020-09-25 15:49:50

hello world 9 2020-09-25 15:49:52
"""
```
**不使用锁的情况下，来自于多进程的输出很容易产生混淆。**

```python
from multiprocessing import Process, Lock
import time

def f(i):
    try:
        cc = time.time()
        value = datetime.datetime.fromtimestamp(cc).strftime('%Y-%m-%d %H:%M:%S') + "\n"
        print('hello world', i, value)
        time.sleep(1)
    except:
        print("not work")


if __name__ == '__main__':
    for num in range(10):
        Process(target=f, args=(num,)).start()


"""
Output:
------------------------------------
hello world 0hello world  hello world12020-09-25 15:51:05
  
22020-09-25 15:51:05
hello world 
 2020-09-25 15:51:05

3hello world  2020-09-25 15:51:05

4hello world  2020-09-25 15:51:05
5
hello world  2020-09-25 15:51:05
6 
hello world2020-09-25 15:51:05
 
7 hello world 2020-09-25 15:51:05
8
 hello world2020-09-25 15:51:05
 
9 2020-09-25 15:51:05
"""
```

## 使用工作进程 Pool （***）
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
**靠谱的还是用 `pool.apply_async` 应对 `for loop`, 如果是直接对一个数组的话，可以考虑用 `pool.map()`**

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
# 杂项
**multiprocessing.cpu_count()**

- 返回系统的CPU数量
- 该数量不同于当前进程可以使用的CPU数量.可用的CPU数量可以由 `len(os.sched_getaffinity(0))` 方法获得。

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

# 非常有用的例子(***)

## pool.apply_async + for loop 部分

### 例 1: get 前置 导致 同步 (一般我们想要避免这种情况)

```Python
import multiprocessing as mp
import time
import datetime

def add_item(k):
    list_ = []
    for i in range(k):
        list_.append(k)
    cc = time.time()
    value = datetime.datetime.fromtimestamp(cc).strftime('%Y-%m-%d %H:%M:%S') + "\n"
    list_.append(value)
    print("done at", value)
    # we use time.sleep() to help us figure out whether tasks are really executed at the same time
    time.sleep(1)
    return list_

a_list = []

if __name__ == "__main__":
    a_list = []
    with mp.Pool(3) as pool:
        for i in range(1,4):
            a_list.append((pool.apply_async(add_item, (i,) )).get())
            
    		print(a_list)
    
# output
"""
done at 2020-09-25 15:40:54

done at 2020-09-25 15:40:55

done at 2020-09-25 15:40:56

[[1, '2020-09-25 15:40:54\n'], [2, 2, '2020-09-25 15:40:55\n'], [3, 3, 3, '2020-09-25 15:40:56\n']]
"""
```

通过上面例子，我们可以从输出时间发现，这个时候加入list的是它的时间戳，而在`for loop` 中，下一个任务是等待上一个任务结束才开始执行的。



### 例2: get 后置 则为异步 （我们想要的）

```python
import multiprocessing as mp
import time
import datetime

def add_item(k):
    list_ = []
    for i in range(k):
        list_.append(k)
    cc = time.time()
    value = datetime.datetime.fromtimestamp(cc).strftime('%Y-%m-%d %H:%M:%S') + "\n"
    list_.append(value)
    print("done at", value)
    time.sleep(1)
    return list_

a_list = []

if __name__ == "__main__":
    a_list = []
    with mp.Pool(4) as pool:
        for i in range(1,7):
            a_list.append((pool.apply_async(add_item, (i,) )))
        
        print([r.get(timeout=2) for r in a_list])
        
# output
"""
done atdone atdone at done at  2020-09-25 17:34:16
2020-09-25 17:34:16
 2020-09-25 17:34:16

2020-09-25 17:34:16



done atdone at  2020-09-25 17:34:17
2020-09-25 17:34:17


[[1, '2020-09-25 17:34:16\n'], [2, 2, '2020-09-25 17:34:16\n'], [3, 3, 3, '2020-09-25 17:34:16\n'], [4, 4, 4, 4, '2020-09-25 17:34:16\n'], [5, 5, 5, 5, 5, '2020-09-25 17:34:17\n'], [6, 6, 6, 6, 6, 6, '2020-09-25 17:34:17\n']]
"""
```

从例2我们看到，3个 `done at` 一起输出，而且 时间戳也一样，这说明大家都是 **一起跑的**，也就是异步。

<font color=#FA8282, size=4> 此时需要注意，我们的 `get()` 操作一定要在 pool里面执行，否则就会出现一只等待的情况，如果设置 .get(timeout=2)的话，就会报出 Timeout Error. </font>



### 例 2.5 

```python
def add_item(k):
    list_ = []
    for i in range(k):
        list_.append(k)
    cc = time.time()
    value = datetime.datetime.fromtimestamp(cc).strftime('%Y-%m-%d %H:%M:%S') + "\n"
    list_.append(value)
    print("done at", value)
    time.sleep(1)
    return list_

a_list = []

if __name__ == "__main__":
    a_list = []
    with mp.Pool(4) as pool:
        for i in range(1,7):
            a_list.append((pool.apply_async(add_item, (i,) )))
        pool.close()
        pool.join()
    print([r.get(timeout=2) for r in a_list])
    
# output

"""
done atdone atdone atdone at   2020-09-25 17:34:19
2020-09-25 17:34:19
 2020-09-25 17:34:19



2020-09-25 17:34:19

done atdone at  2020-09-25 17:34:20
2020-09-25 17:34:20


[[1, '2020-09-25 17:34:19\n'], [2, 2, '2020-09-25 17:34:19\n'], [3, 3, 3, '2020-09-25 17:34:19\n'], [4, 4, 4, 4, '2020-09-25 17:34:19\n'], [5, 5, 5, 5, 5, '2020-09-25 17:34:20\n'], [6, 6, 6, 6, 6, 6, '2020-09-25 17:34:20\n']]
"""
```

相比于 例2， 我们多加了两行: `pool.close(); pool.join()` 但是我们发现结果并没改变。 **这说明在改变非共享变量时，在get()的过程中，程序会自动等待进城池运行结束， 不信的可以调大 range试试**



### 例 3 基本操作

```python
from  multiprocessing import Process,Pool
import os, time, random

def fun1(name):
    print('Run task %s (%s)...' % (name, os.getpid()))
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print('Task %s runs %0.2f seconds.' % (name, (end - start)))

if __name__=='__main__':
    pool = Pool(5) #创建一个5个进程的进程池

    for i in range(10):
        pool.apply_async(func=fun1, args=(i,))

    pool.close()
    pool.join()
    print('结束测试')
    
    
# output:
"""
Run task 2 (52176)...Run task 1 (52175)...Run task 3 (52177)...Run task 0 (52174)...


Run task 4 (52178)...

Task 2 runs 0.47 seconds.
Run task 5 (52176)...
Task 1 runs 1.26 seconds.
Run task 6 (52175)...
Task 4 runs 1.28 seconds.
Run task 7 (52178)...
Task 6 runs 0.37 seconds.
Run task 8 (52175)...
Task 0 runs 2.06 seconds.
Run task 9 (52174)...
Task 5 runs 1.74 seconds.
Task 8 runs 0.76 seconds.
Task 7 runs 1.34 seconds.
Task 3 runs 2.77 seconds.
Task 9 runs 2.03 seconds.
结束测试
"""
```

**对`Pool`对象调用`join()`方法会等待所有子进程执行完毕，调用`join()`之前必须先调用`close()`，调用`close()`之后就不能继续添加新的`Process`了。**

### 例 4， 在pool 中 共享内存 

```python
from multiprocessing import Process, Manager


def fun1(dic,lis,index):

    dic[index] = 'a'
    dic['2'] = 'b'    
    cc = time.time()
    value1 = datetime.datetime.fromtimestamp(cc).strftime('%Y-%m-%d %H:%M:%S') + "\n"
    lis.append((index,value1))    #[0,1,2,3,4,0,1,2,3,4,5,6,7,8,9]
    time.sleep(1)

# case 1
if __name__ == '__main__':
    with Manager() as manager:
        dic = manager.dict()#注意字典的声明方式，不能直接通过{}来定义
        l = manager.list(range(5))#[0,1,2,3,4]
        with mp.Pool(5) as pool:
            for i in range(10):
                pool.apply_async(fun1, (dic,l,i))                
            print("0",dic)
            print()
            print(l)
    
        print("1", dic)
    print("2", dic)

# output
"""
0 {}

[0, 1, 2, 3, 4]
1 {2: 'a', '2': 'b', 0: 'a', 3: 'a', 1: 'a'}
2 <DictProxy object, typeid 'dict' at 0x7fc03da30190; '__str__()' failed>
"""

#############################################      split line        #############################################

# case 2
if __name__ == '__main__':
    with Manager() as manager:
        dic = manager.dict()#注意字典的声明方式，不能直接通过{}来定义
        l = manager.list(range(5))#[0,1,2,3,4]
        with mp.Pool(5) as pool:
            for i in range(10):
                pool.apply_async(fun1, (dic,l,i))                
            print("#",dic)
            print()
            print("#",l)
            a = time.time()
            pool.close()
            pool.join()
            b = time.time()
            print()
            print(f"it take {a-b} seconds to finish")
            print()
            print("###",l)
            print()
            print("###",dic)
# output

"""
# {}

# [0, 1, 2, 3, 4]

it take -2.058048963546753 seconds to finish

### [0, 1, 2, 3, 4, (1, '2020-09-25 17:22:38\n'), (0, '2020-09-25 17:22:38\n'), (2, '2020-09-25 17:22:38\n'), (3, '2020-09-25 17:22:38\n'), (4, '2020-09-25 17:22:38\n'), (5, '2020-09-25 17:22:39\n'), (6, '2020-09-25 17:22:39\n'), (7, '2020-09-25 17:22:39\n'), (8, '2020-09-25 17:22:39\n'), (9, '2020-09-25 17:22:39\n')]

### {1: 'a', '2': 'b', 0: 'a', 3: 'a', 2: 'a', 4: 'a', 5: 'a', 6: 'a', 7: 'a', 8: 'a', 9: 'a'}
"""

#############################################      split line        #############################################


# case 3

if __name__ == '__main__':
    with Manager() as manager:
        dic = manager.dict()#注意字典的声明方式，不能直接通过{}来定义
        l = manager.list(range(5))#[0,1,2,3,4]
        with mp.Pool(5) as pool:
            for i in range(10):
                pool.apply_async(fun1, (dic,l,i))                
            pool.close()
            pool.join()
            
        print(dic)
        print(l)
```

通过例4 我们可以发现

- 调用共享变量结果的时候必须在 With Manager 内部
- 调用 共享变量结果 时，必须使用 pool.close(), pool.join() 去等待所有运行结果

## Process 部分

### 例 1: Process 的 基本理解

```Python
from multiprocessing import  Process
import os

def fun1(name):
    cc = time.time()
    value = datetime.datetime.fromtimestamp(cc).strftime('%Y-%m-%d %H:%M:%S') + "\n"
    pid = str(os.getpid())
    print("测试多进程:"+value+" os pid: "+pid)
    time.sleep(5)
    cc = time.time()
    value = datetime.datetime.fromtimestamp(cc).strftime('%Y-%m-%d %H:%M:%S') + "\n"
    print("测试结束: ", value)


if __name__ == '__main__':
    process_list = []
    for i in range(5):  #开启5个子进程执行fun1函数
        p = Process(target=fun1,args=('Python',)) #实例化进程对象
        p.start()
        process_list.append(p)

    time.sleep(1)
    cc = time.time()
    value1 = datetime.datetime.fromtimestamp(cc).strftime('%Y-%m-%d %H:%M:%S') + "\n"
    
    for i in process_list:
        p.join()
        
    cc = time.time()
    value2 = datetime.datetime.fromtimestamp(cc).strftime('%Y-%m-%d %H:%M:%S') + "\n"

    print('结束测试:',value1, value2)

# Output
"""
测试多进程:2020-09-25 16:42:23
 os pid: 51895
测试多进程:2020-09-25 16:42:23
 os pid: 51896
测试多进程:2020-09-25 16:42:23
 os pid: 51897
测试多进程:2020-09-25 16:42:23
 os pid: 51898
测试多进程:2020-09-25 16:42:23
 os pid: 51899
测试结束:  测试结束: 2020-09-25 16:42:28

 2020-09-25 16:42:28
测试结束: 
 2020-09-25 16:42:28
测试结束: 
 2020-09-25 16:42:28
测试结束: 
 2020-09-25 16:42:28

结束测试: 2020-09-25 16:42:24
 2020-09-25 16:42:28
"""

```

注意：

1. process方法也是通过异步方式运行的。不过有一个 p.start() 和 p.join() 的操作
2. 程序在 `start()` 的时候运行的
3. 通过观察value1，我们可以发现在 `start()` 程序运行的时候，内部子进程可以继续运行而不影响 for loop 的结束。故 value1 的时间会比 "测试结束" 的时间要早。而 join() 则是一个个关闭进程，这时候要保证进程已经运行完毕，所以该时刻取到的时间是程序都运行结束的时间。



### 例 2 共享内存 (共同修改一份数据)

```python
from multiprocessing import Process, Manager

def fun1(dic,lis,index):

    dic[index] = 'a'
    dic['2'] = 'b'    
    cc = time.time()
    value1 = datetime.datetime.fromtimestamp(cc).strftime('%Y-%m-%d %H:%M:%S') + "\n"
    lis.append((index,value1))    #[0,1,2,3,4,0,1,2,3,4,5,6,7,8,9]
    time.sleep(1)

if __name__ == '__main__':
    with Manager() as manager:
        dic = manager.dict()#注意字典的声明方式，不能直接通过{}来定义
        l = manager.list(range(5))#[0,1,2,3,4]

        process_list = []
        for i in range(10):
            p = Process(target=fun1, args=(dic,l,i))
            p.start()
            process_list.append(p)

        for res in process_list:
            res.join()
        print(dic)
        print()
        print(l)
        
# output
"""
{0: 'a', '2': 'b', 1: 'a', 2: 'a', 3: 'a', 4: 'a', 5: 'a', 6: 'a', 7: 'a', 8: 'a', 9: 'a'}

[0, 1, 2, 3, 4, (0, '2020-09-25 16:59:44\n'), (1, '2020-09-25 16:59:44\n'), (2, '2020-09-25 16:59:44\n'), (3, '2020-09-25 16:59:44\n'), (4, '2020-09-25 16:59:44\n'), (5, '2020-09-25 16:59:44\n'), (6, '2020-09-25 16:59:44\n'), (7, '2020-09-25 16:59:44\n'), (8, '2020-09-25 16:59:44\n'), (9, '2020-09-25 16:59:44\n')]
"""
```

通过例2 我们可以看到，修改同一份数据是同时进行的



# 总结（***）

我们可以通过 Process 或者 进程池 Pool 的方式来进行 并行异步的编程。而这个时候如果存在共享变量，且子函数内部就要修改共享变量时，必须用 pool.close() + pool.join() 去 获得正确结果。但是如果我们是在子函数外部的话，就不用。不过为了简单记忆，我们都记得去用 这两个命令准没错。

对于 Process， 也有相应的 p.start()   p.join() 去开始和结束进程

# References

[正确使用Multiprocessing的姿势](https://jingsam.github.io/2015/12/31/multiprocessing.html)

[一篇文章搞定Python多进程](https://juejin.im/post/6844903838000873485)

[廖雪峰 Python教程](https://www.liaoxuefeng.com/wiki/1016959663602400/1017627212385376)





# Pandas 中应用并行(parallel)的方法

## 1. pandarallel library (support Linux, macOS)
[运用这个库](https://github.com/nalepae/pandarallel)

## 2. manually do the parallism

[参考这篇博文，也是通过 Process方法实现的，很机智](https://blog.fangzhou.me/posts/20170702-python-parallelism/)

