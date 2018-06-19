#!/usr/bin/env python

#import all modules under directory modules

print("This is modules __init__ , progress:" + __name__);


def __run_sub_task():
    try:
        import sub_task;
        sub_task.fork_task();
    except Exception, e:
        print("modules autoRun() excp, e:" + e.message);
    finally:
        print("");


def __autoRun():
    try:
        __run_sub_task();
    except Exception, e:
        print("modules autoRun() excp, e:" + e.message);
    finally:
        print("");



#__autoRun();



