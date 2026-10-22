import pytest

from split_ticket import split_ticket


def test_split_ticket():
     assert split_ticket(100, 4) == 25.0
     assert split_ticket(50, 5) == 10.0
     assert split_ticket(0, 1) == 0.0
     assert split_ticket(100, 1) == 100.0

     with pytest.raises(ValueError):
         split_ticket(100, 0)

     with pytest.raises(ValueError):
        split_ticket(0, 0)
        
def test_value_5():
    assert split_ticket(100,20) ==5