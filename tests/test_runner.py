import pytest
import nbformat

from nbpipe.runner import execute_notebook


def make_notebook(path, sources):
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(src) for src in sources]
    nbformat.write(nb, str(path))
    return path


def read_notebook(path):
    return nbformat.read(str(path), as_version=4)


def test_stream_output_captured(tmp_path):
    nb_path = make_notebook(tmp_path / "nb.ipynb", ["print('hello')"])
    execute_notebook(nb_path)

    nb = read_notebook(nb_path)
    assert nb.cells[0].outputs[0]["text"] == "hello\n"


def test_execute_result_captured(tmp_path):
    nb_path = make_notebook(tmp_path / "nb.ipynb", ["1 + 1"])
    execute_notebook(nb_path)

    nb = read_notebook(nb_path)
    assert nb.cells[0].outputs[0]["data"]["text/plain"] == "2"


def test_execution_count_assigned(tmp_path):
    nb_path = make_notebook(tmp_path / "nb.ipynb", ["x = 1", "x + 1"])
    execute_notebook(nb_path)

    nb = read_notebook(nb_path)
    assert nb.cells[0].execution_count == 1
    assert nb.cells[1].execution_count == 2


def test_state_shared_across_cells(tmp_path):
    nb_path = make_notebook(tmp_path / "nb.ipynb", ["x = 10", "print(x * 2)"])
    execute_notebook(nb_path)

    nb = read_notebook(nb_path)
    assert nb.cells[1].outputs[0]["text"] == "20\n"


def test_written_in_place(tmp_path):
    nb_path = make_notebook(tmp_path / "nb.ipynb", ["x = 1"])
    execute_notebook(nb_path)

    nb = read_notebook(nb_path)
    assert nb.cells[0].execution_count == 1


def test_cell_error_raises(tmp_path):
    nb_path = make_notebook(tmp_path / "nb.ipynb", ["raise ValueError('oops')"])

    with pytest.raises(RuntimeError, match="Cell 1 raised an error"):
        execute_notebook(nb_path)


def test_empty_cells_skipped(tmp_path):
    nb_path = make_notebook(tmp_path / "nb.ipynb", ["", "print('hi')"])
    execute_notebook(nb_path)

    nb = read_notebook(nb_path)
    assert nb.cells[0].execution_count is None
    assert nb.cells[1].execution_count == 1
