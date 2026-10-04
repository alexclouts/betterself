from betterself import calories_per_gram, feels_good, is_strong_password, is_valid_email, total_calories

def test_feels_good():
	assert feels_good()

def test_total_calories():
	assert total_calories(10, 20, 30) == 290

def test_calories_per_gram():
	assert calories_per_gram(200, 50) == 4.0

def test_is_strong_password():
	assert is_strong_password("Secure9!")
	assert not is_strong_password("weakpass")
	assert not is_strong_password("Short9!")

def test_is_valid_email():
	assert is_valid_email("user@example.com")
	assert is_valid_email("first.last+tag@example.co.uk")
	assert not is_valid_email("user@example")
	assert not is_valid_email("user @example.com")
	assert not is_valid_email("us..er@example..com")

