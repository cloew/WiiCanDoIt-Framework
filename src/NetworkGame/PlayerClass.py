
""" Class that represents a Human Palyer               """
""" Holds the ID of the player's wiimote               """
"""  and the color of the RouterNode they will control """
class Player:
    def __init__(self, inID, inColor):
        self.wiiID = inID
        self.color = inColor
