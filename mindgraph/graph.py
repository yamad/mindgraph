# -*- coding: utf-8 -*-
from typing import (Any, Callable, Generator, Iterator, List, Optional, Set,
                    Tuple)
from yaml import dump, load


class Task(object):
    """Task class"""

    def __init__(self, name: str = '', priority: int = 1) -> None:
        self._blockers = list()  # type: List[Task]
        self._subtasks = list()  # type: List[Task]
        self._name = ''  # type: str
        self._priority = priority  # type: int
        if type(name) is str:
            self._name = name
        else:
            raise TypeError

    def append(self, newtask) -> "Task":
        """ Creates a new Task and appends it to subtasks """
        if type(newtask) is str:
            newtask = Task(newtask)
        elif type(newtask) is not Task:
            raise TypeError
        self._subtasks.append(newtask)
        return newtask

    def pop(self, index: int) -> "Task":
        """ Pops the Task from subtasks[index] """
        return self._subtasks.pop(index)

    def blockedby(self, task: "Task") -> None:
        """ Adds a task to the subtasks list """
        if type(task) is Task:
            self._blockers.append(task)
            return None
        else:
            raise TypeError

    def blocking(self, task: "Task") -> None:
        """ Adds this task to another task's blockers list """
        if type(task) is Task:
            task._blockers.append(self)
            return None
        else:
            raise TypeError

    def __getitem__(self, key: int) -> "Task":
        return self._subtasks[key]

    def __repr__(self) -> str:
        return '\n'.join(self._format_tree())

    def _format_tree(self: "Task", depth: int = 0) -> Iterator[str]:
        """Generates task and subtasks into a string formatted tree"""
        indent = '    ' * depth
        bullet = '- ' if depth != 0 else ''
        suffix = ':' if self.subtasks else ''
        line = '{indent}{bullet}{self.name}{suffix}'.format(**locals())

        yield line
        for n in self.subtasks:
            yield from n._format_tree(depth+1)

    def _postorder(self,
                   depth: int = 0,
                   visited: Set["Task"] = None,
                   taskkey: Callable[["Task"], Any]=None,
                   ) -> Generator[Tuple[int, "Task"], None, Set["Task"]]:
        """Post-order traversal of Project rooted at Task"""
        if visited is None:
            visited = set()

        children = self._subtasks
        if taskkey is not None:
            children = sorted(self._subtasks, key=taskkey)

        for child in children:
            if child not in visited:
                visited = yield from child._postorder(depth+1,
                                                      visited,
                                                      taskkey)

        yield (depth, self)
        visited.add(self)

        return visited

    def todo(self) -> Iterator["Task"]:
        """Generate Tasks in todo order

        Tasks are scheduled by priority and to resolve blocking tasks
        """
        # sorts by priority (2 before 1), then alphabetical
        def taskkey(Task):
            return (-Task.priority, Task.name)
        return (x[1] for x in self._postorder(taskkey=taskkey))

    def __str__(self) -> str:
        return dump(load(str(self.__repr__())), default_flow_style=False)

    @property
    def blockers(self) -> List["Task"]:
        """ blockers getter """
        return self._blockers

    @property
    def name(self) -> str:
        """ name getter """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """ name setter """
        self._name = name

    @property
    def subtasks(self) -> List["Task"]:
        """ subtasks getter """
        return self._subtasks

    @property
    def priority(self) -> int:
        """ priority getter """
        return self._priority

    @priority.setter
    def priority(self, value: int) -> None:
        """ priority setter """
        self._priority = value

    def to_yaml(self, filename=None) -> None:
        """ Write this Project to a yaml file """
        with open(filename, 'w') as f:
            f.write(dump(self))


class Project(object):
    """Returns a task representing the root of your project"""
    def __new__(cls, name: str=None) -> Task:
        return Task(name)


def read_yaml(filename: str = "") -> Task:
    """ Load a project from a yaml file """
    with open(filename, 'r') as f:
        rv = load(f.read())
        if type(rv) is Task:
            return rv
        else:
            raise TypeError(type(rv))
