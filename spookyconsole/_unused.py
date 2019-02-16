

def _num_slice_elements(sl: slice, len_seq: int):
    return len(range(*sl.indices(len_seq)))


def _assert_constant_length(key, value, len_seq, err_msg):
    if (isinstance(key, slice) and hasattr(value, "__len__") and
            _num_slice_elements(key, len_seq) != len(value)):
        raise ValueError(err_msg)


class GridProxy:

    # TODO: Make column/row objects take a snapshot of grid? Only change underlying grid if not invalidated.
    # TODO: Index by tuple (like numpy).

    PPRINT_WIDTH = 100

    class GridIterator:

        def __init__(self, view):
            self._view = view
            self._idx = -1

        def __iter__(self):
            return self

        def __next__(self):
            self._idx += 1
            if self._idx >= len(self._view):
                raise StopIteration
            return self._view[self._idx]

    class RowView:

        class Row:

            def __init__(self, grid, idx):
                self._grid = grid
                self._idx = idx

            def __len__(self):
                return self._grid.width

            def __contains__(self, item):
                return item in self._grid.raw[self._idx]

            def __iter__(self):
                return iter(self._grid.raw[self._idx])

            def __getitem__(self, item):
                return self._grid.raw[self._idx][item]

            def __setitem__(self, key, value):
                _assert_constant_length(key, value, len(self), "row length must remain constant")
                if isinstance(key, slice) and not isinstance(value, list):
                    value = list(value)
                self._grid.raw[self._idx][key] = value

        def __init__(self, grid):
            self._grid = grid

        def __len__(self):
            return self._grid.height

        def __iter__(self):
            return GridProxy.GridIterator(self)

        def __getitem__(self, item):
            if isinstance(item, slice):
                return [self.Row(self._grid, i) for i in range(*item.indices(len(self)))]
            return self.Row(self._grid, item)

        def __setitem__(self, key, value):
            if isinstance(key, slice):
                _assert_constant_length(key, value, len(self), "column length must remain constant")
                for i, row in enumerate(value):
                    if len(row) != self._grid.width:
                        raise ValueError("row length must remain constant")
                    if not isinstance(row, list):
                        value[i] = list(row)
            elif len(value) != self._grid.width:
                raise ValueError("row length must remain constant")
            elif not isinstance(value, list):
                value = list(value)
            self._grid.raw[key] = value

    class ColumnView:

        class Column:

            def __init__(self, grid, idx):
                self._grid = grid
                self._idx = idx

            def __len__(self):
                return self._grid.height

            def __contains__(self, item):
                return item in iter(self)

            def __iter__(self):
                return (x[self._idx] for x in self._grid.raw)

            def __getitem__(self, item):
                if isinstance(item, slice):
                    return [x[self._idx] for x in self._grid.raw[item]]
                return self._grid.raw[item][self._idx]

            def __setitem__(self, key, value):
                if isinstance(key, slice):
                    _assert_constant_length(key, value, len(self), "column length must remain constant")
                    for i in range(*key.indices(len(self))):
                        self._grid.raw[i][self._idx] = value[i]
                else:
                    self._grid.raw[key][self._idx] = value

        def __init__(self, grid):
            self._grid = grid

        def __len__(self):
            return self._grid.width

        def __iter__(self):
            return GridProxy.GridIterator(self)

        def __getitem__(self, item):
            if isinstance(item, slice):
                return [self.Column(self._grid, i) for i in range(*item.indices(len(self)))]
            return self.Column(self._grid, item)

        def __setitem__(self, key, value):
            if isinstance(key, slice):
                _assert_constant_length(key, value, len(self), "row length must remain constant")
                for column in value:
                    if len(column) != self._grid.height:
                        raise ValueError("column length must remain constant")
                for i, column in enumerate(range(*key.indices(len(self)))):
                    for row in range(self._grid.height):
                        self._grid.raw[row][column] = value[i][row]
            else:
                if len(value) != self._grid.height:
                    raise ValueError("column length must remain constant")
                for row in range(self._grid.height):
                    self._grid.raw[row][key] = value[row]

    def __init__(self, width, height):
        self._data = [[None] * width for _ in range(height)]
        self._row_view = None
        self._column_view = None
        self._width = width
        self._height = height

    def __iter__(self):
        return self.items_iter_rowwise()

    def __len__(self):
        return self.n_items

    def __str__(self):
        from pprint import pformat
        return pformat(self.raw, width=self.PPRINT_WIDTH)

    @property
    def raw(self):
        return self._data

    @property
    def rows(self):
        if self._row_view is None:
            self._row_view = self.RowView(self)
        return self._row_view

    @property
    def columns(self):
        if self._column_view is None:
            self._column_view = self.ColumnView(self)
        return self._column_view

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def n_items(self):
        return self._width * self._height

    def set_size(self, width=None, height=None):
        width = self._width if width is None else width
        height = self._height if height is None else height
        delta_height = height - self.height
        if delta_height > 0:
            for _ in range(delta_height):
                self._data += [[None] * width]
        elif delta_height < 0:
            self._data = self._data[:delta_height]
        delta_width = width - self._width
        if delta_width:
            for i in range(min(height, self._height)):
                if delta_width > 0:
                    self._data[i] += [None] * delta_width
                else:
                    self._data[i] = self._data[i][:delta_width]
            self._width = width
        self._height = height

    def items_iter_rowwise(self):
        return self._unravel(self.rows)

    def items_iter_columnwise(self):
        return self._unravel(self.columns)

    def transpose(self):
        w, h = self._width, self._height
        max_dim = max(w, h)
        self.set_size(max_dim, max_dim)
        self.rows[:] = self.columns[:]
        self.set_size(h, w)

    @staticmethod
    def _unravel(view):
        for item in view:
            yield from item
