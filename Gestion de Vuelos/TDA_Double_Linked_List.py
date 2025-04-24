class _DoublyLinkedBase:
    """Implementación base de lista doblemente enlazada con centinelas."""

    class _Node:
        __slots__ = ('_element', '_prev', '_next')
        def __init__(self, element, prev, next_):
            self._element = element
            self._prev = prev
            self._next = next_

    def __init__(self):
        self._header = self._Node(None, None, None)
        self._trailer = self._Node(None, None, None)
        self._header._next = self._trailer
        self._trailer._prev = self._header
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    def _insert_between(self, e, predecessor, successor):
        node = self._Node(e, predecessor, successor)
        predecessor._next = node
        successor._prev = node
        self._size += 1
        return node

    def add_first(self, e):
        return self._insert_between(e, self._header, self._header._next)

    def add_last(self, e):
        return self._insert_between(e, self._trailer._prev, self._trailer)

    def _delete_node(self, node):
        if node in (self._header, self._trailer):
            raise ValueError("No se pueden eliminar nodos centinela")
        prev = node._prev
        next_ = node._next
        prev._next = next_
        next_._prev = prev
        self._size -= 1
        element = node._element
        node._prev = node._next = node._element = None
        return element

    def delete_first(self):
        if self.is_empty():
            raise Exception("Lista vacía")
        return self._delete_node(self._header._next)

    def delete_last(self):
        if self.is_empty():
            raise Exception("Lista vacía")
        return self._delete_node(self._trailer._prev)

    def __str__(self):
        elems = []
        node = self._header._next
        while node is not self._trailer:
            elems.append(str(node._element))
            node = node._next
        return ' <-> '.join(elems) if elems else 'Empty list'