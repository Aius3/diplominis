"""
check_pasword funckija patikrina ar kodo ilgis didesnis už 5 simbolius
"""
def check_pasword(password):

    if len(password) > 5:
        return True
    else:
        return False