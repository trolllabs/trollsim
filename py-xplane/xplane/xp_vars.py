# Use signed integer type when assigning boolean packet values
XP_True = 0x3F800000
XP_False = 0x00000000

expected_reading = {0: 'sim/test/test_float',
		1: 'sim/joystick/yoke_roll_ratio',
		2: 'sim/joystick/yoke_pitch_ratio',
		3: 'sim/joystick/yoke_heading_ratio'}
