from src.utils.validate import is_valid_positions

def test_valid_4():
    # One known 4-queens solution: (row,col) = (1,2),(2,4),(3,1),(4,3)
    pos = [(1,2),(2,4),(3,1),(4,3)]
    assert is_valid_positions(pos)