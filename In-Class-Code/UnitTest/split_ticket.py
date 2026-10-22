def split_ticket(total, num_people):
    if num_people <= 0:
        raise ValueError("Number of people must be greater than zero.")
    return total / num_people



if __name__ == "__main__":
    # Example usage
    try:
        print(split_ticket(100, 4))  # Should print 25.0
        print(split_ticket(100, 0))  # Should raise ValueError
    except ValueError as e:
        print(e)