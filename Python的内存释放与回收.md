#! https://zhuanlan.zhihu.com/p/249224119

目录：
1. [前言](#一前言-preface)
2. [实用正题](#二实用正题-practical-part)
3. [小学一点](#三小学一点-learn-a-little-bit)

---

# 一、前言 Preface
我一直以来没怎么认真学过python的内存释放机制，对于这东西总处于一种一知半解的情况。总以为我 `del` 一个变量，那就自动在内存里删除了这个变量，自然而然地内存就被释放了。

然而，目前我工作刚满一年，在这一年的时光里，我遇到三四次无法理解的OOM错误，让我不得不认真的research一下单纯的 `del` 到底能不能做到我想做的事。

<font color=#9B9B9B size=2> 我自己虽说一直有个读博的想法，但是在工作中为了效率，其实很多时候能用就行，并不用达到 *知其然，且知其所以然* 的程度。所以我先调查到了一些问题出现的原因以及解决方法，最后再学习一下Python自己的内存回收机制。</font>

Without further ado, let's start.

----

# 二、实用正题 Practical part
[从这篇博文](https://blog.csdn.net/jiangjiang_jian/article/details/79140742) 中，我们可以看到 必须要 `import gc` 然后用 `gc.collect()` 去回收已经 `del` 的大文件。在博文中，作者提到了用一个自定义函数清除环境中所有的全局变量。可能用得上，就转载记录到这里。

```python
def clear():

    for key, value in globals().items():

        if callable(value) or value.__class__.__name__ == "module":

            continue

        del globals()[key]
```
----

# 三、小学一点 Learn a little bit. 
## python的内存管理方式
[这是最新的Python-3.10](https://docs.python.org/zh-cn/3.10/c-api/memory.html) 的关于**内存管理**的文档,文章长度很短，可以花两分钟阅读一下。（不过我也读不懂，或许应该读 `gc` 的文档）

准备知识：[关于变量与指向的对象](https://zhuanlan.zhihu.com/p/55601173)

背景知识：[from here](https://stackify.com/python-garbage-collection/#:~:text=At%20a%20very%20basic%20level,t%20disable%20Python's%20reference%20counting.)
>The values of your program’s objects are stored in memory for quick access. In many programming languages, a variable in your program code is simply a pointer to the address of the object in memory. When a variable is used in a program, the process will read the value from memory and operate on it.

>In early programming languages, developers were responsible for all memory management in their programs. This meant before creating a list or an object, you first needed to allocate the memory for your variable. After you were done with your variable, you then needed to deallocate it to “free” that memory for other users.

>This led to two problems:
>**Forgetting to free your memory**. If you don’t free your memory when you’re done using it, it can result in memory leaks. This can lead to your program using too much memory over time. For long-running applications, this can cause serious problems.

>**Freeing your memory too soon**. The second type of problem consists of freeing your memory while it’s still in use. This can cause your program to crash if it tries to access a value in memory that doesn’t exist, or it can corrupt your data. A variable that refers to memory that has been freed is called a dangling pointer.

所以现在的新发明的语言中，都有着自动的内存管理和垃圾回收机制。而python中用以下策略去实施内存回收。

---


### 3.1 引用计数 (Reference count)

在Python中，每个对象都有指向该对象的引用总数---引用计数 
> Whenever you create an object in Python, the underlying C object (CPython) has both a Python type (such as list, dict, or function) and a reference count.

> 在Python中每一个对象的核心就是一个结构体PyObject，它的内部有一个引用计数器（ob_refcnt）。程序在运行的过程中会实时的更新ob_refcnt的值，来反映引用当前对象的名称数量。当某对象的引用计数值为0,那么它的内存就会被立即释放掉。--[IT界老黑](https://zhuanlan.zhihu.com/p/83251959)

查看对象的引用计数：`sys.getrefcount()`

```python
In [2]: import sys

In [3]: a=[1,2,3]
In [4]: getrefcount(a)
Out[4]: 2
In [5]: b=a
In [6]: getrefcount(a)
Out[6]: 3
In [7]: getrefcount(b)
Out[7]: 3
```
> At a very basic level, a Python object’s reference count is incremented whenever the object is referenced, and it’s decremented when an object is dereferenced. If an object’s reference count is 0, the memory for the object is deallocated.

**以下情况是导致引用计数加一的情况:**
- 对象被创建，例如a=2
- 对象被引用，b=a
- 对象被作为参数，传入到一个函数中
- 对象作为一个元素，存储在容器中

**下面的情况则会导致引用计数减一:**
- 对象别名被显示销毁 del
- 对象别名被赋予新的对象
- 一个对象离开他的作用域
- 对象所在的容器被销毁或者是从容器中删除对象

举个例子
```python
>>> import sys
>>> a = 'my-string'
>>> sys.getrefcount(a)
2
>>> b = [a] # Make a list with a as an element.
>>> c = { 'key': a } # Create a dictionary with a as one of the values.
>>> sys.getrefcount(a)
4
```

#### 引用计数的优点 (pros)
高效，有用，具备实时性，一旦一个对象的引用计数归零，内存就直接释放了。不用等到特定时机释放内存，释放时间就在平时，程序运行比较平稳

#### 引用计数的缺点 (cons)
逻辑虽然简单，但实现有些麻烦。每个对象需要分配单独的空间来统计引用计数，这无形中加大的空间的负担，并且需要对引用计数进行维护

在一些场景下，可能会比较慢。正常来说垃圾回收会比较平稳运行，但是当需要释放一个大的对象时，比如字典，需要对引用的所有对象循环嵌套调用，从而可能会花费比较长的时间。

**循环引用** (Circular References)，这将是引用计数的致命伤，引用计数对此是无解的，因此必须要使用其它的垃圾回收算法对其进行补充。


### 3.2 标记清除 (Mark and Sweep)
> Python采用了“标记-清除”(Mark and Sweep)算法，解决容器对象可能产生的循环引用问题。(注意，只有容器对象才会产生循环引用的情况，比如列表、字典、用户自定义类的对象、元组等。而像数字，字符串这类简单类型不会出现循环引用。作为一种优化策略，对于只包含简单类型的元组也不在标记清除算法的考虑之列)

循环引用示例
```python
list1 = []
list2 = []
list1.append(list2)
list2.append(list1)
```
>针对循环引用这个问题，比如有两个对象互相引用了对方，当外界没有对他们有任何引用，也就是说他们各自的引用计数都只有1的时候，如果可以识别出这个循环引用，把它们属于循环的计数减掉的话，就可以看到他们的真实引用计数了。基于这样一种考虑，有一种方法，比如从对象A出发，沿着引用寻找到对象B，把对象B的引用计数减去1；然后沿着B对A的引用回到A，把A的引用计数减1，这样就可以把这层循环引用关系给去掉了。

>不过这么做还有一个考虑不周的地方。假如A对B的引用是单向的， 在到达B之前我不知道B是否也引用了A，这样子先给B减1的话就会使得B称为不可达的对象了。为了解决这个问题，python中常常把内存块一分为二，将一部分用于保存真的引用计数，另一部分拿来做为一个引用计数的副本，在这个副本上做一些实验。比如在副本中维护两张链表，一张里面放不可被回收的对象合集，另一张里面放被标记为可以被回收（计数经过上面所说的操作减为0）的对象，然后再到后者中找一些被前者表中一些对象直接或间接单向引用的对象，把这些移动到前面的表里面。这样就可以让不应该被回收的对象不会被回收，应该被回收的对象都被回收了。

- [GeeksforGeeks](https://www.geeksforgeeks.org/mark-and-sweep-garbage-collection-algorithm/) 这一篇讲得不错
- [这人回答的也好](https://www.zhihu.com/question/32373436/answer/549698608)

### 3.3 分代回收 (Generational garbage collection)
>一种空间换时间的方法。分代回收是基于这样的一个统计事实，对于程序，存在一定比例的内存块的生存周期比较短；而剩下的内存块，生存周期会比较长，甚至会从程序开始一直持续到程序结束。生存期较短对象的比例通常在 80%～90% 之间，这种思想简单点说就是：对象存在时间越长，越可能不是垃圾，应该越少去收集。这样在执行标记-清除算法时可以有效减小遍历的对象数，从而提高垃圾回收的速度。

>python gc给对象定义了三种世代(0,1,2),每一个新生对象在generation zero中，如果它在一轮gc扫描中活了下来，那么它将被移至generation one,在那里他将较少的被扫描，如果它又活过了一轮gc,它又将被移至generation two，在那里它被扫描的次数将会更少。

>gc的扫描在什么时候会被触发呢?答案是当某一世代中被分配的对象与被释放的对象之差达到某一阈值的时候，就会触发gc对某一世代的扫描。值得注意的是当某一世代的扫描被触发的时候，比该世代年轻的世代也会被扫描。也就是说如果世代2的gc扫描被触发了，那么世代0,世代1也将被扫描，如果世代1的gc扫描被触发，世代0也会被扫描。

该阈值可以通过下面两个函数查看和调整:
```python
gc.get_threshold() # (threshold0, threshold1,threshold2)
gc.set_threshold(threshold0[, threshold1[, threshold2]])
```
常用函数：
```python
# 设置gc的debug日志，一般设置为gc.DEBUG_LEAK
gc.set_debug(flags)

# 显式进行垃圾回收，可以输入参数，0代表只检查第一代的对象，1代表检查一，二代的对象，2代表检查一，二，三代的对象，如果不传参数，执行一个full collection，也就是等于传2。返回不可达（unreachable objects）对象的数目
gc.collect([generation])

# 设置自动执行垃圾回收的频率。
gc.set_threshold(threshold0[, threshold1[, threshold2])

# 获取当前自动执行垃圾回收的计数器，返回一个长度为3的列表gc模块的自动垃圾回收机制必须要import gc模块，并且is_enable()=True 才会启动自动垃圾回收。这个机制的主要作用就是发现并处理不可达的垃圾对象。垃圾回收=垃圾检查+垃圾回收
gc.get_count()
```
>如果垃圾回收不是那么好理解，我们可以用现实生活中的例子来联想。
又提到了开发商来拍地。
每拍一快地，房管局都要登记一下，这个开发商捂地的数量又加一。如果这块地使用完了，开发商捂地的数目减一。这便是引用计数。
如果这块地，一女二嫁，有纠纷。陷入循环死结了。政府就各个击破，请他们喝茶，请他们都退出。这个就是标记-清除。
如果这块地的开发商后台特别强大，捂着就是不开发。地方政府就只能采取一贯的做法，“让后代去解决”。这就是分代回收。

>下面对set_threshold()中的三个参数threshold0, threshold1, threshold2进行介绍。gc会记录自从上次收集以来新分配的对象数量与释放的对象数量，当两者之差超过threshold0的值时，gc的扫描就会启动，初始的时候只有世代0被检查。如果自从世代1最近一次被检查以来，世代0被检查超过 <font color=#F17B44 size=2> threshold_1 </font> 次，那么对世代1的检查将被触发。相同的，如果自从世代2最近一次被检查以来，世代1被检查超过 <font color=#F17B44 size=2> threshold_2 </font> 次，那么对世代2的检查将被触发。get_threshold()是获取三者的值，默认值为(700,10,10).



-----

# References
- [Python Garbage Collection: What It Is and How It Works, ALEX DEBRIE](https://stackify.com/python-garbage-collection/#:~:text=At%20a%20very%20basic%20level,t%20disable%20Python's%20reference%20counting)
- [Python垃圾回收机制！非常实用 -IT届老黑 -知乎](https://zhuanlan.zhihu.com/p/83251959)
- [python内存管理和垃圾回收 -谢小玲 -知乎](https://zhuanlan.zhihu.com/p/55601173)
- [主流的垃圾回收机制都有哪些? - 冒泡的回答 - 知乎](https://www.zhihu.com/question/32373436/answer/549698608)